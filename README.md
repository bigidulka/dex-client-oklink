# OKLink Reverse Client

Python client for endpoints used by [https://www.oklink.com](https://www.oklink.com). The implementation is browser/reverse-engineered from `oklink-engine` and mirrors OKLink web explorer REST calls.

## Install

```bash
pip install git+https://github.com/bigidulka/dex-client-oklink.git
```

For local development:

```bash
pip install -e '.[dev]'
pytest
```

## Quick start

```python
from dex_client_oklink import OklinkClient

client = OklinkClient(use_curl_cffi=True)

blocks = client.recent_blocks("bsc", limit=3)
txs = client.block_transactions("bsc", 12345678, limit=50)
token = client.token_metadata("eth", "0xdac17f958d2ee523a2206206994597c13d831ec7")
```

All methods return decoded OKLink `data` payloads. Use `request_explorer(..., unwrap=False)` to inspect the raw envelope.

## Methods

- `request_explorer`
- `recent_blocks`
- `blocks`
- `block_transactions`
- `block_token_transfers`
- `block_internal_transactions`
- `block_nft_transfers`
- `block_events`
- `block_messages`
- `transaction_logs`
- `token_metadata`
- `address_transactions`
- `address_internal_transactions`
- `address_token_transfers`
- `pending_transactions`
- `light_evm_block_transactions`

## Endpoint inventory

Extracted from `/home/fsdf1234/Projects/oklink-engine`.

- `GET /api/explorer/v2/{chain}/home-blocks`
- `GET /api/explorer/v2/{chain}/blocks`
- `GET /api/explorer/v2/{chain}/blocks/transactions`
- `GET /api/explorer/v2/{chain}/block/transactions`
- `GET /api/explorer/v1/{chain}/transactionsNoRestrict`
- `GET /api/explorer/v2/{chain}/blocks/tokenTransfers`
- `GET /api/explorer/v2/{chain}/block/{height}/transfers/condition/token`
- `GET /api/explorer/v2/{chain}/block/{height}/transfers/condition/nft`
- `GET /api/explorer/v2/{chain}/blocks/internalTransactions`
- `GET /api/explorer/v2/{chain}/block/internalTransactions`
- `GET /api/explorer/v2/{chain}/blocks/event`
- `GET /api/explorer/v2/{chain}/blocks/message`
- `GET /api/explorer/v1/{chain}/transactions/{tx_hash}/logs`
- `GET /api/explorer/v2/{chain}/tokens/{address}`
- `GET /api/explorer/v2/{chain}/addresses/{address}/transactionsByClassfy/condition`
- `GET /api/explorer/v1/{chain}/addresses/{address}/internalTx/condition`
- `GET /api/explorer/v2/{chain}/addresses/{address}/transfers/condition/token`
- `GET /api/explorer/v1/{chain_slug}/transactions?type=pending`
- `GET /priapi/v1/lite/evm/block/detail/transactions`

Full details: [`endpoint_inventory.json`](endpoint_inventory.json).

## Notes

- No official SDK is used.
- Some endpoints are chain-specific and can return OKLink web errors when the explorer does not expose that resource for the selected chain.
- `curl_cffi` is supported for browser-like TLS behavior.
- Do not commit cookies, private headers, proxies, or captured sessions.
