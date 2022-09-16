from typing import Union
import json

from fastapi import FastAPI
from telliot_feeds.utils.decode import decode_query_data
from eth_abi import decode_abi
from eth_utils.conversions import to_bytes

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


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


@app.post("/decode/submit_value_bytes/")
def decode_svb(submit_value_bytes_str: str, abi_type: str):
    try:
        svb = to_bytes(hexstr=submit_value_bytes_str)
        print("svb", svb)
        decoded = decode_abi([abi_type], svb)
        print("decoded", decoded)
    except Exception as e:
        return {"error": str(e)}

    try:
        return {"decoded": decoded}
    except Exception as e:
        return {"error": str(e)}
