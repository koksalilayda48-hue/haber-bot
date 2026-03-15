import telebot
import requests
from bs4 import BeautifulSoup
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

# Güvenilir Türk haber siteleri
siteler = [
    "https://www.hurriyet.com.tr/gundem/",
    "https://www.ntv.com.tr/gundem",
    "https://www.cnnturk.com/gundem",
    "https://www.sabah.com.tr/gundem",
    "https://www.milliyet.com.tr/gundem"
]

def haber_formatla(baslik, metin):
    mesaj = f"""#SONDAKİKA

{baslik}

{metin}
"""
    return mesaj

def haberleri_cek():
    for site in siteler:
        try:
            r = requests.get(site, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Resim ve başlık al
            imgs = soup.find_all("img")
            for img in imgs[:10]:
                src = img.get("src")
                baslik = img.get("alt")
                
                if not src or not baslik:
                    continue
                if "logo" in src:
                    continue
                if baslik in paylasilan_haberler:
                    continue

                # Haber metni: sayfadaki p etiketlerinden al
                paragraphs = soup.find_all("p")
                metin = ""
                for p in paragraphs:
                    metin += p.get_text(strip=True) + "\n"
                if len(metin.strip()) == 0:
                    continue
                
                paylasilan_haberler.add(baslik)
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(list(paylasilan_haberler), f, ensure_ascii=False)
                
                mesaj = haber_formatla(baslik, metin.strip())
                
                bot.send_photo(KANAL, src, caption=mesaj)
                time.sleep(20)
        
        except Exception as e:
            print("Hata:", e)

def haber_dongu():
    while True:
        haberleri_cek()
        time.sleep(300)  # 5 dakikada bir yeni haberleri kontrol

# Flask server (Render için)
app = Flask('')

@app.route('/')
def home():
    return "ULTRA HABER BOT AKTIF"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))

Thread(target=run).start()
Thread(target=haber_dongu).start()

bot.infinity_polling()
