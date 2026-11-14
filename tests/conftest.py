
import pytest
from repairpass.local_chain import contract_artifact, deploy_registry, digest, make_local_chain, send

DEVICE_ID = digest("DEMO-DEVICE-RANDOMIZED-ID-001")
REPAIR_ID = digest("DEMO-REPAIR-RANDOMIZED-ID-001")
HASH_V1 = digest('{"demo":true,"action":"screen replacement","version":1}')
HASH_V2 = digest('{"demo":true,"action":"screen replacement, corrected","version":2}')
TAMPERED = digest('{"demo":true,"action":"battery replacement","version":1}')
ZERO = bytes(32)


@pytest.fixture(scope="session")
def artifact():
    return contract_artifact()


@pytest.fixture
def env(artifact):
    w3 = make_local_chain()
    admin, shop, service, other_service, stranger = w3.eth.accounts[:5]
    contract = deploy_registry(w3, artifact)
    shop_role = contract.functions.SHOP_ROLE().call()
    service_role = contract.functions.SERVICE_ROLE().call()
    send(w3, contract.functions.grantRole(shop_role, shop), admin)
    send(w3, contract.functions.grantRole(service_role, service), admin)
    send(w3, contract.functions.grantRole(service_role, other_service), admin)
    return {
        "w3": w3, "contract": contract,
        "admin": admin, "shop": shop,
        "service": service, "other_service": other_service,
        "stranger": stranger,
        "shop_role": shop_role, "service_role": service_role,
    }


@pytest.fixture
def registered(env):
    send(env["w3"], env["contract"].functions.registerDevice(DEVICE_ID), env["shop"])
    return env


@pytest.fixture
def repaired(registered):
    send(registered["w3"],
         registered["contract"].functions.recordRepair(REPAIR_ID, DEVICE_ID, HASH_V1),
         registered["service"])
    return registered
