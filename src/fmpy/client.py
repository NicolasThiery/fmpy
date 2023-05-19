import requests
import os
import time
import sys
import urllib
import urllib3
import pandas as pd
from . import urls
from . import utils
from datetime import datetime, timedelta


class FmpClient:

    def __init__(self, api_key=None, rate_limit=300, timeout=5, request_retry=5):
        self.api_key = api_key
        self._rate_limit = rate_limit
        self._rate_limit_reference = utils.get_current_minute()
        self._rate = 0
        self._timeout = timeout
        self._request_retry = request_retry
        self.session = None
        self.allow_period = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        self.connect()

    def connect(self):
        headers = {'Content-Type': 'Application/json'}
        retries =urllib3.util.retry.Retry(total=self._request_retry,
                                          backoff_factor=1,
                                          status_forcelist=[429, 500, 503, 502, 413, 504])
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        self.session.headers.update(headers)

        if self.api_key is None and os.environ.get('FMP_API_KEY'):
            self.api_key = os.environ['FMP_API_KEY']
        elif not self.api_key:
            print('API KEY is empty !')
            sys.exit()

        self.session.params.update({"apikey": self.api_key})

    def disconnect(self):
        if self.session:
            self.session.close()

    def check_rate_limit(self):
        if self._rate >= self._rate_limit:
            time.sleep((datetime.now().replace(second=0, microsecond=0)
                        + timedelta(minutes=1) - datetime.now()).seconds)
        now = utils.get_current_minute()
        if now > self._rate_limit_reference:
            self._rate_limit_reference = now
            self._rate = 0
        self._rate += 1

    def _request(self, url):
        self.check_rate_limit()
        request = self.session.get(url, timeout=self._timeout)
        request.raise_for_status()
        return request.json()

    def make_params(self, parmas_dict):
        return {key: val for key, val in parmas_dict.items() if val is not None}

    def get_symbol_info(self, symbol):
        """
        Description
        ----
        Gives current asset information (include stocks,ETF,Funds,Index,Crypto and Commodities).

        Input
        ----
        symbol (string)
            The asset ticker (for example: "TSLA")

        Output
        ----
        data (list)
            List that contain a data dict with the current asset info
        """
        return self._request(f'{urls.QUOTE}/{symbol}')

    def get_symbol_close_price(self, symbol):
        """
        Description
        ----
        Gives current asset close price (include stocks,ETF,Funds,Index,Crypto and Commodities).

        Input
        ----
        symbol (string)
            The asset ticker (for example: "TSLA")

        Output
        ----
        data (float)
            Asset price
        """
        return self.get_symbol_info(symbol)[0]['price']

    def get_symbols_info(self, symbols):
        """
        Description
        ----
        Gives current information for the provided list of assets (can be stocks,ETF,Funds,Index,Crypto and Commodities).

        Input
        ----
        symbols (list)
            A list of assets (for example: ["TSLA", "BTCUSD"])

        Output
        ----
        data (list)
            List that contain the data dict info for all the asset in the requested list
        """
        if not isinstance(symbols, list):
            raise TypeError('symbols must be a list')
        return self._request(f'{urls.QUOTE}/{",".join(symbols)}')

    def get_historical_data(self, symbol, period='1d', start=None, end=None, get_raw_data=False, datetime_index=False):
        """
        Description
        ----
        Gives current information for the provided list of assets (can be stocks,ETF,Funds,Index,Crypto and Commodities).

        Input
        ----
        symbol (string)
            The asset ticker (for example: "TSLA")
        period (string)
            Candlestick period. Can be '1m', '5m', '15m', '30m', '1h', '4h', '1d' ('1d' by default)
        start (string)
            Start date (formated as %Y-%m-%d)
        end (string)
            End date (formated as %Y-%m-%d)
        get_raw_data (bool)
            Return raw historical data (raw FMP API output)

        Output
        ----
        data (list)
            List that contain the data dict info for all the asset in the requested list
        """
        if period not in self.allow_period:
            raise ValueError(f'{period} period is not allow (allowed periods are {",".join(self.allow_period)})')
        _start = f'{start} 00:00:00' if len(start.split(' ')) == 1 else start
        _end = f'{end} 00:00:00' if len(end.split(' ')) == 1 else end
        for date in [_start, _end]:
            if date and not utils.is_valid_time_format(date):
                raise ValueError(f'{date} as a wrong date format')
        formated_period = utils.format_period(period)
        data = self._get_batch_historical_data(symbol, formated_period, _start, _end)
        if not data:
            return None
        elif get_raw_data:
            return data
        else:
            return self._convert_raw_data_to_df(data, datetime_index)

    @staticmethod
    def _convert_raw_data_to_df(raw_data, datetime_index):
        association_dict = {'Date': 'date', 'Open': 'open', 'High': 'high',
                            'Low': 'low', 'Close': 'close', 'Volume': 'volume'}
        data_dict = {item: [] for item in association_dict.keys()}
        for data in raw_data[::-1]:
            for item in association_dict.keys():
                data_dict[item].append(data[association_dict[item]])
        df = pd.DataFrame.from_dict(data_dict)
        df = df.iloc[::-1]
        if datetime_index:
            df['Date'] = pd.to_datetime(df['Date'])
        return df.set_index('Date')

    def _get_historical_url(self, symbol, period, start, end):
        params = {key: val for key, val in {'from': start, 'to': end}.items() if val}
        return f'{urls.HISTORICAL_PRICE_FULL}/{symbol}?{urllib.parse.urlencode(params)}' if period == '1d' else\
                   f'{urls.HISTORICAL_CHART}/{period}/{symbol}?{urllib.parse.urlencode(params)}'

    def _get_batch_historical_data(self, symbol, period, start, end):
        sanitize_start = start.split(' ')[0]
        sanitize_end = end.split(' ')[0]
        target_start_datetime = datetime.strptime(sanitize_start, '%Y-%m-%d')
        _end = sanitize_end
        batch_data = []
        loop_index = 1
        prev_start = None
        while True:
            url = self._get_historical_url(symbol, period, sanitize_start, _end)
            data = self._request(url)
            if not data:
                return batch_data
            data_list = data if isinstance(data, list) else data['historical']
            new_start = data_list[-1]['date'].split(' ')[0]
            if prev_start == new_start:
                break
            start_index = 0
            end_index = len(data_list)-1
            end_target_datetime = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            for i, item in enumerate(data_list):
                date = f'{item["date"]} 00:00:00' if len(item['date'].split(' ')) == 1 else item["date"]
                if loop_index == 1:
                    start_target_datetime = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                    if datetime.strptime(date, "%Y-%m-%d %H:%M:%S") > start_target_datetime:
                        start_index += 1
                if end_target_datetime >= datetime.strptime(date, "%Y-%m-%d %H:%M:%S"):
                    end_index = i
                    break
                if item['date'].split(' ')[0] == new_start:
                    end_index = i + 1
            sanitize_data = data_list[start_index:end_index][::-1]
            batch_data = sanitize_data + batch_data
            new_start_datetime = datetime.strptime(new_start, '%Y-%m-%d')
            if new_start_datetime <= target_start_datetime:
                break
            _end = datetime.strftime(new_start_datetime - timedelta(days=1), "%Y-%m-%d")
            prev_start = _end
            loop_index += 1
        return batch_data

    def download_historical_data_to_excel(self, symbol, file, period='1d', start=None, end=None, sheet_name=None):
        """
        Description
        ----
        Gives current information for the provided list of assets (can be stocks,ETF,Funds,Index,Crypto and Commodities).

        Input
        ----
        symbol (string)
            The asset ticker (for example: "TSLA")
        period (string)
            Candlestick period. Can be '1m', '5m', '15m', '30m', '1h', '4h', '1d' ('1d' by default)
        start (string)
            Start date (formated as %Y-%m-%d)
        end (string)
            End date (formated as %Y-%m-%d)
        get_raw_data (bool)
            Return raw historical data (raw FMP API output)

        """
        if not isinstance(file, str):
            raise TypeError('The file parameter should be a string')
        if not sheet_name:
            sheet_name = symbol
        df = self.get_historical_data(symbol, period=period, start=start, end=end, get_raw_data=False)
        df.to_excel(file, sheet_name=sheet_name)

    ##### STOCK FUNDAMENTALS #####

    def get_sec_filling(self, symbol, page=None, type=None):
        """
        Description
        ----
        Return the SEC filings.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested SEC filing
        """
        params = {key: val for key, val in {'page': page, 'type': type}.items() if val}
        return self._request(f'{urls.SEC_FILLING}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_financial_statement_list(self):
        """
        Description
        ----
        Return a list of all the financial statement symbol available.

        Output
        ----
        symbol_list (list)
            List that contain all the available financial statement symbol
        """
        return self._request(f'{urls.FINANCIAL_STATEMENT_LIST}')

    def get_income_statement(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return income statements for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol income statement
        """
        params = {key: val for key, val in {'period': period, 'limit': limit}.items() if val}
        return self._request(f'{urls.INCOME_STATEMENT}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_balance_sheet_statement(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return balance sheet statements for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol balance sheet statement
        """
        params = {key: val for key, val in {'period': period, 'limit': limit}.items() if val}
        return self._request(f'{urls.BALANCE_SHEET_STATEMENT}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_cash_flow_statement(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return cash flow statements for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol cash flow statement
        """
        params = {key: val for key, val in {'period': period, 'limit': limit}.items() if val}
        return self._request(f'{urls.CASH_FLOW_STATEMENT}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_income_statement_as_reported(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return as reported income statements for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol income statement
        """
        params = {key: val for key, val in {'period': period, 'limit': limit}.items() if val}
        return self._request(f'{urls.INCOME_STATEMENT_AS_REPORTED}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_balance_sheet_statement_as_reported(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return as reported balance sheet statements for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol balance sheet statement
        """
        params = {key: val for key, val in {'period': period, 'limit': limit}.items() if val}
        return self._request(f'{urls.BALANCE_SHEET_STATEMENT_AS_REPORTED}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_cash_flow_statement_as_reported(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return as reported income statements for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol cash flow statement
        """
        params = {key: val for key, val in {'period': period, 'limit': limit}.items() if val}
        return self._request(f'{urls.CASH_FLOW_STATEMENT_AS_REPORTED}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_financial_statement_as_reported(self, symbol, period=None):
        """
        Description
        ----
        Return as reported financial statements for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol financial statement
        """
        params = {key: val for key, val in {'period': period}.items() if val}
        return self._request(f'{urls.INCOME_STATEMENT_AS_REPORTED}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_financial_reports_dates(self, symbol):
        """
        Description
        ----
        Return all available dates for the requested symbol financial reports.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol financial reports dates
        """
        return self._request(f'{urls.FINANCIAL_REPORTS_DATES}?symbol={symbol}')

    def get_financial_reports_dates_json(self, symbol, year, period=None):
        """
        Description
        ----
        Return the Annual reports on Form 10-K in json format.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol annual report
        """
        _period = 'FY' if not period else period
        params = {key: val for key, val in {'symbol': symbol, 'year': year, 'period': _period}.items() if val}
        return self._request(f'{urls.FINANCIAL_REPORT_JSON}?{urllib.parse.urlencode(params)}')

    def get_shares_float(self, symbol):
        """
        Description
        ----
        Return the symbol shares float.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol shares float
        """
        return self._request(f'{urls.SHARES_FLOAT}?symbol={symbol}')

    def get_all_shares_float(self):
        """
        Description
        ----
        Return all availables shares float.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for all shares float availabale
        """
        return self._request(f'{urls.SHARES_FLOAT}/all')

    def get_sec_rss_feeds(self, page=None, datatype=None, limit=None, type=None, start=None, end=None, isDone=None):
        """
        Description
        ----
        Return SEC RSS (Really Simple Syndication) feeds.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested SED RSS feeds
        """
        _isdone= str(isDone).lower() if isDone else None
        params = {key: val for key, val in {'page': page, 'datatype': datatype, 'limit': limit,
                                            'type': type, 'from':start, 'to': end, 'isDone': _isdone}.items() if val}
        return self._request(f'{urls.RSS_FEED}?{urllib.parse.urlencode(params)}')

    def get_earning_call_transcript(self, symbol, year=None, quarter=None):
        """
        Description
        ----
        Return the Earning call transcript for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested earning call transcript
        """
        params = {key: val for key, val in {'symbol': symbol, 'year': year, 'quarter': quarter}.items() if val}
        return self._request(f'{urls.EARNING_CALL_TRANSCRIPT_V4}?{urllib.parse.urlencode(params)}')

    def get_sec_filling(self, symbol, page=None, type=None):
        """
        Description
        ----
        Return the SEC filings.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested SEC filing
        """
        params = {key: val for key, val in {'page': page, 'type': type}.items() if val}
        return self._request(f'{urls.SEC_FILLING}/{symbol}?{urllib.parse.urlencode(params)}')

    def get_sec_rss_feed_8k(self, page=None, limit=None, start=None, end=None, hasFinancial=None):
        """
        Description
        ----
        Return SEC RSS (Really Simple Syndication) feeds 8K (important events).

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested SED RSS feeds 8K
        """
        _hasFinancial = str(hasFinancial).lower() if hasFinancial else None
        params = {key: val for key, val in {'page': page, 'limit': limit, 'from': start,
                                            'to': end, 'hasFinancial': _hasFinancial}.items() if val}
        return self._request(f'{urls.RSS_FEED_8K}?{urllib.parse.urlencode(params)}')

    def get_company_notes(self, symbol):
        """
        Description
        ----
        Return the list of notes due for a given symbol.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested symbol notes due
        """
        params = {key: val for key, val in {'symbol': symbol}.items() if val}
        return self._request(f'{urls.COMPANY_DUE}?{urllib.parse.urlencode(params)}')

    ##### STOCK FUNDAMENTALS ANALYSIS #####

    def get_ttm_ratios(self, symbol):
        """
        Description
        ----
        Return the company TTM ratios (liquidity Measurement Ratios, Profitability Indicator Ratios, Debt Ratios,
        Operating Performance Ratios, Cash Flow Indicator Ratios and Investment Valuation Ratios).
        For more detail on the formulas go to https://site.financialmodelingprep.com/developer/docs/formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company TTM ratios
        """
        return self._request(f'{urls.RATIOS_TTM}/{symbol}')

    def get_ratios(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return the company ratios.
        For more detail on the formulas go to https://site.financialmodelingprep.com/developer/docs/formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company ratios
        """
        return self._request(f'{urls.RATIOS}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"period": period, "limit": limit}))}')

    def get_score(self, symbol):
        """
        Description
        ----
        Return the company's Piotroski score.
        For more detail on the Piotroski score go to https://site.financialmodelingprep.com/developer/docs/piotroski-score

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company Piotroski score
        """
        return self._request(f'{urls.SCORE}/{symbol}')

    def get_owner_earning(self, symbol):
        """
        Description
        ----
        Return the company's owner earning
        For more detail on the owner earning go to https://site.financialmodelingprep.com/developer/docs/owner-earnings

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company owner earning
        """
        return self._request(f'{urls.SCORE}/{symbol}')

    def get_enterprise_value(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return the annual enterprise value.

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested enterprise value
        """
        return self._request(f'{urls.ENTERPRISE_VALUES}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"period": period, "limit": limit}))}')

    def get_income_statement_growth(self, symbol, limit=None):
        """
        Description
        ----
        Return the company income statement growth

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company income statement growth
        """
        return self._request(f'{urls.INCOME_STATEMENT_GROWTH}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_balance_sheet_growth(self, symbol, limit=None):
        """
        Description
        ----
        Return the company balance sheet growth

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company balance sheet growth
        """
        return self._request(f'{urls.BALANCE_SHEET_STATEMENT_GROWTH}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_cash_flow_growth(self, symbol, limit=None):
        """
        Description
        ----
        Return the company cash flow growth

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company cash flow growth
        """
        return self._request(f'{urls.CASH_FLOW_STATEMENT_GROWTH}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_ttm_key_metrics(self, symbol, limit=None):
        """
        Description
        ----
        Return the company TTM key metrics

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company TTM key metrics
        """
        return self._request(f'{urls.KEY_METRICS_TTM}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_key_metrics(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return the company key metrics

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company key metrics
        """
        return self._request(f'{urls.KEY_METRICS}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"period": period, "limit": limit}))}')

    def get_financial_growth(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return the company financial growth

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company financial growth
        """
        return self._request(f'{urls.FINANCIAL_GROWTH}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"period": period, "limit": limit}))}')

    def get_company_rating(self, symbol):
        """
        Description
        ----
        Return the company rating
        For more detail on the companies rating calculation go to https://site.financialmodelingprep.com/developer/docs/recommendations-formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company rating
        """
        return self._request(f'{urls.RATING}/{symbol}')

    def get_companies_historical_rating(self, symbol, limit=None):
        """
        Description
        ----
        Return the company historical rating
        For more detail on the companies rating calculation go to https://site.financialmodelingprep.com/developer/docs/recommendations-formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company historical rating
        """
        return self._request(f'{urls.HISTORICAL_RATING}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_dcf(self, symbol):
        """
        Description
        ----
        Return the company discounted cash flow value (intrinsic value)
        For more detail on the companies discounted cash flow go to https://site.financialmodelingprep.com/developer/docs/dcf-formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company discounted cash flow
        """
        return self._request(f'{urls.DISCOUNTED_CASH_FLOW}/{symbol}')

    def get_advanced_dcf(self, symbol):
        """
        Description
        ----
        Return the company advanced discounted cash flow value (intrinsic value)
        For more detail on the companies discounted cash flow go to https://site.financialmodelingprep.com/developer/docs/dcf-formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company advanced discounted cash flow
        """
        return self._request(f'{urls.ADVANCED_DISCOUNTED_CASH_FLOW}?'
                             f'{urllib.parse.urlencode(self.make_params({"symbol": symbol}))}')

    def get_advanced_levered_dcf(self, symbol):
        """
        Description
        ----
        Return the company advanced levered discounted cash flow value (intrinsic value)
        For more detail on the companies discounted cash flow go to https://site.financialmodelingprep.com/developer/docs/dcf-formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company advanced levered discounted cash flow
        """
        return self._request(f'{urls.ADVANCED_LEVERED_DISCOUNTED_CASH_FLOW}?'
                             f'{urllib.parse.urlencode(self.make_params({"symbol": symbol}))}')

    def get_historical_dcf(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return the company historical discounted cash flow value (intrinsic value)
        For more detail on the companies discounted cash flow go to https://site.financialmodelingprep.com/developer/docs/dcf-formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company historical discounted cash flow
        """
        return self._request(f'{urls.HISTORICAL_DISCOUNTED_CASH_FLOW_STATEMENT}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"period": period, "limit": limit}))}')

    def get_historical_daily_dcf(self, symbol, limit=None):
        """
        Description
        ----
        Return the company historical daily discounted cash flow value (intrinsic value)
        For more detail on the companies discounted cash flow go to https://site.financialmodelingprep.com/developer/docs/dcf-formula

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company historical daily discounted cash flow
        """
        return self._request(f'{urls.HISTORICAL_DAILY_DISCOUNTED_CASH_FLOW}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    ##### STOCK STATISTICS #####

    def get_historical_social_sentiment(self, symbol, page):
        """
        Description
        ----
        Return the historical Social Media sentiment for stock (time in UTC) (intrinsic value)

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company historical Social Media sentiment
        """
        return self._request(f'{urls.HISTORICAL_SOCIAL_SENTIMENT}?'
                             f'{urllib.parse.urlencode(self.make_params({"symbol": symbol, "page": page}))}')

    def get_trending_social_sentiment(self, type=None, source=None):
        """
        Description
        ----
        Return the Trending Social Media sentiment

        Input
        ----
        type: type of sentiment ('bullish' or 'bearish')
        source: source of the sentiment ('twitter' | 'stocktwits')

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the trending social sentiment
        """
        return self._request(f'{urls.TRENDING_SOCIAL_SENTIMENT}?'
                             f'{urllib.parse.urlencode(self.make_params({"type": type, "source": source}))}')

    def get_social_sentiment_biggest_changes(self, type, source):
        """
        Description
        ----
        Return the Biggest changes in the Social Media sentiment

        Input
        ----
        type: type of sentiment ('bullish' or 'bearish')
        source: source of the sentiment ('twitter' | 'stocktwits')

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the trending social sentiment
        """
        return self._request(f'{urls.CHANGES_SOCIAL_SENTIMENT}?'
                             f'{urllib.parse.urlencode(self.make_params({"type": type, "source": source}))}')

    def get_stock_grade(self, symbol, limit=None):
        """
        Description
        ----
        Return the analysts stock grade

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company stock grade from analysts
        """
        return self._request(f'{urls.STOCK_GRADE}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_earning_surprises(self, symbol):
        """
        Description
        ----
        Return the company earning surprises

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested company earning surprises
        """
        return self._request(f'{urls.EARNING_SURPRISES}/{symbol}')

    def get_analyst_estimates(self, symbol, period=None, limit=None):
        """
        Description
        ----
        Return the annual analyst estimates of a stock

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested stock analyst estimates
        """
        return self._request(f'{urls.ANALYST_ESTIMATES}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"period": period, "limit": limit}))}')

    def get_merges_acquisitions_rss_feed(self, page):
        """
        Description
        ----
        Return the mergers and acquisitions rss feed

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the requested mergers and acquisitions rss feed
        """
        return self._request(f'{urls.MERGES_ACQUISITIONS_RSS_FEED}?'
                             f'{urllib.parse.urlencode(self.make_params({"page": page}))}')

    def search_merges_acquisitions(self, name):
        """
        Description
        ----
        Search the mergers and acquisitions by name

        Output
        ----
        symbol_list (list)
            List that contain the data dict info for the searched mergers and acquisitions
        """
        return self._request(f'{urls.MERGES_ACQUISITIONS_SEARCH}?'
                             f'{urllib.parse.urlencode(self.make_params({"name": name}))}')

    ##### STOCK LIST #####

    def get_stock_list(self):
        """
        Description
        ----
        Return all companies ticker symbols available in FMP

        Output
        ----
        symbol_list (list)
            List the all the available stock
        """
        return self._request(f'{urls.STOCK_LIST}')

    def get_tradable_stock_list(self):
        """
        Description
        ----
        Return all tradable ticker symbols

        Output
        ----
        symbol_list (list)
            List the all the tradable stock
        """
        return self._request(f'{urls.TRADABLE_SYMBOL_LIST}')

    def get_etf_list(self):
        """
        Description
        ----
        Return all ETF symbols available in FMP

        Output
        ----
        symbol_list (list)
            List the all the available etf
        """
        return self._request(f'{urls.ETF_LIST}')

    # STOCK LOOK UP TOOL

    def search(self, input, exchange=None, limit=None):
        """
        Description
        ----
        Search via ticker or company name

        Input
        ----
        input (string)
            Ticker or company name to search

        exchange (string)
            Name of the exchange to search on.
            Valid exchange are :ETF | MUTUAL_FUND | COMMODITY | INDEX | CRYPTO |
                                FOREX | TSX | AMEX | NASDAQ | NYSE | EURONEXT |
                                XETRA | NSE | LSE

        limit (integer)
            Maximum number of results.

        Output
        ----
        symbol_list (list)
            List the all the available etf
        """
        return self._request(f'{urls.SEARCH}?'
                             f'{urllib.parse.urlencode(self.make_params({"query": input, "echange": exchange,"limit":limit}))}')

    def search_ticker(self, input, exchange=None, limit=None):
        """
        Description
        ----
        Search via ticker

        Input
        ----
        input (string)
            Ticker or company name to search

        exchange (string)
            Name of the exchange to search on.
            Valid exchange are :ETF | MUTUAL_FUND | COMMODITY | INDEX | CRYPTO |
                                FOREX | TSX | AMEX | NASDAQ | NYSE | EURONEXT |
                                XETRA | NSE | LSE

        limit (integer)
            Maximum number of results.

        Output
        ----
        symbol_list (list)
            List the all the available etf
        """
        return self._request(f'{urls.SEARCH_TICKER}?'
                             f'{urllib.parse.urlencode(self.make_params({"query": input, "echange": exchange,"limit":limit}))}')

    def search_company(self, input, exchange=None, limit=None):
        """
        Description
        ----
        Search via company name

        Input
        ----
        input (string)
            Ticker or company name to search

        exchange (string)
            Name of the exchange to search on.
            Valid exchange are :ETF | MUTUAL_FUND | COMMODITY | INDEX | CRYPTO |
                                FOREX | TSX | AMEX | NASDAQ | NYSE | EURONEXT |
                                XETRA | NSE | LSE

        limit (integer)
            Maximum number of results.

        Output
        ----
        symbol_list (list)
            List the all the available etf
        """
        return self._request(f'{urls.SEARCH_NAME}?'
                             f'{urllib.parse.urlencode(self.make_params({"query": input, "echange": exchange,"limit":limit}))}')

    # STOCK SCREENER

    def stock_screener(self, marketCapMoreThan=None, marketCapLowerThan=None, priceMoreThan=None, priceLowerThan=None,
                             betaMoreThan=None, betaLowerThan=None, volumeMoreThan=None, volumeLowerThan=None,
                             dividendMoreThan=None, dividendLowerThan=None, isEtf=None, isActivelyTrading=None,
                             sector=None, industry=None, country=None, exchange=None, limit=None):
        """
        Description
        ----
        Get the stock screener based on criterias.

        Input
        ----
        marketCapMoreThan (integer)
            Specify the minium marketCap of the stock screener.

        marketCapLowerThan (integer)
            Specify the maximum marketCap of the stock screener.

        priceMoreThan (integer)
            Specify the minimum price of the stock screener.

        priceLowerThan (integer)
            Specify the maximum price of the stock screener.

        betaMoreThan (float)
            Specify the minimum beta of the stock screener.

        betaLowerThan (float)
            Specify the maximum beta of the stock screener.

        volumeMoreThan (integer)
            Specify the minimum volume of the stock screener.

        volumeLowerThan (integer)
            Specify the maximum volume of the stock screener.

        dividendMoreThan (float)
            Specify the minimum dividend of the stock screener.

        dividendLowerThan (float)
            Specify the maximum dividend of the stock screener.

        isEtf (bool)
            Specify if all stock in the screener should be ETF

        isActivelyTrading (bool)
            Specify if all stock in the screener should be actively trading

        sector (string)
            Specify the sector of the stock screener.
            Possible values are : Consumer Cyclical - Energy - Technology - Industrials -
                                  Financial Services - Basic Materials - Communication Services -
                                  Consumer Defensive - Healthcare - Real Estate - Utilities -
                                  Industrial Goods - Financial - Services - Conglomerates

        Industry (string)
            Specify the industry of the stock screener
            Possible values are : Autos - Banks - Banks Diversified - Software - Banks Regional -
                                  Beverages Alcoholic - Beverages Brewers - Beverages Non-Alcoholic

        Country (string)
            Specify the stock's Country for the screener
            Example : US - UK - MX - BR - RU - HK - CA

        exchange (string)
            Specify the exchange of the stock screener
            Example : nyse - nasdaq - amex - euronext - tsx - etf - mutual_fund

        limit (integer)
            Maximum number of results in the stock screener.

        Output
        ----
        symbol_list (list)
            List the all the available etf
        """
        params = {key: val for key, val in {"marketCapMoreThan": marketCapMoreThan, "marketCapLowerThan": marketCapLowerThan,
                                            "priceMoreThan": priceMoreThan, "priceLowerThan": priceLowerThan,
                                            "betaMoreThan": betaMoreThan, "betaLowerThan": betaLowerThan,
                                            "volumeMoreThan": volumeMoreThan, "volumeLowerThan": volumeLowerThan,
                                            "dividendMoreThan": dividendMoreThan, "dividendLowerThan": dividendLowerThan,
                                            "isEtf": isEtf, "isActivelyTrading": isActivelyTrading, "sector": sector,
                                            "industry": industry, "country": country, "exchange": exchange, "limit": limit}.items() if val}
        return self._request(f'{urls.STOCK_SCREENER}?'
                             f'{urllib.parse.urlencode(params)}')

    def get_all_countries(self):
        """
        Description
        ----
        Return all available countries

        Output
        ----
        country_list (list)
            List the all available countries
        """
        return self._request(f'{urls.GET_ALL_COUNTRIES}')

    # COMPANY INFORMATION

    def get_company_profile(self, symbol):
        """
        Description
        ----
        Return the company profile

        Input
        ----
        symbol (string)
            The symbol of the company

        Output
        ----
        data_dict (list)
            Dict containing company profile data
        """
        return self._request(f'{urls.PROFILE}/{symbol}')

    def get_company_key_executives(self, symbol):
        """
        Description
        ----
        Return the company key executives

        Input
        ----
        symbol (string)
            The symbol of the company

        Output
        ----
        data_dict (list)
            Dict containing company key executive
        """
        return self._request(f'{urls.KEY_EXECUTIVES}/{symbol}')

    def get_marketCap(self, symbol):
        """
        Description
        ----
        Return the market capitalization

        Input
        ----
        symbol (string)
            The symbol of the financial asset

        Output
        ----
        data_dict (list)
            Dict containing market capitalization data
        """
        return self._request(f'{urls.MARKET_CAP}/{symbol}')

    def get_historical_marketCap(self, symbol, limit=None):
        """
        Description
        ----
        Return the historical market capitalization

        Input
        ----
        symbol (string)
            The symbol of the financial asset

        limit (integer)
            Maximum number of historical market capitalization

        Output
        ----
        data_dict (list)
            Dict containing historical market capitalization data
        """
        return self._request(f'{urls.HISTORICAL_MARKET_CAP}/{symbol}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_company_outlook(self, symbol):
        """
        Description
        ----
        Return the company outlook

        Input
        ----
        symbol (string)
            The symbol of the financial asset

        Output
        ----
        data_dict (list)
            Dict containing the company outlook data
        """
        return self._request(f'{urls.COMPANY_OUTLOOK}?'
                             f'{urllib.parse.urlencode(self.make_params({"symbol": symbol}))}')

    def get_stock_peers(self, symbol):
        """
        Description
        ----
        Return the stock peers based on sector, exchange and market capitalization

        Input
        ----
        symbol (string)
            The symbol of the financial asset

        Output
        ----
        data_dict (list)
            Dict containing the stock peers
        """
        return self._request(f'{urls.STOCK_PEERS}?'
                             f'{urllib.parse.urlencode(self.make_params({"symbol": symbol}))}')

    def get_market_open(self):
        """
        Description
        ----
        Return NYSE Trading hours and Holidays

        Output
        ----
        data_dict (list)
            Dict containing the NYSE Trading hours and Holidays
        """
        return self._request(f'{urls.IS_MARKET_OPEN}')

    def get_delisted_companies(self, page=None):
        """
        Description
        ----
        Return the delisted companies

        Input
        ----
        page (integer)
            Number of the delisted companies page

        Output
        ----
        data_dict (list)
            Dict containing the delisted companies
        """
        return self._request(f'{urls.DELISTED_COMPANIES}?'
                             f'{urllib.parse.urlencode(self.make_params({"page": page}))}')

    def get_symbol_changes(self):
        """
        Description
        ----
        Return the symbol that have been changed

        Output
        ----
        data_dict (list)
            Dict containing all the symbol changed
        """
        return self._request(f'{urls.SYMBOL_CHANGE}')

    def get_company_core_info(self, symbol):
        """
        Description
        ----
        Return the company core information

        Input
        ----
        symbol (string)
            The symbol of the company

        Output
        ----
        data_dict (list)
            Dict containing the company core inforamtion
        """
        return self._request(f'{urls.COMPANY_CORE_INFO}?'
                             f'{urllib.parse.urlencode(self.make_params({"symbol": symbol}))}')

    # MARKET PERFORMANCE

    def get_sectors_pe_ratio(self, date, exchange=None):
        """
        Description
        ----
        Return the price to earning ratio for all sectors

        Input
        ----
        date (string)
            PE date with format %Y-%m-%d

        exchange (string)
            name of the exchange

        Output
        ----
        data_dict (list)
            Dict containing the sectors price to earning ratio
        """
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f'{date} as a wrong date format')
        else:
            return self._request(f'{urls.SECTOR_PRICE_EARNING_RATIO}?'
                                 f'{urllib.parse.urlencode(self.make_params({"date": date, "exchange": exchange}))}')

    def get_industries_pe_ratio(self, date, exchange=None):
        """
        Description
        ----
        Return the price to earning ratio for all industries

        Input
        ----
        date (string)
            PE date with format %Y-%m-%d

        exchange (string)
            name of the exchange

        Output
        ----
        data_dict (list)
            Dict containing the industries price to earning ratio
        """
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f'{date} as a wrong date format')
        else:
            return self._request(f'{urls.INDUSTRY_PRICE_EARNING_RATIO}?'
                                 f'{urllib.parse.urlencode(self.make_params({"date": date, "exchange": exchange}))}')

    def get_sector_performance(self):
        """
        Description
        ----
        Return the performance sector by sector

        Output
        ----
        data_dict (list)
            Dict containing all sector performance data
        """
        return self._request(f'{urls.SECTOR_PERFORMANCE}')

    def get_historical_sector_performance(self, limit=None):
        """
        Description
        ----
        Return the historical sector performance sector

        Output
        ----
        data_dict (list)
            Dict containing the historical sector performance data
        """
        return self._request(f'{urls.HISTORICAL_SECTOR_PERFORMANCE}?'
                             f'{urllib.parse.urlencode(self.make_params({"limit": limit}))}')

    def get_most_gainers(self):
        """
        Description
        ----
        Return the most gainer stock companies

        Output
        ----
        data_dict (list)
            Dict containing the most gainer stock companies data
        """
        return self._request(f'{urls.MOST_GAINER_STOCK}')

    def get_most_losers(self):
        """
        Description
        ----
        Return the most losers stock companies

        Output
        ----
        data_dict (list)
            Dict containing the most losers stock companies data
        """
        return self._request(f'{urls.MOST_LOSER_STOCK}')

    def get_most_actives(self):
        """
        Description
        ----
        Return the most actives stock companies

        Output
        ----
        data_dict (list)
            Dict containing the most actives stock companies data
        """
        return self._request(f'{urls.MOST_ACTIVE_STOCK}')

    # ECONOMICS

    def get_market_risk_premium(self):
        """
        Description
        ----
        Return the market risk premium country by country

        Output
        ----
        data_dict (list)
            Dict containing the market risk premium
        """
        return self._request(f'{urls.MARKET_RISK_PREMIUM}')

    def get_historical_treasury_rates(self, start=None, end=None):
        """
        Description
        ----
        Return the historical treasury rate (wihtin a maximum interval of 3 months)

        Input
        ----
        start (string)
            start date with format %Y-%m-%d

        end (string)
            end date with format %Y-%m-%d

        Output
        ----
        data_dict (list)
            Dict containing the historical treasury rates
        """
        for date in [start, end]:
            if date:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f'{date} as a wrong date format')
        return self._request(f'{urls.HISTORICAL_TREASURY}?'
                                 f'{urllib.parse.urlencode(self.make_params({"from": start, "to": end}))}')

    def get_economic_indicators(self, source, start=None, end=None):
        """
        Description
        ----
        Return all economic indicators which are: GDP | realGDP | nominalPotentialGDP | realGDPPerCapita |
                                                  federalFunds | CPI | inflationRate | inflation | retailSales |
                                                  consumerSentiment | durableGoods | unemploymentRate | totalNonfarmPayroll |
                                                  initialClaims | industrialProductionTotalIndex | newPrivatelyOwnedHousingUnitsStartedTotalUnits |
                                                  totalVehicleSales | retailMoneyFunds | smoothedUSRecessionProbabilities | 3MonthOr90DayRatesAndYieldsCertificatesOfDeposit |
                                                  commercialBankInterestRateOnCreditCardPlansAllAccounts | 30YearFixedRateMortgageAverage | 15YearFixedRateMortgageAverage

        Input
        ----
        source (string)
            name of the source.
            Example: realGDP, federalFunds, CPI

        start (string)
            start date with format %Y-%m-%d

        start (string)
            end date with format %Y-%m-%d

        Output
        ----
        data_dict (list)
            Dict containing the historical treasury rates
        """
        for date in [start, end]:
            if date:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f'{date} as a wrong date format')
        return self._request(f'{urls.ECONOMICS_INDICATOR}?'
                                 f'{urllib.parse.urlencode(self.make_params({"name": source, "from": start, "to": end}))}')