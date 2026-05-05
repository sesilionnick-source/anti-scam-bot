import json
from pathlib import Path
from typing import Any, List, Optional

from web3 import Web3


NETWORKS = {
    "bsc": {
        "rpc_url": "https://bsc-dataseed.binance.org/",
    },
    "eth": {
        "rpc_url": "https://rpc.ankr.com/eth",
    },
}

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
DEAD_ADDRESS = "0x000000000000000000000000000000000000dEaD"

OWNER_ABI = [
    {
        "name": "owner",
        "inputs": [],
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "getOwner",
        "inputs": [],
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]

SUSPICIOUS_SIGNATURES = [
    "blacklist(address,bool)",
    "setBlacklist(address,bool)",
    "setMaxTxAmount(uint256)",
    "setSellFee(uint256)",
    "setTax(uint256)",
    "pause()",
    "unpause()",
]

MINT_SIGNATURES = [
    "mint(uint256)",
    "mint(address,uint256)",
    "_mint(address,uint256)",
]


def get_web3(network: str) -> Web3:
    config = NETWORKS.get(network)
    if not config:
        raise ValueError(f"Unsupported network: {network}")

    web3 = Web3(
        Web3.HTTPProvider(
            config["rpc_url"],
            request_kwargs={"timeout": 15},
        )
    )
    if not web3.is_connected():
        raise ConnectionError(f"RPC connection failed for network: {network}")
    return web3


def load_erc20_abi() -> List[dict]:
    abi_path = Path(__file__).resolve().parent / "abi" / "erc20.json"
    with abi_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def selector(signature: str) -> str:
    return Web3.keccak(text=signature)[:4].hex()[2:]


def has_selector(bytecode: str, signature: str) -> bool:
    return selector(signature) in bytecode


def safe_call(callable_object, default: Any = None) -> Any:
    try:
        return callable_object()
    except Exception:
        return default


def read_owner(web3: Web3, token_address: str) -> Optional[str]:
    contract = web3.eth.contract(address=token_address, abi=OWNER_ABI)

    for function_name in ["owner", "getOwner"]:
        owner_address = safe_call(
            lambda: getattr(contract.functions, function_name)().call()
        )
        if owner_address:
            return Web3.to_checksum_address(owner_address)

    return None


def analyze_contract(token_address: str, network: str) -> dict:
    web3 = get_web3(network)
    checksum_address = Web3.to_checksum_address(token_address)
    contract = web3.eth.contract(address=checksum_address, abi=load_erc20_abi())

    name = safe_call(lambda: contract.functions.name().call(), "Unknown")
    symbol = safe_call(lambda: contract.functions.symbol().call(), "Unknown")
    decimals = safe_call(lambda: contract.functions.decimals().call(), None)
    total_supply = safe_call(lambda: contract.functions.totalSupply().call(), None)
    owner_address = read_owner(web3, checksum_address)
    bytecode = web3.eth.get_code(checksum_address).hex()

    mint_detected = any(
        has_selector(bytecode, signature) for signature in MINT_SIGNATURES
    )
    suspicious_matches = [
        signature
        for signature in SUSPICIOUS_SIGNATURES
        if has_selector(bytecode, signature)
    ]

    owner_present = bool(
        owner_address
        and owner_address not in {ZERO_ADDRESS, DEAD_ADDRESS}
    )

    return {
        "token_info": {
            "address": checksum_address,
            "network": network,
            "name": name,
            "symbol": symbol,
            "decimals": decimals,
            "total_supply": str(total_supply) if total_supply is not None else "Unknown",
        },
        "contract_analysis": {
            "owner_present": owner_present,
            "owner_address": owner_address or "Not found",
            "mint_function_present": mint_detected,
            "suspicious_patterns": suspicious_matches,
            "bytecode_size": len(bytecode) // 2,
        },
    }
