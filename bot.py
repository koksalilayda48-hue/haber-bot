import feedparser
import telebot
import requests
import json
import os
import time

# -----------------------------
# ENVIRONMENT VARIABLES
# -----------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL")
DB_FILE = os.environ.get("DB_FILE", "paylasilan_haberler.json")

RSS_FEEDS = [
    os.environ.get("RSS_TURKIYE"),
    os.environ.get("RSS_DUNYA"),
    os.environ.get("RSS_SPOR")
]

bot = telebot.TeleBot(BOT_TOKEN)

# Daha önce paylaşılan haberler
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        paylasilan = set(json.load(f))
else:
    paylasilan = set()

def download_image(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            fname = "temp.jpg"
            with open(fname, "wb") as f:
                f.write(r.content)
            return fname
    except:
        return None
    return None

def temiz_haber(haber):
    """Boş veya çerez içerikleri filtrele"""
    if not haber.get("title") or not haber.get("description"):
        return False
    if "?" in haber["title"] or len(haber["description"].strip()) < 50:
        return False
    return True

def check_and_send_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            news_id = entry.id if "id" in entry else entry.link
            if news_id in paylasilan:
                continue
            if not temiz_haber(entry):
                continue

            img_url = None
            if "media_content" in entry:
                img_url = entry.media_content[0]["url"]
            elif "enclosures" in entry and len(entry.enclosures) > 0:
                img_url = entry.enclosures[0]["href"]

            if not img_url:
                continue

            fname = download_image(img_url)
            if fname:
                try:
                    bot.send_photo(CHANNEL, photo=open(fname, "rb"),
                                   caption=f"{entry.title}\n\n{entry.description}")
                    paylasilan.add(news_id)
                    with open(DB_FILE, "w", encoding="utf-8") as f:
                        json.dump(list(paylasilan), f, ensure_ascii=False)
                except Exception as e:
                    print("Hata:", e)

# -----------------------------
# SÜREKLİ ÇALIŞAN LOOP
# -----------------------------
print("Sürekli haber botu aktif...")
while True:
    check_and_send_news()
    time.sleep(300)  # 5 dakikada bir kontrol
