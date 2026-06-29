// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FarmChain {

    struct Batch {
        string batchId;
        address farmer;
        string cropName;
        string harvestDate;
        bool isOrganic;
        uint256 quantityKg;
        bool tamperDetected;
        string[] handlerLog;
        bool exists;
    }

    mapping(string => Batch) public batches;
    mapping(address => string) public farmers;

    event BatchRegistered(string batchId, address farmer, string cropName);
    event HandlerAdded(string batchId, string handler);
    event TamperAlert(string batchId, string handler);

    function registerFarmer(string memory name) public {
        farmers[msg.sender] = name;
    }

    function registerBatch(
        string memory batchId,
        string memory cropName,
        string memory harvestDate,
        bool isOrganic,
        uint256 quantityKg
    ) public {
        require(!batches[batchId].exists, "Batch already registered");
        string[] memory log;
        batches[batchId] = Batch(
            batchId, msg.sender, cropName,
            harvestDate, isOrganic, quantityKg,
            false, log, true
        );
        emit BatchRegistered(batchId, msg.sender, cropName);
    }

    function addHandler(
        string memory batchId,
        string memory handlerInfo,
        bool tamper
    ) public {
        require(batches[batchId].exists, "Batch not found");
        batches[batchId].handlerLog.push(handlerInfo);
        if (tamper) {
            batches[batchId].tamperDetected = true;
            emit TamperAlert(batchId, handlerInfo);
        }
        emit HandlerAdded(batchId, handlerInfo);
    }

    function getBatch(string memory batchId) public view returns (
        string memory, address, string memory,
        bool, bool, string[] memory
    ) {
        Batch memory b = batches[batchId];
        require(b.exists, "Batch not found");
        return (b.cropName, b.farmer, b.harvestDate,
                b.isOrganic, b.tamperDetected, b.handlerLog);
    }
}