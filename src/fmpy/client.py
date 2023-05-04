import requests
import os
import time
import sys
import urllib
import urllib3
import pandas as pd
from fmpy import urls
from fmpy import utils
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
        for date in [start, end]:
            if date and not utils.is_valid_time_format(date):
                raise ValueError(f'{date} as a wrong date format')
        formated_period = utils.format_period(period)
        data = self._get_batch_historical_data(symbol, formated_period, start, end)
        if not data:
            return None
        elif get_raw_data:
            return data
        else:
            return self._convert_raw_data_to_df(data)

    def _get_historical_url(self, symbol, period, start, end):
        params = {key: val for key, val in {'from': start, 'to': end}.items() if val}
        return f'{urls.HISTORICAL_PRICE_FULL}/{symbol}?{urllib.parse.urlencode(params)}' if period == '1d' else\
                   f'{urls.HISTORICAL_CHART}/{period}/{symbol}?{urllib.parse.urlencode(params)}'

    def _get_batch_historical_data(self, symbol, period, start, end):
        target_start_datetime = datetime.strptime(start, '%Y-%m-%d')
        _end = end
        batch_data = []
        end_date = None
        prev_start = None
        while True:
            url = self._get_historical_url(symbol, period, start, _end)
            data = self._request(url)
            if not data:
                return None
            data_list = data if isinstance(data, list) else data['historical']
            new_start = datetime.strftime(datetime.strptime(data_list[-1]['date'].split(' ')[0], '%Y-%m-%d') - timedelta(days=3), '%Y-%m-%d')
            sanitize_data = utils.limit_data_list(data_list, date_target=new_start, end_target=end_date)
            batch_data = sanitize_data + batch_data
            end_date = new_start
            new_start_datetime = datetime.strptime(new_start, '%Y-%m-%d')
            if new_start_datetime <= target_start_datetime or prev_start == new_start:
                break
            _end = new_start
            prev_start = new_start
        return batch_data

    def _convert_raw_data_to_df(self, raw_data):
        data_dict = {item: [] for item in raw_data[0].keys()}
        for data in raw_data[::-1]:
            for key, value in data.items():
                data_dict[key].append(value)
        df = pd.DataFrame.from_dict(data_dict)
        df = df.iloc[::-1]
        return df.set_index('date')

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

