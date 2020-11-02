import jsonpickle
from config import *
from app import App
import os

if "nb_data_loc" in os.environ:
    print(os.environ["nb_data_loc"])
else:
    print("!!!!!!!!!!!!!!!!!!!!env not set !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

app = App()

opt = 1
while opt != -1:
    opt = int(input(
        "1. mine, 2. tx,3. Display, 4. My Balance, 5. Create Contract 6. Run Contract 7. Register as Validator 8. "
        "View Contract state -1. "
        "End\n"))
    if opt == 1:
        app.start_mining()
    elif opt == 2:
        to = input("Enter vk\n")
        # to is in hex
        val, fee = list(map(float, input("val fee\n").split()))
        app.send_tx(to, val, fee)
    elif opt == 3:
        print("BlockChain:--------\n", app.blockCallBack.blockchain)
        print("Tx Pool:------------\n", app.txCallBack.tx_pool)
        accounts, applied_txs, validators, contract_accounts = app.get_complete_state()

        print("ACCOUNTS:", jsonpickle.encode(accounts))
        print("VALIDATORS", jsonpickle.encode(validators))
        print("CONTRACT ACCOUNTS", jsonpickle.encode(contract_accounts))
        # print("TXS", applied_txs)

    elif opt == 4:
        # TODO use default dict instead of Accounts class
        bal, val = app.get_state()
        print("Your balance:", bal)
        if val:
            print("You are a validator")

    elif opt == 5:
        fnames = input("Enter mapper, shuffler, reducer file locations\n")
        fnames = fnames.split()
        try:
            codes = []
            for f in fnames:
                with open(f, "r") as ft:
                    code = ft.read()
                    codes.append(code)
            num_shards = int(input("Enter number of shards"))
            app.send_tx(DEPLOY_ADDR, DEPLOY_COST, 0, mapper_code=codes[0], shard_num=num_shards, shuffler_code=codes[1],
                        reducer_code=codes[2])
        except FileNotFoundError:
            print("File not found")

    elif opt == 6:
        if app.run_contract():
            print("Successfully sent tx")
        else:
            print("err")

    elif opt == 7:
        app.register_as_validator()

    elif opt == 8:
        print("State:-----------------\n", app.get_contract_state())

    else:
        print("Invalid opt")

print("--------------END--------------")
