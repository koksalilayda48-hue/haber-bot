from telethon import TelegramClient, events
import telebot
import os

# Telegram API bilgileri (senin verdiğin)
API_ID = 33397779
API_HASH = "b253283cd2c3df8d7187c85850b918ae"

# Bot token
BOT_TOKEN = "8062154104:AAHKYLzFRbZ8EiRhm7zPJsYqQitHmcUEqWA"

# Kaynak gizli kanal (Global News TR)
KAYNAK_KANAL = "globalnewsturkiye"

# Haberlerin gönderileceği kanal
HEDEF_KANAL = "@anlikhaberi"

bot = telebot.TeleBot(BOT_TOKEN)

# Daha önce paylaşılmış haberlerin ID’leri
DB_FILE = "paylasilan_haberler.json"
import json
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        paylasilan = set(json.load(f))
else:
    paylasilan = set()

# Telegram client (kullanıcı hesabı)
client = TelegramClient("haber_session", API_ID, API_HASH)

@client.on(events.NewMessage(chats=KAYNAK_KANAL))
async def handler(event):
    mesaj = event.message

    # Daha önce paylaşılmış mı kontrol
    if mesaj.id in paylasilan:
        return

    paylasilan.add(mesaj.id)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(list(paylasilan), f, ensure_ascii=False)

    text = mesaj.text or ""

    # Fotoğraf varsa gönder
    if mesaj.photo:
        file = await mesaj.download_media()
        bot.send_photo(
            HEDEF_KANAL,
            photo=open(file, "rb"),
            caption=text
        )
    # Video varsa gönder
    elif mesaj.video:
        file = await mesaj.download_media()
        bot.send_video(
            HEDEF_KANAL,
            video=open(file, "rb"),
            caption=text
        )
    else:
        # Görsel veya video yoksa atlama
        return

client.start()
print("ULTRA HABER BOT AKTİF")
client.run_until_disconnected()
