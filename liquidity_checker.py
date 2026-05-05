from web3 import Web3

from contract_analyzer import get_web3


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
        ],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "type": "function",
    }
]

PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"},
        ],
        "type": "function",
    }
]

NETWORK_DEX = {
    "bsc": {
        "factory": "0xCA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
        "wrapped_native": "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "dex_name": "PancakeSwap V2",
    },
    "eth": {
        "factory": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        "wrapped_native": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "dex_name": "Uniswap V2",
    },
}


def analyze_liquidity(token_address: str, network: str) -> dict:
    network_config = NETWORK_DEX.get(network)

    if not network_config:
        return {
            "status": "UNKNOWN",
            "dex": "Unknown",
            "pair_address": None,
            "has_liquidity": None,
            "reserves": None,
            "message": f"No DEX configuration for network: {network}",
        }

    try:
        web3 = get_web3(network)
        token_address = Web3.to_checksum_address(token_address)
        factory = web3.eth.contract(
            address=Web3.to_checksum_address(network_config["factory"]),
            abi=FACTORY_ABI,
        )
        wrapped_native = Web3.to_checksum_address(network_config["wrapped_native"])
        pair_address = factory.functions.getPair(token_address, wrapped_native).call()
    except Exception as error:
        return {
            "status": "UNKNOWN",
            "dex": network_config["dex_name"],
            "pair_address": None,
            "has_liquidity": None,
            "reserves": None,
            "message": f"Liquidity check failed: {error}",
        }

    if pair_address == ZERO_ADDRESS:
        return {
            "status": "NOT_DETECTED",
            "dex": network_config["dex_name"],
            "pair_address": None,
            "has_liquidity": False,
            "reserves": {"reserve0": 0, "reserve1": 0},
            "message": "No pair found against the wrapped native asset.",
        }

    try:
        pair = web3.eth.contract(
            address=Web3.to_checksum_address(pair_address),
            abi=PAIR_ABI,
        )
        reserve0, reserve1, _ = pair.functions.getReserves().call()
    except Exception as error:
        return {
            "status": "UNKNOWN",
            "dex": network_config["dex_name"],
            "pair_address": Web3.to_checksum_address(pair_address),
            "has_liquidity": None,
            "reserves": None,
            "message": f"Pair found, but reserve check failed: {error}",
        }

    has_liquidity = reserve0 > 0 and reserve1 > 0

    return {
        "status": "DETECTED" if has_liquidity else "NOT_DETECTED",
        "dex": network_config["dex_name"],
        "pair_address": Web3.to_checksum_address(pair_address),
        "has_liquidity": has_liquidity,
        "reserves": {
            "reserve0": int(reserve0),
            "reserve1": int(reserve1),
        },
        "message": (
            "Liquidity detected in the main DEX pair."
            if has_liquidity
            else "Pair exists, but reserves are empty."
        ),
    }


def analyze_sellability(token_address: str, network: str) -> dict:
    _ = token_address
    _ = network
    return {
        "status": "UNKNOWN",
        "can_sell": None,
        "message": (
            "Sell simulation is not executed in this MVP because a reliable test "
            "requires a funded wallet, token approval, and a safe transaction "
            "environment."
        ),
    }
