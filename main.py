import os
import sys

# MUST SET ENVIRONMENT BEFORE ANY PYGAME IMPORT
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_VIDEODRIVER"] = "fbcon"
os.environ["SDL_NOMOUSE"] = "1"

import time
import pygame
import requests
from io import BytesIO
import config
from weather_service import get_weather
import date_utils
import ext_services
import datetime
import random
import textwrap
import importlib

# --- GLOBAL HANDLES ---
screen = None # This will be the Virtual Canvas
FONT_TIME = None
FONT_TEMP = None
FONT_DATE = None
FONT_SUB = None
FONT_TINY = None
FONT_MED_BOLD = None
FONT_NEWS = None
FONT_HEADER = None

COLOR_BG = (5, 6, 12)
COLOR_TEXT_MAIN = (255, 255, 255)
COLOR_TEXT_DIM = (120, 125, 140)
COLOR_ACCENT = (0, 255, 230)
COLOR_ACCENT_2 = (255, 200, 60)
COLOR_CITY = (100, 255, 180)
COLOR_DANGER = (248, 81, 73)

def safe_str(text):
    """Remove characters that crash Pygame 1.9.6"""
    if not isinstance(text, str):
        text = str(text)
    return "".join(c for c in text if ord(c) <= 0xFFFF)

class SafeFont:
    """Wrapper that auto-sanitizes text before rendering"""
    def __init__(self, font):
        self.font = font
    
    def render(self, text, antialias, color, background=None):
        try:
            clean = safe_str(text)
            if background:
                return self.font.render(clean, antialias, color, background)
            return self.font.render(clean, antialias, color)
        except Exception as e:
            # Fallback if render fails (e.g. wide char issue despite sanitize)
            print(f"Font Render Error: {e} | Text: {text.encode('utf-8', 'ignore')}")
            return self.font.render("?", antialias, color)
    
    def size(self, text):
        return self.font.size(safe_str(text))
    
    def get_height(self):
        return self.font.get_height()
    
    def get_rect(self):
        return self.font.get_rect()

def init_fonts():
    global FONT_TIME, FONT_TEMP, FONT_DATE, FONT_SUB, FONT_TINY, FONT_MED_BOLD, FONT_NEWS, FONT_HEADER
    font_names = ["dejavusans", "freesans", "liberationsans", "arial"]
    
    def try_load(size, bold=False):
        for name in font_names:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f: return SafeFont(f)
            except: continue
        return SafeFont(pygame.font.Font(None, size))

    FONT_TIME = try_load(145, bold=True) 
    FONT_TEMP = try_load(95, bold=True)  
    FONT_DATE = try_load(32, bold=True)  
    FONT_SUB = try_load(26, bold=True)  
    FONT_TINY = try_load(22, bold=True)             
    FONT_MED_BOLD = try_load(52, bold=True) 
    FONT_NEWS = try_load(32, bold=False)
    FONT_HEADER = try_load(24, bold=True)

def get_icon(icon_code):
    url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return pygame.image.load(BytesIO(r.content))
    except:
        return None

