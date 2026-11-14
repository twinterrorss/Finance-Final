Educational project for the course Introduction to Finance. Not a real product, service or investment offer. Do not use with real funds.

# RepairPass

RepairPass is our university project about keeping repair records for electronic devices more reliable. The idea is simple: if someone changes a repair record later, we want to be able to notice it.

We don't put the full repair history on the blockchain. Instead, we save a hash of each record. The actual information would be kept separately. This way we can check whether a record was changed without publishing its contents.

This repository is just a working prototype of that idea, not a finished application.

## How it works

1. An approved shop registers a device using an ID.
2. An approved service center adds a repair record by saving its hash.
3. Anyone can check if a hash matches the latest saved version.
4. If a mistake needs to be corrected, the original service center can add a new version. The old one stays in the history.

The contract also has simple permissions: an admin gives or removes access for shops and service centers.

**One important detail:** matching hashes show that the checked data matches the saved version. They don't prove that a repair actually happened.

## What we used

- **Solidity** — the `DeviceRegistry` smart contract.
- **Python and web3.py** — to work with the contract.
- **eth-tester + py-evm** — a local test blockchain.
- **py-solc-x** — to compile the Solidity contract.
- **pytest** — for the automated tests.

Everything runs locally. We don't use real wallets, cryptocurrency or customer information. Node.js and npm are not needed for this Python version.

## How to run

You need Python and an internet connection for the first installation (to download the packages and Solidity compiler). Open a terminal **in the project folder**, where `requirements.txt` is located.

### Windows (PowerShell)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m scripts.setup_compiler
.\.venv\Scripts\python.exe -m scripts.demo
.\.venv\Scripts\python.exe -m pytest -v
```

These commands use Python 3.13. If you have another compatible Python version, create the virtual environment with that version instead. You don't need to activate the environment in PowerShell.

### Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m scripts.setup_compiler
python -m scripts.demo
python -m pytest -v
```

The compiler setup installs Solidity compiler version **0.8.28**. You only need to install it once.

## Demo and tests

The demo script (`scripts/demo.py`) goes through our main example: deploying the contract, giving roles, registering a device, adding a repair, checking a changed record, and saving a corrected version.

We also wrote **15 unit tests** for registration, permissions, duplicate records, hash verification, corrections and version history.

We need to check that all tests pass before submitting the project.

**Demo video:** https://drive.google.com/file/d/1bGnvMBnUxCXLnLFp6Q9Kb6oMwIFRJUUq/view?usp=sharing

## Main files

```text
contracts/DeviceRegistry.sol        Smart contract
repairpass/local_chain.py           Local blockchain setup and deployment
scripts/setup_compiler.py           Solidity compiler setup
scripts/demo.py                     Main demo
tests/test_device_registry.py       Unit tests
requirements.txt                    Python packages                            
```

## What's not included yet

This is a small prototype, so we haven't built the full system with a real database, API, file storage or a Hyperledger Besu network. Those are part of the proposed architecture, not something running in this repository. The local blockchain also starts fresh each time.

We only use fictional IDs and sample repair data. A real system would need stronger account management, secure storage for the original records, and a security audit before launch.

## Team contributions

Each team member is responsible for their own work and commits changes from their own GitHub account. The commit history is used to show who worked on which part.

