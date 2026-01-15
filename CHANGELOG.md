# Changelog

All notable changes to Weather Pi project.

## [2.0.0] - 2026-01-15

### Added
- ✨ Web Dashboard for easy configuration
- 📍 Precise location selection (Province → Kabupaten → Kecamatan → Desa)
- ⚡ Restart Display button (fast but risky)
- 🔄 Reboot Pi button (safe but slow)
- 🌐 Auto-refresh browser after saving settings
- 💬 "Quote of the Day" slide (replaced "Kata Bijak")
- 📊 System monitor slide with IP address and WiFi info
- 🎨 Premium UI design for dashboard
- 🔧 Configurable slide durations via dashboard
- 📝 Comprehensive logging system

### Changed
- 🔄 Improved auto-start reliability with systemd service
- 🎯 Better error handling for API failures
- 📱 Responsive dashboard design
- ⚙️ Optimized config.py structure
- 🌡️ Enhanced weather display with more details

### Fixed
- 🐛 Fixed rotation issues (now uses ROTATE_ANGLE = 0)
- 🔧 Fixed AUTO_REBOOT_HOURS type conversion
- 📡 Fixed WiFi connection delay on boot
- 🎨 Fixed text rendering issues with Pygame

### Known Issues
- ⚠️ Slide stuck bug (TypeError) - Workaround: Reboot via dashboard
- ⏱️ Reboot response slow (2 min) - Workaround: Close browser after clicking
- 📶 WiFi APIPA delay - Workaround: Wait 1-2 minutes for DHCP

## [1.0.0] - Initial Release

### Features
- 🌦️ Weather display with OpenWeatherMap API
- 📰 News headlines from Google News
- 🌊 BMKG forecast integration
- 🕌 Prayer times (Aladhan API)
- 💰 Financial data (crypto + forex)
- 💬 Random quotes
- 🔄 Auto-start on boot
- 📺 3.5" LCD support

---

**Note:** Version 2.0.0 is production-ready with known issues documented.
