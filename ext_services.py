import requests
import xml.etree.ElementTree as ET
import html

def get_google_news():
    """
    Fetches headline news from Google News RSS (Indonesia) with snippets.
    Improved sanitization for Pygame rendering safety.
    """
    import random
    import re
    import config
    
    url = "https://news.google.com/rss?hl=id&gl=ID&ceid=ID:id"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        news_items = []
        
        # Regex to remove non-printable/non-standard characters that might crash Pygame
        # Keeps basic Indonesian alphabet, numbers, and common punctuation
        # Replaces everything else with a space
        def clean_text(text):
            if not text: return ""
            text = html.unescape(text)
            # Remove HTML tags
            text = re.sub('<[^<]+?>', '', text)
            # Remove characters outside common range (basic emojis, rare symbols)
            # Standard ASCII + typical Latin-1 / Indonesian chars
            text = "".join(c for c in text if ord(c) < 65535 and not (0 <= ord(c) <= 31 and ord(c) not in [9, 10, 13]))
            return text.strip()

        for item in root.findall('./channel/item'):
            title = item.find('title').text
            desc_html = item.find('description').text
            
            clean_title = clean_text(title)
            if " - " in clean_title:
                clean_title = clean_title.rsplit(" - ", 1)[0]
            
            # Clean up the description snippet
            clean_desc = clean_text(desc_html)
            # Often the description starts with the title, let's remove it
            display_desc = clean_desc.replace(clean_title, "").strip()
            # If after cleaning description is empty, use a fallback
            if not display_desc:
                display_desc = "Lihat berita selengkapnya di Google News."

            news_items.append({
                "title": clean_title,
                "desc": display_desc[:250] + "..." if len(display_desc) > 250 else display_desc
            })
            
        return news_items # Return the whole pool, randomization happens in main.py
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def get_sholat_times(lat=None, lon=None, city="Jakarta"):
    """
    Fetches Sholat times using Aladhan API.
    Prioritizes Latitude and Longitude if provided.
    """
    if lat and lon:
        url = f"http://api.aladhan.com/v1/timings?latitude={lat}&longitude={lon}&method=20"
    else:
        address = f"{city}, Indonesia"
        url = f"http://api.aladhan.com/v1/timingsByAddress?address={address}&method=20"
        
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200 and city != "Jakarta":
            return get_sholat_times(city="Jakarta")
            
        response.raise_for_status()
        data = response.json()
        
        timings = data['data']['timings']
        hijri_data = data['data']['date']['hijri']
        
        hijri_formatted = f"{hijri_data['day']} {hijri_data['month']['en']} {hijri_data['year']}H"
        
        important_times = {
            "Imsak": timings['Imsak'],
            "Subuh": timings['Fajr'],
            "Dzuhur": timings['Dhuhr'],
            "Ashar": timings['Asr'],
            "Maghrib": timings['Maghrib'],
            "Isya": timings['Isha'],
            "hijri_date": hijri_formatted
        }
        return important_times
    except Exception as e:
        print(f"Error fetching sholat times: {e}")
        if city != "Jakarta":
            return get_sholat_times(city="Jakarta")
        return None

def get_javanese_date():
    """
    Fetches Javanese date info from tanggalanjawa.com.
    """
    import datetime
    now = datetime.datetime.now()
    url = f"https://tanggalanjawa.com/api/calendar?year={now.year}&month={now.month}&day={now.day}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f"{data['weekday']} {data['pasaran']}"
    except Exception as e:
        print(f"Error fetching Javanese date: {e}")
        return None

def get_bmkg_warning(province="Jawa Tengah", city=None):
    """
    Fetches latest weather warning from BMKG RSS feed.
    """
    url = "https://cuaca.bmkg.go.id/data/public/cap/feed/id/rss.xml"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Normalize search province (remove prefixes like DKI, DAERAH ISTIMEWA)
        search_term = province.upper()
        for prefix in ["DKI ", "DAERAH ISTIMEWA ", "PROVINSI "]:
            if search_term.startswith(prefix):
                search_term = search_term.replace(prefix, "").strip()
        
        root = ET.fromstring(response.content)
        for item in root.findall('.//item'):
            title = item.find('title').text
            description = item.find('description').text
            
            # Match normalized search term
            if search_term.lower() in title.lower() or search_term.lower() in description.lower():
                return {
                    "headline": html.unescape(title),
                    "desc": html.unescape(description)
                }
        return None
    except Exception as e:
        print(f"Error fetching BMKG warning: {e}")
        return None

def get_bmkg_forecast(location_id):
    """
    Fetches 3-hourly forecast from BMKG for a specific village ID (adm4).
    Location ID format example: '3329122001' -> converts to '33.29.12.2001'
    """
    if not location_id or len(str(location_id)) < 10:
        return None
        
    try:
        # Format ID: 1234567890 -> 12.34.56.7890
        s = str(location_id)
        if "." not in s:
            adm4 = f"{s[:2]}.{s[2:4]}.{s[4:6]}.{s[6:]}"
        else:
            adm4 = s
            
        url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        # Structure is data['data'][0]['cuaca'][0] -> list of intervals
        # But structure might be nested lists. Based on curl: "cuaca": [[{...}, {...}]]
        if 'data' in data and len(data['data']) > 0:
             cuaca_list = data['data'][0]['cuaca']
             # Flatten if it's list of lists
             forecasts = []
             for item in cuaca_list:
                 if isinstance(item, list):
                     forecasts.extend(item)
                 else:
                     forecasts.append(item)
             return forecasts
        return None
    except Exception as e:
        print(f"BMKG Forecast Error: {e}")
        return None

