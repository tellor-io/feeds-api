from typing import Union
import json

from fastapi import FastAPI
from telliot_feeds.utils.decode import decode_query_data
from eth_abi import decode_abi
from eth_utils.conversions import to_bytes
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fastapi import Body
from timestamps_tip_scanner.call import call
from timestamps_tip_scanner.timestamps_scanner import run


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