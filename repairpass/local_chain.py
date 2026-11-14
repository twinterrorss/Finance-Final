
from functools import lru_cache
from pathlib import Path

from eth_tester import EthereumTester, PyEVMBackend
from solcx import compile_source, get_installed_solc_versions
from web3 import EthereumTesterProvider, Web3


SOLC_VERSION = "0.8.28"
CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "DeviceRegistry.sol"


@lru_cache(maxsize=1)
def contract_artifact() -> dict:
    """Compile the unchanged Solidity source and return its ABI and bytecode.

    Only the first compiler installation requires downloading solc; this
    function never silently installs a compiler during tests or the demo.
    """
    if SOLC_VERSION not in {str(v) for v in get_installed_solc_versions()}:
        raise RuntimeError(
            f"Solidity compiler {SOLC_VERSION} not installed. "
            "Run: python -m scripts.setup_compiler"
        )
    source = CONTRACT_PATH.read_text(encoding="utf-8")
    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
        evm_version="paris",  
        optimize=True,
    )
    artifact = next(
        (v for key, v in compiled.items() if key.endswith(":DeviceRegistry")),
        None,
    )
    if artifact is None:
        raise RuntimeError("Solidity compiler did not produce DeviceRegistry")
    return {"abi": artifact["abi"], "bytecode": "0x" + artifact["bin"]}


def make_local_chain() -> Web3:
    """Create a fresh local EVM with fictional, pre-funded test accounts."""
    backend = PyEVMBackend()
    tester = EthereumTester(backend=backend)
    w3 = Web3(EthereumTesterProvider(tester))
    if not w3.is_connected() or len(w3.eth.accounts) < 5:
        raise RuntimeError("In-memory local Ethereum tester failed to initialize")
    return w3


def wait_success(w3: Web3, tx_hash, label: str = "transaction"):
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] != 1:
        raise RuntimeError(f"{label} reverted (status=0)")
    return receipt


def deploy_registry(w3: Web3, artifact: dict | None = None):
    """Deploy the real compiled Solidity contract to this ephemeral chain."""
    compiled = artifact if artifact is not None else contract_artifact()
    factory = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
    tx_hash = factory.constructor().transact({"from": w3.eth.accounts[0]})
    receipt = wait_success(w3, tx_hash, "contract deployment")
    if not receipt["contractAddress"]:
        raise RuntimeError("Deployment receipt has no contract address")
    return w3.eth.contract(address=receipt["contractAddress"], abi=compiled["abi"])


def send(w3: Web3, fn, sender: str, label: str = "transaction"):
    """Submit a local EVM transaction and verify success."""
    return wait_success(w3, fn.transact({"from": sender}), label)


def digest(text: str) -> bytes:
    """Ethereum keccak256 of UTF-8 text, exactly like ethers.id(text)."""
    return Web3.keccak(text=text)
