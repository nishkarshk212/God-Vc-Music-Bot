from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
import os
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=env_path)

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

def main():
    if not API_ID or not API_HASH:
        raise RuntimeError("Missing API_ID/API_HASH in .env")
    app = Client("assistant", api_id=API_ID, api_hash=API_HASH)
    app.connect()
    phone = input("Phone number (with country code): ").strip()
    sent = app.send_code(phone)
    code = input("Login code: ").strip()
    try:
        app.sign_in(
            phone_number=phone,
            phone_code=code,
            phone_code_hash=sent.phone_code_hash,
        )
    except SessionPasswordNeeded:
        pw = input("Two-step verification password: ").strip()
        app.check_password(pw)
    print(app.export_session_string())
    app.disconnect()

if __name__ == "__main__":
    main()
