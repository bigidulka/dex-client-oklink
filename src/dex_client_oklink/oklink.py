from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from .core import APIError, BaseClient, Json, DEFAULT_UA, drop_empty, generate_oklink_api_key, now_ms

ExplorerMethod = Literal["GET", "POST"]


@dataclass(frozen=True, slots=True)
class OklinkChain:
    inst_id: str
    slug: str
    api_slug: str
    kind: str
    name: str


OKLINK_CHAINS: tuple[OklinkChain, ...] = (
    OklinkChain("BTC", "bitcoin", "btc", "utxo", "Bitcoin"),
    OklinkChain("ETH", "ethereum", "eth", "evm", "Ethereum"),
    OklinkChain("X1", "x-layer", "x1", "evm", "X Layer"),
    OklinkChain("SOLANA", "solana", "sol", "solana", "Solana"),
    OklinkChain("TRON", "tron", "tron", "tron", "TRON"),
    OklinkChain("BSC", "bsc", "bsc", "evm", "BNB Chain"),
    OklinkChain("BASE", "base", "base", "evm", "Base"),
    OklinkChain("SUI", "sui", "sui", "move", "Sui"),
    OklinkChain("APT", "aptos", "aptos", "move", "Aptos"),
    OklinkChain("ARBITRUM", "arbitrum-one", "arbitrum", "evm", "Arbitrum One"),
    OklinkChain("OPTIMISM", "optimism", "optimism", "evm", "OP Mainnet"),
    OklinkChain("POLYGON", "polygon", "polygon", "evm", "Polygon"),
    OklinkChain("AVAXC", "avalanche", "avax", "evm", "Avalanche-C"),
    OklinkChain("POLYGON_ZKEVM", "polygon-zkevm", "polygon-zkevm", "evm", "Polygon zkEVM"),
    OklinkChain("ZKSYNC", "zksync-era", "zksync", "evm", "zkSync Era"),
    OklinkChain("TON", "ton", "ton", "ton", "TON"),
    OklinkChain("GRAVITY", "gravity-alpha", "gravity", "evm", "Gravity Alpha Mainnet"),
    OklinkChain("BITLAYER", "bitlayer", "bitlayer", "evm", "Bitlayer Mainnet"),
    OklinkChain("LINEA", "linea", "linea", "evm", "Linea"),
    OklinkChain("BOB", "bob", "bob", "evm", "BOB Mainnet"),
    OklinkChain("B2", "bsquared", "b2", "evm", "B Squared Mainnet"),
    OklinkChain("DUCKCHAIN", "duckchain", "duckchain", "evm", "Duckchain Mainnet"),
    OklinkChain("APE", "apechain", "ape", "evm", "ApeChain Mainnet"),
    OklinkChain("MANTAPACIFIC", "manta", "mantapacific", "evm", "Manta Pacific"),
    OklinkChain("OPBNB", "opbnb", "opbnb", "evm", "opBNB Mainnet"),
    OklinkChain("SCROLL", "scroll", "scroll", "evm", "Scroll"),
    OklinkChain("FTM", "fantom", "ftm", "evm", "Fantom"),
    OklinkChain("COSMOS", "cosmos", "cosmos", "cosmos", "Cosmos Hub"),
    OklinkChain("OKEXCHAIN", "oktc", "okexchain", "evm", "OKT Chain"),
    OklinkChain("KAVA", "kava", "kava", "evm", "Kava"),
    OklinkChain("KLAYTN", "kaia", "klaytn", "evm", "Kaia Network"),
    OklinkChain("RONIN", "ronin", "ronin", "evm", "Ronin"),
    OklinkChain("GNOSIS", "gnosis", "gnosis", "evm", "Gnosis"),
    OklinkChain("ETC", "etc", "etc", "evm", "Ethereum Classic"),
    OklinkChain("ETHW", "ethereum-pow", "ethw", "evm", "EthereumPoW"),
    OklinkChain("BEACON", "beacon", "beacon", "beacon", "Beacon Chain"),
    OklinkChain("DOGE", "dogecoin", "doge", "utxo", "Dogecoin"),
    OklinkChain("LTC", "litecoin", "ltc", "utxo", "Litecoin"),
    OklinkChain("BCH", "bch", "bch", "utxo", "Bitcoin Cash"),
    OklinkChain("DASH", "dash", "dash", "utxo", "DASH"),
    OklinkChain("XGON_TEST2", "x-layer-testnet", "xgon_test2", "evm", "X Layer Testnet"),
    OklinkChain("ETHSEPOLIA", "sepolia", "ethsepolia", "evm", "Sepolia Testnet"),
)