def draw_weather_slide(weather, date_info, sholat_data, java_date=None):
    screen.fill(COLOR_BG)
    Y_OFF = 25 # ADJUSTED FOR ROTATION MARGIN
    CENTER_RIGHT = 380 
    LEFT_MARGIN = 20    
    
    if weather:
        # City name at top right
        city = safe_str(config.LOCATION_NAME or "Indonesia").split(',')[0].upper()
        text_city = FONT_DATE.render(city, True, COLOR_CITY)
        rect_city = text_city.get_rect()
        rect_city.center = (CENTER_RIGHT, Y_OFF + 20)
        screen.blit(text_city, rect_city)
        
        # Weather icon
        if 'icon_surface' not in weather:
             raw_icon = get_icon(weather['icon_code'])
             if raw_icon:
                 weather['icon_surface'] = pygame.transform.scale(raw_icon, (120, 120))
             else:
                 weather['icon_surface'] = None
        
        if weather['icon_surface']:
            rect_icon = weather['icon_surface'].get_rect()
            rect_icon.center = (CENTER_RIGHT, Y_OFF + 90)
            screen.blit(weather['icon_surface'], rect_icon)
            
        # Temperature (Restore Degree Symbol)
        temp_str = f"{weather['temp']:.0f}\u00B0C" 
        text_temp = FONT_TEMP.render(temp_str, True, COLOR_TEXT_MAIN)
        rect_temp = text_temp.get_rect()
        rect_temp.center = (CENTER_RIGHT, Y_OFF + 180)
        screen.blit(text_temp, rect_temp)
        
        # Description
        # Description - Dynamic Size & Wrap
        desc = safe_str(weather['description']).upper()
        
        # Determine max width allowed (Area kanan layar)
        MAX_W = 180 
        
        # Try normal font
        if FONT_SUB.size(desc)[0] <= MAX_W:
             text_desc = FONT_SUB.render(desc, True, COLOR_ACCENT)
             rect_desc = text_desc.get_rect(center=(CENTER_RIGHT, Y_OFF + 240))
             screen.blit(text_desc, rect_desc)
        else:
             # Try split lines or tiny font
             import textwrap
             lines = textwrap.wrap(desc, width=20) # Approx char width
             y_desc = Y_OFF + 230
             for line in lines[:2]: # Max 2 baris
                 # Use Tiny Font if split
                 t_rend = FONT_TINY.render(line, True, COLOR_ACCENT)
                 t_rect = t_rend.get_rect(center=(CENTER_RIGHT, y_desc))
                 screen.blit(t_rend, t_rect)
                 y_desc += 22

    # Time (big on left)
    text_time = FONT_TIME.render(date_info['time'], True, COLOR_TEXT_MAIN)
    screen.blit(text_time, (LEFT_MARGIN - 5, Y_OFF + 25))
    
    # Gregorian date
    text_date = FONT_DATE.render(date_info['date_gregorian'], True, COLOR_ACCENT)
    screen.blit(text_date, (LEFT_MARGIN, Y_OFF + 160))
    
    # Javanese date (big and prominent)
    java_str = java_date if java_date else date_info['date_javanese']
    text_java = FONT_MED_BOLD.render(java_str, True, COLOR_TEXT_MAIN)
    screen.blit(text_java, (LEFT_MARGIN, Y_OFF + 200))
    
    # Hijri date
    hijri_str = sholat_data.get('hijri_date', date_info['date_hijri']) if sholat_data else date_info['date_hijri']
    text_hijri = FONT_SUB.render(hijri_str, True, COLOR_ACCENT_2)
    screen.blit(text_hijri, (LEFT_MARGIN, Y_OFF + 255))

def draw_news_slide(news_list, date_info, page=0):
    screen.fill(COLOR_BG)
    Y_OFF = 25
    header_lbl = FONT_DATE.render("BERITA INDONESIA", True, COLOR_ACCENT)
    screen.blit(header_lbl, (20, Y_OFF))
    header_time = FONT_DATE.render(date_info['time'], True, COLOR_ACCENT_2)
    screen.blit(header_time, (380, Y_OFF))
    pygame.draw.line(screen, (40, 45, 60), (20, Y_OFF + 40), (460, Y_OFF + 40), 2)
    
    if not news_list:
        text = FONT_NEWS.render("Mengambil berita...", True, COLOR_TEXT_DIM)
        screen.blit(text, (20, 100))
        return

    news = news_list[page]
    
    y = 80
    wrapped_title = textwrap.wrap(news['title'], width=36)
    for line in wrapped_title[:3]:
        text = FONT_SUB.render(line, True, COLOR_ACCENT_2)
        screen.blit(text, (20, y))
        y += 32
        
    y += 10
    pygame.draw.line(screen, (50, 60, 80), (20, y), (80, y), 2)
    y += 15
    
    wrapped_desc = textwrap.wrap(news['desc'], width=48)
    for line in wrapped_desc[:5]:
        text = FONT_TINY.render(line, True, (200, 210, 230))
        screen.blit(text, (20, y))
        y += 26

    page_lbl = FONT_TINY.render(f"HALAMAN {page+1}/{len(news_list)}", True, (60, 65, 80))
    screen.blit(page_lbl, (350, 290))

def map_bmkg_to_owm(code):
    """Maps BMKG weather code to OpenWeatherMap icon code"""
    mapping = {
        0: "01d", 1: "02d", 2: "02d", 3: "03d", 4: "04d", 
        5: "50d", 10: "50d", 45: "50d", 
        60: "10d", 61: "09d", 63: "09d", 
        80: "09d", 95: "11d", 97: "11d"
    }
    return mapping.get(int(code), "03d") # Default to cloudy

