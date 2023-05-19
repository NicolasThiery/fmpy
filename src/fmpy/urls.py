BASE_URL = 'https://financialmodelingprep.com'
API_V3_URL = f'{BASE_URL}/api/v3'
API_V4_URL = f'{BASE_URL}/api/v4'

# STOCK FUNDAMENTALS
FINANCIAL_STATEMENT_LIST = f'{API_V3_URL}/financial-statement-symbol-lists'
INCOME_STATEMENT = f'{API_V3_URL}/income-statement'
BALANCE_SHEET_STATEMENT = f'{API_V3_URL}/balance-sheet-statement'
CASH_FLOW_STATEMENT = f'{API_V3_URL}/cash-flow-statement'
REVENUE_PRODUCT_SEGMENTATION = f'{API_V4_URL}/revenue-product-segmentation'
REVENUE_GEOGRAPHIC_SEGMENTATION = f'{API_V4_URL}/revenue-geographic-segmentation'
INCOME_STATEMENT_AS_REPORTED = f'{API_V3_URL}/income-statement-as-reported'
BALANCE_SHEET_STATEMENT_AS_REPORTED = f'{API_V3_URL}/balance-sheet-statement-as-reported'
CASH_FLOW_STATEMENT_AS_REPORTED = f'{API_V3_URL}/cash-flow-statement-as-reported'
FULL_FINANCIAL_STATEMENT_AS_REPORTED = f'{API_V3_URL}/financial-statement-full-as-reported'
FINANCIAL_REPORTS_DATES = f'{API_V4_URL}/financial-reports-dates'
FINANCIAL_REPORT_JSON = f'{API_V4_URL}/financial-reports-json'
FINANCIAL_REPORT_EXCEL = f'{API_V4_URL}/financial-reports-xlsx'
SHARES_FLOAT = f'{API_V4_URL}/shares_float'
RSS_FEED = f'{API_V3_URL}/rss_feed'
EARNING_CALL_TRANSCRIPT_V3 = f'{API_V3_URL}/earning_call_transcript'
EARNING_CALL_TRANSCRIPT_V4 = f'{API_V4_URL}/earning_call_transcript'
BATCH_EARNING_CALL_TRANSCRIPT = f'{API_V4_URL}/batch_earning_call_transcript'
SEC_FILLING = f'{API_V3_URL}/sec_filings'
RSS_FEED_8K = f'{API_V4_URL}/rss_feed_8k'
COMPANY_DUE = f'{API_V4_URL}/company-notes'

# STOCK FUNDAMENTALS ANALYSIS
RATIOS = f'{API_V3_URL}/ratios'
RATIOS_TTM = f'{API_V3_URL}/ratios-ttm'
SCORE = f'{API_V4_URL}/score'
OWNER_EARNING = f'{API_V4_URL}/owner_earnings'
ENTERPRISE_VALUES = f'{API_V3_URL}/enterprise-values'
INCOME_STATEMENT_GROWTH = f'{API_V3_URL}/income-statement-growth'
BALANCE_SHEET_STATEMENT_GROWTH = f'{API_V3_URL}/balance-sheet-statement-growth'
CASH_FLOW_STATEMENT_GROWTH = f'{API_V3_URL}/cash-flow-statement-growth'
KEY_METRICS_TTM = f'{API_V3_URL}/key-metrics-ttm'
KEY_METRICS = f'{API_V3_URL}/key-metrics'
FINANCIAL_GROWTH = f'{API_V3_URL}/financial-growth'
RATING = f'{API_V3_URL}/rating'
HISTORICAL_RATING = f'{API_V3_URL}/historical-rating'
DISCOUNTED_CASH_FLOW = f'{API_V3_URL}/discounted-cash-flow'
ADVANCED_DISCOUNTED_CASH_FLOW = f'{API_V4_URL}/advanced_discounted_cash_flow'
ADVANCED_LEVERED_DISCOUNTED_CASH_FLOW = f'{API_V4_URL}/advanced_levered_discounted_cash_flow'
HISTORICAL_DISCOUNTED_CASH_FLOW_STATEMENT = f'{API_V3_URL}/historical-discounted-cash-flow-statement'
HISTORICAL_DAILY_DISCOUNTED_CASH_FLOW = f'{API_V3_URL}/historical-daily-discounted-cash-flow'

