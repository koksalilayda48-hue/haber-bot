import feedparser
import telebot
import time
import json
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")

bot = telebot.TeleBot(BOT_TOKEN)

RSS_SOURCES = [
"https://www.aa.com.tr/tr/rss/default?cat=guncel",
"https://www.trthaber.com/rss/turkiye.rss",
"https://www.trthaber.com/rss/dunya.rss",
"https://www.trthaber.com/rss/ekonomi.rss",
"https://feeds.bbci.co.uk/turkce/rss.xml"
]

KEYWORDS = [
"deprem",
"yangın",
"operasyon",
"açıklama",
"karar",
"ekonomi",
"seçim",
"yasa",
"güvenlik",
"bakan",
"cumhurbaşkanı",
"kriz"
]

DB_FILE = "news.json"

if os.path.exists(DB_FILE):
    with open(DB_FILE,"r") as f:
        sent_news = json.load(f)
else:
    sent_news = []

def save_db():
    with open(DB_FILE,"w") as f:
        json.dump(sent_news,f)

def temizle(text):
    soup = BeautifulSoup(text,"html.parser")
    return soup.get_text().strip()

def get_image(entry):

    if "media_content" in entry:
        return entry.media_content[0]["url"]

    if "links" in entry:
        for link in entry.links:
            if "image" in link.type:
                return link.href

    return None

def onemli_mi(text):

    for k in KEYWORDS:
        if k.lower() in text.lower():
            return True

    return False

def haber_kontrol():

    for rss in RSS_SOURCES:

        feed = feedparser.parse(rss)

        for entry in feed.entries[:6]:

            if entry.link in sent_news:
                continue

            title = temizle(entry.title)
            desc = temizle(entry.summary)

            text = title + " " + desc

            if not onemli_mi(text):
                continue

            if len(desc) < 80:
                continue

            image = get_image(entry)

            message = f"{title}\n\n{desc}"

            try:

                if image:
                    bot.send_photo(CHANNEL,image,caption=message[:1000])
                else:
                    bot.send_message(CHANNEL,message[:4000])

                sent_news.append(entry.link)

                if len(sent_news) > 500:
                    sent_news.pop(0)

                save_db()

                time.sleep(2)

            except Exception as e:
                print(e)

while True:

    try:
        haber_kontrol()
    except Exception as e:
        print(e)

    time.sleep(60)
