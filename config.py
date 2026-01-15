
# Configuration
API_KEY = "41596bf10fdbea6e53c3ddf0084add2b"
CITY = "Kertabesuki,ID"
UNITS = "metric" # metric for Celsius

# Precise Location (New for v2.2)
LAT = -6.9016
LON = 108.9837
LOCATION_NAME = "Kertabesuki, Wanasari"
BMKG_PROVINCE = "Jawa Tengah"
LOCATION_ID = "3329122001" # Kode Wilayah 10 Digit (Desa/Kelurahan)
TIMEZONE_OFFSET = 25200 # Offset in seconds (e.g., 25200 for GMT+7)
ROTATE_ANGLE = 0 # 0, 90, 180, 270

# Screen Dimensions (3.5 inch RPi Display)
WIDTH = 480
HEIGHT = 320

# Framebuffer path for Pi
FB_PATH = "/dev/fb1"

# UI Colors (R, G, B)
BG_COLOR = (5, 6, 12)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 255, 230)

# Refresh intervals in seconds
REFRESH_INTERVAL = 180     # 3 minutes - weather updates
NEWS_INTERVAL = 600         # 10 minutes - news updates
SHOLAT_INTERVAL = 14400     # 4 hours
BMKG_INTERVAL = 600         # 10 minutes

CITY_SHOLAT = "Brebes" # Legacy fallback
NEWS_CATEGORY = "all" 

# Slide durations (seconds)
SLIDE_DURATION_WEATHER = 15
SLIDE_DURATION_NEWS = 10
SLIDE_DURATION_SHOLAT = 10
SLIDE_DURATION_BMKG = 6
SLIDE_DURATION_FINANCE = 10
SLIDE_DURATION_QUOTE = 10
SLIDE_DURATION_SYSTEM = 8
# Auto Reboot (Hours). 0 = Disable
AUTO_REBOOT_HOURS = 3

# Pagination
NEWS_PER_PAGE = 1
NEWS_LIMIT = 5

# UI Layout
HEADER_HEIGHT = 45

# Date Adjustments (Days)
JAVA_DATE_OFFSET = 0
HIJRI_DATE_OFFSET = 0
