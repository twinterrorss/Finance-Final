
from solcx import get_installed_solc_versions, install_solc
from repairpass.local_chain import SOLC_VERSION


def main():
    existing = {str(v) for v in get_installed_solc_versions()}
    if SOLC_VERSION in existing:
        print(f"solc {SOLC_VERSION} is already installed")
        return
    print(f"Downloading solc {SOLC_VERSION} (one-time setup)...")
    try:
        install_solc(SOLC_VERSION, show_progress=False)
    except Exception as exc:
        raise SystemExit(
            f"Could not install solc {SOLC_VERSION}. "
            "Check internet access and run this command again. "
            f"Technical details: {exc}"
        ) from exc
    print(f"solc {SOLC_VERSION} installed successfully")


if __name__ == "__main__":
    main()