def get_finance_data():
    """
    Fetches Crypto (BTC, ETH), USD Rate, and Gold Price (XAU).
    Source: CoinGecko (Crypto) & Frankfurter (Forex).
    Returns dict: {'usd': 15000, 'btc': 1000000000, 'eth': 50000000, 'gold': 1200000}
    """
    results = {}
    
    # 1. Get USD -> IDR
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=USD&to=IDR", timeout=10)
        data = r.json()
        usd_rate = data['rates']['IDR']
        # USD: Change will be calculated locally or set to 0
        results['usd'] = {'val': int(usd_rate), 'change': 0}
    except:
        results['usd'] = {'val': 16000, 'change': 0} # Fallback
        
    # 2. Get Crypto (BTC, ETH) & Gold (PAX Gold)
    try:
        # CoinGecko: Add include_24hr_change=true
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,pax-gold&vs_currencies=idr&include_24hr_change=true"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        results['btc'] = {
            'val': int(data['bitcoin']['idr']),
            'change': data['bitcoin'].get('idr_24h_change', 0)
        }
        results['eth'] = {
            'val': int(data['ethereum']['idr']),
            'change': data['ethereum'].get('idr_24h_change', 0)
        }
        
        # Gold
        paxg_idr = data['pax-gold']['idr']
        gold_gram = paxg_idr / 31.1035
        # Gold Change is same as PAXG Change
        results['gold'] = {
            'val': int(gold_gram),
            'change': data['pax-gold'].get('idr_24h_change', 0)
        }
        
    except Exception as e:
        print(f"Finance API Error: {e}")
        # Fallbacks (preserving structure)
        results['btc'] = results.get('btc', {'val': 0, 'change': 0})
        results['eth'] = results.get('eth', {'val': 0, 'change': 0})
        results['gold'] = results.get('gold', {'val': 0, 'change': 0})
        
    return results

def get_system_info():
    """
    Returns system stats: CPU Temp, RAM Usage, Disk Usage, Uptime, IP.
    Uses shell commands to avoid extra dependencies.
    """
    import subprocess
    import socket
    
    info = {'temp': 'N/A', 'ram_used': 0, 'ram_total': 0, 'disk_percent': 0, 'ip': '127.0.0.1'}
    
    try:
        # CPU Temp
        out = subprocess.check_output("vcgencmd measure_temp", shell=True).decode()
        info['temp'] = out.replace("temp=", "").replace("'", " ").strip() # 45.0 C
    except: pass
    
    
    try:
        # RAM (free -m)
        out = subprocess.check_output("free -m", shell=True).decode().splitlines()
        # Row 1: Mem: total used free ...
        mem = [x for x in out[1].split() if x] # Handle multiple spaces
        info['ram_total'] = int(mem[1])
        info['ram_used'] = int(mem[2])
    except: pass
    
    try:
        # Disk (df -h /)
        out = subprocess.check_output("df -h /", shell=True).decode().splitlines()
        # Row 1: /dev/root size used avail use% ...
        disk = [x for x in out[1].split() if x]
        info['disk_percent'] = disk[4] # Usually 5th column
    except: pass
    
    try:
        # IP Address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['ip'] = s.getsockname()[0]
        s.close()
    except: pass
    
    try:
        # WiFi SSID
        out = subprocess.check_output("iwgetid -r", shell=True).decode().strip()
        info['wifi_ssid'] = out if out else 'N/A'
    except:
        info['wifi_ssid'] = 'N/A'
    
    try:
        # WiFi Signal Strength
        out = subprocess.check_output("iwconfig wlan0 | grep 'Signal level'", shell=True).decode()
        # Extract signal level (e.g., "Signal level=-45 dBm")
        if 'Signal level=' in out:
            signal = out.split('Signal level=')[1].split()[0]
            info['wifi_signal'] = signal
        else:
            info['wifi_signal'] = 'N/A'
    except:
        info['wifi_signal'] = 'N/A'
    
    return info

# Global cache for quotes
QUOTES_CACHE = []

def get_random_quote():
    """
    Fetch random quote from local JSON file.
    Source: /home/pi/weather/quotes.json
    """
    global QUOTES_CACHE
    import json
    import random
    
    # Load if empty
    if not QUOTES_CACHE:
        try:
            with open('/home/pi/weather/quotes.json', 'r', encoding='utf-8') as f:
                QUOTES_CACHE = json.load(f)
            print(f"Loaded {len(QUOTES_CACHE)} quotes from local file.")
        except Exception as e:
            print(f"Error loading quotes.json: {e}")
            
    # Return random item
    if QUOTES_CACHE:
        item = random.choice(QUOTES_CACHE)
        return {
            'text': item.get('quote', 'No Quote'), 
            'author': item.get('author', 'Unknown')
        }
        
    # Fallback if file load failed completely
    return {
        'text': "Urip iku urup.", 
        'author': "Pepatah Jawa"
    }
