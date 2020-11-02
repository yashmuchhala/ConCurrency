from .account import Account
import jsonpickle


class Accounts:
    def __init__(self):
        self.accounts = dict()

    def __getitem__(self, item):
        if item not in self.accounts:
            self.accounts[item] = Account(vk=item)
        return self.accounts[item]

    def __setitem__(self, key, value):
        self.accounts[key] = value

    def __str__(self):
        return jsonpickle.encode(self, indent=4)
