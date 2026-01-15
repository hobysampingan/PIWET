#!/bin/bash
# Weather Pi Auto Installer
# Tested on Raspberry Pi Zero W with 3.5" LCD

echo "========================================="
echo "  Weather Pi Auto Installer"
echo "========================================="
echo ""

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    echo "ERROR: Please run this script as user 'pi'"
    exit 1
fi

# Update system
echo "[1/8] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install dependencies
echo "[2/8] Installing dependencies..."
sudo apt-get install -y python3-pip python3-pygame python3-flask git

# Install Python packages
echo "[3/8] Installing Python packages..."
pip3 install requests hijridate

# Copy files to /home/pi/weather
echo "[4/8] Copying application files..."
INSTALL_DIR="/home/pi/weather"
mkdir -p $INSTALL_DIR

# Copy main application files
cp main.py $INSTALL_DIR/
cp app.py $INSTALL_DIR/
cp config.py $INSTALL_DIR/
cp date_utils.py $INSTALL_DIR/
cp ext_services.py $INSTALL_DIR/
cp weather_service.py $INSTALL_DIR/
cp quotes.json $INSTALL_DIR/
cp requirements.txt $INSTALL_DIR/
cp -r templates $INSTALL_DIR/

# Set permissions
chmod +x $INSTALL_DIR/*.py

# Install systemd services
echo "[5/8] Installing systemd services..."
sudo cp weather.service /etc/systemd/system/
sudo cp weather-dashboard.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/weather.service
sudo chmod 644 /etc/systemd/system/weather-dashboard.service

# Disable getty on tty1 (prevent terminal from showing on LCD)
echo "[6/8] Disabling terminal on LCD..."
sudo systemctl stop getty@tty1.service
sudo systemctl disable getty@tty1.service
sudo systemctl mask getty@tty1.service

# Enable and start services
echo "[7/8] Enabling auto-start services..."
sudo systemctl daemon-reload
sudo systemctl enable weather.service
sudo systemctl enable weather-dashboard.service

# Configure autologin (optional but recommended)
echo "[8/8] Configuring autologin..."
sudo raspi-config nonint do_boot_behaviour B2

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "The system will reboot in 5 seconds..."
echo "After reboot, the weather display will start automatically."
echo ""
echo "Web dashboard will be available at: http://$(hostname -I | awk '{print $1}'):5000"
echo ""

sleep 5
sudo reboot
