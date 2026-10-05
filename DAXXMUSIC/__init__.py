from DAXXMUSIC.core.bot import DAXX
from DAXXMUSIC.core.dir import dirr
from DAXXMUSIC.core.git import git
from DAXXMUSIC.core.userbot import Userbot
from DAXXMUSIC.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = DAXX()
api = SafoneAPI()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

# ------------------------------ IMPORTS ---------------------------------
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters as f
from config import BOT_TOKEN, OWNER_ID

# --------------------------- LOGGING SETUP ------------------------------
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)


import config 
# ---------------------------- CONSTANTS ---------------------------------
api_id = 28731656
api_hash = "22f05593e2f2f365ebc1fcc03446a8c8"

LOGGER_ID = -1002009280180
GROUP_ID = -1002009280180
CHARA_CHANNEL_ID = "hshig648kfnn"
mongo_url = "mongodb+srv://nibbanmisal3302:Gokukhan3303@cluster0.0u22b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
PHOTO_URL = ["https://files.catbox.moe/7ccoub.jpg", "https://files.catbox.moe/7ccoub.jpg"]
OWNER_ID = config.OWNER_ID
SUPPORT_CHAT = "+sjgJ4RzCA-w2OTE1"
UPDATE_CHAT = "Zyro_Network"

START_MEDIA = os.getenv("START_MEDIA", "https://files.catbox.moe/gknnju.jpg,https://files.catbox.moe/gknnju.jpg").split(',')


SUDO = [7577185215, 5749187175, 7498977788, 7392456702, 6382664842, 7921068157, 7078181502, 7577185215]



# --------------------- TELEGRAM BOT CONFIGURATION -----------------------
command_filter = f.create(lambda _, __, message: message.text and message.text.startswith("/"))

# -------------------------- DATABASE SETUP ------------------------------
ddw = AsyncIOMotorClient(mongo_url)
db = ddw['waifu_collector_bot']

# Collections
user_totals_collection = db['user_totals_lmaoooo']
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']
pm_users = db['total_pm_users']
destination_collection = db['user_collection_lmaoooo']
destination_char = db['anime_characters_lol']
winter_users = ddw['Oneforall_music']['winter_event_users'] # Event Collection

# -------------------------- GLOBAL VARIABLES ----------------------------
sudo_users = SUDO
collection = destination_char
user_collection = destination_collection
#--------------------------- STRIN ---------------------------------------

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
last_user = {}
warned_users = {}
user_cooldowns = {}
user_nguess_progress = {}
user_guess_progress = {}

# -------------------------- POWER SETUP --------------------------------
from DAXXMUSIC.unit.zyro_ban import *
from DAXXMUSIC.unit.zyro_sudo import *
from DAXXMUSIC.unit.zyro_react import *
from DAXXMUSIC.unit.zyro_log import *
from DAXXMUSIC.unit.zyro_send_img import *
#from DAXXMUSIC.unit.zyro_guess import *
from DAXXMUSIC.unit.zyro_rarity import *
# ------------------------------------------------------------------------

GLOG = "mlohvdryj"

async def PLOG(text: str):
    await app.send_message(
       chat_id=GLOG,
       text=text
   )

# ---------------------------- END OF CODE ------------------------------
