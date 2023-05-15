from web3 import Web3, eth
import web3



w3 = Web3(Web3.HTTPProvider('http://121.8.169.179:8545'))

w3.is_connected()

w3.eth.get_block('latest')