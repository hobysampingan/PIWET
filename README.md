# 🌦️ Weather Pi - Raspberry Pi Zero Weather Station

A beautiful, feature-rich weather display for Raspberry Pi Zero W with 3.5" LCD screen.

![Weather Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%20W-C51A4A?logo=raspberry-pi)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🌡️ **Real-time Weather** - Current conditions from OpenWeatherMap API
- 📰 **News Headlines** - Latest news from Google News RSS
- 🌊 **BMKG Forecast** - Indonesian weather warnings and 3-hour forecasts
- 🕌 **Prayer Times** - Accurate Islamic prayer schedule (Aladhan API)
- 💰 **Financial Data** - Crypto prices and forex rates
- 💬 **Quote of the Day** - Inspirational quotes
- 📊 **System Monitor** - CPU, RAM, disk, IP address, WiFi
- 🌐 **Web Dashboard** - Easy configuration via browser
- 🔄 **Auto-start** - Runs automatically on boot
- 📍 **Precise Location** - Down to village/kelurahan level (Indonesia)

## 🛠️ Hardware Requirements

- **Raspberry Pi Zero W** (or any Pi with WiFi)
- **3.5" TFT LCD** (480x320, SPI interface)
  - Tested with: WaveShare 3.5" LCD, MPI3508
  - Framebuffer: `/dev/fb1`
- **MicroSD Card** (8GB minimum, 16GB recommended)
- **Power Supply** (5V 2A recommended)

## 📦 Software Requirements

- **Raspberry Pi OS Lite** (Bookworm or Bullseye)
- **Python 3.7+**
- **Internet connection** (WiFi)

## 🚀 Quick Start

### 1. Flash Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash **Raspberry Pi OS Lite (32-bit)** to SD card
3. **Important:** In Imager settings:
   - Enable SSH
   - Set username: `pi`
   - Set password: (your choice)
   - Configure WiFi (SSID & password)
   - Set timezone

### 2. First Boot & SSH

```bash
# Find Pi's IP address (check your router or use)
ping raspberrypi.local

# SSH into Pi
ssh pi@<IP_ADDRESS>
# Example: ssh pi@192.168.0.171
```

### 3. Install LCD Driver

```bash
# Clone LCD driver
cd ~
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show

# Install driver for 3.5" LCD
sudo ./LCD35-show
# Pi will reboot automatically
```

### 4. Install Weather Pi

```bash
# After reboot, SSH again
ssh pi@<IP_ADDRESS>

# Transfer files from your computer
# On your Windows PC (PowerShell):
pscp -r weather pi@<IP_ADDRESS>:/home/pi/

# On Pi, run installer
cd /home/pi/weather
chmod +x install.sh
sudo ./install.sh

# Pi will reboot automatically
```

### 5. Configure via Web Dashboard

After reboot (wait 2-3 minutes):

1. Open browser: `http://<IP_ADDRESS>:5000`
2. Configure location (Province → Kabupaten → Kecamatan → Desa)
3. Adjust slide durations if needed
4. Click "Simpan Lokasi Presisi"
5. Click "🔄 Reboot Pi (Safe, Slow)"
6. Wait 2-3 minutes for changes to apply

## 🎨 Display Slides

The display rotates through these slides:

1. **Weather** (15s) - Current temperature, conditions, feels like, humidity, wind
2. **BMKG Forecast** (6s) - Today's 3-hour forecasts with icons
3. **News** (10s) - Latest headlines (5 news items, paginated)
4. **Finance** (10s) - Bitcoin, Ethereum, USD/IDR rates
5. **Prayer Times** (10s) - Today's Islamic prayer schedule
6. **Quote of the Day** (10s) - Random inspirational quote
7. **System Monitor** (8s) - CPU temp, RAM, disk, IP, WiFi

## ⚙️ Configuration

### Via Web Dashboard (Recommended)

Access: `http://<IP_ADDRESS>:5000`

**Available Settings:**
- Location (Province, Kabupaten, Kecamatan, Desa)
- Slide durations (seconds)
- News limit (number of headlines)
- Auto-reboot interval (hours)

### Via config.py (Advanced)

Edit `/home/pi/weather/config.py`:

```python
# API Keys
API_KEY = "your_openweathermap_api_key"

# Location
LAT = -6.2632169434
LON = 106.8183223867
LOCATION_NAME = "Your Location"
BMKG_PROVINCE = "Your Province"

# Slide Durations (seconds)
SLIDE_DURATION_WEATHER = 15
SLIDE_DURATION_NEWS = 10
SLIDE_DURATION_SHOLAT = 10
SLIDE_DURATION_BMKG = 6
SLIDE_DURATION_FINANCE = 10
SLIDE_DURATION_QUOTE = 10
SLIDE_DURATION_SYSTEM = 8

# Auto Reboot (0 = disabled)
AUTO_REBOOT_HOURS = 3
```

