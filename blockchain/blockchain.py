from .block import Block
from typing import Set, Dict
import sys, time
from threading import Semaphore

sys.path.append("../")
from config import MINE_RATE
from account.accounts import Accounts
from transaction.transaction import Transaction
from account.account import Account

MAX_HASH = "f" * 64
MAX_NONCE = 2 ** 64


class Blockchain:
    def __init__(self):
        # key: hash, value: block
        self.chain = {}
        # key: num, value: block
        self.num_to_block = {}
        # prevents concurrent access to the the global tx_pool set
        self.tx_pool_sem = Semaphore()
        # prevents concurrent access to this blockchain object
        self.blockchain_sem = Semaphore()
        self.add_block(Block())

    def __str__(self):
        ret = ""
        for h in self.chain:
            ret += h + ":\n"
            ret += str(self.chain[h]) + "\n"
        return ret

    def add_block(self, block: Block):
        self.blockchain_sem.acquire()
        h = Block.calc_hash(block)
        self.chain[h] = block
        if block.num in self.num_to_block:
            self.num_to_block[block.num].append(block)
        else:
            self.num_to_block[block.num] = [block, ]
        self.blockchain_sem.release()

    def get_highest_block(self):
        self.blockchain_sem.acquire()
        ret = self.num_to_block[max(self.num_to_block.keys())][0]
        self.blockchain_sem.release()
        return ret

    def get_state(self, block_hash):
        self.blockchain_sem.acquire()
        ret = self._get_state_helper(block_hash)
        self.blockchain_sem.release()
        return ret

    def _get_state_helper(self, block_hash) -> (Accounts, Set[Transaction], Set[Account], Dict):
        """
        Applies all transactions from genesis till given block and returns the final state
        ,all the transactions in the entire chain, the validators registered till that block and the contract accounts
         until then
        :param block_hash:
        :return: Accounts
        """
        if self.chain[block_hash].num == 0:  # if genesis, init account state, applied txs, validators
            # and contract accounts to nulls
            return Accounts(), set(), set(), {}

        accounts, txs, validators, existing_contract_accounts = self._get_state_helper(
            self.chain[block_hash].parent_hash)
        txs = txs.union(set(self.chain[block_hash].txs))
        b, new_accounts, temp_vals, new_contract_accounts = Transaction.apply_txs(self.chain[block_hash].txs,
                                                                                  accounts,
                                                                                  existing_contract_accounts,
                                                                                  self.chain[block_hash].benef,
                                                                                  validators)
        validators = validators.union(temp_vals)
        assert b
        return new_accounts, txs, validators, new_contract_accounts

    def mine_block(self, last_block: Block, all_txs, benef="", max_txs_per_block=300) -> Block:
        """
        Calculates headers for a new block with parent block as last_block
        finds mutually valid set of txs from all_txs - txs included till parent
        :param last_block:
        :param all_txs:
        :param benef:
        :return:
        """
        max_hash_val = int(MAX_HASH, 16)
        target_hash_val = max_hash_val // last_block.diff
        new_diff = last_block.diff
        if time.time() - last_block.timestamp > MINE_RATE:
            new_diff -= 1
        else:
            new_diff += 1

        if new_diff < 1:
            new_diff = 1

        accounts_state, applied_txs, existing_validators, existing_contract_accounts = self.get_state(
            Block.calc_hash(last_block))
        new_txs = []
        self.tx_pool_sem.acquire()
        # loop to get new txs to include in mined block. effectively all_txs - applied_txs
        for tx in all_txs:
            if len(new_txs) > max_txs_per_block:
                break
            found = False
            for ttx in applied_txs:
                if ttx.__dict__ == tx.__dict__:
                    found = True
                    break
            if not found:
                new_txs.append(tx)
        self.tx_pool_sem.release()
        if new_txs:
            val_txs, new_state, new_validators, new_contract_accounts = Transaction.get_mutually_valid_txs(
                new_txs, accounts_state, existing_contract_accounts, benef, existing_validators)
            if len(val_txs) > 0:
                block = Block(timestamp=time.time(), parent_hash=Block.calc_hash(last_block), benef=benef,
                              num=last_block.num + 1,
                              diff=new_diff, txs=val_txs)
                print("Attempting to mine, headers calculated, number of txs = ", len(val_txs))
                curr_nonce = 0
                while int(Block.calc_hash(block), 16) > target_hash_val:
                    if curr_nonce > MAX_NONCE:
                        print("nonce exceeded max")
                    # print(hex(target_hash_val), Block.calc_hash(block))
                    curr_nonce += 1
                    block.nonce = curr_nonce

                return block
            else:
                return None
        else:
            return None


if __name__ == '__main__':
    blockchain = Blockchain()
    blockchain.add_block(Block())
    for i in range(20):
        new_block = blockchain.mine_block(blockchain.get_highest_block(), benef="benef%s" % i)
        blockchain.add_block(new_block)
    print(blockchain)
