# 🚀 Weather Pi - Quick Start Guide

**Get your Weather Pi running in 30 minutes!**

## 📋 What You Need

- Raspberry Pi Zero W
- 3.5" LCD Screen (SPI)
- MicroSD Card (8GB+)
- WiFi network
- Computer with SD card reader

---

## ⚡ 5-Step Installation

### Step 1: Flash SD Card (5 min)

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert SD card
3. Choose: **Raspberry Pi OS Lite (32-bit)**
4. Click ⚙️ Settings:
   - ✅ Enable SSH
   - Username: `pi`
   - Password: (your choice)
   - ✅ Configure WiFi (your SSID & password)
   - ✅ Set timezone
5. Click **WRITE**

### Step 2: Boot & Connect (5 min)

1. Insert SD card into Pi
2. Connect LCD screen
3. Power on Pi
4. Wait 2 minutes for boot
5. Find Pi's IP:
   ```
   ping raspberrypi.local
   ```
   Or check your router's DHCP list

### Step 3: Install LCD Driver (10 min)

```bash
# SSH into Pi
ssh pi@<IP_ADDRESS>

# Install LCD driver
cd ~
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show
sudo ./LCD35-show

# Pi will reboot (wait 2 min)
```

### Step 4: Install Weather Pi (5 min)

**On your PC (PowerShell):**
```powershell
# Extract WeatherPi-v2.0.zip
# Navigate to extracted folder
cd path\to\WeatherPi-v2.0

# Transfer to Pi
pscp -r * pi@<IP_ADDRESS>:/home/pi/weather/
```

**On Pi (SSH):**
```bash
ssh pi@<IP_ADDRESS>
cd /home/pi/weather
chmod +x install.sh
sudo ./install.sh

# Pi will reboot (wait 3 min)
```

### Step 5: Configure (5 min)

1. Open browser: `http://<IP_ADDRESS>:5000`
2. Select your location:
   - Province → Kabupaten → Kecamatan → Desa
3. Click **"Simpan Lokasi Presisi"**
4. Click **"🔄 Reboot Pi (Safe, Slow)"**
5. Close browser tab
6. Wait 3 minutes
7. **DONE!** Weather display is running! 🎉

---

## 🎯 What You'll See

The display rotates through:
1. 🌡️ Current Weather
2. 🌊 BMKG Forecast
3. 📰 News Headlines
4. 💰 Crypto & Forex
5. 🕌 Prayer Times
6. 💬 Quote of the Day
7. 📊 System Info

---

## 🔧 Quick Troubleshooting

**Blank screen?**
```bash
ssh pi@<IP_ADDRESS>
sudo reboot
```

**Wrong location?**
1. Open: `http://<IP_ADDRESS>:5000`
2. Change location
3. Click "🔄 Reboot Pi"

**Display stuck?**
1. Open: `http://<IP_ADDRESS>:5000`
2. Click "🔄 Reboot Pi (Safe, Slow)"
3. Wait 3 minutes

---

## 📚 Need More Help?

- **Full Documentation:** See `README.md`
- **Installation Details:** See `INSTALL_GUIDE.md`
- **Troubleshooting:** See `README.md` → Troubleshooting section

---

**Enjoy your Weather Pi! 🌦️**
