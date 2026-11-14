
from repairpass.local_chain import contract_artifact, deploy_registry, digest, make_local_chain, send


def main():
    print("RepairPass — educational local blockchain demo (Python)")
    print("No real customer data, payments, or public network.\n")

    w3 = make_local_chain()
    admin, shop, service, verifier = w3.eth.accounts[:4]
    registry = deploy_registry(w3, contract_artifact())
    print("[1] Deployed DeviceRegistry on local py-evm:", registry.address)

    shop_role = registry.functions.SHOP_ROLE().call()
    service_role = registry.functions.SERVICE_ROLE().call()
    send(w3, registry.functions.grantRole(shop_role, shop), admin, "grant shop role")
    send(w3, registry.functions.grantRole(service_role, service), admin, "grant service role")
    print("[2] Approved fictional shop and service accounts")

    device_id = digest("FICTIONAL-DEVICE-2026-001")
    repair_id = digest("FICTIONAL-REPAIR-2026-001")
    old_record = '{"fake_device":"device-001","service":"screen replacement","status":"completed"}'
    updated_record = '{"fake_device":"device-001","service":"screen replacement","status":"completed","correction":"date fixed"}'
    old_hash = digest(old_record)
    updated_hash = digest(updated_record)

    send(w3, registry.functions.registerDevice(device_id), shop, "device registration")
    print("[3] Fictional device registered by approved shop")
    send(w3, registry.functions.recordRepair(repair_id, device_id, old_hash), service, "repair record")
    print("[4] Repair content hash stored on chain:", old_hash.hex())

    original_match = registry.functions.verifyRepair(repair_id, old_hash).call({"from": verifier})
    tampered_match = registry.functions.verifyRepair(repair_id, digest("FICTIONAL-TAMPERED-CONTENT")).call({"from": verifier})
    print("[5] Original content matches:", original_match)
    print("[6] Tampered content matches:", tampered_match)
    assert original_match is True and tampered_match is False

    send(w3, registry.functions.correctRepair(repair_id, updated_hash), service, "repair correction")
    print("[7] Correction appended (original version preserved)")
    old_is_current = registry.functions.verifyRepair(repair_id, old_hash).call()
    new_is_current = registry.functions.verifyRepair(repair_id, updated_hash).call()
    count = registry.functions.getVersionCount(repair_id).call()
    first_hash, first_author, _ = registry.functions.getRepairVersion(repair_id, 0).call()
    print("[8] Old hash still current:", old_is_current)
    print("[9] Corrected hash is current:", new_is_current)
    print("[10] Version count:", count)
    print("[11] Historical version 0 hash:", first_hash.hex())
    assert old_is_current is False and new_is_current is True
    assert count == 2 and first_hash == old_hash and first_author == service
    print("\nDemo completed successfully — temporary local blockchain only.")


if __name__ == "__main__":
    main()