# INSTITUTIONAL STOCK OWNERSHIP
INSTITUTIONAL_OWNERSHIP = f'{API_V4_URL}/institutional-ownership'
SYMBOL_OWNERSHIP = f'{INSTITUTIONAL_OWNERSHIP}/symbol-ownership'
INSTITUTIONAL_HOLDERS = f'{INSTITUTIONAL_OWNERSHIP}/institutional-holders/symbol-ownership-percent'
PORTFOLIO_HOLDING_SUMMARY = f'{INSTITUTIONAL_OWNERSHIP}/portfolio-holdings-summary'
INSTITUTIONAL_HOLDERS_RSS_FEED = f'{INSTITUTIONAL_OWNERSHIP}/rss_feed'
INSTITUTIONAL_HOLDERS_LIST = f'{INSTITUTIONAL_OWNERSHIP}/list'
INSTITUTIONAL_HOLDERS_NAME = f'{INSTITUTIONAL_OWNERSHIP}/name'
INSTITUTIONAL_HOLDERS_PORTFOLIO_DATE = f'{INSTITUTIONAL_OWNERSHIP}/portfolio-date'
INSTITUTIONAL_HOLDERS_BY_SHAREs = f'{INSTITUTIONAL_OWNERSHIP}/institutional-holders/symbol-ownership'
INSTITUTIONAL_HOLDERS_PORTFOLIO_SUMMARY = f'{INSTITUTIONAL_OWNERSHIP}industry/portfolio-holdings-summary'
INSTITUTIONAL_HOLDERS_PORTFOLIO_COMPOSITION = f'{INSTITUTIONAL_OWNERSHIP}/portfolio-holdings'

# ENVIRONMENTAL SOCIAL GOVERNANCE
ESG_SCORE = f'{API_V4_URL}/esg-environmental-social-governance-data'
ESG_RISK_RATING = f'{API_V4_URL}/esg-environmental-social-governance-data-ratings'
ESG_BENCHMARK = f'{API_V4_URL}/esg-environmental-social-governance-sector-benchmark'

# PRIVATE COMPANIES FUNDRAISING DATA
CROWDFUNDING_OFFERING_RSS_FEED = f'{API_V4_URL}/crowdfunding-offerings-rss-feed'
CROWDFUNDING_OFFERING_SEARCH = f'{API_V4_URL}/crowdfunding-offerings/search'
CROWDFUNDING_OFFERING = f'{API_V4_URL}/crowdfunding-offerings'
FUNDRAISING_RSS_FEED = f'{API_V4_URL}/fundraising-rss-feed'
FUNDRAISING_SEARCH = f'{API_V4_URL}/fundraising/search'
FUNDRAISING = f'{API_V4_URL}/fundraising'

# PRICE TARGET
PRICE_TARGET = f'{API_V4_URL}/price-target'
PRICE_TARGET_SUMMARY = f'{API_V4_URL}/price-target-summary'
PRICE_TARGET_BY_ANALYST_NAME = f'{API_V4_URL}/price-target-analyst-name'
PRICE_TARGET_BY_ANALYST_COMPANY = f'{API_V4_URL}/price-target-analyst-company'
PRICE_TARGET_CONSENSUS = f'{API_V4_URL}/price-target-consensus'
PRICE_TARGET_RSS_FEED = f'{API_V4_URL}/price-target-rss-feed'

# UPGRADE AND DOWNGRADES
UPDOWNGRADES = f'{API_V4_URL}/upgrades-downgrades'
UPDOWNGRADES_RSS_FEED = f'{API_V4_URL}/upgrades-downgrades-rss-feed'
UPDOWNGRADES_CONSENSUS = f'{API_V4_URL}/upgrades-downgrades-consensus'
UPDOWNGRADES_GRADING_COMPANY = f'{API_V4_URL}/upgrades-downgrades-grading-company'

