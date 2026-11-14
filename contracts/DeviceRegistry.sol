
pragma solidity ^0.8.28;


contract DeviceRegistry {
    bytes32 public constant SHOP_ROLE = keccak256("SHOP_ROLE");
    bytes32 public constant SERVICE_ROLE = keccak256("SERVICE_ROLE");

    address public immutable administrator;
    mapping(bytes32 => mapping(address => bool)) private permissions;

    struct Device {
        bool exists;
        address registeredBy;
        uint64 registeredAt;
    }

    struct Version {
        bytes32 dataHash;
        address author;
        uint64 recordedAt;
    }

    struct Repair {
        bool exists;
        bytes32 deviceId;
        address service;
        Version[] versions;
    }

    mapping(bytes32 => Device) private devices;
    mapping(bytes32 => Repair) private repairs;

    event RoleGranted(bytes32 indexed role, address indexed account);
    event RoleRevoked(bytes32 indexed role, address indexed account);
    event DeviceRegistered(bytes32 indexed deviceId, address indexed shop);
    event RepairRecorded(bytes32 indexed repairId, bytes32 indexed deviceId, address indexed service, bytes32 dataHash);
    event RepairCorrected(bytes32 indexed repairId, uint256 indexed newVersion, bytes32 newDataHash);

    modifier onlyAdmin() {
        require(msg.sender == administrator, "Only administrator");
        _;
    }

    modifier onlyRole(bytes32 role) {
        require(permissions[role][msg.sender], "Missing role");
        _;
    }

    constructor() {
        administrator = msg.sender;
    }

    function hasRole(bytes32 role, address account) external view returns (bool) {
        return permissions[role][account];
    }

    function grantRole(bytes32 role, address account) external onlyAdmin {
        require(role == SHOP_ROLE || role == SERVICE_ROLE, "Unknown role");
        require(account != address(0), "Zero address");
        require(!permissions[role][account], "Already granted");
        permissions[role][account] = true;
        emit RoleGranted(role, account);
    }

    function revokeRole(bytes32 role, address account) external onlyAdmin {
        require(role == SHOP_ROLE || role == SERVICE_ROLE, "Unknown role");
        require(permissions[role][account], "Role not granted");
        permissions[role][account] = false;
        emit RoleRevoked(role, account);
    }

    
    function registerDevice(bytes32 deviceId) external onlyRole(SHOP_ROLE) {
        require(deviceId != bytes32(0), "Empty device id");
        require(!devices[deviceId].exists, "Device already registered");
        devices[deviceId] = Device(true, msg.sender, uint64(block.timestamp));
        emit DeviceRegistered(deviceId, msg.sender);
    }

    
    function recordRepair(bytes32 repairId, bytes32 deviceId, bytes32 dataHash)
        external onlyRole(SERVICE_ROLE)
    {
        require(repairId != bytes32(0), "Empty repair id");
        require(dataHash != bytes32(0), "Empty record hash");
        require(devices[deviceId].exists, "Device not registered");
        require(!repairs[repairId].exists, "Repair already recorded");

        Repair storage r = repairs[repairId];
        r.exists = true;
        r.deviceId = deviceId;
        r.service = msg.sender;
        r.versions.push(Version(dataHash, msg.sender, uint64(block.timestamp)));
        emit RepairRecorded(repairId, deviceId, msg.sender, dataHash);
    }

    
    function correctRepair(bytes32 repairId, bytes32 newDataHash)
        external onlyRole(SERVICE_ROLE)
    {
        Repair storage r = repairs[repairId];
        require(r.exists, "Repair not found");
        require(msg.sender == r.service, "Only original service");
        require(newDataHash != bytes32(0), "Empty record hash");
        require(newDataHash != r.versions[r.versions.length - 1].dataHash, "Hash unchanged");

        r.versions.push(Version(newDataHash, msg.sender, uint64(block.timestamp)));
        emit RepairCorrected(repairId, r.versions.length - 1, newDataHash);
    }

    
    function verifyRepair(bytes32 repairId, bytes32 candidateHash) external view returns (bool) {
        Repair storage r = repairs[repairId];
        if (!r.exists) return false;
        return candidateHash == r.versions[r.versions.length - 1].dataHash;
    }

    function getDevice(bytes32 deviceId)
        external view returns (bool exists, address registeredBy, uint64 registeredAt)
    {
        Device storage d = devices[deviceId];
        return (d.exists, d.registeredBy, d.registeredAt);
    }

    function getRepair(bytes32 repairId)
        external view returns (
            bool exists,
            bytes32 deviceId,
            address service,
            bytes32 latestHash,
            uint256 latestVersion
        )
    {
        Repair storage r = repairs[repairId];
        if (!r.exists) return (false, bytes32(0), address(0), bytes32(0), 0);
        return (true, r.deviceId, r.service, r.versions[r.versions.length - 1].dataHash, r.versions.length - 1);
    }

    function getVersionCount(bytes32 repairId) external view returns (uint256) {
        return repairs[repairId].versions.length;
    }

    function getRepairVersion(bytes32 repairId, uint256 version)
        external view returns (bytes32 dataHash, address author, uint64 recordedAt)
    {
        require(repairs[repairId].exists, "Repair not found");
        require(version < repairs[repairId].versions.length, "Version out of range");
        Version storage v = repairs[repairId].versions[version];
        return (v.dataHash, v.author, v.recordedAt);
    }
}
