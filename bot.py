import telebot
import feedparser
from flask import Flask
from threading import Thread
import time
import json
import os

# Telegram bilgileri
TOKEN = "8062154104:AAHKYLzFRbZ8EiRhm7zPJsYqQitHmcUEqWA"
KANAL = "@anlikhaberi"
DB_FILE = "paylasilan_haberler.json"

bot = telebot.TeleBot(TOKEN)

# Daha önce paylaşılan haberler
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        paylasilan_haberler = set(json.load(f))
else:
    paylasilan_haberler = set()

# Güvenilir RSS kaynakları
RSS_FEEDS = [
    "https://www.hurriyet.com.tr/rss/gundem",
    "https://www.ntv.com.tr/son-dakika.rss",
    "https://www.cnnturk.com/feed/rss/gundem",
    "https://www.sabah.com.tr/rss/gundem.xml",
    "https://www.milliyet.com.tr/rss/gundem/rss.xml"
]

def haber_formatla(baslik, metin):
    mesaj = f"""#SONDAKİKA

{baslik}

{metin}
"""
    return mesaj

def haberleri_cek():
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:  # en yeni 5 haber
                baslik = entry.title
                metin = entry.summary
                img = None

                # Görsel alma (RSS içinde media:content veya enclosure)
                if 'media_content' in entry:
                    img = entry.media_content[0]['url']
                elif 'enclosures' in entry and len(entry.enclosures) > 0:
                    img = entry.enclosures[0]['url']

                if not img:
                    continue  # görsel yoksa atlama

                if baslik in paylasilan_haberler:
                    continue

                paylasilan_haberler.add(baslik)
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(list(paylasilan_haberler), f, ensure_ascii=False)

                mesaj = haber_formatla(baslik, metin)
                bot.send_photo(KANAL, img, caption=mesaj)
                time.sleep(20)

        except Exception as e:
            print("Hata:", e)

def haber_dongu():
    while True:
        haberleri_cek()
        time.sleep(300)  # 5 dakikada bir güncel haberleri kontrol

# Flask server (Render için)
app = Flask('')

@app.route('/')
def home():
    return "ULTRA HABER BOT AKTİF"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))

Thread(target=run).start()
Thread(target=haber_dongu).start()

bot.infinity_polling()
