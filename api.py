from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import *
from app import App
import base64

api = FastAPI()
app = App()


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContractModel(BaseModel):
    b64mapper: str
    b64shuffler: str
    b64reducer: str
    shards: int


@api.get("/")
async def read_root(status_code=200):
    blockchain = app.blockCallBack.blockchain
    tx_pool = app.txCallBack.tx_pool
    accounts_data, applied_txs, validators, contract_accounts = app.get_complete_state()

    chain = {}
    for k, v in blockchain.chain.items():
        chain[k] = v.create_dict()

    tx_pool = [tx.__dict__.copy() for tx in tx_pool]
    accounts = [v.__dict__.copy() for _, v in accounts_data.accounts.items()]
    return {"success": True, "chain": chain, "txPool": tx_pool, "accounts": accounts, "validators": validators, "appliedTxs": applied_txs, "contractAccounts": contract_accounts}


@api.post("/mine", status_code=201)
async def send_mine_initiation_command():
    try:
        app.start_mining()
        return {"message": "Mining started", "success": True}
    except Exception as e:
        return {"message": e, "success": False}


@api.post("/transfer", status_code=201)
async def send_currency(to: str, val: int, fee: int):
    try:
        app.send_tx(to, val, fee)
        return {"message": "Currency transfer request sent", "success": True}
    except Exception as e:
        return {"message": e, "success": False}


@api.get("/balance", status_code=200)
async def read_balance():
    data, val = app.get_state()
    print("val", val, "type", type(val))
    return {"balance": data.bal, "vk": data.vk, "is_validator": val}


@api.post("/validate", status_code=201)
async def register_as_validator():
    try:
        app.register_as_validator()
        return {"message": "Validator registration request sent", "success": True}
    except Exception as e:
        return {"message": e, "success": False}


@api.post("/contract", status_code=201)
async def create_contract(data: ContractModel):

    try:
        mapper = base64.b64decode(
            data.b64mapper.encode("ascii")).decode("ascii")
        shuffler = base64.b64decode(
            data.b64shuffler.encode("ascii")).decode("ascii")
        reducer = base64.b64decode(
            data.b64reducer.encode("ascii")).decode("ascii")
        app.send_tx(DEPLOY_ADDR, DEPLOY_COST, 0, mapper_code=mapper,
                    shard_num=data.shards, shuffler_code=shuffler, reducer_code=reducer)
        return {"message": "Contract creation request sent", "success": True}
    except Exception as e:
        print(e)
        return {"message": e, "success": False}


@api.post("/contract/run", status_code=201)
async def run_contract():
    try:
        if app.run_contract():
            return {"message": "Transaction sent", "success": True}
        else:
            return {"message": "Transaction failed", "success": False}
    except Exception as e:
        return {"message": e, "success": False}


@api.get("/contract", status_code=200)
def get_contract_state():
    try:
        return {"contract": app.get_contract_state()}
    except Exception as e:
        return {"message": e, "success": False}
