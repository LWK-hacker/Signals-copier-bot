import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = 33698486
API_HASH = "61e4a7c1b861b141eede9901dbf6935b"
SESSION_STRING = os.getenv("SESSION_STRING")

SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "@forexg")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "@xaussdelite")
CUSTOM_CONTACT = os.getenv("CUSTOM_FOOTER", "@Mr_tradern")

if not SESSION_STRING:
    print("ERROR: SESSION_STRING environment variable is missing!")
    exit(1)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


def clean_text(raw_text: str) -> str:
    text = raw_text or ""

    # Agar text mein koi link ya contact mojood hai
    has_link_or_contact = bool(
        re.search(
            r"https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@\w+",
            text,
            flags=re.IGNORECASE,
        )
    )

    if has_link_or_contact:
        # Pehle link ya contact ko aapke contact se replace karne ka logic
        # Hum pehle t.me/websites ya @username ko dhund kar pehle wale ko replace kar denge
        replaced = False

        def replace_first(match):
            nonlocal replaced
            if not replaced:
                replaced = True
                return CUSTOM_CONTACT
            return ""  # Baqi extra links remove ho jayengi

        # Links aur usernames ko process karna
        text = re.sub(
            r"https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@\w+",
            replace_first,
            text,
            flags=re.IGNORECASE,
        )

        # Agar koi link replace nahi hua lekin text mein contact lafz tha toh end mein jorr dein
        if not replaced and CUSTOM_CONTACT not in text:
            text += f"\n\nContact: {CUSTOM_CONTACT}"

    return text.strip()


@client.on(events.Album(chats=SOURCE_CHANNEL))
async def album_handler(event):
    try:
        # Album ke andar jo bhi caption/text mojood ho usay nikal kar clean karna
        album_text = ""
        for msg in event.messages:
            if msg.raw_text:
                album_text = msg.raw_text
                break

        text = clean_text(album_text)
        medias = [msg.media for msg in event.messages if msg.media]

        if medias:
            await client.send_file(TARGET_CHANNEL, medias, caption=text if text else None)
        elif text:
            await client.send_message(TARGET_CHANNEL, text)

    except Exception as e:
        print(f"Album Error: {e}")


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        # Agar message kisi album ka hissa hai toh album_handler usay sambhal lega
        if event.grouped_id:
            return

        text = clean_text(event.raw_text or "")

        # Target channel par bhejna (Single photos, videos aur text sab bina kisi skip ke jayenge)
        if event.media:
            await client.send_file(TARGET_CHANNEL, event.media, caption=text)
        elif text:
            await client.send_message(TARGET_CHANNEL, text)

    except Exception as e:
        print(f"Error: {e}")


print("Bot is running with exact copy, album support & single-link replacement logic...")
client.start()
client.run_until_disconnected()