# HISTORICAL MUTUAL FOND HOLDINGS
MUTUAL_FOND_HOLDINGS = f'{API_V4_URL}/mutual-fund-holdings'
MUTUAL_FOND_HOLDINGS_PORTFOLIO_DATE = f'{MUTUAL_FOND_HOLDINGS}/portfolio-date'
MUTUAL_FOND_HOLDINGS_NAME_SEARCH = f'{MUTUAL_FOND_HOLDINGS}/name'
ETF_HOLDINGS = f'{API_V4_URL}/etf-holdings'
ETF_HOLDINGS_PORTFOLIO_DATE = f'{ETF_HOLDINGS}/portfolio-date'

# HISTORICAL NUMBER OF EMPLOYEES
HISTORICAL_EMPLOYEE_COUNT = f'{API_V4_URL}/historical/employee_count'

# EXECUTIVE COMPENSATION
EXECUITVE_COMPENSATION = f'{API_V4_URL}/governance/executive_compensation'
EXECUITVE_COMPENSATION_BENCHMARK = f'{API_V4_URL}/executive-compensation-benchmark'

# INDIVIDUAL BENEFICIAL OWNERSHIP
INDIVIDUAL_BENEFICIAL_OWNERSHIP = f'{API_V4_URL}/insider/ownership/acquisition_of_beneficial_ownership'

# EARNING CALENDAR
EARNING_CALENDAR = f'{API_V3_URL}/earning_calendar'
HISTORICAL_EARNING_CALENDAR = f'{API_V3_URL}/historical/earning_calendar'
EARNING_CALENDAR_CONFIRMED = f'{API_V4_URL}/earning-calendar-confirmed'
IPO_CALENDAR = f'{API_V3_URL}/ipo_calendar'
IPO_CALENDAR_PROSPECTUS = f'{API_V4_URL}/ipo-calendar-prospectus'
IPO_CALENDAR_CONFIRMED = f'{API_V4_URL}/ipo-calendar-confirmed'
STOCK_SPLIT_CALENDAR = f'{API_V3_URL}/stock_split_calendar'
STOCK_DIVIDEND_CALENDAR = f'{API_V3_URL}/stock_dividend_calendar'
HISTORICAL_DIVIDENDS = f'{API_V3_URL}/historical-price-full/stock_dividend'
ECONOMIC_CALENDAR = f'{API_V3_URL}/economic_calendar'

# STOCK LOOK UP TOOL
SEARCH = f'{API_V3_URL}/search'
SEARCH_TICKER = f'{API_V3_URL}/search-ticker'
SEARCH_NAME = f'{API_V3_URL}/search-name'

# STOCK SCREENER
STOCK_SCREENER = f'{API_V3_URL}/stock-screener'
GET_ALL_COUNTRIES = f'{API_V3_URL}/get-all-countries'

# COMPANY INFORMATION
PROFILE = f'{API_V3_URL}/profile'
KEY_EXECUTIVES = f'{API_V3_URL}/key-executives'
MARKET_CAP = f'{API_V3_URL}/market-capitalization'
HISTORICAL_MARKET_CAP = f'{API_V3_URL}/historical-market-capitalization'
COMPANY_OUTLOOK = f'{API_V4_URL}/company-outlook'
STOCK_PEERS = f'{API_V4_URL}/stock_peers'
IS_MARKET_OPEN = f'{API_V3_URL}/is-the-market-open'
DELISTED_COMPANIES = f'{API_V3_URL}/delisted-companies'
SYMBOL_CHANGE = f'{API_V4_URL}/symbol_change'
COMPANY_CORE_INFO = f'{API_V4_URL}/company-core-information'

