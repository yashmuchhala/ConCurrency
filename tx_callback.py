from transaction.transaction import Transaction

from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from logger import Logger
from config import *
from blockchain.block import Block
from threading import Thread
import time


class TxCallback(SubscribeCallback):
    def __init__(self, sub_key, pub_key, channel_name, vk="", blockchain=None, sk=None):
        super()
        self.tx_pool = set()
        self.channel_name = channel_name
        self.vk = vk
        self.sk = sk
        self.blockchain = blockchain
        self.nonce = 0

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = sub_key
        pnconfig.publish_key = pub_key
        self.pubnub = PubNub(pnconfig)
        self.pubnub.add_listener(self)
        self.pubnub.subscribe().channels(channel_name).execute()

    def status(self, pubnub, status):
        pass

    def presence(self, pubnub, presence):
        pass

    def message(self, pubnub, message):
        Logger.pubnub_log(message)
        tx = Transaction.from_dict(message.message)
        # if tx.verify_sign():
        self.blockchain.tx_pool_sem.acquire()
        self.tx_pool.add(tx)
        self.blockchain.tx_pool_sem.release()
        if tx.to_vk == RUN_ADDR:
            highest_block = self.blockchain.get_highest_block()
            accounts, txs, validators, contract_accounts = self.blockchain.get_state(Block.calc_hash(highest_block))
            if tx.from_vk in contract_accounts and self.vk in validators:
                def f(contract_accounts, vk, publish, from_vk):
                    def check_completion(type_op):
                        # type_op is either "m", "s" or "r"
                        Logger.p("Checking completion," + type_op)
                        highest_block = self.blockchain.get_highest_block()
                        accounts, txs, validators, contract_accounts = self.blockchain.get_state(
                            Block.calc_hash(highest_block))
                        state = contract_accounts[tx.from_vk].state
                        print(state)
                        for elm in state:
                            if (type(elm) == tuple or type(elm) == list) and elm[1] == type_op:
                                continue
                            else:
                                return False
                        return True

                    def run(type_op):
                        highest_block = self.blockchain.get_highest_block()
                        accounts, txs, validators, contract_accounts = self.blockchain.get_state(
                            Block.calc_hash(highest_block))
                        new_state, shard_num = Transaction.run_contract(contract_accounts[from_vk], vk, type_op)
                        new_tx = Transaction(0, vk, from_vk, 0, 0, shard_num=shard_num)
                        new_tx.new_state = new_state
                        publish(new_tx)

                    run("m")
                    while not check_completion("m"):
                        time.sleep(SLEEP_BETWEEN_COMPLETION_CHECK)
                    run("s")
                    while not check_completion("s"):
                        time.sleep(SLEEP_BETWEEN_COMPLETION_CHECK)
                    run("r")

                Logger.p("Creating and starting new thread")
                Thread(target=f, args=(contract_accounts, self.vk, self.publish, tx.from_vk)).start()
            else:
                Logger.p("Tx has RUN_ADDR but not a contract account or you are not in validator set")
        else:
            Logger.p("Tx does not have RUN_ADDR")
        Logger.p("signature verified, tx added to tx pool")

    # else:
    #         Logger.p("tx with invalid signature received")

    def publish(self, tx):
        tx.nonce = self.nonce
        self.nonce += 1
        tx.sign = tx.create_sign(self.sk)
        Logger.publish_attempt(tx)
        self.pubnub.publish().channel(self.channel_name).message(tx.__dict__).pn_async(
            Logger.succesfull_publish)
