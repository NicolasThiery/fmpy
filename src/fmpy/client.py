import requests
import os
import time
import sys
import urllib
import urllib3
import pandas as pd
from src.fmpy import urls
from src.fmpy import utils
from datetime import datetime, timedelta


class FmpClient:

    rate_limit = 300

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

    def get_historical_data(self, symbol, period='1d', start=None, end=None, get_raw_data=False):
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
            return self._convert_raw_data_to_df(data)

    @staticmethod
    def _convert_raw_data_to_df(raw_data):
        association_dict = {'Date': 'date', 'Open': 'open', 'High': 'high',
                            'Low': 'low', 'Close': 'close', 'Volume': 'volume'}
        data_dict = {item: [] for item in association_dict.keys()}
        for data in raw_data[::-1]:
            for item in association_dict.keys():
                data_dict[item].append(data[association_dict[item]])
        df = pd.DataFrame.from_dict(data_dict)
        df = df.iloc[::-1]
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
                if not batch_data:
                    return None
                else:
                    return batch_data
            data_list = data if isinstance(data, list) else data['historical']
            new_start = data_list[-1]['date'].split(' ')[0]
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
                    end_index = i + 1
                    break
                if item['date'].split(' ')[0] == new_start:
                    end_index = i + 1
            sanitize_data = data_list[start_index:end_index][::-1]
            batch_data = sanitize_data + batch_data
            new_start_datetime = datetime.strptime(new_start, '%Y-%m-%d')
            if new_start_datetime <= target_start_datetime or prev_start == new_start:
                break
            _end = new_start
            prev_start = new_start
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

    ##### STOCK STATISTICS #####