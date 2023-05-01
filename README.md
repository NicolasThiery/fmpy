# fmpy
A python wrapper for the [Financial Modeling Prep](https://site.financialmodelingprep.com/) (FMP) API (unofficial). This package focus on providing a simple
and powerful interface for the FMP API. 

For more information on subscription plans and obtaining an API key, please visit the [FMP website](https://site.financialmodelingprep.com/developer/docs/pricing/).

## Installation
***
Install fmpy using the pip command:
```
$ pip install fmpy
```

## Usage
***
To begin, you need to create an FmpClient object by passing your API key (provided by FMP) as parameter:
```
import fmpy as fp

client = FmpClient(api_key="YOU_API_KEY")
```

Note that fmpy allow you have to store your API key in as an environment variable under the name 
**FMP_API_KEY** (in that case no need to provide the *api_key* parameter for the FmpClient instantiation)

FmpClient can be initialised with other parameters:

    rate_limit: number of call per minute tolerance (300 by default). This allow to not exceed the rate limit
    timeout: number of seconds to wait a request before raising a timeout (5 by default)
    request_retry: number of request retries before abording (5 by default)

Here is an example:
```
import fmpy as fp

client = FmpClient(api_key="YOU_API_KEY", rate_limit=750, timeout=20, request_retry=1)
# Will not make more than 750 requests per minute, 
# with 20s of timeout and a potential request retry limited to 1
```

## Historical data
```
import fmpy as fp

client = FmpClient(api_key="YOU_API_KEY")
hist_data = client.get_historical_data('TSLA', period='1h', start='2020-01-02', end='2022-06-25')
# Retreive historical 1h candles for Tesla stock between 2020-01-02 and 2022-06-25
```


## Licence
***
© 2021 Nicolas Thiery

This repository is licensed under the MIT license See LICENSE for details.

Please note that this package is not endorsed, supported, or affiliated with FMP.
We do not have any formal relationship with FMP, nor do we receive any financial compensation for developing or distributing this package.