def draw_bmkg_forecast_slide(forecasts, date_info):
    screen.fill(COLOR_BG)
    Y_OFF = 25
    header_lbl = FONT_DATE.render("PRAKIRAAN CUACA", True, COLOR_ACCENT)
    screen.blit(header_lbl, (20, Y_OFF))
    
    header_time = FONT_DATE.render(date_info['time'], True, COLOR_ACCENT_2)
    screen.blit(header_time, (380, Y_OFF))
    pygame.draw.line(screen, (40, 45, 60), (20, Y_OFF + 40), (460, Y_OFF + 40), 2)
    
    if not forecasts:
        text = FONT_NEWS.render("Memuat data BMKG...", True, COLOR_TEXT_DIM)
        screen.blit(text, (20, 100))
        return

    display_items = []
    count = 0 
    for fc in forecasts:
        if count >= 3: break
        dt_str = fc.get('local_datetime', '')
        if not dt_str: continue
        display_items.append(fc)
        count += 1
        
    if not display_items: return

    col_width = 160
    y_start = 100 # Adjusted for spacing
    
    for i, fc in enumerate(display_items):
        center_x = (i * col_width) + (col_width // 2)
        
        try:
            dt_str = fc.get('local_datetime', '')
            dt_obj = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            time_str = dt_obj.strftime("%H:%M")
            date_str = dt_obj.strftime("%d/%m")
            
            t_render = FONT_DATE.render(time_str, True, COLOR_TEXT_MAIN)
            d_render = FONT_TINY.render(date_str, True, COLOR_TEXT_DIM)
            t_rect = t_render.get_rect(center=(center_x, y_start))
            d_rect = d_render.get_rect(center=(center_x, y_start + 30))
            screen.blit(t_render, t_rect)
            screen.blit(d_render, d_rect)
            
            weather_code = fc.get('weather', 3)
            owm_code = map_bmkg_to_owm(weather_code)
            icon = get_icon(owm_code)
            if icon:
                icon = pygame.transform.scale(icon, (80, 80))
                rect = icon.get_rect()
                rect.center = (center_x, y_start + 90)
                screen.blit(icon, rect)
            
            temp = fc.get('t', 0)
            # Restore Degree Symbol
            temp_render = FONT_MED_BOLD.render(f"{temp}\u00B0C", True, COLOR_ACCENT_2)
            temp_rect = temp_render.get_rect(center=(center_x, y_start + 150))
            screen.blit(temp_render, temp_rect)
            
            desc = safe_str(fc.get('weather_desc', ''))
            if len(desc) > 15: desc = desc[:13] + ".."
            desc_render = FONT_TINY.render(desc, True, COLOR_TEXT_MAIN)
            desc_rect = desc_render.get_rect(center=(center_x, y_start + 190))
            screen.blit(desc_render, desc_rect)

        except Exception as e:
            continue

def draw_bmkg_slide(warning, date_info):
    screen.fill((20, 5, 5))
    Y_OFF = 25
    header_lbl = FONT_DATE.render("PERINGATAN DINI BMKG", True, COLOR_DANGER)
    screen.blit(header_lbl, (20, Y_OFF))
    header_time = FONT_DATE.render(date_info['time'], True, COLOR_TEXT_MAIN)
    screen.blit(header_time, (380, Y_OFF))
    pygame.draw.line(screen, COLOR_DANGER, (20, Y_OFF + 40), (460, Y_OFF + 40), 2)
    
    if not warning: return

    y = 80
    wrapped_head = textwrap.wrap(warning['headline'].upper(), width=32)
    for line in wrapped_head[:3]:
        text = FONT_SUB.render(line, True, COLOR_DANGER)
        screen.blit(text, (20, y))
        y += 30
        
    y += 15
    wrapped_desc = textwrap.wrap(warning['desc'], width=48)
    for line in wrapped_desc[:6]:
        text = FONT_TINY.render(line, True, COLOR_TEXT_MAIN)
        screen.blit(text, (20, y))
        y += 25

def draw_sholat_slide(sholat_data, date_info, city):
    screen.fill(COLOR_BG)
    Y_OFF = 25
    loc_lbl = safe_str(city).split(',')[0].upper()
    header_lbl = FONT_DATE.render(f"SHOLAT - {loc_lbl}", True, COLOR_ACCENT_2)
    screen.blit(header_lbl, (20, Y_OFF))
    header_time = FONT_DATE.render(date_info['time'], True, COLOR_ACCENT)
    screen.blit(header_time, (380, Y_OFF))
    pygame.draw.line(screen, (40, 45, 60), (20, Y_OFF + 40), (460, Y_OFF + 40), 2)
    
    if not sholat_data:
        text = FONT_NEWS.render("Mengambil jadwal...", True, COLOR_TEXT_DIM)
        screen.blit(text, (20, 100))
        return

    # NEW COMPACT GRID LAYOUT
    keys = ["Imsak", "Subuh", "Dzuhur", "Ashar", "Maghrib", "Isya"]
    
    start_y = 90
    row_h = 70
    col_w = 210
    margin_x = 35
    
    for i, key in enumerate(keys):
        row = i // 2
        col = i % 2
        
        x = margin_x + (col * col_w)
        y = start_y + (row * row_h)
        
        # Background Rect
        pygame.draw.rect(screen, (20, 30, 40), (x, y, 200, 60))
        
        # Label Title
        lbl = FONT_TINY.render(key.upper(), True, COLOR_ACCENT)
        screen.blit(lbl, (x + 15, y + 8))
        
        # Time Value (Align Right)
        val = FONT_MED_BOLD.render(sholat_data[key], True, COLOR_TEXT_MAIN)
        val_rect = val.get_rect()
        val_rect.bottomright = (x + 185, y + 55)
        screen.blit(val, val_rect)

def draw_finance_slide(data, date_info):
    screen.fill(COLOR_BG)
    Y_OFF = 25
    header_lbl = FONT_DATE.render("PASAR KEUANGAN", True, COLOR_ACCENT)
    screen.blit(header_lbl, (20, Y_OFF))
    
    header_time = FONT_DATE.render(date_info['time'], True, COLOR_ACCENT_2)
    screen.blit(header_time, (380, Y_OFF))
    pygame.draw.line(screen, (40, 45, 60), (20, Y_OFF + 40), (460, Y_OFF + 40), 2)
    
    if not data:
        text = FONT_NEWS.render("Memuat data pasar...", True, COLOR_TEXT_DIM)
        screen.blit(text, (20, 100))
        return

    # Layout Grid 2x2
    # Items: USD, BTC, ETH, GOLD
    items = [
        {"title": "USD / IDR", "key": "usd", "fmt": "Rp {:,}", "color": (85, 239, 196)}, 
        {"title": "EMAS / GR", "key": "gold", "fmt": "Rp {:,}", "color": (253, 203, 110)}, 
        {"title": "BITCOIN", "key": "btc", "fmt": "Rp {:,}", "color": (247, 159, 31)}, 
        {"title": "ETHEREUM", "key": "eth", "fmt": "Rp {:,}", "color": (116, 185, 255)}  
    ]
    
    start_y = 80
    box_w = 210
    box_h = 100
    margin = 20
    
    for i, item in enumerate(items):
        row = i // 2
        col = i % 2
        
        x = margin + (col * (box_w + margin))
        y = start_y + (row * (box_h + margin))
        
        # Box Bg
        pygame.draw.rect(screen, (20, 25, 35), (x, y, box_w, box_h))
        
        # Title
        t_lbl = FONT_SUB.render(item['title'], True, COLOR_TEXT_DIM)
        screen.blit(t_lbl, (x + 15, y + 10))
        
        # Get Data
        d_obj = data.get(item['key'], {'val': 0, 'change': 0})
        # Handle if data is still old format (int)
        if isinstance(d_obj, int): d_obj = {'val': d_obj, 'change': 0}
        
        val = d_obj.get('val', 0)
        if val is None: val = 0
        
        change = d_obj.get('change', 0)
        if change is None: change = 0
        try:
             change = float(change)
        except: 
             change = 0.0
        
        # Value
        val_str = item['fmt'].format(val).replace(',', '.')
        if len(val_str) > 13: val_str = val_str.replace('Rp ', '') 
        
        v_lbl = FONT_NEWS.render(val_str, True, item['color'])
        v_rect = v_lbl.get_rect()
        v_rect.bottomright = (x + box_w - 15, y + box_h - 15)
        screen.blit(v_lbl, v_rect)
        
        # Trend Arrow
        if change != 0:
            arrow_color = (0, 255, 100) if change > 0 else (255, 50, 50)
            ax = x + box_w - 25
            ay = y + 20 # Top right corner of box
            
            # Simple Triangle
            if change > 0: # Green Up
                points = [(ax, ay), (ax-6, ay+10), (ax+6, ay+10)]
            else: # Red Down
                points = [(ax, ay+10), (ax-6, ay), (ax+6, ay)]
                
            pygame.draw.polygon(screen, arrow_color, points)
            
            # Show % text (Tiny)
            pct_str = f"{abs(change):.1f}%"
            p_lbl = FONT_TINY.render(pct_str, True, arrow_color)
            # Right align text relative to arrow to create consistent gap
            p_w = p_lbl.get_width()
            # Arrow center X = ax
            # Text end X = ax - 10 (gap)
            screen.blit(p_lbl, (ax - 10 - p_w, ay - 5))

def draw_quote_slide(quote, date_info):
    screen.fill((50, 20, 40)) # Dark Purple
    Y_OFF = 25
    header_lbl = FONT_DATE.render("QUOTE OF THE DAY", True, (255, 120, 200)) # Pink
    screen.blit(header_lbl, (20, Y_OFF))
    
    header_time = FONT_DATE.render(date_info['time'], True, COLOR_TEXT_MAIN)
    screen.blit(header_time, (380, Y_OFF))
    pygame.draw.line(screen, (255, 120, 200), (20, Y_OFF + 40), (460, Y_OFF + 40), 2)
    
    if not quote:
        text = FONT_NEWS.render("Memilih kata...", True, COLOR_TEXT_DIM)
        screen.blit(text, (20, 100))
        return

    text = quote.get('text', '')
    author = quote.get('author', 'Unknown')
    
    # Textwrap manually for large font
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_str = ' '.join(current_line)
        # Use FONT_NEWS for calculation (same as rendering)
        if FONT_NEWS.size(test_str)[0] > 440:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    y = 90 # Start higher
    for line in lines[:6]: # Max 6 lines
        rend = FONT_NEWS.render(line, True, COLOR_TEXT_MAIN)
        screen.blit(rend, (20, y))
        y += 35 # Tighter spacing
        
    # Author at bottom right fixed position
    auth_rend = FONT_SUB.render(f"- {author}", True, (200, 200, 255))
    auth_rect = auth_rend.get_rect()
    auth_rect.bottomright = (460, 300) # Fixed position
    screen.blit(auth_rend, auth_rect)

def draw_system_slide(data, date_info):
    screen.fill((10, 20, 30)) # Dark Blue
    Y_OFF = 25
    header_lbl = FONT_DATE.render("SYSTEM MONITOR", True, (0, 200, 255))
    screen.blit(header_lbl, (20, Y_OFF))
    
    header_time = FONT_DATE.render(date_info['time'], True, COLOR_TEXT_MAIN)
    screen.blit(header_time, (380, Y_OFF))
    pygame.draw.line(screen, (0, 100, 150), (20, Y_OFF + 40), (460, Y_OFF + 40), 2)
    
    if not data:
        text = FONT_NEWS.render("Memindai system...", True, COLOR_TEXT_DIM)
        screen.blit(text, (20, 100))
        return

    # List: CPU Temp, RAM, Disk, IP
    y_start = 90
    spacing = 50
    
    # 1. CPU Temp
    icon_rect = pygame.Rect(20, y_start, 440, 40)
    pygame.draw.rect(screen, (20, 40, 60), icon_rect)
    lbl = FONT_NEWS.render(f"CPU TEMP: {data.get('temp', 'N/A')}", True, COLOR_ACCENT)
    screen.blit(lbl, (30, y_start + 8))
    
    # 2. RAM Usage
    y_start += spacing
    ram_total = data.get('ram_total', 1)
    ram_used = data.get('ram_used', 0)
    ram_pct = (ram_used / ram_total) * 100 if ram_total > 0 else 0
    
    lbl_ram = FONT_NEWS.render(f"RAM: {ram_used}/{ram_total} MB ({int(ram_pct)}%)", True, COLOR_ACCENT_2)
    screen.blit(lbl_ram, (30, y_start))
    
    # Bar RAM
    pygame.draw.rect(screen, (40, 40, 50), (30, y_start + 28, 400, 8))
    pygame.draw.rect(screen, COLOR_ACCENT_2, (30, y_start + 28, int(4 * ram_pct), 8))
    
    
    # 3. Disk Usage
    y_start += spacing
    lbl_disk = FONT_NEWS.render(f"DISK: {data.get('disk_percent', '0%')}", True, (255, 100, 100))
    screen.blit(lbl_disk, (30, y_start))
    
    # 4. IP Address
    y_start += spacing
    lbl_ip = FONT_NEWS.render(f"IP: {data.get('ip', '-')}", True, COLOR_TEXT_MAIN)
    screen.blit(lbl_ip, (30, y_start))
    
    # 5. WiFi SSID
    y_start += spacing
    wifi_ssid = data.get('wifi_ssid', 'N/A')
    lbl_wifi = FONT_SUB.render(f"WiFi: {wifi_ssid}", True, (100, 200, 255))
    screen.blit(lbl_wifi, (30, y_start))

def sanitize_data(data):
    """Recursively sanitize all strings in data structure"""
    if isinstance(data, str):
        return safe_str(data)
    elif isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data

def main():
    global screen
    try:
        # Force reload config to pick up changes from dashboard
        importlib.reload(config)
        
        with open("/home/pi/weather/debug.log", "a") as f:
            f.write(f"\n=== STARTUP {datetime.datetime.now()} ===\n")
            f.write(f"Location: {config.LOCATION_NAME}\n")
            f.write(f"Coords: {config.LAT}, {config.LON}\n")
        
        pygame.display.init()
        pygame.font.init()
        
        # KEY CHANGE: Real Screen vs Virtual Screen
        try:
            real_screen = pygame.display.set_mode((480, 320), pygame.FULLSCREEN, 16)
        except:
            real_screen = pygame.display.set_mode((480, 320), pygame.FULLSCREEN, 24)
            
        # Virtual Canvas for Drawing elements (This is what global 'screen' points to)
        screen = pygame.Surface((480, 320))
        
        pygame.mouse.set_visible(False)
        init_fonts()
        
        last_weather_upd = 0
        last_news_upd = 0
        last_sholat_upd = 0
        last_java_upd = 0
        last_bmkg_upd = 0
        last_bmkg_forecast_upd = 0
        last_finance_upd = 0
        last_system_upd = 0
        last_quote_upd = 0
        
        weather_data = None
        news_pool = []
        news_display = []
        sholat_data = None
        java_date = None
        bmkg_warning = None
        bmkg_forecast = None
        finance_data = None
        system_data = None
        quote_data = None
        
        slides = ["weather", "bmkg_forecast", "news", "finance", "sholat", "quote", "system"]
        current_slide_idx = 0
        news_page_idx = 0
        last_net_check = 0
        net_fail_count = 0
        boot_time = time.time()  # Track when system started
        slide_start_time = time.time()
        
        running = True
        while running:
            pygame.event.pump()
            curr = time.time()
            date_info = date_utils.get_full_date_info()

            # Update weather
            if curr - last_weather_upd > config.REFRESH_INTERVAL or weather_data is None:
                try:
                    raw_weather = get_weather(lat=config.LAT, lon=config.LON)
                    weather_data = sanitize_data(raw_weather) if raw_weather else None
                    if weather_data and 'icon_surface' in weather_data: 
                        del weather_data['icon_surface']
                    last_weather_upd = curr
                except Exception as e:
                    with open("/home/pi/weather/debug.log", "a") as f:
                        f.write(f"Weather error: {e}\n")
            
            # Update BMKG Forecast
            if curr - last_bmkg_forecast_upd > 1800 or bmkg_forecast is None:
                try:
                    if hasattr(config, 'LOCATION_ID'):
                       raw_fc = ext_services.get_bmkg_forecast(config.LOCATION_ID)
                       bmkg_forecast = sanitize_data(raw_fc) if raw_fc else None
                    last_bmkg_forecast_upd = curr
                except Exception as e:
                     with open("/home/pi/weather/debug.log", "a") as f:
                        f.write(f"BMKG Forecast error: {e}\n")

            # Update Finance (Every 15 mins)
            if curr - last_finance_upd > 900 or finance_data is None:
                try:
                    raw_fin = ext_services.get_finance_data()
                    finance_data = sanitize_data(raw_fin) if raw_fin else None
                    last_finance_upd = curr
                except Exception as e:
                     with open("/home/pi/weather/debug.log", "a") as f:
                        f.write(f"Finance error: {e}\n")

            # Robust Internet Watchdog (Every 5 mins)
            # Grace period: Wait 2 mins after boot before checking
            # Tolerance: 10 failures (50 mins) before reboot
            # Auto WiFi reconnect attempt before giving up
            if curr - boot_time > 120:  # Grace period: 2 minutes after boot
                if curr - last_net_check > 300:  # Check every 5 minutes
                    last_net_check = curr
                    try:
                        # Ping Google DNS with 3 sec timeout
                        res = os.system("ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1")
                        if res != 0:
                            net_fail_count += 1
                            print(f"Network Check Failed! Attempt {net_fail_count}/10")
                            
                            # Try WiFi reconnect at 5th failure (before reboot threshold)
                            if net_fail_count == 5:
                                print("Attempting WiFi reconnect...")
                                os.system("sudo wpa_cli -i wlan0 reconfigure")
                                time.sleep(10)  # Wait for reconnect
                        else:
                            # Success! Reset counter
                            if net_fail_count > 0:
                                print("Network restored!")
                            net_fail_count = 0 
                        
                        # Reboot only after 10 consecutive failures (50 mins)
                        if net_fail_count >= 10:
                            print("Persistent Network Failure. Rebooting...")
                            with open("/home/pi/weather/debug.log", "a") as f:
                                f.write(f"{time.ctime()}: Network Watchdog Reboot (10 failures)\n")
                            import os
                            os.system("sudo reboot")
                    except Exception as e:
                        print(f"Watchdog error: {e}")


            # Update System Info (Every 10s)
            # Retry every 5s if fail
            if (curr - last_system_upd > 10) or (system_data is None and curr - last_system_upd > 5):
                try:
                    raw_sys = ext_services.get_system_info()
                    if raw_sys:
                         system_data = sanitize_data(raw_sys)
                    last_system_upd = curr
                except: pass

            # Update Quote (Every 45 seconds - New quote each cycle)
            if (curr - last_quote_upd > 45) or (quote_data is None and curr - last_quote_upd > 30):
                try:
                    raw_quote = ext_services.get_random_quote()
                    if raw_quote:
                         quote_data = sanitize_data(raw_quote)
                    last_quote_upd = curr
                except: pass

            # Update news
            if curr - last_news_upd > config.NEWS_INTERVAL or not news_pool:
                try:
                    raw_news = ext_services.get_google_news()
                    news_pool = sanitize_data(raw_news) if raw_news else []
                    if news_pool:
                        news_display = random.sample(news_pool, min(len(news_pool), config.NEWS_LIMIT))
                    last_news_upd = curr
                except Exception as e:
                    with open("/home/pi/weather/debug.log", "a") as f:
                        f.write(f"News error: {e}\n")

            # Update sholat
            if curr - last_sholat_upd > config.SHOLAT_INTERVAL or sholat_data is None:
                try:
                    raw_sholat = ext_services.get_sholat_times(lat=config.LAT, lon=config.LON)
                    sholat_data = sanitize_data(raw_sholat) if raw_sholat else None
                    last_sholat_upd = curr
                except Exception as e:
                    with open("/home/pi/weather/debug.log", "a") as f:
                        f.write(f"Sholat error: {e}\n")

            # Update javanese
            if curr - last_java_upd > 21600 or java_date is None: 
                try:
                    raw_java = ext_services.get_javanese_date()
                    java_date = safe_str(raw_java) if raw_java else None
                    last_java_upd = curr
                except: pass

            # Update BMKG Warning
            if curr - last_bmkg_upd > config.BMKG_INTERVAL:
                try:
                    raw_bmkg = ext_services.get_bmkg_warning(config.BMKG_PROVINCE)
                    bmkg_warning = sanitize_data(raw_bmkg) if raw_bmkg else None
                    last_bmkg_upd = curr
                    if bmkg_warning and "bmkg" not in slides:
                        slides.insert(1, "bmkg")
                    elif not bmkg_warning and "bmkg" in slides:
                        slides.remove("bmkg")
                except: pass
            
            # Slide duration logic
            slide_duration = config.SLIDE_DURATION_WEATHER
            s_type = slides[current_slide_idx]
            
            if s_type == "news": slide_duration = config.SLIDE_DURATION_NEWS
            elif s_type == "sholat": slide_duration = config.SLIDE_DURATION_SHOLAT
            elif s_type == "bmkg": slide_duration = config.SLIDE_DURATION_BMKG
            elif s_type == "bmkg_forecast": slide_duration = getattr(config, 'SLIDE_DURATION_BMKG', 5)
            elif s_type == "finance": slide_duration = getattr(config, 'SLIDE_DURATION_FINANCE', 10)
            elif s_type == "quote": slide_duration = getattr(config, 'SLIDE_DURATION_QUOTE', 10)
            elif s_type == "system": slide_duration = getattr(config, 'SLIDE_DURATION_SYSTEM', 8)

            # Convert to int in case it's a string from config
            try:
                slide_duration = int(slide_duration)
            except (ValueError, TypeError):
                slide_duration = 10  # Default fallback

            # Slide transition
            if curr - slide_start_time > slide_duration:
                if slides[current_slide_idx] == "news" and news_display:
                    if news_page_idx < len(news_display) - 1:
                        news_page_idx += 1
                        slide_start_time = curr
                    else:
                        news_page_idx = 0
                        current_slide_idx = (current_slide_idx + 1) % len(slides)
                        slide_start_time = curr
                        if slides[current_slide_idx] == "news" and news_pool:
                            news_display = random.sample(news_pool, min(len(news_pool), config.NEWS_LIMIT))
                else:
                    current_slide_idx = (current_slide_idx + 1) % len(slides)
                    slide_start_time = curr
                    if slides[current_slide_idx] == "news" and news_pool:
                        news_display = random.sample(news_pool, min(len(news_pool), config.NEWS_LIMIT))

            # Auto Reboot Logic (Once per loop is fine, low overhead)
            # Use getattr with default 0 to avoid crash if config not updated yet
            reboot_hours = getattr(config, 'AUTO_REBOOT_HOURS', 0)
            # Convert to int in case it's a string from config
            try:
                reboot_hours = int(reboot_hours)
            except (ValueError, TypeError):
                reboot_hours = 0
            if reboot_hours > 0:
                try:
                    with open('/proc/uptime', 'r') as f:
                        uptime_seconds = float(f.readline().split()[0])
                    
                    # Convert Hours to Seconds (3600)
                    limit_seconds = reboot_hours * 3600
                    if uptime_seconds > limit_seconds:
                        print("AUTO REBOOT TRIGGERED")
                        import os
                        os.system("sudo reboot")
                except: pass
            
            # Draw current slide to Virtual Screen
            screen.fill(COLOR_BG)
            s_type = slides[current_slide_idx]
            
            try:
                if s_type == "weather":
                    draw_weather_slide(weather_data, date_info, sholat_data, java_date)
                elif s_type == "bmkg_forecast":
                    draw_bmkg_forecast_slide(bmkg_forecast, date_info)
                elif s_type == "news":
                    draw_news_slide(news_display, date_info, news_page_idx)
                elif s_type == "sholat":
                    draw_sholat_slide(sholat_data, date_info, config.LOCATION_NAME or "Indonesia")
                elif s_type == "bmkg":
                    draw_bmkg_slide(bmkg_warning, date_info)
                elif s_type == "finance":
                    draw_finance_slide(finance_data, date_info)
                elif s_type == "system":
                    draw_system_slide(system_data, date_info)
                elif s_type == "quote":
                    draw_quote_slide(quote_data, date_info)
            except Exception as e:
                with open("/home/pi/weather/debug.log", "a") as f:
                    f.write(f"Draw error ({s_type}): {e}\n")
            
            # ROTATION: Use config.ROTATE_ANGLE
            if config.ROTATE_ANGLE > 0:
                rotated_surface = pygame.transform.rotate(screen, config.ROTATE_ANGLE)
            else:
                rotated_surface = screen
            real_screen.blit(rotated_surface, (0, 0))

            pygame.display.flip()
            time.sleep(0.1)
            
    except Exception as e:
        with open("/home/pi/weather/fatal_error.txt", "w") as f:
            import traceback
            f.write(f"{e}\n{traceback.format_exc()}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
