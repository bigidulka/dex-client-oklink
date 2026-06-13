import base64
import inspect

from dex_client_oklink import OKLINK_CHAINS, OklinkClient
from dex_client_oklink.core import generate_oklink_api_key


def test_client_imports_and_instantiates():
    client = OklinkClient()
    assert client.chain("bsc").api_slug == "bsc"
    assert client.chain("BSC").slug == "bsc"
    assert OKLINK_CHAINS


def test_public_methods_present():
    methods = {name for name, value in inspect.getmembers(OklinkClient, inspect.isfunction) if not name.startswith("_")}
    assert {
        "request_explorer",
        "recent_blocks",
        "blocks",
        "block_transactions",
        "block_token_transfers",
        "block_internal_transactions",
        "block_nft_transfers",
        "block_events",
        "block_messages",
        "transaction_logs",
        "token_metadata",
        "address_transactions",
        "address_internal_transactions",
        "address_token_transfers",
        "pending_transactions",
        "light_evm_block_transactions",
    } <= methods


def test_generated_api_key_shape():
    encoded = generate_oklink_api_key(1_700_000_000_000)
    decoded = base64.b64decode(encoded).decode()
    rotated, timestamp = decoded.split("|")
    assert rotated.endswith("a2c903cc")
    assert timestamp.startswith(str(1_700_000_000_000 + 1_111_111_111_111))
    assert len(timestamp) == len(str(1_700_000_000_000 + 1_111_111_111_111)) + 3
