import requests
import time
import os
import re
from datetime import datetime

BOT_TOKEN = "8378331130:AAGWa--sBNlys7SOkUOHdQb5AP3z9JWmtl4"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

BOT_FOLDER = "MyBotFiles"
if not os.path.exists(BOT_FOLDER):
    os.makedirs(BOT_FOLDER)

def sanitize_name(name):
    return re.sub(r'[^a-zA-Z0-9ğüşöçıİĞÜŞÖÇ\s._-]', '', name).strip()

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    resp = requests.get(url, params=params)
    return resp.json()

def get_file(file_id):
    url = f"{BASE_URL}/getFile"
    resp = requests.get(url, params={"file_id": file_id}).json()
    return resp['result']['file_path']

def unique_filename(folder, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base} ({counter}){ext}"
        counter += 1
    return new_filename

def download_file(file_path, local_name, folder):
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    r = requests.get(url)
    save_path = os.path.join(folder, local_name)
    with open(save_path, "wb") as f:
        f.write(r.content)
    print(f"Dosya indirildi: {save_path}")

def append_message(chat_folder, text):
    log_file = os.path.join(chat_folder, "messages.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{text}\n")

def format_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    offset = None
    print("Bot çalışıyor. Mesajlar ayrı klasörlere kaydedilecek...")

    while True:
        updates = get_updates(offset)
        for update in updates["result"]:
            offset = update["update_id"] + 1

            if "message" in update:
                msg = update["message"]
                first_name = msg["from"]["first_name"]
                username = msg["from"].get("username", "")
                display_name = f"@{username} ({first_name})" if username else first_name

                chat_type = msg["chat"]["type"]
                chat_title = msg["chat"].get("title", "")
                chat_id = msg["chat"]["id"]
                message_id = msg["message_id"]
                timestamp = format_timestamp()

                folder_name = sanitize_name(chat_title or username or str(chat_id))
                chat_folder = os.path.join(BOT_FOLDER, folder_name)
                if not os.path.exists(chat_folder):
                    os.makedirs(chat_folder)

                chat_label = chat_title if chat_type != "private" else username or first_name

                # ---- TEXT MESAJ ----
                if "text" in msg:
                    text = msg["text"]
                    log_entry = f"[{timestamp}] [{chat_label}] {display_name} (metin, {message_id}): {text}"
                    append_message(chat_folder, log_entry)
                    print(log_entry)

                # ---- DOCUMENT / PHOTO / VIDEO / VOICE / AUDIO ----
                file_id = None
                file_name = None
                file_type = None

                if "document" in msg:
                    file_type = "dosya"
                    file_name = sanitize_name(msg["document"]["file_name"])
                    file_id = msg["document"]["file_id"]
                elif "photo" in msg:
                    file_type = "fotoğraf"
                    photo = msg["photo"][-1]
                    file_id = photo["file_id"]
                    file_name = f"photo_{message_id}.jpg"
                elif "video" in msg:
                    file_type = "video"
                    file_id = msg["video"]["file_id"]
                    file_name = f"video_{message_id}.mp4"
                elif "voice" in msg:
                    file_type = "ses"
                    file_id = msg["voice"]["file_id"]
                    file_name = f"voice_{message_id}.ogg"
                elif "audio" in msg:
                    file_type = "audio"
                    title = msg["audio"].get("title", f"audio_{message_id}")
                    ext = os.path.splitext(msg["audio"].get("file_name", ".mp3"))[1]
                    file_name = sanitize_name(f"{title}{ext}")
                    file_id = msg["audio"]["file_id"]

                if file_id and file_name:
                    safe_name = unique_filename(chat_folder, file_name)
                    log_entry = f"[{timestamp}] [{chat_label}] {display_name} ({file_type}, {message_id}): Gönderdi: {safe_name}"
                    append_message(chat_folder, log_entry)
                    print(log_entry)
                    file_path = get_file(file_id)
                    download_file(file_path, safe_name, chat_folder)

                # ---- KONUM ----
                if "location" in msg:
                    lat = msg["location"]["latitude"]
                    lon = msg["location"]["longitude"]
                    maps_link = f"https://maps.google.com/?q={lat},{lon}"
                    log_entry = f"[{timestamp}] [{chat_label}] {display_name} (konum, {message_id}): Gönderdi: {maps_link}"
                    append_message(chat_folder, log_entry)
                    print(log_entry)

                # ---- ANKET ----
                if "poll" in msg:
                    question = msg["poll"]["question"]
                    options = ", ".join([o["text"] for o in msg["poll"]["options"]])
                    log_entry = f"[{timestamp}] [{chat_label}] {display_name} (anket, {message_id}): Soru: {question} | Seçenekler: {options}"
                    append_message(chat_folder, log_entry)
                    print(log_entry)

                # ---- STICKER ----
                if "sticker" in msg:
                    emoji = msg["sticker"].get("emoji", "")
                    log_entry = f"[{timestamp}] [{chat_label}] {display_name} (çıkartma, {message_id}): Gönderdi: {emoji}"
                    append_message(chat_folder, log_entry)
                    print(log_entry)

                # ---- CONTACT ----
                if "contact" in msg:
                    phone = msg["contact"]["phone_number"]
                    name = msg["contact"].get("first_name", "") + " " + msg["contact"].get("last_name", "")
                    log_entry = f"[{timestamp}] [{chat_label}] {display_name} (kişi, {message_id}): Gönderdi: {name.strip()} ({phone})"
                    append_message(chat_folder, log_entry)
                    print(log_entry)

        time.sleep(1)

if __name__ == "__main__":
    main()