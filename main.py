from typing import Union

from fastapi import FastAPI
from telliot_feeds.utils.decode import decode_query_data
# from telliot_feeds.utils.decode import decode_submit_value_bytes

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/decode/query_data/")
def decode_qd(query_data_str: str):
    status, query = decode_query_data(query_data_str)
    if not status.ok:
        return {"error": status.error}
    return {"query": str(query)}

# @app.post("/decode/submit_value_bytes/")
# def decode_svb(submit_value_bytes_str: str, query_type_str: str):
#     query = query_from_str(query_type_str)
#     status, value = decode_submit_value_bytes(submit_value_bytes_str, query_type_str)
#     if not status.ok:
#         return {"error": status.error}
#     return {"value": str(value)}

