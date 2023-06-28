from decouple import config
try:
    ALLOWED_CHANNELS = config("ALLOWED_CHANNELS")
    APP_ID = config("APP_ID", default=6, cast=int)
    API_HASH = config("API_HASH", default="eb06d4abfb49dc3eeb1aeb98ae0f581e")
    BOT_TOKEN = config("BOT_TOKEN")
    PASSWD = config("PASSWORD", default="0")
    SUDO = config("SUDO")
except Exception:
    print("Something went wrong! or an important variable is missing check the below traceback for more info.")
    print(traceback.format_exc())
    exit()