# STOCK NEWS
FMP_ARTICLES = f'{API_V3_URL}/fmp/articles'
STOCK_NEWS = f'{API_V3_URL}/stock_news'
STOCK_SENTIMENTS_RSS_FEED = f'{API_V4_URL}/stock-news-sentiments-rss-feed'
CRYPTO_NEWS = f'{API_V4_URL}/crypto_news'
FOREX_NEWS = f'{API_V4_URL}/forex_news'
GENERAL_NEWS = f'{API_V4_URL}/general_news'
PRESS_RELEASES = f'{API_V3_URL}/press-releases'

# MARKET PERFORMANCE
SECTOR_PRICE_EARNING_RATIO = f'{API_V4_URL}/sector_price_earning_ratio'
INDUSTRY_PRICE_EARNING_RATIO = f'{API_V4_URL}/industry_price_earning_ratio'
SECTOR_PERFORMANCE = f'{API_V3_URL}/sector-performance'
HISTORICAL_SECTOR_PERFORMANCE = f'{API_V3_URL}/historical-sectors-performance'
MOST_GAINER_STOCK = f'{API_V3_URL}/stock_market/gainers'
MOST_LOSER_STOCK = f'{API_V3_URL}/stock_market/losers'
MOST_ACTIVE_STOCK = f'{API_V3_URL}/stock_market/actives'

# ADVANCED DATA
STANDARD_INDUSTRIAL_CLASSIFICATION = f'{API_V4_URL}/standard_industrial_classification'
ALL_STANDARD_INDUSTRIAL_CLASSIFICATION = f'{API_V4_URL}/standard_industrial_classification/all'
STANDARD_INDUSTRIAL_CLASSIFICATION_LIST = f'{API_V4_URL}/standard_industrial_classification_list'
COT_LIST = f'{API_V4_URL}/commitment_of_traders_report/list'
COT_REPORT = f'{API_V4_URL}/commitment_of_traders_report'
COT_REPORT_LIST = f'{API_V4_URL}/commitment_of_traders_report/ES'
COT_ANALYSIS = f'{API_V4_URL}/commitment_of_traders_report_analysis'

# STOCK STATISTICS
HISTORICAL_SOCIAL_SENTIMENT = f'{API_V4_URL}/historical/social-sentiment'
TRENDING_SOCIAL_SENTIMENT = f'{API_V4_URL}/social-sentiment/trending'
CHANGES_SOCIAL_SENTIMENT = f'{API_V4_URL}/social-sentiments/change'
STOCK_GRADE = f'{API_V3_URL}/grade'
EARNING_SURPRISES = f'{API_V3_URL}/earnings-surprises'
ANALYST_ESTIMATES = f'{API_V3_URL}/analyst-estimates'
MERGES_ACQUISITIONS_RSS_FEED = f'{API_V4_URL}/mergers-acquisitions-rss-feed'
MERGES_ACQUISITIONS_SEARCH = f'{API_V4_URL}/mergers-acquisitions/search'

# STOCK INSIDER
INSIDER_TRADING = f'{API_V4_URL}/insider-trading'
INSIDER_TRADING_TRANSACTION_TYPES_LIST = f'{API_V4_URL}/insider-trading-transaction-type'
CIK_NAME = f'{API_V4_URL}/mapper-cik-name'
CIK_COMPANY = f'{API_V4_URL}/mapper-cik-company'
INSIDER_ROASTER = f'{API_V4_URL}/insider-roaster'
INSIDER_ROASTER_STATISTIC = f'{API_V4_URL}/insider-roaster-statistic'
INSIDER_TRADING_RSS_FEED = f'{API_V4_URL}/insider-trading-rss-feed'
FAIL_TO_DELIVER = f'{API_V4_URL}/fail_to_deliver'

# SENATE TRADING
SENATE_TRADING = f'{API_V4_URL}/senate-trading'
SENETE_TRADING_RSS_FEED = f'{API_V4_URL}/senate-trading-rss-feed'
SENATE_DISCLOSURE = f'{API_V4_URL}/senate-disclosure'
SENATE_DISCLOSURE_RSS_FEED = f'{API_V4_URL}/senate-disclosure-rss-feed'