_CHAIN_BY_KEY = {
    key.lower(): chain
    for chain in OKLINK_CHAINS
    for key in (chain.inst_id, chain.slug, chain.api_slug)
}

_BTC_SERIES = {"btc", "usdt", "doge", "ltc", "bch", "dash", "fractal-bitcoin"}
_BLOCK_SINGULAR = {"bsc", "x1", "xlayer", "tron", "base", "arbitrum", "optimism", "polygon", "avax", "zksync", "linea", "scroll", "opbnb"}
_LIGHTWEIGHT_EVM_PREFIX = "/priapi/v1/lite/evm/"


class OklinkClient(BaseClient):
    def __init__(
        self,
        *,
        base_url: str = "https://www.oklink.com",
        timeout: float = 15.0,
        use_curl_cffi: bool = False,
        referer: str = "https://www.oklink.com/ru/bsc",
        headers: Mapping[str, str] | None = None,
    ):
        super().__init__(
            base_url,
            timeout=timeout,
            use_curl_cffi=use_curl_cffi,
            headers={
                "Accept": "application/json",
                "User-Agent": DEFAULT_UA,
                "Referer": referer,
                **(headers or {}),
            },
        )

    def chain(self, value: str | OklinkChain) -> OklinkChain:
        if isinstance(value, OklinkChain):
            return value
        key = value.lower()
        if key not in _CHAIN_BY_KEY:
            raise ValueError(f"unsupported OKLink chain: {value}")
        return _CHAIN_BY_KEY[key]

    def request_explorer(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        method: ExplorerMethod = "GET",
        prefix: str = "/api/explorer/",
        unwrap: bool = True,
    ) -> Any:
        url_path = f"{prefix.rstrip('/')}/{path.lstrip('/')}"
        query = dict(params or {})
        query["t"] = now_ms()
        headers = {"x-apiKey": generate_oklink_api_key()}
        if method == "GET":
            payload = self.request("GET", url_path, params=query, headers=headers)
        else:
            payload = self.request("POST", url_path, params={"t": query.pop("t")}, json_body=query, headers=headers)
        if payload.get("code") not in (None, 0):
            raise APIError(f"OKLink API error: {payload.get('msg') or payload.get('detailMsg') or payload.get('code')}", payload=payload)
        return payload.get("data") if unwrap else payload

    def recent_blocks(self, chain: str | OklinkChain, *, limit: int = 20, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/home-blocks", params={"offset": offset, "limit": limit})

    def blocks(self, chain: str | OklinkChain, *, limit: int = 20, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/blocks", params={"offset": offset, "limit": limit})

    def block_transactions(self, chain: str | OklinkChain, block_height: int | str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(_transaction_endpoint(c, block_height), params=_block_params(c, block_height, offset, limit))

    def block_token_transfers(self, chain: str | OklinkChain, block_height: int | str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        if c.api_slug in _BTC_SERIES:
            path = f"v2/{c.api_slug}/inscription/transfer/list"
        else:
            path = f"v2/{c.api_slug}/blocks/tokenTransfers"
        return self.request_explorer(path, params={"offset": offset, "limit": limit, "blockHeight": block_height})

    def block_internal_transactions(self, chain: str | OklinkChain, block_height: int | str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        path = f"v2/{c.api_slug}/block/internalTransactions" if c.api_slug in _BLOCK_SINGULAR else f"v2/{c.api_slug}/blocks/internalTransactions"
        return self.request_explorer(path, params={"offset": offset, "limit": limit, "blockHeight": block_height})

    def block_nft_transfers(self, chain: str | OklinkChain, block_height: int | str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/block/{block_height}/transfers/condition/nft", params={"offset": offset, "limit": limit, "blockHeight": block_height})

    def block_events(self, chain: str | OklinkChain, block_height: int | str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/blocks/event", params={"offset": offset, "limit": limit, "blockHeight": block_height})

    def block_messages(self, chain: str | OklinkChain, block_height: int | str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/blocks/message", params={"offset": offset, "limit": limit, "blockHeight": block_height})

    def transaction_logs(self, chain: str | OklinkChain, tx_hash: str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v1/{c.api_slug}/transactions/{tx_hash}/logs", params={"offset": offset, "limit": limit})

    def token_metadata(self, chain: str | OklinkChain, address: str) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/tokens/{address}", params={})

    def address_transactions(self, chain: str | OklinkChain, address: str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/addresses/{address}/transactionsByClassfy/condition", params={"offset": offset, "limit": limit, "address": address})

    def address_internal_transactions(self, chain: str | OklinkChain, address: str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v1/{c.api_slug}/addresses/{address}/internalTx/condition", params={"offset": offset, "limit": limit, "address": address})

    def address_token_transfers(self, chain: str | OklinkChain, address: str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v2/{c.api_slug}/addresses/{address}/transfers/condition/token", params={"offset": offset, "limit": limit, "address": address})

    def pending_transactions(self, chain: str | OklinkChain, *, limit: int = 50, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer(f"v1/{c.slug}/transactions", params={"offset": offset, "limit": limit, "type": "pending"})

    def light_evm_block_transactions(self, chain: str | OklinkChain, block_height: int | str, *, limit: int = 100, offset: int = 0) -> Any:
        c = self.chain(chain)
        return self.request_explorer("block/detail/transactions", prefix=_LIGHTWEIGHT_EVM_PREFIX, params={"chain": c.api_slug, "offset": offset, "limit": limit, "blockHeight": block_height, "block": block_height})


def _transaction_endpoint(chain: OklinkChain, block_height: int | str) -> str:
    slug = chain.api_slug
    if slug == "sol":
        return f"v2/sol/block/transactions/{block_height}"
    if slug == "ton":
        return "v2/ton/block/detail/transactions"
    if slug == "sui":
        return f"v1/sui/addresses/{block_height}/searchCheckpointTx"
    if slug in {"aptos", "polygon-zkevm"}:
        return f"v2/{slug}/transactionsNoRestrict" if slug == "aptos" else f"v1/{slug}/transactionsNoRestrict"
    if slug == "usdt" or (slug in _BTC_SERIES and slug != "fractal-bitcoin"):
        return f"v1/{slug}/transactionsNoRestrict"
    if slug == "fractal-bitcoin":
        return f"v2/{slug}/transactionsNoRestrict"
    if slug in {"cosmos", "kava"}:
        return f"v2/{slug}/messageTransaction/list"
    if slug in _BLOCK_SINGULAR:
        return f"v2/{slug}/block/transactions"
    return f"v2/{slug}/blocks/transactions"


def _block_params(chain: OklinkChain, block_height: int | str, offset: int, limit: int) -> dict[str, Any]:
    values: dict[str, Any] = {"offset": offset, "limit": limit, "blockHeight": block_height}
    if chain.api_slug == "sui":
        values = {"offset": offset, "limit": limit, "hash": block_height}
    if chain.api_slug == "aptos":
        values = {"offset": offset, "limit": limit, "height": block_height}
    if chain.api_slug == "usdt":
        values["chain"] = chain.inst_id
    return drop_empty(values)
