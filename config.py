"""Configuration for TenderGram - Telegram tender channel bot."""
import os

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")

POST_INTERVAL_SECONDS = 3.5
MAX_POSTS_PER_RUN = 25

# Visual cards: post each tender as an image card with caption (needs Pillow).
# Falls back to plain text automatically if Pillow is unavailable.
VISUAL_CARDS = True

# --- Storage ---
DB_PATH = os.environ.get("TENDERGRAM_DB", os.path.join(os.path.dirname(__file__), "tenders.db"))

# --- Region filter ---
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

ALL_COUNTRIES = {c for countries in REGIONS.values() for c in countries}

# Region accent colors for visual cards
REGION_COLORS = {
    "Turkey": "#C8102E",
    "CIS": "#1B5FAA",
    "Middle East": "#C77B0A",
    "Africa": "#1E7B45",
}

# --- Sector filter ---
ACCEPT_PROCUREMENT_GROUPS = {"CW"}

SECTOR_KEYWORDS = [
    "epc", "engineering, procurement", "design-build", "design and build",
    "construction", "civil works", "infrastructure", "turnkey",
    "road", "highway", "bridge", "tunnel", "railway", "metro",
    "pipeline", "power plant", "substation", "transmission line",
    "water treatment", "wastewater", "desalination", "sewerage", "irrigation",
    "building", "housing", "hospital construction", "airport", "port ",
    "dam ", "hydropower", "solar plant", "wind farm", "refinery",
    "supervision of works", "front end engineering", "feed study",
    "rehabilitation of", "renovation", "facade", "hvac", "mechanical works",
    "electrical works",
]

SKIP_NOTICE_TYPES = {"Contract Award"}
