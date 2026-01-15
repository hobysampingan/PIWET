# Panduan Instalasi Cepat - Weather Pi

## Ringkasan
Panduan ini untuk install Weather Pi di Raspberry Pi Zero W dengan LCD 3.5" dari NOL.

## Yang Kamu Butuhkan
1. Raspberry Pi Zero W
2. LCD 3.5" SPI (MPI3508)
3. MicroSD 8GB+
4. Komputer dengan Raspberry Pi Imager
5. Koneksi WiFi

## Langkah Instalasi

### STEP 1: Flash SD Card (di Komputer)
1. Download & install **Raspberry Pi Imager**
2. Pilih OS: **Raspberry Pi OS Lite (32-bit)**
3. Pilih SD Card kmu
4. Klik ⚙️ (Settings):
   - ✅ Enable SSH
   - ✅ Set username: `pi`
   - ✅ Set password: `<password-kmu>`
   - ✅ Configure WiFi (SSID & password)
   - ✅ Set locale (Asia/Jakarta, keyboard US)
5. Klik **Write** dan tunggu selesai

### STEP 2: Boot & SSH
1. Masukkan SD card ke Raspberry Pi
2. Nyalakan Pi (tunggu 2 menit)
3. Cari IP Pi di router atau gunakan:
   ```
   ping raspberrypi.local
   ```
4. SSH ke Pi:
   ```bash
   ssh pi@<ip-address>
   # atau
   ssh pi@raspberrypi.local
   ```

### STEP 3: Install LCD Driver
```bash
cd ~
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show
sudo ./MPI3508-show
```
**Pi akan reboot otomatis. Tunggu 2 menit, lalu SSH lagi.**

### STEP 4: Transfer File Weather Pi
**Dari komputer Windows:**
```powershell
# Masuk ke folder weather
cd C:\Users\NEWLIFE\Documents\Arduino\weather

# Kirim semua file ke Pi (ganti <ip-pi> dengan IP Pi kmu)
pscp -r * pi@<ip-pi>:/home/pi/weather/
```

**Atau dari komputer Linux/Mac:**
```bash
scp -r * pi@<ip-pi>:/home/pi/weather/
```

### STEP 5: Jalankan Installer
```bash
# SSH ke Pi
ssh pi@<ip-pi>

# Masuk ke folder weather
cd /home/pi/weather

# Jalankan installer
chmod +x install.sh
./install.sh
```

**Pi akan reboot otomatis setelah instalasi selesai.**

### STEP 6: Selesai!
Setelah reboot (tunggu 2 menit), layar LCD akan menampilkan cuaca otomatis.

## Akses Web Dashboard
Buka browser dan akses:
```
http://<ip-pi>:5000
```

Dari dashboard kmu bisa:
- Ganti lokasi
- Atur durasi slide
- Reboot sistem

## Troubleshooting

### Pi tidak connect WiFi
1. Cabut power Pi
2. Masukkan SD card ke komputer
3. Edit file `wpa_supplicant.conf` di partisi `boot`
4. Pastikan SSID dan password benar
5. Masukkan kembali SD card ke Pi

### Layar blank setelah install
```bash
# SSH ke Pi
ssh pi@<ip-pi>

# Cek status
sudo systemctl status weather.service

# Restart service
sudo systemctl restart weather.service
```

### Layar terbalik
```bash
# SSH ke Pi
ssh pi@<ip-pi>

# Edit main.py
nano /home/pi/weather/main.py

# Cari baris 824, ganti:
# Dari: rotated_surface = screen
# Jadi: rotated_surface = pygame.transform.rotate(screen, 180)

# Save (Ctrl+O, Enter, Ctrl+X)

# Restart
sudo systemctl restart weather.service
```

## Perintah Berguna

```bash
# Restart aplikasi cuaca
sudo systemctl restart weather.service

# Restart web dashboard
sudo systemctl restart weather-dashboard.service

# Lihat log aplikasi
sudo journalctl -u weather.service -f

# Reboot Pi
sudo reboot

# Shutdown Pi
sudo shutdown now
```

## Selesai!
Selamat menikmati Weather Pi kmu! 🌦️