# ECONOMICS
MARKET_RISK_PREMIUM = f'{API_V4_URL}/market_risk_premium'
HISTORICAL_TREASURY = f'{API_V4_URL}/treasury'
ECONOMICS_INDICATOR = f'{API_V4_URL}/economic'

# STOCK PRICE
QUOTE = f'{API_V3_URL}/quote'
OTC_REAL_TIME = f'{API_V3_URL}/otc/real-time-price'
PRICE_CHANGE = f'{API_V3_URL}/stock-price-change'
QUOTE_REAL_TIME = f'{API_V3_URL}/quote-short'
QUOTES = f'{API_V3_URL}/quotes'
HISTORICAL_CHART = f'{API_V3_URL}/historical-chart'
HISTORICAL_PRICE_FULL = f'{API_V3_URL}/historical-price-full'
HISTORICAL_PRICE_FULL_SPLITS = f'{HISTORICAL_PRICE_FULL}/stock_split'
SUVIVORSHIP_BIAS_FREE_EOD = f'{API_V4_URL}/historical-price-full'
TECHNICAL_INDICATOR = f'{API_V3_URL}/technical_indicator'
DAILY_TECHNICAL_INDICATOR = f'{TECHNICAL_INDICATOR}/daily'

# FUND HOLDINGS
ETF_HOLDER = f'{API_V3_URL}/etf-holder'
ETF_INFO = f'{API_V4_URL}/etf-info'
FUND_INSTITUTIONAL_HOLDERS = f'{API_V3_URL}/institutional-holder'
MUTUAL_FUND_HOLDER = f'{API_V3_URL}/mutual-fund-holder'
ETF_SECTOR_WEIGHTINGS = f'{API_V3_URL}/etf-sector-weightings'
ETF_COUNTRY_WEIGHTINGS = f'{API_V3_URL}/etf-country-weightings'
ETF_STOCK_EXPOSURE = f'{API_V3_URL}/etf-stock-exposure'
CIK_LIST = f'{API_V3_URL}/cik_list'
CIK_SEARCH = f'{API_V3_URL}/cik-search'
COMPANY_NAME_BY_CIK = f'{API_V3_URL}/cik'
FORM_13F = f'{API_V3_URL}/form-thirteen'
FORM_13F_DATE_BY_CIK = f'{API_V3_URL}/form-thirteen-date'
CUSIP = f'{API_V3_URL}/cusip'
FORM_13F_ASSET_ALLOCATION = f'{API_V4_URL}/13f-asset-allocation-date'

# STOCK LIST
STOCK_LIST = f'{API_V3_URL}/stock/list'
TRADABLE_SYMBOL_LIST = f'{API_V3_URL}/available-traded/list'
ETF_LIST = f'{API_V3_URL}/etf/list'

# BULK ENDPOINT
#TODO

# MARKET INDEXES
ALL_INDEXES_QUOTE = f'{API_V3_URL}/quotes/index'
SnP_CONSTITUENT = f'{API_V3_URL}/sp500_constituent'
HISTORICAL_SnP_CONSTITUENT = f'{API_V3_URL}/historical/sp500_constituent'
NASDAQ_CONSTITUENT = f'{API_V3_URL}/nasdaq_constituent'
DOWJONES_CONSTITUENT = f'{API_V3_URL}/dowjones_constituent'
AVAILABLE_INDEXES = f'{API_V3_URL}/symbol/available-indexes'

# EURONEXT
AVAILABLE_EURONEXT = f'{API_V3_URL}symbol/available-euronext'

# TSX
AVAILABLE_TSX = f'{API_V3_URL}/symbol/available-tsx'

# CRYPTO, FOREX AND COMMODITIES
AVAILABLE_CRYPTO = f'{API_V3_URL}/symbol/available-cryptocurrencies'
CURRENT_FOREX_RATE = f'{API_V3_URL}'
CURRENT_FOREX_RATE_FX = f'{API_V3_URL}/fx'
AVAILABLE_FOREX_PAIRS = f'{API_V3_URL}/symbol/available-forex-currency-pairs'
AVAILABLE_COMMODITIES = f'{API_V3_URL}/symbol/available-commodities'
