"""Configuration for TenderGram - Telegram tender channel bot.

Set credentials via environment variables (preferred) or edit defaults here.
"""
import os

# --- Telegram ---
# Create a bot with @BotFather, then add it as an ADMIN to your channel.
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
# Channel username like "@cis_mea_tenders" or numeric id like "-1001234567890"
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")

# Seconds between posts (Telegram allows ~20 msgs/min per channel)
POST_INTERVAL_SECONDS = 3.5
# Max posts per run (safety valve so a first run doesn't flood the channel)
MAX_POSTS_PER_RUN = 25

# --- Storage ---
DB_PATH = os.environ.get("TENDERGRAM_DB", os.path.join(os.path.dirname(__file__), "tenders.db"))

# --- Region filter (country names as they appear in World Bank/UN data) ---
REGIONS = {
    "Turkey": ["Turkiye", "Turkey"],
    "CIS": [
        "Azerbaijan", "Armenia", "Belarus", "Georgia", "Kazakhstan",
        "Kyrgyz Republic", "Kyrgyzstan", "Moldova", "Russian Federation",
        "Tajikistan", "Turkmenistan", "Ukraine", "Uzbekistan",
    ],
    "Middle East": [
        "Saudi Arabia", "United Arab Emirates", "Qatar", "Kuwait", "Bahrain",
        "Oman", "Iraq", "Jordan", "Lebanon", "Syrian Arab Republic", "Yemen",
        "West Bank and Gaza", "Iran, Islamic Republic of",
    ],
    "Africa": [
        "Egypt, Arab Republic of", "Egypt", "Morocco", "Algeria", "Tunisia",
        "Libya", "Nigeria", "Kenya", "Ethiopia", "Tanzania", "Ghana",
        "Senegal", "Cote d'Ivoire", "Mozambique", "Angola", "Zambia",
        "Uganda", "Rwanda", "Cameroon", "Congo, Democratic Republic of",
        "South Africa", "Botswana", "Namibia", "Djibouti", "Sudan", "Somalia",
        "Mauritania", "Mali", "Niger", "Chad", "Benin", "Togo", "Guinea",
        "Burkina Faso", "Madagascar", "Malawi", "Zimbabwe",
    ],
}

# Flattened convenience set
ALL_COUNTRIES = {c for countries in REGIONS.values() for c in countries}

# --- Sector filter ---
# World Bank procurement_group codes to always accept: CW = Civil Works
ACCEPT_PROCUREMENT_GROUPS = {"CW"}

# Keyword match (case-insensitive) on tender title/description for non-CW notices
SECTOR_KEYWORDS = [
    "epc", "engineering, procurement", "design-build", "design and build",
    "construction", "civil works", "infrastructure", "turnkey",
    "road", "highway", "bridge", "tunnel", "railway", "metro",
    "pipeline", "power plant", "substation", "transmission line",
    "water treatment", "wastewater", "desalination", "sewerage", "irrigation",
    "building", "housing", "hospital construction", "airport", "port ",
    "dam ", "hydropower", "solar plant", "wind farm", "refinery",
    "supervision of works", "front end engineering", "feed study",
]

# Notice types to skip (set to empty set to allow all)
SKIP_NOTICE_TYPES = {"Contract Award"}
