import os
from dotenv import load_dotenv

load_dotenv()

# Bot token
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN .env faylida ko'rsatilmagan!")

# Admin ID lar
_raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = []
if _raw_admins:
    try:
        ADMIN_IDS = [int(x.strip()) for x in _raw_admins.split(",") if x.strip()]
    except ValueError:
        raise ValueError("❌ ADMIN_IDS noto'g'ri formatda! Mısalı: 123456,789012")

# Database
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database.db")

# School info
SCHOOL_NAME = "Abu Ali ibn Sino atındaǵı qánigelestirilgen mekteptiń Xojeli filialı"
