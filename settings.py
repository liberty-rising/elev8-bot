import os
import logging

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Get environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL_INTROS = os.getenv("WEBHOOK_URL_INTROS")
WEBHOOK_URL_USERNAME_CHANGES = os.getenv("WEBHOOK_URL_USERNAME_CHANGES")
WEBHOOK_URL_TG_DATA_UPDATE = os.getenv("WEBHOOK_URL_TG_DATA_UPDATE")
AUTHORIZED_USER_IDS = list(map(int, os.getenv("AUTHORIZED_USER_IDS", "").split(",")))

# Logging
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOGGING_LEVEL)
)

# Elev8 Council Supergroup
ELEV8_COUNCIL_SUPERGROUP_ID = int(os.getenv("ELEV8_COUNCIL_SUPERGROUP_ID"))
INTRODUCTIONS_THREAD_ID = int(os.getenv("INTRODUCTIONS_THREAD_ID"))