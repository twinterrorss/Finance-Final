
import pytest
from eth_tester.exceptions import TransactionFailed
from web3 import Web3

from repairpass.local_chain import send
from .conftest import DEVICE_ID, REPAIR_ID, HASH_V1, HASH_V2, TAMPERED, ZERO


def call_reverts(method, from_address, reason):
    with pytest.raises(TransactionFailed, match=reason):
        method.call({"from": from_address})


def test_01_approved_shop_registers_device(env):
    c = env["contract"]
    receipt = send(env["w3"], c.functions.registerDevice(DEVICE_ID), env["shop"])
    events = c.events.DeviceRegistered().process_receipt(receipt)
    assert len(events) == 1
    assert events[0]["args"]["deviceId"] == DEVICE_ID
    assert events[0]["args"]["shop"] == env["shop"]
    exists, registered_by, registered_at = c.functions.getDevice(DEVICE_ID).call()
    assert exists is True and registered_by == env["shop"] and registered_at > 0


def test_02_unapproved_account_cannot_register_device(env):
    call_reverts(env["contract"].functions.registerDevice(DEVICE_ID), env["stranger"], "Missing role")


def test_03_duplicate_device_registration_rejected(registered):
    call_reverts(registered["contract"].functions.registerDevice(DEVICE_ID), registered["shop"], "Device already registered")


def test_04_service_records_and_verifies_repair(registered):
    c = registered["contract"]
    receipt = send(registered["w3"], c.functions.recordRepair(REPAIR_ID, DEVICE_ID, HASH_V1), registered["service"])
    events = c.events.RepairRecorded().process_receipt(receipt)
    assert len(events) == 1
    assert events[0]["args"]["repairId"] == REPAIR_ID
    assert events[0]["args"]["deviceId"] == DEVICE_ID
    assert events[0]["args"]["service"] == registered["service"]
    assert events[0]["args"]["dataHash"] == HASH_V1
    assert c.functions.verifyRepair(REPAIR_ID, HASH_V1).call() is True
    assert c.functions.getVersionCount(REPAIR_ID).call() == 1


def test_05_cannot_repair_unregistered_device(env):
    call_reverts(env["contract"].functions.recordRepair(REPAIR_ID, DEVICE_ID, HASH_V1), env["service"], "Device not registered")


def test_06_stranger_cannot_record_repair(registered):
    call_reverts(registered["contract"].functions.recordRepair(REPAIR_ID, DEVICE_ID, HASH_V1), registered["stranger"], "Missing role")


def test_07_modified_record_detected(repaired):
    c = repaired["contract"]
    assert c.functions.verifyRepair(REPAIR_ID, TAMPERED).call() is False
    assert c.functions.verifyRepair(Web3.keccak(text="unknown"), HASH_V1).call() is False


def test_08_correction_retains_history(repaired):
    c = repaired["contract"]
    receipt = send(repaired["w3"], c.functions.correctRepair(REPAIR_ID, HASH_V2), repaired["service"])
    events = c.events.RepairCorrected().process_receipt(receipt)
    assert len(events) == 1
    assert events[0]["args"]["repairId"] == REPAIR_ID
    assert events[0]["args"]["newVersion"] == 1
    assert events[0]["args"]["newDataHash"] == HASH_V2
    assert c.functions.getVersionCount(REPAIR_ID).call() == 2
    assert c.functions.getRepairVersion(REPAIR_ID, 0).call()[0] == HASH_V1
    assert c.functions.getRepairVersion(REPAIR_ID, 1).call()[0] == HASH_V2
    assert c.functions.verifyRepair(REPAIR_ID, HASH_V1).call() is False
    assert c.functions.verifyRepair(REPAIR_ID, HASH_V2).call() is True


def test_09_other_service_cannot_correct_repair(repaired):
    call_reverts(repaired["contract"].functions.correctRepair(REPAIR_ID, HASH_V2), repaired["other_service"], "Only original service")


def test_10_duplicate_repair_id_rejected(repaired):
    call_reverts(repaired["contract"].functions.recordRepair(REPAIR_ID, DEVICE_ID, HASH_V2), repaired["service"], "Repair already recorded")


def test_11_zero_identifiers_and_hashes_rejected(registered):
    c = registered["contract"]
    call_reverts(c.functions.registerDevice(ZERO), registered["shop"], "Empty device id")
    call_reverts(c.functions.recordRepair(ZERO, DEVICE_ID, HASH_V1), registered["service"], "Empty repair id")
    call_reverts(c.functions.recordRepair(REPAIR_ID, DEVICE_ID, ZERO), registered["service"], "Empty record hash")


def test_12_only_admin_can_grant_or_revoke_roles(env):
    c = env["contract"]
    call_reverts(c.functions.grantRole(env["shop_role"], env["stranger"]), env["stranger"], "Only administrator")
    call_reverts(c.functions.revokeRole(env["shop_role"], env["shop"]), env["stranger"], "Only administrator")


def test_13_revoked_service_cannot_correct(repaired):
    c = repaired["contract"]
    send(repaired["w3"], c.functions.revokeRole(repaired["service_role"], repaired["service"]), repaired["admin"])
    assert c.functions.hasRole(repaired["service_role"], repaired["service"]).call() is False
    call_reverts(c.functions.correctRepair(REPAIR_ID, HASH_V2), repaired["service"], "Missing role")


def test_14_identical_correction_hash_rejected(repaired):
    call_reverts(repaired["contract"].functions.correctRepair(REPAIR_ID, HASH_V1), repaired["service"], "Hash unchanged")


def test_15_public_read_only_verification(repaired):
    c = repaired["contract"]
    assert c.functions.verifyRepair(REPAIR_ID, HASH_V1).call({"from": repaired["stranger"]}) is True
    exists, device_id, service, latest_hash, latest_version = c.functions.getRepair(REPAIR_ID).call({"from": repaired["stranger"]})
    assert exists is True and device_id == DEVICE_ID
    assert service == repaired["service"]
    assert latest_hash == HASH_V1 and latest_version == 0
