import os
import re
import subprocess
import logging
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Setup Logging
LOG_FILE = os.path.join(os.path.dirname(__file__), 'weather_app.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Path to the configuration file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.py')

def get_config_value(key, default=None):
    try:
        with open(CONFIG_PATH, 'r') as f:
            content = f.read()
            string_match = re.search(fr'^{key} = ["\'](.*?)["\']', content, re.MULTILINE)
            if string_match: return string_match.group(1)
            number_match = re.search(fr'^{key} = ([-0-9.]+)', content, re.MULTILINE)
            if number_match:
                val = number_match.group(1)
                return float(val) if '.' in val else int(val)
    except: pass
    return default

def update_config_values(updates):
    try:
        with open(CONFIG_PATH, 'r') as f:
            content = f.read()
        
        new_content = content
        for key, value in updates.items():
            if isinstance(value, str):
                pattern = fr'^{key} = ["\'].*?["\']'
                replacement = f'{key} = "{value}"'
            else:
                pattern = fr'^{key} = [-0-9.]+'
                replacement = f'{key} = {value}'
            
            if re.search(pattern, new_content, re.MULTILINE):
                new_content = re.sub(pattern, replacement, new_content, flags=re.MULTILINE)
            else:
                new_content += f"\n{replacement}"
        
        with open(CONFIG_PATH, 'w') as f:
            f.write(new_content)
        return True
    except Exception as e:
        logging.error(f"Failed to update config.py: {e}")
        return False

@app.route('/')
def index():
    config_values = {
        "lat": get_config_value("LAT", -6.2),
        "lon": get_config_value("LON", 106.8),
        "loc_name": get_config_value("LOCATION_NAME", "Jakarta"),
        "bmkg_province": get_config_value("BMKG_PROVINCE", "Jawa Tengah"),
        "tz_offset": get_config_value("TIMEZONE_OFFSET", 25200),
        "weather_dur": get_config_value("SLIDE_DURATION_WEATHER", 15),
        "news_dur": get_config_value("SLIDE_DURATION_NEWS", 10),
        "sholat_dur": get_config_value("SLIDE_DURATION_SHOLAT", 15),
        "bmkg_dur": get_config_value("SLIDE_DURATION_BMKG", 5),
        "finance_dur": get_config_value("SLIDE_DURATION_FINANCE", 10),
        "quote_dur": get_config_value("SLIDE_DURATION_QUOTE", 10),
        "system_dur": get_config_value("SLIDE_DURATION_SYSTEM", 8),
        "news_limit": get_config_value("NEWS_LIMIT", 5),
        "auto_reboot": get_config_value("AUTO_REBOOT_HOURS", 3)
    }
    return render_template('index.html', **config_values)

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    logging.info(f"USER ACTION: Update Settings Request - Data: {data}")
    
    updates = {}
    mapping = {
        "lat": "LAT", "lon": "LON", "loc_name": "LOCATION_NAME", "loc_id": "LOCATION_ID",
        "bmkg_province": "BMKG_PROVINCE", "weather_dur": "SLIDE_DURATION_WEATHER",
        "news_dur": "SLIDE_DURATION_NEWS", "sholat_dur": "SLIDE_DURATION_SHOLAT",
        "bmkg_dur": "SLIDE_DURATION_BMKG", "finance_dur": "SLIDE_DURATION_FINANCE",
        "quote_dur": "SLIDE_DURATION_QUOTE", "system_dur": "SLIDE_DURATION_SYSTEM",
        "news_limit": "NEWS_LIMIT", "auto_reboot": "AUTO_REBOOT_HOURS",
        "tz_offset": "TIMEZONE_OFFSET"
    }
    
    # Auto-Calculate Timezone based on Province
    if "bmkg_province" in data:
        prov = data["bmkg_province"].upper()
        wib = ["ACEH", "SUMATERA UTARA", "SUMATERA BARAT", "RIAU", "JAMBI", "SUMATERA SELATAN", 
               "BENGKULU", "LAMPUNG", "KEPULAUAN BANGKA BELITUNG", "KEPULAUAN RIAU", 
               "DKI JAKARTA", "JAWA BARAT", "JAWA TENGAH", "DAERAH ISTIMEWA YOGYAKARTA", 
               "JAWA TIMUR", "BANTEN", "KALIMANTAN BARAT", "KALIMANTAN TENGAH"]
        wit = ["MALUKU", "MALUKU UTARA", "PAPUA", "PAPUA BARAT", "PAPUA SELATAN", 
               "PAPUA TENGAH", "PAPUA PEGUNUNGAN", "PAPUA BARAT DAYA"]
        
        if any(x in prov for x in wib): data["tz_offset"] = 25200
        elif any(x in prov for x in wit): data["tz_offset"] = 32400
        else: data["tz_offset"] = 28800
        logging.info(f"AUTO-TZ: Province {prov} set to TZ Offset {data['tz_offset']}")

    for req_key, config_key in mapping.items():
        if req_key in data:
            val = data[req_key]
            if config_key in ["SLIDE_DURATION_WEATHER", "SLIDE_DURATION_NEWS", "SLIDE_DURATION_SHOLAT", "SLIDE_DURATION_BMKG", "NEWS_LIMIT", "TIMEZONE_OFFSET"]:
                updates[config_key] = int(val)
            elif config_key in ["LAT", "LON"]:
                updates[config_key] = float(val)
            else:
                updates[config_key] = str(val)
        
    if updates:
        if update_config_values(updates):
            os.sync() # Force write to SD card immediately
            logging.info(f"INJECTION: config.py updated successfully with {updates}")
            
            
            # Config saved successfully
            logging.info("CONFIG: Settings applied successfully")
            return jsonify({"status": "success", "message": "Settings saved! Restart service to apply."})
        else:
            logging.error("INJECTION FAILED: Could not update config.py")
            return jsonify({"status": "error", "message": "Failed to save settings"})
    
    return jsonify({"status": "error", "message": "Check logs for failure details"})

@app.route('/api/logs')
def get_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            return "<pre>" + "".join(lines[-50:]) + "</pre>" # Show last 50 lines
    except:
        return "No logs found."

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    action = data.get('action')
    logging.info(f"USER ACTION: Control Request - Action: {action}")
    
    try:
        if action == 'restart':
            logging.info("CONTROL: Restarting weather display service...")
            subprocess.Popen(["sudo", "systemctl", "restart", "weather.service"])
            return jsonify({"status": "success", "message": "Display restarting... (may stuck, reboot if needed)"})
        elif action == 'reboot':
            logging.warning("CONTROL: System reboot triggered!")
            # Use nohup to detach reboot from Flask process
            # This allows response to be sent before Pi shuts down
            subprocess.Popen(
                "nohup sh -c 'sleep 0.2 && sudo reboot' > /dev/null 2>&1 &",
                shell=True
            )
            return jsonify({"status": "success", "message": "Rebooting system..."})
        else:
            return jsonify({"status": "error", "message": "Unknown action"})
    except Exception as e:
        logging.error(f"CONTROL FAILED: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
