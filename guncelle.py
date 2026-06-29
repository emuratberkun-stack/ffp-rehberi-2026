#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFP Otomatik Haber Guncelleyici
Her sabah calisir, 5 kaynaktan haber ceker, index.html'i gunceller
"""

import re
import time
import json
from datetime import datetime, timezone, timedelta

try:
    import requests
    import feedparser
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'requests', 'feedparser', 'beautifulsoup4'])
    import requests
    import feedparser
    from bs4 import BeautifulSoup

# Turkiye saati
TR_NOW = datetime.now(timezone(timedelta(hours=3)))
TR_DATE = TR_NOW.strftime("%d.%m.%Y %H:%M")

AY = {1:"Ocak",2:"Subat",3:"Mart",4:"Nisan",5:"Mayis",6:"Haziran",
      7:"Temmuz",8:"Agustos",9:"Eylul",10:"Ekim",11:"Kasim",12:"Aralik"}

def tarih_tr(entry):
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            t = datetime(*entry.published_parsed[:6])
            return f"{t.day} {AY[t.month]} {t.year}"
    except:
        pass
    return f"{TR_NOW.day} {AY[TR_NOW.month]} {TR_NOW.year}"

def temizle(metin, limit=250):
    if not metin:
        return ""
    soup = BeautifulSoup(metin, "html.parser")
    temiz = soup.get_text(" ", strip=True)
    temiz = re.sub(r'\s+', ' ', temiz).strip()
    if len(temiz) > limit:
        temiz = temiz[:limit-3] + "..."
    # JS string icin guvenli hale getir
    temiz = temiz.replace("\\", "").replace('"', "'").replace("\n", " ")
    return temiz

# Program RSS tanımlari
PROGRAMLAR = [
    {
        "id": "skymiles",
        "anahtar": ["skymiles", "delta skymiles", "delta medallion"],
        "feeds": [
            "https://loyaltylobby.com/tag/skymiles/feed/",
            "https://onemileatatime.com/tag/delta-skymiles/feed/",
        ]
    },
    {
        "id": "aadvantage", 
        "anahtar": ["aadvantage", "american airlines miles", "admirals club"],
        "feeds": [
            "https://loyaltylobby.com/tag/aadvantage/feed/",
            "https://onemileatatime.com/tag/aadvantage/feed/",
        ]
    },
    {
        "id": "mileageplus",
        "anahtar": ["mileageplus", "united miles", "premier 1k"],
        "feeds": [
            "https://loyaltylobby.com/tag/mileageplus/feed/",
            "https://onemileatatime.com/tag/mileageplus/feed/",
        ]
    },
    {
        "id": "skywards",
        "anahtar": ["skywards", "emirates miles", "emirates skywards"],
        "feeds": [
            "https://loyaltylobby.com/tag/emirates-skywards/feed/",
            "https://onemileatatime.com/tag/emirates-skywards/feed/",
        ]
    },
    {
        "id": "privilege",
        "anahtar": ["privilege club", "qatar miles", "qpoints", "avios qatar"],
        "feeds": [
            "https://loyaltylobby.com/tag/privilege-club/feed/",
            "https://onemileatatime.com/tag/qatar-privilege-club/feed/",
        ]
    },
    {
        "id": "flyingblue",
        "anahtar": ["flying blue", "air france miles", "klm miles"],
        "feeds": [
            "https://loyaltylobby.com/tag/flying-blue/feed/",
            "https://onemileatatime.com/tag/flying-blue/feed/",
        ]
    },
    {
        "id": "krisflyer",
        "anahtar": ["krisflyer", "singapore airlines miles", "kris flyer"],
        "feeds": [
            "https://loyaltylobby.com/tag/krisflyer/feed/",
            "https://onemileatatime.com/tag/krisflyer/feed/",
        ]
    },
    {
        "id": "aeroplan",
        "anahtar": ["aeroplan", "air canada miles", "aeroplan points"],
        "feeds": [
            "https://loyaltylobby.com/tag/aeroplan/feed/",
            "https://onemileatatime.com/tag/aeroplan/feed/",
        ]
    },
    {
        "id": "avios",
        "anahtar": ["avios", "british airways miles", "executive club", "ba miles"],
        "feeds": [
            "https://loyaltylobby.com/tag/avios/feed/",
            "https://onemileatatime.com/tag/avios/feed/",
        ]
    },
    {
        "id": "qff",
        "anahtar": ["qantas frequent flyer", "qantas points", "qantas miles"],
        "feeds": [
            "https://loyaltylobby.com/tag/qantas-frequent-flyer/feed/",
            "https://onemileatatime.com/tag/qantas-frequent-flyer/feed/",
        ]
    },
    {
        "id": "milesmore",
        "anahtar": ["miles and more", "miles & more", "lufthansa miles"],
        "feeds": [
            "https://loyaltylobby.com/tag/miles-and-more/feed/",
            "https://onemileatatime.com/tag/miles-more/feed/",
        ]
    },
    {
        "id": "asiamiles",
        "anahtar": ["asia miles", "cathay miles", "marco polo club"],
        "feeds": [
            "https://loyaltylobby.com/tag/asia-miles/feed/",
            "https://onemileatatime.com/tag/asia-miles/feed/",
        ]
    },
    {
        "id": "mileageplan",
        "anahtar": ["mileage plan", "alaska miles", "alaska airlines miles"],
        "feeds": [
            "https://loyaltylobby.com/tag/mileage-plan/feed/",
            "https://onemileatatime.com/tag/alaska-mileage-plan/feed/",
        ]
    },
    {
        "id": "rapidrewards",
        "anahtar": ["rapid rewards", "southwest miles", "southwest points"],
        "feeds": [
            "https://loyaltylobby.com/tag/rapid-rewards/feed/",
            "https://onemileatatime.com/tag/southwest-rapid-rewards/feed/",
        ]
    },
    {
        "id": "lifemiles",
        "anahtar": ["lifemiles", "avianca miles", "avianca lifemiles"],
        "feeds": [
            "https://loyaltylobby.com/tag/lifemiles/feed/",
            "https://onemileatatime.com/tag/lifemiles/feed/",
        ]
    },
    {
        "id": "milessmiles",
        "anahtar": ["miles and smiles", "miles smiles", "turkish airlines miles", "thy mil"],
        "feeds": [
            "https://loyaltylobby.com/tag/miles-smiles/feed/",
            "https://onemileatatime.com/tag/turkish-airlines/feed/",
        ]
    },
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) FFP-Updater/2.0'
}

def feed_cek(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception as e:
        print(f"  Feed hatasi ({url[:50]}): {e}")
        return None

def program_haber_cek(prog):
    haberler = []
    goruldu = set()
    
    for feed_url in prog["feeds"]:
        feed = feed_cek(feed_url)
        if not feed:
            continue
            
        for entry in feed.entries[:10]:
            baslik = getattr(entry, 'title', '')
            ozet = getattr(entry, 'summary', '')
            metin = (baslik + " " + ozet).lower()
            
            # Ilgili mi?
            if not any(k in metin for k in prog["anahtar"]):
                continue
            
            # Tekrar mi?
            anahtar = baslik[:40]
            if anahtar in goruldu:
                continue
            goruldu.add(anahtar)
            
            temiz_metin = temizle(baslik + ". " + ozet)
            if len(temiz_metin) < 30:
                continue
                
            haberler.append({
                "date": tarih_tr(entry),
                "text": temiz_metin,
                "link": getattr(entry, 'link', '')
            })
            
            if len(haberler) >= 4:
                break
        
        time.sleep(1)
        
        if len(haberler) >= 4:
            break
    
    return haberler

def html_guncelle(haberler_dict):
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    degisen = 0
    for pid, haberler in haberler_dict.items():
        if not haberler:
            continue
        
        # news:[...] bloğunu bul ve değiştir
        # id:"pid" ile başlayan program bloğunda
        pattern = r'(id:"' + pid + r'".*?news:\[)(.*?)(\])'
        
        yeni_news = ",".join([
            '{date:"' + h["date"] + '",text:"' + h["text"] + '",link:"' + h.get("link","") + '"}'
            for h in haberler
        ])
        
        def replace_news(m):
            return m.group(1) + yeni_news + m.group(3)
        
        yeni_html, n = re.subn(pattern, replace_news, html, count=1, flags=re.DOTALL)
        if n > 0:
            html = yeni_html
            degisen += 1
    
    # Güncelleme zamanını güncelle
    html = re.sub(
        r'Son guncelleme: [\d\.:]+',
        f'Son guncelleme: {TR_DATE}',
        html
    )
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"HTML guncellendi: {degisen} program, {TR_DATE}")

def main():
    print(f"FFP Guncelleyici baslatildi: {TR_DATE}")
    print(f"16 program taranacak...")
    
    tum_haberler = {}
    
    for i, prog in enumerate(PROGRAMLAR, 1):
        print(f"\n[{i:02d}/16] {prog['id'].upper()}")
        haberler = program_haber_cek(prog)
        tum_haberler[prog["id"]] = haberler
        print(f"  {len(haberler)} haber bulundu")
    
    html_guncelle(tum_haberler)
    print("\nTamamlandi!")

if __name__ == "__main__":
    main()
