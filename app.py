from threading import Thread

import ecdsa
import jsonpickle

from block_callback import BlockCallback
from blockchain.block import Block
from config import *
from logger import Logger
from transaction.transaction import Transaction
from tx_callback import TxCallback
import time


class App:
    def __init__(self):
        print("Generating keys")
        # time.sleep(5)
        self.sk = ecdsa.SigningKey.generate()
        self.vk = self.sk.verifying_key
        print("Keys generated", "vk", self.vk.to_string().hex())
        for i in range(1, 10):
            print(i, int(self.vk.to_string().hex(), 16) % i)
        self.blockCallBack = BlockCallback(SUBSCRIBE_KEY, PUBLISH_KEY, BLOCK_CHANNEL)
        self.txCallBack = TxCallback(SUBSCRIBE_KEY, PUBLISH_KEY, TX_CHANNEL, sk=self.sk,
                                     blockchain=self.blockCallBack.blockchain,
                                     vk=self.vk.to_string().hex())

    def start_mining(self):
        def g():
            while True:
                parent_block = self.blockCallBack.blockchain.get_highest_block()
                mined_block = self.blockCallBack.blockchain.mine_block(parent_block, self.txCallBack.tx_pool,
                                                                       benef=self.vk.to_string().hex())
                if mined_block:
                    self.blockCallBack.publish(mined_block)
                time.sleep(SLEEP_BETWEEN_MINE)

        t = Thread(target=g)
        t.start()
        print("Mining started in background thread")

    def send_tx(self, to, val, fee, mapper_code="", shard_num=-1, shuffler_code="", reducer_code=""):
        tx = Transaction(0, self.vk.to_string().hex(), to, val, fee, shard_num=shard_num)
        tx.mapper_code = mapper_code
        tx.reducer_code = reducer_code
        tx.shuffler_code = shuffler_code
        self.txCallBack.publish(tx)

    def get_complete_state(self):
        # print(self.blockCallBack.blockchain)
        # print(self.txCallBack.tx_pool)
        accounts, applied_txs, validators, contract_accounts = self.blockCallBack.blockchain.get_state(
            Block.calc_hash(self.blockCallBack.blockchain.get_highest_block()))
        return accounts, applied_txs, validators, contract_accounts

    def get_state(self):
        accounts, txs, validators, contract_accounts = self.get_complete_state()
        # bal = INITIAL_BALANCE
        # if self.vk.to_string().hex() in accounts:
        bal = accounts[self.vk.to_string().hex()]
        val = self.vk.to_string().hex() in validators
        return bal, val
        # print("Your balance:", accounts[self.vk.to_string().hex()].bal)
        # if self.vk.to_string().hex() in validators:
        #     print("You are a validator")

    def run_contract(self):
        accounts, txs, validators, contract_accounts = self.blockCallBack.blockchain.get_state(
            Block.calc_hash(self.blockCallBack.blockchain.get_highest_block()))
        if self.vk.to_string().hex() in contract_accounts:
            tx = Transaction(0, self.vk.to_string().hex(), RUN_ADDR, 0, 0)
            self.txCallBack.publish(tx)
            return True
        return False

    def register_as_validator(self):
        self.send_tx(VAL_ADDR, VAL_COST, 0)

    def get_contract_state(self):
        accounts, txs, validators, contract_accounts = self.get_complete_state()
        h = self.vk.to_string().hex()
        if h in contract_accounts:
            return contract_accounts[h].state
        return None
