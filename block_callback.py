from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from logger import Logger
from blockchain.blockchain import Blockchain, Block


class BlockCallback(SubscribeCallback):
    def __init__(self, sub_key, pub_key, channel_name):
        super()
        self.channel_name = channel_name

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = sub_key
        pnconfig.publish_key = pub_key
        self.pubnub = PubNub(pnconfig)
        self.pubnub.add_listener(self)
        self.pubnub.subscribe().channels(channel_name).execute()

        self.blockchain = Blockchain()

    def status(self, pubnub, status):
        pass

    def presence(self, pubnub, presence):
        pass

    def message(self, pubnub, message):
        Logger.pubnub_log(message)
        block = Block.from_dict(message.message)

        if block.parent_hash in self.blockchain.chain:
            parent_block = self.blockchain.chain[block.parent_hash]
            accounts, txs, validators, contract_accounts = self.blockchain.get_state(block.parent_hash)
            if Block.validate_block(block, parent_block, accounts, contract_accounts):
                self.blockchain.add_block(block)
                Logger.p("Block successfully added to chain")
            else:
                Logger.p("Invalid block received, Block failed validation")
        else:
            Logger.p("Invalid block received, parent hash not found")

    def publish(self, block):
        Logger.publish_attempt(block)
        d = block.create_dict()
        self.pubnub.publish().channel(self.channel_name).message(d).pn_async(
            Logger.succesfull_publish)