## 🔧 Troubleshooting

### Display shows cursor/blank screen

```bash
# Check if service is running
sudo systemctl status weather.service

# Check logs
sudo journalctl -u weather.service -n 50

# Restart service
sudo systemctl restart weather.service

# If still not working, reboot
sudo reboot
```

### WiFi not connecting

```bash
# Check WiFi status
iwconfig

# Reconfigure WiFi
sudo raspi-config
# Select: System Options → Wireless LAN
```

### Display is upside down

Edit `/home/pi/weather/config.py`:
```python
ROTATE_ANGLE = 180  # Try 0, 90, 180, or 270
```

Then reboot:
```bash
sudo reboot
```

### Web dashboard not accessible

```bash
# Check dashboard service
sudo systemctl status weather-dashboard.service

# Restart dashboard
sudo systemctl restart weather-dashboard.service
```

### Slide stuck on one screen

**This is a known issue with TypeError bug.**

**Solution:**
1. Open dashboard: `http://<IP_ADDRESS>:5000`
2. Click "🔄 Reboot Pi (Safe, Slow)"
3. Wait 2-3 minutes
4. Display should work normally

**Alternative (faster but risky):**
1. Click "⚡ Restart Display (Fast, Risky)"
2. If it works, great! If stuck again, use Reboot.

## 📁 File Structure

```
weather/
├── main.py                 # Main display application
├── app.py                  # Web dashboard (Flask)
├── config.py               # Configuration file
├── ext_services.py         # External API services
├── date_utils.py           # Date/time utilities
├── weather_service.py      # OpenWeatherMap integration
├── install.sh              # Installation script
├── templates/
│   └── index.html          # Dashboard UI
├── quotes.json             # Quote database
├── weather.service         # Systemd service (display)
├── weather-dashboard.service  # Systemd service (web)
└── README.md               # This file
```

## 🔄 Update Workflow

### Option 1: Restart Display (Fast, Risky)
- **Time:** 10 seconds
- **Risk:** May stuck on one slide
- **Use when:** Quick testing

1. Update config via dashboard
2. Click "⚡ Restart Display (Fast, Risky)"
3. If stuck, use Option 2

### Option 2: Reboot Pi (Safe, Slow)
- **Time:** 2-3 minutes
- **Risk:** None (100% safe)
- **Use when:** Final deployment

1. Update config via dashboard
2. Click "🔄 Reboot Pi (Safe, Slow)"
3. **Close browser tab** (don't wait for response)
4. Wait 2-3 minutes
5. Refresh dashboard

## 🌐 API Services Used

- **OpenWeatherMap** - Weather data
- **Google News RSS** - News headlines
- **BMKG** - Indonesian weather warnings
- **Aladhan API** - Islamic prayer times
- **CoinGecko** - Cryptocurrency prices
- **Frankfurter** - Forex rates

## 📝 License

MIT License - Feel free to modify and distribute!

## 🙏 Credits

- LCD Driver: [goodtft/LCD-show](https://github.com/goodtft/LCD-show)
- Weather API: [OpenWeatherMap](https://openweathermap.org/)
- Prayer Times: [Aladhan API](https://aladhan.com/prayer-times-api)

## 🐛 Known Issues

1. **Slide stuck bug** - Occasional TypeError causes display to freeze on one slide
   - **Workaround:** Reboot via dashboard or SSH
   - **Root cause:** Config type conversion issue (string vs int)

2. **Reboot response slow** - Dashboard reboot button takes 2 minutes to respond
   - **Workaround:** Close browser tab after clicking, Pi will reboot in background
   - **Root cause:** HTTP timeout due to Pi shutdown

3. **WiFi delay on boot** - Sometimes gets APIPA address (169.254.x.x) before connecting
   - **Workaround:** Wait 1-2 minutes, WiFi will connect automatically
   - **Root cause:** DHCP timing on Pi Zero W

## 💡 Tips

- **Set static IP** in your router for easier access
- **Bookmark dashboard** for quick configuration
- **Use SSH** for fastest reboot: `ssh pi@<IP> "sudo reboot"`
- **Check logs** if something goes wrong: `sudo journalctl -u weather.service`
- **Auto-reboot** is enabled by default (every 3 hours) to prevent memory leaks

## 📞 Support

If you encounter issues:
1. Check logs: `sudo journalctl -u weather.service -n 50`
2. Check service status: `sudo systemctl status weather.service`
3. Try reboot: `sudo reboot`
4. Check this README's Troubleshooting section

---

**Enjoy your Weather Pi! 🌦️🚀**
