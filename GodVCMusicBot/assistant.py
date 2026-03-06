from hydrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, SESSION_STRING

assistant = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

call_py = PyTgCalls(assistant)
