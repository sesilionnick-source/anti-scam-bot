import argparse
import sys

from contract_analyzer import analyze_contract
from liquidity_checker import analyze_liquidity, analyze_sellability
from report import print_console_report, print_json_report
from risk_engine import build_risk_assessment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Blockchain Token Risk Analyzer"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Token contract address, for example 0x1234...",
    )
    parser.add_argument(
        "--network",
        default="bsc",
        choices=["bsc", "eth"],
        help="Target network: bsc or eth",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print report in JSON format",
    )
    return parser.parse_args()


def analyze_token(token_address: str, network: str) -> dict:
    contract_data = analyze_contract(token_address, network)
    liquidity_data = analyze_liquidity(token_address, network)
    sellability_data = analyze_sellability(token_address, network)
    return build_risk_assessment(
        token_address=token_address,
        network=network,
        contract_data=contract_data,
        liquidity_data=liquidity_data,
        sellability_data=sellability_data,
    )


def main() -> int:
    args = parse_args()

    try:
        result = analyze_token(args.token, args.network)
    except Exception as error:
        message = {
            "status": "error",
            "message": str(error),
        }
        if args.json:
            print_json_report(message)
        else:
            print(f"Error: {message['message']}")
        return 1

    if args.json:
        print_json_report(result)
    else:
        print_console_report(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
