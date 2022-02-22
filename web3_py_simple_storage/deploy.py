import json
from solcx import compile_standard, install_solc
from web3 import Web3

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc('0.6.0')

compile_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "SimpleStorage.sol": {
                "content": simple_storage_file
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.6.0"
)

with open("compiled_code.json", "w") as file:
    json.dump(compile_sol, file)

bytecode = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
abi = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# To run with GANACHE:
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = "YOUR_PRIVATE_KEY"

# To run with INFURA:
# w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/4020f615ae40479ea722c08822315a40"))
# chain_id = 4
# my_address = "0x7cc2D8c9D03604af807274Bd4C09d12fa9204E85"
# private_key = "YOUR_PRIVATE_KEY"

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# When we call a function, we just simulate working with it.
# It's like "blue buttons" from rememix. That's why when we call
# `store(15)` we'll not have 15 as result when retrieving it right
# after.

# When using Infura we need to especify `"from": w3.toChecksumAddress(my_address)` because
# it doesn't default to my first account.
print(simple_storage.functions.retrieve().call({"from": w3.toChecksumAddress(my_address)}))
print(simple_storage.functions.store(15).call())
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
        "gasPrice": w3.eth.gas_price,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
print("Updating contract...")
send_store_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_hash)
print("Updated!")

print(simple_storage.functions.retrieve().call())
