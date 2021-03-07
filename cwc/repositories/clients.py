import abc
import asyncio
import hashlib
import hmac
import time
from typing import Union

import requests
import settings
from aiohttp import ClientSession
from exceptions import FailedRequest


class TicketAPIClient(abc.ABC):
    @abc.abstractmethod
    def get_assets_rates(self, assets, references):
        pass


class CryptonatorAPIClient(TicketAPIClient):
    def __init__(self):
        self.base_url = settings.CRYPTONATOR_BASE_URL

    @staticmethod
    def _serialize_data(data: dict) -> dict:
        ticker = data['ticker']
        return {
            'asset': ticker['base'],
            'reference': ticker['target'],
            'rate': float(ticker['price']),
        }

    async def get(self, client: ClientSession, url: str, **kwargs) -> dict:
        async with client.get(url, params=kwargs) as resp:
            data = await resp.json()
            if not (resp.status == 200 and data.get('success')):
                raise FailedRequest(resp.text)
            return data

    async def _get_ticker(self, client, asset: str, reference: str) -> dict:
        url = f'{self.base_url}/ticker/{asset}-{reference}'
        raw_data = await self.get(client, url)
        data = self._serialize_data(raw_data)
        return data

    async def _get_conversions(self, assets: list, references: list) -> list:
        async with ClientSession() as client:
            tasks = []
            for asset in assets:
                tasks.extend(
                    [
                        self._get_ticker(client, asset, reference)
                        for reference in references
                        if reference != asset
                    ]
                )
            return await asyncio.gather(*tasks)

    def get_assets_rates(self, assets: list, references: list) -> dict:
        return asyncio.run(self._get_conversions(assets, references))


def get_ticker_api() -> TicketAPIClient:
    return CryptonatorAPIClient()


class AccountAPIClient(abc.ABC):
    @abc.abstractmethod
    def get_crypto_wallet(self) -> dict:
        pass


class BinanceAPIClient(AccountAPIClient):
    def __init__(self):
        self.secret_key = settings.BINANCE['secret_key']
        self.api_key = settings.BINANCE['api_key']
        self.base_url = settings.BINANCE['url']
        self.headers = self.build_headers()

    def build_headers(self):
        return {'Accept': 'application/json', 'X-MBX-APIKEY': self.api_key}

    @staticmethod
    def _parse_asset(asset: dict) -> Union[dict, None]:
        free = float(asset.get('free'))
        locked = float(asset.get('locked'))
        if free or locked:
            asset['free'] = free
            asset['locked'] = locked
            asset['total'] = free + locked
            return asset
        return None

    def _serialize_data(self, data: list) -> list:
        assets = list(map(self._parse_asset, data['balances']))
        return list(filter(None, assets))

    def _generate_signature(self, **kwargs) -> dict:
        timestamp = round(time.time() * 1000)
        kwargs.update({'timestamp': timestamp})
        msg = '&'.join([f'{key}={val}' for key, val in kwargs.items()])
        signature = hmac.new(
            key=self.secret_key.encode('utf-8'),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).hexdigest()
        kwargs.update({'signature': signature})
        return kwargs

    def _get(self, url, signature: bool = False, **kwargs):
        params = kwargs
        if signature:
            params = self._generate_signature(**kwargs)
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            raise FailedRequest(response.text)
        return response.json()

    def get_crypto_wallet(self) -> dict:
        url = f'{self.base_url}/api/v3/account'
        data = self._get(url, signature=True)
        data = self._serialize_data(data)
        return data


def get_account_api() -> AccountAPIClient:
    return BinanceAPIClient()
