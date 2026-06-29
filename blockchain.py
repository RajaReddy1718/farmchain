from web3 import Web3
import json, os
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "name", "type": "string"}],
        "name": "registerFarmer",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "batchId", "type": "string"},
            {"internalType": "string", "name": "cropName", "type": "string"},
            {"internalType": "string", "name": "harvestDate", "type": "string"},
            {"internalType": "bool", "name": "isOrganic", "type": "bool"},
            {"internalType": "uint256", "name": "quantityKg", "type": "uint256"}
        ],
        "name": "registerBatch",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "batchId", "type": "string"},
            {"internalType": "string", "name": "handlerInfo", "type": "string"},
            {"internalType": "bool", "name": "tamper", "type": "bool"}
        ],
        "name": "addHandler",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "batchId", "type": "string"}],
        "name": "getBatch",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "bool", "name": "", "type": "bool"},
            {"internalType": "bool", "name": "", "type": "bool"},
            {"internalType": "string[]", "name": "", "type": "string[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "string", "name": "batchId", "type": "string"},
            {"indexed": False, "internalType": "address", "name": "farmer", "type": "address"},
            {"indexed": False, "internalType": "string", "name": "cropName", "type": "string"}
        ],
        "name": "BatchRegistered",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "string", "name": "batchId", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "handler", "type": "string"}
        ],
        "name": "HandlerAdded",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "string", "name": "batchId", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "handler", "type": "string"}
        ],
        "name": "TamperAlert",
        "type": "event"
    }
]

def get_contract():
    if not CONTRACT_ADDRESS or not CONTRACT_ABI:
        return None
    return w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI
    )

def _send_tx(fn, private_key):
    account = w3.eth.account.from_key(private_key)
    tx = fn.build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return {"tx_hash": tx_hash.hex()}

def register_farmer_on_chain(name, private_key):
    contract = get_contract()
    if not contract:
        return {"status": "blockchain not configured"}
    return _send_tx(contract.functions.registerFarmer(name), private_key)

def register_batch_on_chain(batch_id, crop_name, harvest_date, is_organic, quantity_kg, private_key):
    contract = get_contract()
    if not contract:
        return {"status": "blockchain not configured"}
    return _send_tx(
        contract.functions.registerBatch(batch_id, crop_name, harvest_date, is_organic, int(quantity_kg)),
        private_key
    )

def add_handler_on_chain(batch_id, handler_info, tamper, private_key):
    contract = get_contract()
    if not contract:
        return {"status": "blockchain not configured"}
    return _send_tx(
        contract.functions.addHandler(batch_id, handler_info, tamper),
        private_key
    )

def get_batch_from_chain(batch_id):
    contract = get_contract()
    if not contract:
        return None
    return contract.functions.getBatch(batch_id).call()