from account.contract_account import ContractAccount
from typing import Dict
from account.accounts import Accounts
from copy import deepcopy
from config import *
import ecdsa


class Transaction:
    def __init__(self, nonce, from_vk, to_vk, val, fee, shard_num=-1):
        self.nonce = nonce
        self.from_vk = from_vk
        self.to_vk = to_vk
        self.val = val
        self.fee = fee
        self.shard_num = shard_num
        self.new_state = False
        self.sign = ""
        self.mapper_code = ""
        self.reducer_code = ""
        self.shuffler_code = ""

    def __str__(self):
        return "Transaction:" + str(self.__dict__)

    def get_dict_wo_sign(self):
        t = self.__dict__.copy()
        t["sign"] = ""
        return t

    def verify_sign(self):
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.from_vk))
        data = bytes(str(self.get_dict_wo_sign()), "utf-8")
        sign = bytes.fromhex(self.sign)
        return vk.verify(sign, data)

    def create_sign(self, sk: ecdsa.SigningKey):
        data = bytes(str(self.get_dict_wo_sign()), "utf-8")
        return sk.sign(data).hex()

    @staticmethod
    def from_dict(d):
        t = Transaction(0, 0, 0, 0, 0)
        t.__dict__ = d
        return t

    @staticmethod
    def _get_num_validators_for_shard(vals, shard_num, num_shards):
        r = 0
        for val in vals:
            if int(val, 16) % num_shards == shard_num:
                r += 1
        return r

    @staticmethod
    def apply_txs(txs, accounts: Accounts, contract_accounts: Dict, benef, existing_validators):
        """
        Applies given transactions on the given state(accounts, contracts accounts) also calculates
        newly registered validators in these txs.
        To register a new contract send a tx to DEPLOY_ADDR with val as DEPLOY_VAL and number of shards in tx.shard_num
        and code in tx.code. This will add tx.from_vk as a contract address with empty state
        To register as a validator send VAL_COST to VAL_ADDR
        To run the code associated with a contract address send a tx from it to RUN_ADDR
        :param txs:
        :param accounts:
        :param contract_accounts:
        :param benef:
        :return:
        """

        temp_accounts = deepcopy(accounts)
        temp_contract_accounts = deepcopy(contract_accounts)
        d = {}
        validators = set()
        for tx in sorted(txs, key=lambda x: x.from_vk):
            if temp_accounts[tx.from_vk].withdraw(tx.val + tx.fee):
                temp_accounts[benef].deposit(tx.fee)
                temp_accounts[tx.to_vk].deposit(tx.val)
                if tx.to_vk == VAL_ADDR and tx.val == VAL_COST:
                    validators.add(tx.from_vk)
                elif tx.to_vk == DEPLOY_ADDR and tx.val == DEPLOY_COST:
                    temp_contract_accounts[tx.from_vk] = ContractAccount(tx.from_vk, mapper=tx.mapper_code,
                                                                         num_shards=tx.shard_num,
                                                                         reducer=tx.reducer_code,
                                                                         shuffler=tx.shuffler_code)
            else:
                return False, None, None, None
            if tx.shard_num != -1 and tx.new_state and tx.to_vk in contract_accounts:
                tu = (tx.shard_num, tx.to_vk, str(tx.new_state))
                if tu in d:
                    d[tu][0] += 1
                    d[tu][1].append(tx)
                else:
                    d[tu] = [1, [tx, ]]
                if d[tu][0] > 0.5 * Transaction._get_num_validators_for_shard(existing_validators, tx.shard_num,
                                                                              contract_accounts[tx.to_vk].num_shards):
                    temp_contract_accounts[tx.to_vk].state[tx.shard_num] = tx.new_state
        return True, temp_accounts, validators, temp_contract_accounts

    @staticmethod
    def get_mutually_valid_txs(txs, accounts: Accounts, contract_accounts, benef, existing_validators):
        """
        Same as apply_txs but if a tx is found invalid it is ignored.
        Returns list of mutually valid txs and state
        :param txs:
        :param accounts:
        :param contract_accounts:
        :param benef:
        :return:
        """
        temp_accounts = deepcopy(accounts)
        mutually_val_txs = set()
        validators = set()
        d = {}
        temp_contract_accounts = deepcopy(contract_accounts)
        for tx in sorted(txs, key=lambda x: x.from_vk):
            if temp_accounts[tx.from_vk].withdraw(tx.val + tx.fee) and tx.new_state is False:
                temp_accounts[benef].deposit(tx.fee)
                temp_accounts[tx.to_vk].deposit(tx.val)
                if tx.to_vk == VAL_ADDR and tx.val == VAL_COST:
                    validators.add(tx.from_vk)
                elif tx.to_vk == DEPLOY_ADDR and tx.val == DEPLOY_COST:
                    temp_contract_accounts[tx.from_vk] = ContractAccount(tx.from_vk, mapper=tx.mapper_code,
                                                                         num_shards=tx.shard_num,
                                                                         reducer=tx.reducer_code,
                                                                         shuffler=tx.shuffler_code)
                mutually_val_txs.add(tx)
            if tx.shard_num != -1 and tx.new_state is not False and tx.to_vk in contract_accounts:
                tu = (tx.shard_num, tx.to_vk, str(tx.new_state))
                if tu in d:
                    d[tu][0] += 1
                    d[tu][1].append(tx)
                else:
                    d[tu] = [1, [tx, ]]
                if d[tu][0] > 0.5 * Transaction._get_num_validators_for_shard(existing_validators, tx.shard_num,
                                                                              contract_accounts[tx.to_vk].num_shards):
                    temp_contract_accounts[tx.to_vk].state[tx.shard_num] = tx.new_state
                    for ttxs in d[tu][1]:
                        mutually_val_txs.add(ttxs)
                    d[tu] = [0, []]
            else:
                continue
        return mutually_val_txs, temp_accounts, validators, temp_contract_accounts

    @staticmethod
    def run_contract(contract_account: ContractAccount, vk, type_op):
        shard_num = int(vk, 16) % contract_account.num_shards
        print(
            ":::::::::::::::Received tx is a valid run contract tx, running contract now, %s:::::::::::::::" % type_op)
        print(":::::::::::::::You are in shard:", shard_num)
        if type_op == "m":
            exec(contract_account.mapper, globals())
        if type_op == "s":
            exec(contract_account.shuffler, globals())
        if type_op == "r":
            exec(contract_account.reducer, globals())
        d = f(contract_account.state, shard_num)
        d = (d, type_op)
        # contract_account.state[shard_num] = d
        print(":::::::::::::::Execution done:::::::::::::::")
        return d, shard_num
