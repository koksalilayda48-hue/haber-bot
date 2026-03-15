import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time

TOKEN = "8062154104:AAHKYLzFRbZ8EiRhm7zPJsYqQitHmcUEqWA"
KANAL = "@anlikhaberi"

bot = telebot.TeleBot(TOKEN)

gonderilen = set()

siteler = [
"https://www.hurriyet.com.tr",
"https://www.sabah.com.tr",
"https://www.ntv.com.tr",
"https://www.cnnturk.com",
"https://www.milliyet.com.tr"
]

def haber_cek():

    for site in siteler:

        try:

            r = requests.get(site,timeout=10)

            soup = BeautifulSoup(r.text,"html.parser")

            imgs = soup.find_all("img")

            for img in imgs[:10]:

                src = img.get("src")
                alt = img.get("alt")

                if not src or not alt:
                    continue

                if src in gonderilen:
                    continue

                if "logo" in src:
                    continue

                gonderilen.add(src)

                mesaj = f"🚨 SON DAKİKA\n\n{alt}"

                bot.send_photo(KANAL,src,caption=mesaj)

                time.sleep(20)

        except Exception as e:

            print("Hata:",e)

def haber_dongu():

    while True:

        haber_cek()

        time.sleep(300)

app = Flask('')

@app.route('/')
def home():
    return "HABER BOT AKTIF"

def run():
    app.run(host='0.0.0.0',port=3000)

Thread(target=run).start()
Thread(target=haber_dongu).start()

bot.infinity_polling()
