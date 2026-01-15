import datetime
from hijridate import Gregorian
import config

# Constants for Javanese Date
PASARAN = ["Legi", "Pahing", "Pon", "Wage", "Kliwon"]
# Reference: 1 January 2014 was a Wednesday and Legi
REF_DATE = datetime.date(2014, 1, 1)
REF_PASARAN_IDX = 0 # Legi

# Indonesian Localization
DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
MONTHS_ID = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
             "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
MONTHS_HIJRI = ["", "Muharram", "Safar", "Rabi'ul Awal", "Rabi'ul Akhir", 
                "Jumadil Awal", "Jumadil Akhir", "Rajab", "Sya'ban", 
                "Ramadhan", "Syawal", "Dzulkaidah", "Dzulhijjah"]

def get_javanese_pasaran(date_obj):
    """
    Calculate Javanese Pasaran (Legi, Pahing, etc.)
    """
    try:
        # Apply global offset
        adjusted_date = date_obj + datetime.timedelta(days=config.JAVA_DATE_OFFSET)
        
        delta = adjusted_date - REF_DATE
        days_passed = delta.days
        
        # Calculate index
        # User feedback: 12 Jan 2026 should be Wage, but was Kliwon.
        # Calculation showed Kliwon (4), Reality Wage (3). Difference -1.
        # Adjusting offset.
        pasaran_idx = (days_passed + REF_PASARAN_IDX - 1) % 5
        return PASARAN[pasaran_idx]
    except:
        return ""

def get_hijri_date(date_obj):
    """
    Get Hijri date string (e.g., "10 Ramadhan 1445")
    """
    try:
        # Apply global offset
        adjusted_date = date_obj + datetime.timedelta(days=config.HIJRI_DATE_OFFSET)
        
        h_date = Gregorian(adjusted_date.year, adjusted_date.month, adjusted_date.day).to_hijri()
        return f"{h_date.day} {MONTHS_HIJRI[h_date.month]} {h_date.year} H"
    except Exception as e:
        return ""

def get_full_date_info():
    """
    Returns a dictionary with formatted date strings.
    Uses config.TIMEZONE_OFFSET to handle WIB/WITA/WIT automatically.
    """
    # Calculate local time based on UTC + Offset
    utc_now = datetime.datetime.utcnow()
    now = utc_now + datetime.timedelta(seconds=config.TIMEZONE_OFFSET)
    
    date_obj = now.date()
    
    # Standard Date (Indonesian)
    day_name = DAYS_ID[now.weekday()]
    month_name = MONTHS_ID[now.month]
    date_str = f"{day_name}, {now.day} {month_name} {now.year}"
    
    # Time
    time_str = now.strftime("%H:%M")
    
    # Javanese
    pasaran = get_javanese_pasaran(date_obj)
    javanese_str = f"{day_name} {pasaran}"
    
    # Hijri
    hijri_str = get_hijri_date(date_obj)
    
    return {
        "time": time_str,
        "date_gregorian": date_str,
        "date_javanese": javanese_str,
        "date_hijri": hijri_str,
        "timestamp": now # for checking update intervals
    }
