# Blockchain Token Risk Analyzer

## Description

Blockchain Token Risk Analyzer is a small academic MVP for heuristic analysis of EVM tokens.
The project checks a token smart contract and produces a simple, explainable risk assessment.

This is not a production security scanner.
It is a demonstration project focused on clarity, structure, and stable execution.

## Features

- Token metadata lookup: name, symbol, decimals, total supply
- Contract analysis:
  - owner detection
  - mint function detection
  - suspicious pattern detection in bytecode
- Liquidity analysis through the main DEX pair
- Sellability status with honest `UNKNOWN` fallback
- Risk score from 0 to 100
- Final classification:
  - `LOW RISK`
  - `MEDIUM RISK`
  - `HIGH RISK`
- Two output formats:
  - human-readable console report
  - JSON report with `--json`

## Technologies

- Python 3
- [Web3.py](https://github.com/ethereum/web3.py)
- JSON ABI
- Public RPC endpoints for BSC and Ethereum

## Project Structure

```text
honeypot-checker/
├── abi/
│   └── erc20.json
├── checker.py
├── contract_analyzer.py
├── liquidity_checker.py
├── report.py
├── risk_engine.py
└── README.md
```

## Risk Model

The scoring model is intentionally simple and easy to explain:

- owner present: `+20`
- mint function detected: `+25`
- no liquidity detected: `+25`
- sell simulation unknown or failed: `+15`
- suspicious patterns detected: `+15`

Classification:

- `0-29` -> `LOW RISK`
- `30-59` -> `MEDIUM RISK`
- `60-100` -> `HIGH RISK`

## How To Run

Install dependencies:

```bash
pip install web3
```

Run in console mode:

```bash
python checker.py --token 0xTOKEN_ADDRESS --network bsc
```

Run in JSON mode:

```bash
python checker.py --token 0xTOKEN_ADDRESS --network bsc --json
```

Supported networks:

- `bsc`
- `eth`

## Example Command

```bash
python checker.py --token 0x55d398326f99059fF775485246999027B3197955 --network bsc
```

## Example Output

```text
Blockchain Token Risk Analyzer
==================================

Token Info
----------
Address      : 0x...
Network      : bsc
Name         : Example Token
Symbol       : EXT
Decimals     : 18
Total Supply : 1000000000000000000000000

Contract Analysis
-----------------
Owner Present        : True
Owner Address        : 0x...
Mint Function        : False
Suspicious Patterns  : setTax(uint256)
Bytecode Size        : 14321 bytes

Liquidity Analysis
------------------
DEX                  : PancakeSwap V2
Pair Address         : 0x...
Has Liquidity        : True
Message              : Liquidity detected in the main DEX pair.

Sellability
-----------
Status               : UNKNOWN
Can Sell             : None
Message              : Sell simulation is not implemented in this MVP...

Final Assessment
----------------
Risk Score           : 50/100
Risk Level           : MEDIUM RISK
Reasons              :
  - Owner is present: +20
  - Sell simulation is unknown or failed: +15
  - Suspicious contract patterns detected: +15
```

## Limitations

- This project uses heuristic checks, not formal smart contract verification.
- Sellability is returned as `UNKNOWN` because safe simulation requires a funded wallet, token approvals, and controlled transaction execution.
- Liquidity is checked through the main wrapped-native pair only.
- The project may miss hidden malicious behavior implemented through uncommon contract logic.
- Public RPC endpoints may be slow or temporarily unavailable.

## Future Improvements

- Add safer sell simulation in a test environment
- Add support for more DEX pairs and more chains
- Improve suspicious pattern detection
- Add unit tests for the scoring engine and report formatting
- Add export to file for research or coursework reports
