import json


def print_json_report(data: dict) -> None:
    print(json.dumps(data, indent=2))


def _verdict_label(risk_level: str) -> str:
    if risk_level == "LOW RISK":
        return "LOW RISK"
    if risk_level == "MEDIUM RISK":
        return "CAUTION"
    return "HIGH RISK"


def _yes_no_unknown(value) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Unknown"


def format_security_report(result: dict) -> str:
    token = result["token"]
    contract = result["contract_analysis"]
    liquidity = result["liquidity_analysis"]
    sellability = result["sellability"]
    final = result["final_assessment"]

    risk_factors = final["reasons"][:]
    if not risk_factors:
        risk_factors = ["No major heuristic risk factors were detected."]

    liquidity_status_map = {
        "DETECTED": "Detected",
        "NOT_DETECTED": "Not detected",
        "UNKNOWN": "Unknown",
    }
    sell_status_map = {
        "OK": "Sellable",
        "FAILED": "Failed",
        "UNKNOWN": "Unknown",
    }

    lines = [
        "Blockchain Token Risk Analyzer",
        "Professional Security Report",
        "",
        "Address",
        f"- {token['address']}",
        "",
        "Network",
        f"- {token['network']}",
        "",
        "Summary",
        f"- Verdict: {_verdict_label(final['risk_level'])}",
        f"- Risk Score: {final['risk_score']}/100",
        "",
        "Contract Details",
        f"- Name: {token['name']}",
        f"- Symbol: {token['symbol']}",
        f"- Decimals: {token['decimals']}",
        f"- Total Supply: {token['total_supply']}",
        f"- Owner Present: {_yes_no_unknown(contract['owner_present'])}",
        f"- Owner Address: {contract['owner_address']}",
        f"- Mint Function: {_yes_no_unknown(contract['mint_function_present'])}",
        "",
        "Liquidity",
        f"- DEX: {liquidity.get('dex', 'Unknown')}",
        f"- Status: {liquidity_status_map.get(liquidity.get('status'), 'Unknown')}",
        f"- Pair Address: {liquidity.get('pair_address') or 'Not found'}",
        f"- Has Liquidity: {_yes_no_unknown(liquidity.get('has_liquidity'))}",
        f"- Details: {liquidity.get('message', 'No details')}",
        "",
        "Sellability",
        f"- Status: {sell_status_map.get(sellability.get('status'), 'Unknown')}",
        f"- Can Sell: {_yes_no_unknown(sellability.get('can_sell'))}",
        f"- Details: {sellability.get('message', 'No details')}",
        "",
        "Risk Factors",
    ]

    for factor in risk_factors:
        lines.append(f"- {factor}")

    suspicious_patterns = contract.get("suspicious_patterns", [])
    if suspicious_patterns:
        lines.append(
            f"- Suspicious Patterns: {', '.join(suspicious_patterns)}"
        )

    lines.extend(
        [
            "",
            "Recommendation",
            f"- {final['recommendation']}",
        ]
    )

    return "\n".join(lines)


def print_console_report(result: dict) -> None:
    print(format_security_report(result))
