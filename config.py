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
API_ID = getenv("API_ID", "22792918")
API_HASH = getenv("API_HASH", "ff10095d2bb96d43d6eb7a7d9fc85f81")

MUSIC_IMAGES = [
    "https://files.catbox.moe/g4mqt6.jpg",
    "https://files.catbox.moe/3tmmva.jpg"
]

def get_random_music_img():
    return random.choice(MUSIC_IMAGES)
# ------------------------------------

# -----------------------------------------------------
API_ID = getenv("API_ID", "22792918")
API_HASH = getenv("API_HASH", "ff10095d2bb96d43d6eb7a7d9fc85f81")

EVAL = list(map(int, getenv("EVAL", "000000 0000000").split()))
# ------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", "8269694220:AAET7rM8E-EMKNcH-9KhdZBrpvbphS8l110")
# --------------------------------------------------------
BOT_USERNAME = getenv("BOT_USERNAME" , "none")
# --------------------------------------------------------

#---------------------------------------------------------------
#---------------------------------------------------------------
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://nibbanmisal3302:Gokukhan3303@cluster0.0u22b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = getenv("DB_NAME", "WaifuZyro")
#---------------------------------------------------------------
# ----------------------------------------------------------------
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
# ----------------------------------------------------------------
# make your bots privacy from telegra.ph and put your url here 
PRIVACY_LINK = getenv("PRIVACY_LINK", "https://telegra.ph/Privacy-Policy-for-DAXXMUSIC-08-14")

# ----------------------------------------------------------------
# Chat id of a group for logging bot's activities
LOG_GROUP_ID  = int(getenv("LOGGER_ID", -1002009280180))
LOGGER_ID = LOG_GROUP_ID
# ----------------------------------------------------------------
# ----------------------------------------------------------------
OWNER_ID = int(getenv("OWNER_ID", 7078181502))
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# ----------------------------------------------------------------
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/TeamZyro/WAIFUMUSIC",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # ----------------------------------------------------------------
# -------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
API_URL = getenv("API_URL", 'https://api.nexgenbots.xyz') #youtube song url
VIDEO_API_URL = getenv("VIDEO_API_URL", 'https://api.video.nexgenbots.xyz')
API_KEY = getenv("API_KEY", "30DxNexGenBotsda3c23")
API2_URL = getenv("API2_URL", "https://shrutibots.site")

# XBit API (New)
XBIT_API_KEY = getenv("XBIT_API_KEY", "xbit_U5YQ2yzGGd7syFGVNMgVa2Y7W-DJPn4E")
# ------------------------------------------------------------------------
# -------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/Zyro_Network")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/oneforall_support")

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
STRING1 = getenv("STRING_SESSION", "BQFa2kUAa-djQHdik52oMVExmv1b1zdoMDMaf5L-5rf9IGPfavfvu9Fqj4Y4HUZAQtzAXDmYS06geVAJ3wzOLNWgVB1mEWQBjSDEjHiY5QC6rwYE9IKeaQI0BCz-Tham7kXe5g1XKpVvZQchldF2JbcW1OonO2DUTNfxIlm-zYQgzTqLceZBLXqIZfWPJ0kAHMuj44QYDVyc-ysHOQWI13Q0_q6DarKUcmODDfSM1ek_Oi2c8pOaQlYUUfrcRwRoaxnXM315UQWbxZF_eyvSuT4xY-RqiaWij7IWIHLZsfLZhvrR9EGPRwBcuYl0os7ti8WPQQG7RinC2Mh61Ijo6pQvtoCjeQAAAAG-B05oAA")
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
