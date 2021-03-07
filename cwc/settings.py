from decouple import Csv, config

CRYPTONATOR_BASE_URL = "https://www.cryptonator.com/api"
BINANCE = {
    'url': 'https://api.binance.com',
    'secret_key': config('BINANCE_SECRET_KEY'),
    'api_key': config('BINANCE_API_KEY'),
}
CURRENCIES = config('CURRENCIES', cast=Csv(), default=['USD'])
