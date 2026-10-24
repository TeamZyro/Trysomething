import re
from os import getenv
# ------------------------------------
# ------------------------------------
from dotenv import load_dotenv
from pyrogram import filters

import random

# ------------------------------------
# ------------------------------------
load_dotenv()
# ------------------------------------
# -----------------------------------------------------
API_ID = getenv("API_ID", "20366712")
API_HASH = getenv("API_HASH", "a05398c005f6381009a9bb5d55118842")

MUSIC_IMAGES = [
    "https://files.catbox.moe/g4mqt6.jpg",
    "https://files.catbox.moe/3tmmva.jpg"
]

def get_random_music_img():
    return random.choice(MUSIC_IMAGES)
# ------------------------------------

# -----------------------------------------------------
API_ID = getenv("API_ID", "20366712")
API_HASH = getenv("API_HASH", "a05398c005f6381009a9bb5d55118842")

EVAL = list(map(int, getenv("EVAL", "000000 0000000").split()))
# ------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", "8983557694:AAFSwlluFzKIKHnQ8XhFQVttRm_NE3AY2v8")
# --------------------------------------------------------
BOT_USERNAME = getenv("BOT_USERNAME" , "none")
# --------------------------------------------------------

#---------------------------------------------------------------
#---------------------------------------------------------------
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://mehermusic369_db_user:mehermusic@cluster0.t7miuqv.mongodb.net/?appName=Cluster0")
DB_NAME = getenv("DB_NAME", "WaifuZy1ro")
#---------------------------------------------------------------
# ----------------------------------------------------------------
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
# ----------------------------------------------------------------
# make your bots privacy from telegra.ph and put your url here 
PRIVACY_LINK = getenv("PRIVACY_LINK", "https://telegra.ph/Privacy-Policy-for-DAXXMUSIC-08-14")

# ----------------------------------------------------------------
# Chat id of a group for logging bot's activities
LOG_GROUP_ID  = int(getenv("LOGGER_ID", -1004394013188))
LOGGER_ID = LOG_GROUP_ID
# ----------------------------------------------------------------
# ----------------------------------------------------------------
OWNER_ID = int(getenv("OWNER_ID", 5719281608))
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# ----------------------------------------------------------------
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/TeamZyro/Trysomething",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # ----------------------------------------------------------------
# -------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
API_URL = getenv("API_URL", 'https://api.nexgenbots.xyz') #youtube song url
VIDEO_API_URL = getenv("VIDEO_API_URL", 'https://api.video.nexgenbots.xyz')
API_KEY = getenv("API_KEY", "30DxNexGenBotsda3c23")
API2_URL = getenv("API2_URL", "https://shrutibots.site")

# Shruti API
SHRUTI_API_URL = getenv("SHRUTI_API_URL", "https://api.shrutibots.site")
SHRUTI_API_KEYS = [
    "ShrutiBotsGFNPwZL0paMa6BEprQZK",
    "ShrutiBots1TUj0Zwi953Muk3Uo8rb",
    "ShrutiBotsOeVE7tBj4DTZe4bVaSTc",
]

# XBit API (New)
XBIT_API_KEY = getenv("XBIT_API_KEY", "xbit_U5YQ2yzGGd7syFGVNMgVa2Y7W-DJPn4E")
# ------------------------------------------------------------------------
# -------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/pittu_support")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/+wR6uIBDUF2w2YzI1")

SUPPORT_GROUP = SUPPORT_CHAT



# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True").lower() == "true"

AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")
# ----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
# ------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))
# --------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------



# ------------------------------------
# ------------------------------------
# ------------------------------------
# ------------------------------------
# Get your pyrogram v2 session from @StringFatherBot on Telegram
# Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING1 = getenv("STRING_SESSION", "BQE2xXgASfgU7AmhxXfyH7UMlXEiI3jVQAREyoWYeuQ9B2FDjGonu60MU0d-SdNcFYn4IflyMjCcqQCUNvJS2mOMnIEWwcaQFVjfHrm9YGcE65aI_moWhbKWECxfVqGhkPfIpbhalz_iTzcOYf1US2H3uaIKUspzd_laD2ttboA4LDCXqYcz_EJ00aMLbpeHE6YbSyIlkxiF9JTXviTvNdPh21ky2WpXy53OVc4PmiJtb3j1DOAqnpWj66WG83cF3Ib41MxNioJSjLvTukYZxAcFFXTJ2ug4PERtURYz9AxSHaPhOIr9uxZA-VSG884W9LN3VGu1TtXO-afZ2J34Li9nFos3HAAAAAH76MrBAA")
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

STRING6 = getenv("STRING_SESSION6", None)
STRING7 = getenv("STRING_SESSION7", None)
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# ------------------------------------
# ------------------------------------
# ------------------------------------
# ------------------------------------

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
START_IMG_URL = getenv(
    "START_IMG_URL", "https://files.catbox.moe/uxqcay.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://files.catbox.moe/uxqcay.jpg"
)
STATS_IMG_URL = "https://files.catbox.moe/uxqcay.jpg"
def __getattr__(name):
    if name in [
        "PLAYLIST_IMG_URL",
        "TELEGRAM_AUDIO_URL",
        "TELEGRAM_VIDEO_URL",
        "STREAM_IMG_URL",
        "SOUNCLOUD_IMG_URL",
        "YOUTUBE_IMG_URL",
        "SPOTIFY_ARTIST_IMG_URL",
        "SPOTIFY_ALBUM_IMG_URL",
        "SPOTIFY_PLAYLIST_IMG_URL",
    ]:
        return get_random_music_img()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")



# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_GROUP:
    if not re.match("(?:http|https)://", SUPPORT_GROUP):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )
# ---------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
