import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = 33698486
API_HASH = "61e4a7c1b861b141eede9901dbf6935b"
SESSION_STRING = os.getenv("SESSION_STRING")

SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "@forexg")
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
        
        # 1. Strict Link & Promotion Filter:
        # Agar message mein t.me link ya website hai, toh hum check karenge ke yeh valid trading signal hai ya nahi.
        if re.search(r'(?:https?://|www\.|t\.me/|telegram\.me/|join|subscribe|vip channel|screenshots to)', text, flags=re.IGNORECASE):
            # Sirf tab allow karein jab message ke andar proper trading signal ke lafz (TP, SL, Entry) mojood hon
            is_valid_signal = ("TP" in text or "SL" in text or "ENTRY" in text or "BUY" in text or "SELL" in text)
            if not is_valid_signal:
                return  # Agar signal nahi hai aur sirf link/promotion hai (jaise screenshot wala msg), toh poora skip ho jaye ga!

        # 2. Smart Contact Replacement:
        has_contact = bool(re.search(r'(@\w+|\bcontact\b|\badmin\b|\bmanager\b)', text, flags=re.IGNORECASE))
        
        if has_contact:
            # Purane usernames/contacts hata kar apna contact set karein
            text = re.sub(r'@\w+', CUSTOM_CONTACT, text)
            text = re.sub(r'(?:Contact|Admin|Manager)[\s:]*@?\w+', f"Contact: {CUSTOM_CONTACT}", text, flags=re.IGNORECASE)
            
            if CUSTOM_CONTACT not in text and text:
                text += f"\n\nContact: {CUSTOM_CONTACT}"
        
        # Baqi saare fazool links ya t.me links ko saaf/remove karna
        text = re.sub(r'https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+', '', text, flags=re.IGNORECASE)
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

print("Bot is running with strict promotion filtering...")
client.start()
client.run_until_disconnected()
