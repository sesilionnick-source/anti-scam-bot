def classify_risk(score: int) -> str:
    if score <= 29:
        return "LOW RISK"
    if score <= 59:
        return "MEDIUM RISK"
    return "HIGH RISK"


def build_recommendation(
    risk_level: str,
    liquidity_status: str,
    sell_status: str,
) -> str:
    if risk_level == "HIGH RISK":
        return (
            "High-risk indicators were detected. Avoid interacting with this token "
            "until manual review of ownership, liquidity, and transfer behavior is completed."
        )

    if risk_level == "MEDIUM RISK":
        return (
            "This token requires caution. Review owner privileges, mint capability, "
            "and trading conditions before making any transaction."
        )

    if liquidity_status == "UNKNOWN" or sell_status in {"UNKNOWN", "FAILED"}:
        return (
            "No critical red flags were found, but the analysis is incomplete. "
            "Manual verification is recommended before interacting with the token."
        )

    return (
        "The token looks relatively safer under this heuristic model, but it still "
        "should be manually verified before use."
    )


def build_risk_assessment(
    token_address: str,
    network: str,
    contract_data: dict,
    liquidity_data: dict,
    sellability_data: dict,
) -> dict:
    score = 0
    reasons = []

    contract_analysis = contract_data["contract_analysis"]
    suspicious_patterns = contract_analysis["suspicious_patterns"]
    liquidity_status = liquidity_data.get("status", "UNKNOWN")
    sell_status = sellability_data.get("status", "UNKNOWN")

    if contract_analysis["owner_present"]:
        score += 20
        reasons.append("Contract owner privileges are present: +20")

    if contract_analysis["mint_function_present"]:
        score += 25
        reasons.append("Mint function detected in contract bytecode: +25")

    if liquidity_status == "NOT_DETECTED":
        score += 25
        reasons.append("Liquidity was not detected in the main DEX pair: +25")

    if liquidity_status == "UNKNOWN":
        score += 10
        reasons.append("Liquidity could not be verified reliably: +10")

    if sell_status == "FAILED":
        score += 20
        reasons.append("Sell simulation failed: +20")

    if sell_status == "UNKNOWN":
        score += 15
        reasons.append("Sellability remains unknown in this MVP: +15")

    if suspicious_patterns:
        score += 15
        reasons.append("Suspicious administrative patterns were detected: +15")

    score = min(score, 100)
    risk_level = classify_risk(score)

    return {
        "status": "ok",
        "token": {
            "address": contract_data["token_info"]["address"],
            "network": network,
            "name": contract_data["token_info"]["name"],
            "symbol": contract_data["token_info"]["symbol"],
            "decimals": contract_data["token_info"]["decimals"],
            "total_supply": contract_data["token_info"]["total_supply"],
        },
        "contract_analysis": contract_analysis,
        "liquidity_analysis": liquidity_data,
        "sellability": sellability_data,
        "final_assessment": {
            "risk_score": score,
            "risk_level": risk_level,
            "reasons": reasons,
            "recommendation": build_recommendation(
                risk_level=risk_level,
                liquidity_status=liquidity_status,
                sell_status=sell_status,
            ),
        },
        "metadata": {
            "input_token": token_address,
            "network": network,
            "scoring_model": {
                "owner_present": 20,
                "mint_function": 25,
                "liquidity_not_detected": 25,
                "liquidity_unknown": 10,
                "sell_unknown": 15,
                "sell_failed": 20,
                "suspicious_patterns": 15,
            },
        },
    }
