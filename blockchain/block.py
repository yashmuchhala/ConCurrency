import jsonpickle, time
import hashlib
import sys, copy
from typing import Dict

sys.path.append("../")
from config import MINE_RATE
from transaction.transaction import Transaction
from account.accounts import Accounts
from copy import deepcopy

MAX_HASH = "f" * 64
MAX_NONCE = 2 ** 64


class Block:
    def __init__(self, timestamp=0., nonce=0, parent_hash="", benef="", num=0, diff=4000, txs=[]):
        self.timestamp = timestamp
        self.nonce = nonce
        self.parent_hash = parent_hash
        self.benef = benef
        self.num = num
        self.diff = diff
        self.txs = txs

    @staticmethod
    def from_dict(d):
        b = Block()
        txs = d["txs"]
        b.__dict__ = d
        b.txs = []
        for d_tx in txs:
            tx = Transaction.from_dict(d_tx)
            b.txs.append(tx)
        return b

    def create_dict(self):
        d = deepcopy(self.__dict__)
        txs = self.txs
        d["txs"] = []
        for tx in txs:
            d["txs"].append(tx.__dict__)
        return d

    def __str__(self):
        return str(self.__dict__)

    def add_tx(self, tx: Transaction):
        self.txs.append(tx)

    @staticmethod
    def calc_hash(block):
        def sort_chars(block):
            d = block.__dict__.copy()
            txs = block.txs
            d["txs"] = []
            for tx in txs:
                d["txs"].append(tx.__dict__)
            return "".join(sorted(str(d)))

        # k = sha3.keccak_256(bytes(sort_chars(block), "utf-8"))
        # h = k.hexdigest()
        h = hashlib.sha1(bytes(sort_chars(block), "utf-8")).hexdigest()
        return h

    @staticmethod
    def validate_block(block, prev_block, accounts: Accounts, contract_accounts):
        basic = block.parent_hash == Block.calc_hash(
            prev_block) and block.num == prev_block.num + 1 and block.timestamp > prev_block.timestamp

        expected_diff = prev_block.diff
        if block.timestamp - prev_block.timestamp > MINE_RATE:
            expected_diff -= 1
        else:
            expected_diff += 1
        basic = basic and expected_diff == block.diff

        max_hash_val = int(MAX_HASH, 16)
        target_hash_val = max_hash_val // prev_block.diff
        nonce_val = int(Block.calc_hash(block), 16) <= target_hash_val
        basic = basic and nonce_val
        if not nonce_val:
            print("Nonce validation failed")

        # b, new_accounts, validators, new_contract_accounts = Transaction.apply_txs(block.txs, accounts,
        #                                                                            contract_accounts, block.benef)
        # if not b:
        #     print("apply_txs failed")

        return basic  # and b
