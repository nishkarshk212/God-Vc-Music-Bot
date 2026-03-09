
import asyncio
from hydrogram import Client

async def main():
    print("--------------------------------------------------")
    print("Hydrogram Session String Generator")
    print("--------------------------------------------------")
    
    # Prompt for API credentials
    try:
        api_id = int(input("Enter your API ID: "))
        api_hash = input("Enter your API HASH: ")
    except ValueError:
        print("Error: API ID must be an integer.")
        return

    # Initialize client
    # Using :memory: storage to avoid creating a .session file
    async with Client(":memory:", api_id=api_id, api_hash=api_hash) as app:
        print("\n--------------------------------------------------")
        print("Client created. You will now be prompted to log in.")
        print("Enter your phone number, the code Telegram sends you, and your 2FA password if enabled.")
        print("--------------------------------------------------\n")
        
        # Export session string
        session_string = await app.export_session_string()
        
        print("--------------------------------------------------")
        print("✅ Success! Here is your session string:")
        print("--------------------------------------------------\n")
        print(session_string)
        print("\n--------------------------------------------------")
        print("IMPORTANT: Copy this string and store it securely.")
        print("Do not share it with anyone.")
        print("--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
