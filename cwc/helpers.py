import json
from datetime import datetime

import settings
from repositories.clients import get_account_api, get_ticker_api


def get_conversions_rates(assets: list) -> list:
    currencies = settings.CURRENCIES
    ticker_api = get_ticker_api()
    return ticker_api.get_assets_rates(assets, currencies)


def save_to_file(data: list):
    with open('history.json', 'w+') as json_file:
        file_data = []
        if json_file.read():
            file_data = json.load(json_file)
        current_time = datetime.today().strftime('%Y%m%d%H%M')
        file_data.append({'date': current_time, 'data': data})
        json_file.seek(0)
        json.dump(file_data, json_file)


def convert_asset_value(balance: dict, rates: list) -> list:
    return [
        {
            'asset': balance['asset'],
            'reference': rate['reference'],
            'value': rate['rate'] * balance['total'],
        }
        for rate in rates
    ]


def get_balance_conversions():
    account_api = get_account_api()
    account_balance = account_api.get_crypto_wallet()
    assets_symbols = list(map(lambda x: x['asset'], account_balance))
    rates = get_conversions_rates(assets_symbols)
    conversions = []
    for asset_balance in account_balance:
        rates = list(
            filter(
                lambda x, ab=asset_balance: x['asset'] == ab['asset'], rates
            )
        )
        conversions.extend(convert_asset_value(asset_balance, rates))
    return conversions
