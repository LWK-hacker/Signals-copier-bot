import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = 33698486
API_HASH = "61e4a7c1b861b141eede9901dbf6935b"
SESSION_STRING = os.getenv("SESSION_STRING")

SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "@XAUUSD_GOLD_TRADING_FOREX")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "@fxxauusdelite")
CUSTOM_CONTACT = os.getenv("CUSTOM_FOOTER", "@Mr_tradern")

if not SESSION_STRING:
    print("ERROR: SESSION_STRING environment variable is missing!")
    exit(1)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        text = event.raw_text or ""
        
        # Check karein ke message mein koi link ya contact mojood hai ya nahi
        has_link_or_contact = bool(re.search(r't\.me/|telegram\.me/|@\w+|\bcontact\b', text, flags=re.IGNORECASE))
        
        if has_link_or_contact:
            # Sabhi external t.me links, websites aur purane usernames ko remove kar do
            text = re.sub(r'https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+', '', text, flags=re.IGNORECASE)
            text = re.sub(r'@\w+', '', text)
            
            # Extra khali lines saaf karna
            text = re.sub(r'\n\s*\n', '\n\n', text).strip()
            
            # Sirf ek jagah end mein aapka contact add kar dena
            if CUSTOM_CONTACT not in text:
                text += f"\n\nContact: {CUSTOM_CONTACT}"
        
        text = text.strip()
        
        if not text and not event.media:
            return

        # Target channel par bhejna
        if event.media:
            await client.send_file(TARGET_CHANNEL, event.media, caption=text)
        elif text:
            await client.send_message(TARGET_CHANNEL, text)
            
    except Exception as e:
        print(f"Error: {e}")

print("Bot is running with clean single-contact replacement logic...")
client.start()
client.run_until_disconnected()
