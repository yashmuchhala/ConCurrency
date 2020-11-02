from .account import Account


class ContractAccount(Account):
    def __init__(self, vk=None, bal=10, mapper="", num_shards=1, shuffler="", reducer=""):
        super().__init__(vk, bal)
        self.mapper = mapper
        self.shuffler = shuffler
        self.reducer = reducer
        self.num_shards = num_shards
        self.state = []
        for i in range(num_shards):
            self.state.append(-1)
