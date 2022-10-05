# delete telliot_homedir if exists

from typing import Union
import json
import os
import shutil
from pathlib import Path


try:
    from telliot_feeds.utils.decode import decode_query_data
except:
    # Heroku dynos cycle daily, and this produces a config error in
    # telliot_core and in chaind_accounts.  This is a workaround.

    # Delete telliot_homedir & chained accounts file if exists
    telliot_homedir = Path.home() / ("telliot")
    if os.path.exists(telliot_homedir):
        shutil.rmtree(telliot_homedir)
    chained_accounts_file = Path.home() / (".chained_accounts")
    if os.path.exists(chained_accounts_file):
        os.remove(chained_accounts_file)

    from telliot_feeds.utils.decode import decode_query_data

from fastapi import FastAPI
from eth_abi import decode_abi
from eth_utils.conversions import to_bytes
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fastapi import Body
from timestamps_tip_scanner.call import call
from timestamps_tip_scanner.timestamps_scanner import run

from utils import generate_docs_msg


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubmitValueData(BaseModel):
    byte_str: Optional[str]
    sol_type: Optional[str]

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/decode/submit_value_bytes/")
def decode_svb(payload: SubmitValueData = Body(...)):
    try:
        print(payload.byte_str)
        print(payload.sol_type)
        svb = to_bytes(hexstr=payload.byte_str)
        print("svb", svb)
        decoded = decode_abi([payload.sol_type], svb)
        print("decoded", decoded)
        return {"decoded": decoded}
    except Exception as e:
        return {"error": str(e)}


@app.post("/decode/query_data/")
def decode_qd(query_data_str: str):
    try:
        status, query = decode_query_data(query_data_str)
    except Exception as e:
        return {"error": str(e)}
    if not status.ok:
        return {"error": status.error}
    try:
        return {
            "query_type": query.__class__.__name__,
            "query_id": query.query_id.hex(), 
            "query_data": query.query_data.hex(), 
            "query_parameters": query.__dict__.items(),
            "data_spec": generate_docs_msg(query.__class__.__name__),
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/claim-timestamps/{network}/{address}/")
async def start_block_num(network: str,address: str, start_block: int=None):
    # scan for timestamps
    run(network, address, start_block)
    # filter timestamps
    state = await call(network, address)
    if not state:
        return "No timestamps to claim found!"
    last_scanned_block = {"last_scanned_block": state.get_last_scanned_block()}
    return last_scanned_block, state.single_tips, state.feed_tips