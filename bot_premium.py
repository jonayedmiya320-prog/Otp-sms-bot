"""
╔══════════════════════════════════════════════════════════════════╗
║          JAMES SHOP BOT — Professional Reply Keyboard UI        ║
║   aiogram 3.x  |  JSON DB  |  100% Reply Keyboard Navigation     ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import atexit
import html as html_lib
import io
import json
import logging
import os
import random
import re
import shutil
import signal
import sys
import threading
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests as _requests
import urllib.request as _urllib_request

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
import pyotp
import pytz
from aiohttp import web
from aiogram import BaseMiddleware, Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    Document,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    TelegramObject,
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# ╔══════════════════════════════════════════════════════════════════╗
# ║                CONFIGURATION — আপনার মান এখানে বসান           ║
# ╚══════════════════════════════════════════════════════════════════╝

# ── ১. Telegram ─────────────────────────────────────────────────────
BOT_TOKEN_VALUE          = "7907217678:AAHAmCLtMKr0JLK4g0b0cNX965nFtsBMXy8"
ADMIN_IDS_VALUE          = "7095358778"

# ── ২. ডাটাবেস (শুধু JSON ফাইল) ─────────────────────────────────────
# সব ডাটা একটাই JSON ফাইলে সেভ হবে। খালি রাখলে বটের ফোল্ডারের data/database.json ব্যবহার হবে।
DB_FILE_VALUE            = ""

# ── ৩. Optional ─────────────────────────────────────────────────────
FORCE_JOIN_CHANNEL_VALUE = ""
SUPPORT_USERNAME_VALUE   = ""

# ── ৪. Dongvan Mail API ─────────────────────────────────────────────
DONGVAN_API_KEY_VALUE    = "ChXbDXJGgQMYFwqYfRANwLc7i"

# ════════════════════════════════════════════════════════════════════
os.environ.setdefault("BOT_TOKEN",                BOT_TOKEN_VALUE)
os.environ.setdefault("ADMIN_IDS",                ADMIN_IDS_VALUE)
os.environ.setdefault("DB_FILE",                  DB_FILE_VALUE)
os.environ.setdefault("FORCE_JOIN_CHANNEL",       FORCE_JOIN_CHANNEL_VALUE)
os.environ.setdefault("SUPPORT_USERNAME",         SUPPORT_USERNAME_VALUE)
os.environ.setdefault("DONGVAN_API_KEY",          DONGVAN_API_KEY_VALUE)
# ════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
# UNICODE BOLD & FONT HELPER (Mathematical Sans-Serif Bold Italic)
# ══════════════════════════════════════════════════════════════════

def _b(text: str) -> str:
    """Convert ASCII letters/digits → Unicode Mathematical Sans-Serif Bold Italic (e.g. 𝙒𝙀𝙇𝘾𝙊𝙈𝙀, 𝘿𝙀𝙋𝙊𝙎𝙄𝙏).
    Emojis, spaces and punctuation are left as-is, so _b("Home") → "𝙃𝙤𝙢𝙚".
    """
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr(0x1D63C + ord(ch) - ord("A")))
        elif "a" <= ch <= "z":
            out.append(chr(0x1D656 + ord(ch) - ord("a")))
        elif "0" <= ch <= "9":
            out.append(chr(0x1D7EC + ord(ch) - ord("0")))
        else:
            out.append(ch)
    return "".join(out)


def _unb(text: str) -> str:
    """Decode styled Unicode bold/italic characters back to standard ASCII."""
    out = []
    for ch in text:
        cp = ord(ch)
        # Mathematical Sans-Serif Bold Italic Capital (𝙒 -> W)
        if 0x1D63C <= cp <= 0x1D655:
            out.append(chr(ord("A") + cp - 0x1D63C))
        # Mathematical Sans-Serif Bold Italic Small (𝙤 -> o)
        elif 0x1D656 <= cp <= 0x1D66F:
            out.append(chr(ord("a") + cp - 0x1D656))
        # Mathematical Sans-Serif Bold Capital (old style)
        elif 0x1D5D4 <= cp <= 0x1D5ED:
            out.append(chr(ord("A") + cp - 0x1D5D4))
        # Mathematical Sans-Serif Bold Small (old style)
        elif 0x1D5EE <= cp <= 0x1D607:
            out.append(chr(ord("a") + cp - 0x1D5EE))
        # Mathematical Sans-Serif Bold Digits
        elif 0x1D7EC <= cp <= 0x1D7F5:
            out.append(chr(ord("0") + cp - 0x1D7EC))
        else:
            out.append(ch)
    return "".join(out)


# ══════════════════════════════════════════════════════════════════
# PREMIUM EMOJI DATABASE
# ══════════════════════════════════════════════════════════════════

PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="6089346083274626176">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="6312301920123887895">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="6314398126157340467">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>',
    "reply": '<tg-emoji emoji-id="6311845322150652183">💬</tg-emoji>',
    "close": '<tg-emoji emoji-id="6311965254817423602">❌</tg-emoji>',
    "payment": '<tg-emoji emoji-id="6312344027983257537">💳</tg-emoji>',
    "approval": '<tg-emoji emoji-id="6311983130471308119">✅</tg-emoji>',
    "delete": '<tg-emoji emoji-id="6314398126157340467">🗑</tg-emoji>',
    "fire": '<tg-emoji emoji-id="6314080118188808371">🔥</tg-emoji>',
    "buy": '<tg-emoji emoji-id="6312234398943026185">🛒</tg-emoji>',
    "add": '<tg-emoji emoji-id="6312260233171312151">➕</tg-emoji>',
    "date": '<tg-emoji emoji-id="6314128625549450770">📅</tg-emoji>',
    "okay": '<tg-emoji emoji-id="6314082948572256406">👌</tg-emoji>',
    "1": '<tg-emoji emoji-id="5866189817481531778">1️⃣</tg-emoji>',
    "2": '<tg-emoji emoji-id="6089331218392813822">2️⃣</tg-emoji>',
    "3": '<tg-emoji emoji-id="5866206774012416141">3️⃣</tg-emoji>',
    "4": '<tg-emoji emoji-id="5866324451821358773">4️⃣</tg-emoji>',
    "5": '<tg-emoji emoji-id="5866474230215873258">5️⃣</tg-emoji>',
    "6": '<tg-emoji emoji-id="5866354903139487976">6️⃣</tg-emoji>',
    "7": '<tg-emoji emoji-id="5866208942970901081">7️⃣</tg-emoji>',
    "8": '<tg-emoji emoji-id="5866395366026384460">8️⃣</tg-emoji>',
    "down": '<tg-emoji emoji-id="6053169517905845173">⬇️</tg-emoji>',
    "mail": '<tg-emoji emoji-id="6053193097276298985">📨</tg-emoji>',
    "telegram": '<tg-emoji emoji-id="6109560346853251750">✈️</tg-emoji>',
    "confirm": '<tg-emoji emoji-id="6311983130471308119">✅</tg-emoji>',
    "time": '<tg-emoji emoji-id="6336809269802833182">⏱</tg-emoji>',
    "btn_click": '<tg-emoji emoji-id="6233136657722251031">🔘</tg-emoji>',
    "stock_off": '<tg-emoji emoji-id="5100657930429006538">🚫</tg-emoji>',
    "binance": '<tg-emoji emoji-id="6237610939902858402">🟡</tg-emoji>',
    "bkash": '<tg-emoji emoji-id="6237975191784266396">🟢</tg-emoji>',
    "nogod": '<tg-emoji emoji-id="6235336389647407554">🟠</tg-emoji>',
    "nagad": '<tg-emoji emoji-id="6235336389647407554">🟠</tg-emoji>',
    "diamond": '<tg-emoji emoji-id="5352838545826420397">💎</tg-emoji>',
    "gold": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "silver": '<tg-emoji emoji-id="5352638632278660622">🔹</tg-emoji>',
    "bronze": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "shield": '<tg-emoji emoji-id="5190447043545438788">🛡</tg-emoji>',
    "card": '<tg-emoji emoji-id="5190899075968441286">💳</tg-emoji>',
    "bell": '<tg-emoji emoji-id="5352980533150259581">🔔</tg-emoji>',
    "search": '<tg-emoji emoji-id="5463352748751753567">🔍</tg-emoji>',
    "history": '<tg-emoji emoji-id="5192739271886282680">📋</tg-emoji>',
    "support": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "bot": '<tg-emoji emoji-id="5352597830089347330">🤖</tg-emoji>',
    "online": '<tg-emoji emoji-id="5192812028632274956">🟢</tg-emoji>',
    "offline": '<tg-emoji emoji-id="5420130255174145507">🔴</tg-emoji>',
    "crown": '<tg-emoji emoji-id="5353032893096567467">👑</tg-emoji>',
    "package": '<tg-emoji emoji-id="5352721946054268944">📦</tg-emoji>',
    "coupon": '<tg-emoji emoji-id="5420396762189831222">🎟</tg-emoji>',
    "trending": '<tg-emoji emoji-id="6314080118188808371">🔥</tg-emoji>',
    "favorite": '<tg-emoji emoji-id="5352552689983067014">⭐</tg-emoji>',
    "vip": '<tg-emoji emoji-id="5352838545826420397">💎</tg-emoji>',
    "chart": '<tg-emoji emoji-id="5352877703043258544">📈</tg-emoji>',
    "key": '<tg-emoji emoji-id="5197288647275071607">🔑</tg-emoji>',
    "code": '<tg-emoji emoji-id="5337132498965010628">📲</tg-emoji>',
    "balance_low": '<tg-emoji emoji-id="5454125707300978880">⚠️</tg-emoji>',
    "live": '<tg-emoji emoji-id="6312004025487204067">🟢</tg-emoji>',
    "help_q": '<tg-emoji emoji-id="6312235051778056164">❓</tg-emoji>',
    "vpn_express": '<tg-emoji emoji-id="5814184382071574423">🛡</tg-emoji>',
    "vpn_ipvanish": '<tg-emoji emoji-id="5816876665141202258">🛡</tg-emoji>',
    "vpn_nord": '<tg-emoji emoji-id="5816931709442068156">🛡</tg-emoji>',
    "vpn_hotspot": '<tg-emoji emoji-id="5816437229857280693">🛡</tg-emoji>',
    "vpn_surfshark": '<tg-emoji emoji-id="5816864355764932607">🛡</tg-emoji>',
    "2fa_2": '<tg-emoji emoji-id="6089331218392813822">2️⃣</tg-emoji>',
    "2fa_f": '<tg-emoji emoji-id="6086887764253480137">🇫</tg-emoji>',
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "6312235051778056164",
    "❓": "6312235051778056164",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "6089346083274626176", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "6311983130471308119",
    "1️⃣": "5352651766288652742", "2️⃣": "6089331218392813822", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "6311965254817423602", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "6312260233171312151", "🗑": "6314398126157340467", "🎁": "6312301920123887895",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "6312344027983257537",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "6312004025487204067", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "🔍": "5463352748751753567", "🔑": "5197288647275071607"
}

def pem(key: str, fallback: str = "") -> str:
    """Return tg-emoji HTML tag for key or fallback."""
    if key in PEM:
        return PEM[key]
    if key in GLOBAL_BODY_EMOJIS:
        return f'<tg-emoji emoji-id="{GLOBAL_BODY_EMOJIS[key]}">{key}</tg-emoji>'
    return fallback or key



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════

def _csv_list(key: str) -> List[int]:
    raw = os.getenv(key, "").strip()
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


BOT_TOKEN            = os.environ["BOT_TOKEN"]
ADMIN_IDS: List[int] = _csv_list("ADMIN_IDS")
_RAILWAY_VOL = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "").strip()
DB_FILE             = (os.getenv("DB_FILE", "").strip()
                       or (str(Path(_RAILWAY_VOL) / "database.json") if _RAILWAY_VOL else "")
                       or str(Path(__file__).resolve().parent / "data" / "database.json"))

DONGVAN_API_KEY  = os.getenv("DONGVAN_API_KEY", DONGVAN_API_KEY_VALUE)

# Dongvan API endpoints
_DV_OAUTH2_URL     = "https://api.dongvanfb.net/api/getOauth2"
_DV_GET_CODE_URL   = "https://tools.dongvanfb.net/api/get_code_oauth2"
_DV_GET_MSGS_URL   = "https://tools.dongvanfb.net/api/get_messages_oauth2"
_DV_GRAPH_MSGS_URL = "https://tools.dongvanfb.net/api/graph_messages"

# In-memory mail sessions: uid -> {email, password, refresh_token, client_id}
_mail_sessions: Dict[int, Dict] = {}

WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL") or None
WEBHOOK_PATH   = os.getenv("WEBHOOK_PATH", "/webhook")
WEBAPP_HOST    = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT    = int(os.getenv("PORT") or os.getenv("WEBAPP_PORT", "8080"))

SPAM_COOLDOWN  = float(os.getenv("SPAM_COOLDOWN_SECONDS", "2"))
SPAM_MAX_MSGS  = int(os.getenv("SPAM_MAX_MESSAGES", "5"))
SPAM_WINDOW    = float(os.getenv("SPAM_WINDOW_SECONDS", "10"))
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@support")
WELCOME_MSG    = os.getenv("WELCOME_MESSAGE", "Welcome to our premium shop!")
DEFAULT_FORCE_JOIN = os.getenv("FORCE_JOIN_CHANNEL") or None

STOCK_EXPORT_GROUP_ID = -1004382561394
_stock_export_task: Optional[asyncio.Task] = None
_backup_task: Optional[asyncio.Task] = None

MAIL_SHOP_FILE = Path(__file__).parent / "My_Mail_Shop_Orders.xlsx"

_MAIL_SHEET_HEADERS = [
    "Order ID", "Date (UTC)", "User ID", "Username",
    "Product", "Qty", "Total ($)", "Items Delivered",
]
_HEADER_FONT  = Font(bold=True, color="FFFFFF")
_HEADER_FILL  = PatternFill("solid", fgColor="1F4E79")
_HEADER_ALIGN = Alignment(horizontal="center", vertical="center")


def _init_mail_shop_file() -> None:
    if MAIL_SHOP_FILE.exists():
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mail Orders"
    ws.append(_MAIL_SHEET_HEADERS)
    for cell in ws[1]:
        cell.font  = _HEADER_FONT
        cell.fill  = _HEADER_FILL
        cell.alignment = _HEADER_ALIGN
    ws.freeze_panes = "A2"
    wb.save(str(MAIL_SHOP_FILE))


def make_stock_template_xlsx(product_name: str) -> bytes:
    """Generate a blank xlsx template for admins to fill in stock accounts."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Stock"

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")
    eg_fill   = PatternFill("solid", fgColor="E2EFDA")

    ws.append(["Email", "Password"])
    for cell in ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    examples = [
        ("user1@gmail.com", "pass1234"),
        ("user2@gmail.com", "secret99"),
        ("user3@yahoo.com",  "hello456"),
    ]
    for row in examples:
        ws.append(list(row))
        for cell in ws[ws.max_row]:
            cell.fill = eg_fill

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 20
    ws.freeze_panes = "A2"

    note_row = ws.max_row + 2
    ws.cell(row=note_row, column=1, value="Replace example rows with real accounts. Keep Email in column A, Password in column B.")
    ws.cell(row=note_row, column=1).font = Font(italic=True, color="FF0000")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_stock_export_xlsx(product_name: str, stock_items: dict) -> bytes:
    """Export current stock items for a product to xlsx (admin download)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Stock"

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")
    alt_fill  = PatternFill("solid", fgColor="DCE6F1")

    ws.append(["#", "Email", "Password", "Raw"])
    for cell in ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    # Normalise: list-like data in edge cases
    if isinstance(stock_items, list):
        stock_items = {str(i): v for i, v in enumerate(stock_items)}

    for i, (key, item) in enumerate(stock_items.items(), 1):
        item_str = str(item).strip()
        if ":"in item_str:
            parts = item_str.split(":", 1)
            email, password = parts[0].strip(), parts[1].strip()
        else:
            email, password = item_str, ""
        ws.append([i, email, password, item_str])
        if i % 2 == 0:
            for cell in ws[ws.max_row]:
                cell.fill = alt_fill

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 25
    ws.column_dimensions["D"].width = 65
    ws.freeze_panes = "A2"

    info_sheet = wb.create_sheet("Info")
    info_sheet.append(["Product", product_name])
    info_sheet.append(["Total Items", len(stock_items)])
    info_sheet.append(["Exported At", time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())])
    info_sheet.append([])
    info_sheet.append(["Note", "Column D (Raw) contains the original account string. Use this column when re-importing."])
    info_sheet.column_dimensions["A"].width = 18
    info_sheet.column_dimensions["B"].width = 65

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_all_stock_export_xlsx(products: dict, all_stocks: dict) -> bytes:
    """Export stock for ALL products into a single multi-sheet xlsx file."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")
    alt_fill  = PatternFill("solid", fgColor="DCE6F1")

    summary_ws = wb.create_sheet("Summary")
    summary_ws.append(["Product", "Category", "Stock Count", "Exported At"])
    for cell in summary_ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    for pid, product in products.items():
        pname    = product.get("name", pid)
        category = product.get("category", "mail")
        stock    = all_stocks.get(pid) or {}
        summary_ws.append([pname, category.upper(), len(stock), time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())])

        safe_title = re.sub(r"[\\/*?:\[\]]", "", pname)[:28] or pid[:28]
        ws = wb.create_sheet(safe_title)
        ws.append(["#", "Email", "Password", "Raw"])
        for cell in ws[1]:
            cell.font      = hdr_font
            cell.fill      = hdr_fill
            cell.alignment = hdr_align
        # Normalise: list-like data in edge cases
        if isinstance(stock, list):
            stock = {str(i): v for i, v in enumerate(stock)}
        for i, (key, item) in enumerate(stock.items(), 1):
            item_str = str(item).strip()
            if ":"in item_str:
                parts = item_str.split(":", 1)
                email, password = parts[0].strip(), parts[1].strip()
            else:
                email, password = item_str, ""
            ws.append([i, email, password, item_str])
            if i % 2 == 0:
                for cell in ws[ws.max_row]:
                    cell.fill = alt_fill
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 35
        ws.column_dimensions["C"].width = 25
        ws.column_dimensions["D"].width = 65
        ws.freeze_panes = "A2"

    for col in ["A", "B", "C", "D"]:
        summary_ws.column_dimensions[col].width = 25

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_user_order_xlsx(
    order_id: str, product_name: str, qty: int, total: float, items: List[str]
) -> bytes:
    """Build an in-memory xlsx of the user's purchased mail accounts."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Your Order"

    info_font  = Font(bold=True)
    hdr_font   = Font(bold=True, color="FFFFFF")
    hdr_fill   = PatternFill("solid", fgColor="1F4E79")
    hdr_align  = Alignment(horizontal="center", vertical="center")
    alt_fill   = PatternFill("solid", fgColor="DCE6F1")

    for label, value in [
        ("Order ID",    order_id),
        ("Product",     product_name),
        ("Quantity",    qty),
        ("Total Paid",  f"${total:.2f}"),
    ]:
        ws.append([label, value])
        ws.cell(row=ws.max_row, column=1).font = info_font

    ws.append([])
    ws.append(["#", "Account"])
    hdr_row = ws.max_row
    for cell in ws[hdr_row]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    for i, item in enumerate(items, 1):
        ws.append([i, item])
        if i % 2 == 0:
            for cell in ws[ws.max_row]:
                cell.fill = alt_fill

    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 55
    ws.freeze_panes = f"A{hdr_row + 1}"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_products_xlsx(products: dict, all_stocks: dict = None) -> bytes:
    """Export all products to an xlsx file for admin download.
    If all_stocks is provided, also creates per-product stock sheets."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Products"

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")

    headers = ["Name", "Emoji", "Category", "Price (USD)", "Delivery Mode", "Hidden", "Stock Count"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    alt_fill = PatternFill("solid", fgColor="DCE6F1")
    for i, (pid, p) in enumerate(products.items(), 1):
        row = [
            p.get("name", ""),
            p.get("emoji", ""),
            p.get("category", "mail"),
            p.get("price", 0.0),
            p.get("delivery_mode", "manual"),
            "yes"if p.get("hidden") else "no",
            p.get("stock_count", 0),
        ]
        ws.append(row)
        if i % 2 == 0:
            for cell in ws[ws.max_row]:
                cell.fill = alt_fill

    col_widths = [30, 10, 12, 14, 16, 10, 14]
    for col_idx, width in enumerate(col_widths, 1):
        ws.column_dimensions[ws.cell(1, col_idx).column_letter].width = width
    ws.freeze_panes = "A2"

    # Per-product stock sheets
    if all_stocks:
        used_sheet_names = set()
        for pid, product in products.items():
            stock = all_stocks.get(pid) or {}
            if not stock:
                continue
            pname = product.get("name", pid)
            safe_title = re.sub(r"[\\/*?:\[\]]", "", pname)[:28] or pid[:28]
            # Handle sheet-name collisions
            original_title = safe_title
            counter = 2
            while safe_title.lower() in used_sheet_names:
                suffix = f"({counter})"
                safe_title = original_title[:28 - len(suffix)] + suffix
                counter += 1
            used_sheet_names.add(safe_title.lower())
            stock_ws = wb.create_sheet(safe_title)
            stock_ws.append(["#", "Email", "Password", "Raw"])
            for cell in stock_ws[1]:
                cell.font      = hdr_font
                cell.fill      = hdr_fill
                cell.alignment = hdr_align
            if isinstance(stock, list):
                stock = {str(i): v for i, v in enumerate(stock)}
            for idx, (key, item) in enumerate(stock.items(), 1):
                item_str = str(item).strip()
                if ":"in item_str:
                    parts = item_str.split(":", 1)
                    email, password = parts[0].strip(), parts[1].strip()
                else:
                    email, password = item_str, ""
                stock_ws.append([idx, email, password, item_str])
                if idx % 2 == 0:
                    for cell in stock_ws[stock_ws.max_row]:
                        cell.fill = alt_fill
            stock_ws.column_dimensions["A"].width = 6
            stock_ws.column_dimensions["B"].width = 35
            stock_ws.column_dimensions["C"].width = 25
            stock_ws.column_dimensions["D"].width = 65
            stock_ws.freeze_panes = "A2"

    # Instructions sheet
    ws2 = wb.create_sheet("Import Guide")
    ws2.append(["Import Guide — How to add products via file"])
    ws2.append([])
    ws2.append(["Column", "Description", "Allowed Values"])
    for cell in ws2[3]:
        cell.font = Font(bold=True)
    guide = [
        ("Name",          "Product name",                                   "Any text"),
        ("Emoji",         "Product emoji icon",                             "Any emoji, e.g.   "),
        ("Category",      "Product type",                                   "mail / vpn / proxy"),
        ("Price (USD)",   "Price per unit / per day",                       "Number, e.g. 1.50"),
        ("Delivery Mode", "How product is delivered (proxy only)",           "manual / auto"),
        ("Hidden",        "Whether product is visible to users",             "yes / no"),
    ]
    for row in guide:
        ws2.append(list(row))
    for col in ["A", "B", "C"]:
        ws2.column_dimensions[col].width = 25

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def parse_products_xlsx(content: bytes) -> List[dict]:
    """Parse an xlsx/csv file and return a list of product dicts to import.
    Also parses per-product stock sheets and attaches stock_items to each product."""
    results = []
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception:
        return results

    if not rows:
        return results

    # Detect header row
    header = [str(c).strip().lower() if c else ""for c in rows[0]]
    col = {}
    for i, h in enumerate(header):
        if "name"in h:
            col["name"] = i
        elif "emoji"in h:
            col["emoji"] = i
        elif "cat"in h:
            col["category"] = i
        elif "price"in h:
            col["price"] = i
        elif "delivery"in h or "mode"in h:
            col["delivery_mode"] = i
        elif "hidden"in h:
            col["hidden"] = i

    if "name"not in col or "price"not in col:
        return results

    for row in rows[1:]:
        if not row or not row[col["name"]]:
            continue
        name  = str(row[col["name"]]).strip()
        if not name:
            continue
        try:
            price = float(str(row[col["price"]]).replace("$", "").strip())
        except Exception:
            continue
        emoji    = str(row[col["emoji"]]).strip() if "emoji"in col and row[col["emoji"]] else ""
        category = str(row[col["category"]]).strip().lower() if "category"in col and row[col["category"]] else "mail"
        if category not in ("mail", "vpn", "proxy"):
            category = "mail"
        delivery = str(row[col["delivery_mode"]]).strip().lower() if "delivery_mode"in col and row[col["delivery_mode"]] else "manual"
        if delivery not in ("manual", "auto"):
            delivery = "manual"
        hidden_v = str(row[col["hidden"]]).strip().lower() if "hidden"in col and row[col["hidden"]] else "no"
        hidden   = hidden_v in ("yes", "true", "1")
        results.append({
            "name": name, "emoji": emoji, "category": category,
            "price": round(price, 4), "delivery_mode": delivery, "hidden": hidden,
            "stock_items": [],
        })

    # Parse per-product stock sheets (match by product name)
    product_names = {p["name"].lower(): p for p in results}
    skip_sheets = {"products", "import guide", "summary"}
    for sheet_name in wb.sheetnames:
        if sheet_name.lower() in skip_sheets:
            continue
        try:
            stock_ws = wb[sheet_name]
            stock_rows = list(stock_ws.iter_rows(values_only=True))
        except Exception:
            continue
        if not stock_rows:
            continue
        # Try to match sheet name to a product
        matched_product = product_names.get(sheet_name.strip().lower())
        if not matched_product:
            # Try partial match
            for pname_lower, prod in product_names.items():
                if pname_lower[:28].rstrip() == sheet_name.strip().lower()[:28].rstrip():
                    matched_product = prod
                    break
        if not matched_product:
            continue
        # Parse stock rows - look for Raw or Email column
        stock_header = [str(c).strip().lower() if c else ""for c in stock_rows[0]]
        raw_col = None
        email_col = None
        pass_col = None
        for si, sh in enumerate(stock_header):
            if "raw"in sh:
                raw_col = si
            elif "email"in sh:
                email_col = si
            elif "password"in sh or "pass"in sh:
                pass_col = si
        for srow in stock_rows[1:]:
            if not srow:
                continue
            if raw_col is not None and srow[raw_col]:
                item_str = str(srow[raw_col]).strip()
                if item_str:
                    matched_product["stock_items"].append(item_str)
            elif email_col is not None and srow[email_col]:
                email = str(srow[email_col]).strip()
                if pass_col is not None and srow[pass_col]:
                    password = str(srow[pass_col]).strip()
                    matched_product["stock_items"].append(f"{email}:{password}")
                else:
                    matched_product["stock_items"].append(email)

    return results


def append_to_mail_shop_file(
    order_id: str, uid: int, username: str,
    product_name: str, qty: int, total: float,
    items: List[str], ts: int,
) -> None:
    _init_mail_shop_file()
    wb = openpyxl.load_workbook(str(MAIL_SHOP_FILE))
    ws = wb.active
    date_s  = time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts))
    items_s = "\n".join(items) if items else ""
    ws.append([order_id, date_s, uid, username, product_name, qty, round(total, 2), items_s])
    # Refresh column widths
    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)
    wb.save(str(MAIL_SHOP_FILE))

HOME_BTN   = _b("Home")
BACK_BTN   = _b("Back")
CANCEL_BTN = _b("Cancel")

# ── User menu ──────────────────────────────────────────────────────
BTN_BALANCE  = _b("Balance")
BTN_GET_MAIL   = _b("Get Mail")
BTN_TEMP_MAIL  = _b("Temp Mail")
BTN_BUY_VPN  = _b("Buy VPN")
BTN_BUY_PROXY= _b("Buy Proxy")
BTN_DEPOSIT  = _b("Deposit")
BTN_GET_CODE = _b("Get Code")
BTN_GET_2FA  = _b("Get 2FA")

# ── Get Code Sub-menu ───────────────────────────────────────────────
BTN_GC_SET_MAIL = _b("Set Mail")
BTN_GC_CODES    = _b("Get Codes")
BTN_GC_INBOX    = _b("Read Inbox")
BTN_GC_REFRESH  = _b("Refresh Inbox")
BTN_GC_FILTER   = _b("Filter Mail")
BTN_GC_CHANGE   = _b("Change Mail")
BTN_HISTORY  = _b("Order History")
BTN_SUPPORT  = _b("Support")
BTN_AI_SUPPORT = _b("AI Support")
BTN_REFERRAL = _b("Referral")

# ── AI Support FAQ Topics ──────────────────────────────────────────
BTN_AI_HOW_BUY     = _b("How to Buy")
BTN_AI_HOW_DEPOSIT = _b("How to Deposit")
BTN_AI_STOCK       = _b("Check Stock")
BTN_AI_REFERRAL    = _b("Referral Info")
BTN_AI_ORDERS      = _b("My Orders")
BTN_AI_2FA         = _b("2FA Help")
BTN_AI_MAIL        = _b("Mail Codes")
BTN_AI_ASK         = _b("Ask a Question")
BTN_CONFIRM  = _b("Confirm Purchase")
BTN_COUPON   = _b("Apply Coupon")

# ── User Panel Enhancement buttons ────────────────────────────────
BTN_TRENDING    = _b("Trending")
BTN_FAVORITES   = _b("Favorites")
BTN_MY_STATS    = _b("My Stats")
BTN_SEARCH      = _b("Search")
BTN_MORE        = _b("More")

# ── Duration ───────────────────────────────────────────────────────
BTN_1DAY   = _b("1 Day")
BTN_7DAYS  = _b("7 Days")
BTN_30DAYS = _b("30 Days")
BTN_90DAYS = _b("90 Days")
BTN_CUSTOM = _b("Custom")

# ── Deposit methods ────────────────────────────────────────────────
BTN_BKASH   = _b("bKash")
BTN_NAGAD   = _b("Nagad")
BTN_BINANCE = _b("Binance")

# ── Admin menu ─────────────────────────────────────────────────────
BTN_ADM_DASHBOARD     = _b("Dashboard")
BTN_ADM_PRODUCTS      = _b("Products")
BTN_ADM_STOCK         = _b("Stock")
BTN_ADM_USERS         = _b("Users")
BTN_ADM_DEPOSITS      = _b("Deposits")
BTN_ADM_VPN_ORDERS    = _b("VPN Orders")
BTN_ADM_PROXY_ORDERS  = _b("Proxy Orders")
BTN_ADM_COUPONS       = _b("Coupons")
BTN_ADM_BROADCAST     = _b("Broadcast")
BTN_ADM_SETTINGS      = _b("Settings")
BTN_ADM_EXPORT        = _b("Export Mail Orders")
BTN_ADM_PROXY_PKGS    = _b("Data Packages")
BTN_ADM_ORDER_LOOKUP  = _b("Order Lookup")
BTN_ADM_ANALYTICS     = _b("Analytics")
BTN_PKG_ADD           = _b("Add Package")

# ── Admin sub-menu buttons ─────────────────────────────────────────
BTN_ADM_ORDERS_MENU   = _b("Orders")
BTN_ADM_REPORTS_MENU  = _b("Reports")
BTN_ADM_TOOLS_MENU    = _b("Tools")

# ── Admin panel enhancements (FEAT-002) ────────────────────────────
BTN_ADM_LOW_STOCK     = _b("Low Stock Alerts")
BTN_ADM_ROLES         = _b("Admin Roles")
BTN_ADM_EXPORT_TX     = _b("Export Transactions")
BTN_ADM_STATUS_MGR    = _b("Service Status")
BTN_ADM_PROFIT        = _b("Profit Calculator")
BTN_ADM_LOGS          = _b("Activity Logs")
BTN_ADM_PRICE_SYNC    = _b("Price Sync")
BTN_ADM_AUTO_IMPORT   = _b("Auto Import")

# ── Admin product actions ──────────────────────────────────────────
BTN_EDIT_NAME   = _b("Edit Name")
BTN_EDIT_PRICE  = _b("Edit Price")
BTN_EDIT_EMOJI  = _b("Edit Emoji")
BTN_EDIT_DESC   = _b("Edit Description")
BTN_HIDE_PROD          = _b("Hide Product")
BTN_SHOW_PROD          = _b("Show Product")
BTN_DELETE             = _b("Delete")
BTN_ADD_PRODUCT        = _b("Add Product")
BTN_DOWNLOAD_PRODUCTS  = _b("Download Products")
BTN_IMPORT_PRODUCTS    = _b("Import Products")
BTN_ADD_STOCK   = _b("Add Stock")

# ── Admin stock actions ────────────────────────────────────────────
BTN_UPLOAD_FILE      = _b("Upload File")
BTN_MANUAL_ADD       = _b("Manual Add")
BTN_CLEAR_STOCK      = _b("Clear Stock")
BTN_GET_TEMPLATE     = _b("Download Template")
BTN_DOWNLOAD_STOCK     = _b("Download Stock")
BTN_DOWNLOAD_ALL_STOCK = _b("Download All Stock")
BTN_IMPORT_ALL_STOCK   = _b("Import All Stock")

# ── Admin user actions ─────────────────────────────────────────────
BTN_BAN_USER    = _b("Ban User")
BTN_UNBAN_USER  = _b("Unban User")
BTN_ADD_BAL     = _b("Add Balance")
BTN_REMOVE_BAL  = _b("Remove Balance")
BTN_ADD_BONUS   = _b("Add Bonus")
BTN_REMOVE_BONUS = _b("Remove Bonus")
BTN_BONUS_ALL_USERS = _b("Bonus All Users")
BTN_BONUS_TOP10 = _b("Bonus Top 10")
BTN_SEARCH_USER = _b("Search User")

# ── Admin coupon actions ───────────────────────────────────────────
BTN_DELETE_COUPON = _b("Delete Coupon")
BTN_CREATE_COUPON = _b("Create Coupon")

# ── Categories ─────────────────────────────────────────────────────
BTN_CAT_MAIL  = _b("Mail (Auto Delivery)")
BTN_CAT_VPN   = _b("VPN (Manual)")
BTN_CAT_PROXY = _b("Proxy (Auto+Manual)")

# ── Proxy delivery mode toggle ──────────────────────────────────────
BTN_TOGGLE_AUTO   = _b("Set Auto Delivery")
BTN_TOGGLE_MANUAL = _b("Set Manual Delivery")


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ══════════════════════════════════════════════════════════════════
# DATABASE — JSON file store (single JSON file)
# ══════════════════════════════════════════════════════════════════

def _jcopy(v: Any) -> Any:
    """Fast deep copy for JSON-like data (dict / list / scalars)."""
    t = type(v)
    if t is dict:
        return {k: _jcopy(x) for k, x in v.items()}
    if t is list:
        return [_jcopy(x) for x in v]
    return v


def _jclean(v: Any) -> Any:
    """Copy + normalise a value like a realtime tree DB:
    string keys, None / empty dict / empty list are dropped."""
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            x = _jclean(x)
            if x is not None:
                out[str(k)] = x
        return out or None
    if isinstance(v, (list, tuple)):
        out = [_jclean(x) for x in v]
        return out if any(x is not None for x in out) else None
    return v


class JsonDB:
    """Tiny path-based database (path based get/set/update/push) that keeps
    everything in memory and persists it to ONE json file.

    * writes are atomic (temp file + fsync + os.replace)
    * saves are coalesced in a background thread (<1s after a change)
    * a .bak copy is refreshed every 10 minutes
    * a lock file prevents two bot processes from using the same file
    """

    _PUSH_CHARS = "-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"

    def __init__(self, file_path: str):
        self.path = Path(file_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._bak = Path(str(self.path) + ".bak")
        self._lock = threading.RLock()
        self._wake = threading.Event()
        self._closed = False
        self._dirty = False
        self._last_bak = 0.0
        self._last_push_ms = 0
        self._last_rand = [0] * 12
        self._lock_fh = None
        self._acquire_process_lock()
        self._data: Dict[str, Any] = self._load()
        self._writer = threading.Thread(target=self._writer_loop, name="jsondb-writer", daemon=True)
        self._writer.start()
        atexit.register(self.flush)

    # ── process lock ────────────────────────────────────────────────
    def _acquire_process_lock(self) -> None:
        try:
            import fcntl  # not available on Windows
        except ImportError:
            return
        try:
            fh = open(str(self.path) + ".lock", "w")
        except OSError:
            return
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(
                f"Another bot instance is already running and using {self.path}. "
                f"Stop it first (two bots must never share one database file)."
            )
        except OSError:
            return  # filesystem without lock support — continue without it
        self._lock_fh = fh

    # ── load / save ─────────────────────────────────────────────────
    @staticmethod
    def _read_file(p: Path) -> Dict[str, Any]:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("database root must be a JSON object")
        return data

    def _load(self) -> Dict[str, Any]:
        if self.path.exists() and self.path.stat().st_size > 0:
            try:
                data = self._read_file(self.path)
                logger.info("JsonDB loaded: %s (%d top-level keys)", self.path, len(data))
                return data
            except Exception as e:
                logger.error("JsonDB: %s is unreadable (%s)", self.path, e)
                if self._bak.exists():
                    try:
                        data = self._read_file(self._bak)
                        logger.error("JsonDB: restored from backup copy %s", self._bak)
                        return data
                    except Exception as e2:
                        logger.error("JsonDB: backup copy unreadable too (%s)", e2)
                broken = self.path.with_name(self.path.name + f".corrupt-{int(time.time())}")
                try:
                    self.path.replace(broken)
                    logger.critical("JsonDB: broken file moved to %s — starting EMPTY", broken)
                except OSError:
                    pass
        else:
            logger.info("JsonDB: new empty database at %s", self.path)
        return {}

    def _touch(self) -> None:
        self._dirty = True
        self._wake.set()

    def _write_now(self) -> None:
        with self._lock:
            if not self._dirty:
                return
            payload = json.dumps(self._data, ensure_ascii=False,
                                 separators=(",", ":"), default=str)
            self._dirty = False
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            now = time.time()
            if self.path.exists() and now - self._last_bak > 600:
                try:
                    shutil.copy2(self.path, self._bak)
                    self._last_bak = now
                except OSError:
                    pass
            os.replace(tmp, self.path)
        except Exception:
            with self._lock:
                self._dirty = True
            logger.exception("JsonDB: save failed")

    def _writer_loop(self) -> None:
        while not self._closed:
            self._wake.wait(timeout=5)
            if self._closed:
                break
            self._wake.clear()
            time.sleep(0.3)          # coalesce bursts of writes
            self._write_now()

    def flush(self) -> None:
        """Write pending changes to disk right now."""
        try:
            self._write_now()
        except Exception:
            logger.exception("JsonDB: flush failed")

    def close(self) -> None:
        self._closed = True
        self._wake.set()
        self.flush()
        if self._lock_fh is not None:
            try:
                self._lock_fh.close()
            except OSError:
                pass
            self._lock_fh = None

    # ── path helpers ────────────────────────────────────────────────
    @staticmethod
    def _parts(path: str) -> List[str]:
        return [p for p in str(path).split("/") if p]

    def _node(self, parts: List[str]) -> Any:
        node: Any = self._data
        for k in parts:
            if isinstance(node, dict):
                node = node.get(k)
            elif isinstance(node, list) and k.isdigit() and int(k) < len(node):
                node = node[int(k)]
            else:
                return None
            if node is None:
                return None
        return node

    @classmethod
    def _set_in(cls, node: Any, parts: List[str], value: Any) -> Any:
        if not parts:
            return value
        if isinstance(node, list):
            node = {str(i): v for i, v in enumerate(node) if v is not None}
        elif not isinstance(node, dict):
            node = {}
        key = parts[0]
        child = cls._set_in(node.get(key), parts[1:], value)
        if child is None:
            node.pop(key, None)
        else:
            node[key] = child
        return node or None

    # ── public API ──────────────────────────────────────────────────
    def get(self, path: str) -> Any:
        with self._lock:
            return _jcopy(self._node(self._parts(path)))

    def exists(self, path: str) -> bool:
        with self._lock:
            return self._node(self._parts(path)) is not None

    def set(self, path: str, value: Any) -> None:
        parts = self._parts(path)
        value = _jclean(value)
        with self._lock:
            if not parts:
                self._data = value if isinstance(value, dict) else {}
            else:
                self._data = self._set_in(self._data, parts, value) or {}
            self._touch()

    def update(self, path: str, data: dict) -> None:
        base = self._parts(path)
        with self._lock:
            for k, v in (data or {}).items():
                sub = self._parts(k)
                if not sub:
                    continue
                self._data = self._set_in(self._data, base + sub, _jclean(v)) or {}
            self._touch()

    def delete(self, path: str) -> None:
        self.set(path, None)

    def _next_push_id(self) -> str:
        now = int(time.time() * 1000)
        dup = now == self._last_push_ms
        self._last_push_ms = now
        chars = self._PUSH_CHARS
        ts = []
        for _ in range(8):
            ts.append(chars[now % 64])
            now //= 64
        out = "".join(reversed(ts))
        if not dup:
            self._last_rand = [random.randint(0, 63) for _ in range(12)]
        else:
            i = 11
            while i >= 0 and self._last_rand[i] == 63:
                self._last_rand[i] = 0
                i -= 1
            if i >= 0:
                self._last_rand[i] += 1
        return out + "".join(chars[c] for c in self._last_rand)

    def push(self, path: str, data: Any) -> str:
        with self._lock:
            key = self._next_push_id()
            self.set(f"{path}/{key}", data)
            return key

    def incr(self, path: str, by: int = 1) -> int:
        with self._lock:
            cur = self._node(self._parts(path))
            new = (cur if isinstance(cur, (int, float)) and not isinstance(cur, bool) else 0) + by
            self.set(path, new)
            return new


_db = JsonDB(DB_FILE)


def _on_term_signal(signum, frame):  # make sure nothing is lost on kill / stop
    _db.flush()
    sys.exit(0)


try:
    signal.signal(signal.SIGTERM, _on_term_signal)
except (ValueError, OSError, AttributeError):
    pass


async def _run(fn, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))


async def _safe_delete(msg) -> None:
    try:
        await msg.delete()
    except Exception:
        pass


def _session_has_oauth2(session: dict) -> bool:
    return bool(session.get("refresh_token") and session.get("client_id"))


def _truncate_msg(text: str, limit: int = 3900) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n<i>… (truncated, too long)</i>"


# ══════════════════════════════════════════════════════════════════
# DATABASE — Generic helpers
# ══════════════════════════════════════════════════════════════════

async def db_get(path: str) -> Any:
    return _db.get(path)

async def db_set(path: str, data: Any) -> None:
    _db.set(path, data)

async def db_update(path: str, data: dict) -> None:
    _db.update(path, data)

async def db_push(path: str, data: Any) -> str:
    return _db.push(path, data)

async def db_delete(path: str) -> None:
    _db.delete(path)


_ID_COLLECTIONS = {"PRD": "products", "ORD": "orders", "VPN": "vpn_orders", "PXY": "proxy_orders"}


async def generate_id(prefix: str) -> str:
    """Generate a human-friendly incrementing ID like ORD-0001, PRD-001.
    Skips any ID that already exists (safe after importing an old database)."""
    coll = _ID_COLLECTIONS.get(prefix)
    while True:
        n = _db.incr(f"counters/{prefix}")
        new_id = f"{prefix}-{n:03d}" if prefix == "PRD" else f"{prefix}-{n:04d}"
        if not coll or not _db.exists(f"{coll}/{new_id}"):
            return new_id


# ══════════════════════════════════════════════════════════════════
# DATABASE — Users
# ══════════════════════════════════════════════════════════════════

async def get_user(uid: int) -> Optional[dict]:
    return await db_get(f"users/{uid}")

async def get_all_users() -> Dict[str, dict]:
    return await db_get("users") or {}

async def create_or_update_user(uid: int, username: str, full_name: str) -> dict:
    existing = await get_user(uid)
    if existing:
        await db_update(f"users/{uid}", {"username": username, "full_name": full_name})
        return {**existing, "username": username, "full_name": full_name}
    data = {
        "user_id": uid, "username": username, "full_name": full_name,
        "balance": 0.0, "is_banned": False, "joined_at": int(time.time()),
        "total_spent": 0.0, "order_count": 0,
        "referral": {"referred_by": None, "referred_count": 0, "total_earned": 0.0},
    }
    await db_set(f"users/{uid}", data)
    return data

async def update_balance(uid: int, delta: float) -> float:
    user = await get_user(uid)
    new_bal = round((user.get("balance") or 0) + delta, 4)
    await db_update(f"users/{uid}", {"balance": new_bal})
    return new_bal

async def ban_user(uid: int, banned: bool) -> None:
    await db_update(f"users/{uid}", {"is_banned": banned})


async def get_bonus(uid: int) -> dict:
    bonus = await db_get(f"users/{uid}/bonus")
    if not bonus:
        return {"amount": 0.0, "allowed_products": []}
    return {
        "amount": bonus.get("amount", 0.0),
        "allowed_products": bonus.get("allowed_products", []),
    }


async def set_bonus(uid: int, amount: float, allowed_products: list) -> None:
    await db_set(f"users/{uid}/bonus", {"amount": amount, "allowed_products": allowed_products})


async def use_bonus(uid: int, amount: float) -> float:
    bonus = await get_bonus(uid)
    new_amount = round(max(bonus["amount"] - amount, 0), 4)
    await db_update(f"users/{uid}/bonus", {"amount": new_amount})
    return new_amount


def compute_bonus_usage(bonus: dict, pid: str, total: float) -> tuple:
    """Return (bonus_used, remaining_cost) for a purchase."""
    bonus_used = 0.0
    allowed = bonus.get("allowed_products", [])
    if ("*"in allowed or pid in allowed) and bonus.get("amount", 0) > 0:
        if bonus["amount"] >= total:
            bonus_used = total
        else:
            bonus_used = bonus["amount"]
    remaining_cost = round(total - bonus_used, 4)
    return bonus_used, remaining_cost

async def get_totp_secret(uid: int) -> Optional[str]:
    user = await get_user(uid)
    return user.get("totp_secret") if user else None

async def set_totp_secret(uid: int, secret: str) -> None:
    await db_update(f"users/{uid}", {"totp_secret": secret})


# ── Referral helpers ───────────────────────────────────────────────

async def get_referral_info(uid: int) -> dict:
    data = await db_get(f"users/{uid}/referral")
    if not data:
        return {"referred_by": None, "referred_count": 0, "total_earned": 0.0}
    return {
        "referred_by": data.get("referred_by"),
        "referred_count": data.get("referred_count", 0),
        "total_earned": data.get("total_earned", 0.0),
    }


async def set_referrer(uid: int, referrer_uid: int) -> None:
    await db_update(f"users/{uid}/referral", {
        "referred_by": referrer_uid,
        "referred_count": 0,
        "total_earned": 0.0,
    })
    ref_info = await get_referral_info(referrer_uid)
    new_count = ref_info.get("referred_count", 0) + 1
    await db_update(f"users/{referrer_uid}/referral", {"referred_count": new_count})


async def add_referral_earning(referrer_uid: int, amount: float, from_uid: int, order_id: str) -> None:
    await db_push(f"users/{referrer_uid}/referral_earnings", {
        "amount": amount,
        "from_uid": from_uid,
        "order_id": order_id,
        "ts": int(time.time()),
    })
    ref_info = await get_referral_info(referrer_uid)
    new_total = round(ref_info.get("total_earned", 0.0) + amount, 4)
    await db_update(f"users/{referrer_uid}/referral", {"total_earned": new_total})



async def pay_referral_commission(bot: Bot, buyer_uid: int, purchase_amount: float, order_id: str) -> None:
    """Credit referral bonus to the referrer after purchase.

    The referrer earns a Bonus Balance (not real money) that can only
    be used as a discount on future purchases.
    """
    try:
        ref_info = await get_referral_info(buyer_uid)
        referrer_uid = ref_info.get("referred_by")
        if referrer_uid:
            settings = await get_settings()
            bonus_pct = settings.get("referral_bonus_pct", 5.0)
            commission = round(purchase_amount * bonus_pct / 100, 4)
            if commission > 0:
                # Credit referrer's BONUS balance (not real money)
                current_bonus = await get_bonus(referrer_uid)
                new_amount = round(current_bonus["amount"] + commission, 4)
                existing_allowed = current_bonus.get("allowed_products", [])
                if "*"not in existing_allowed:
                    existing_allowed = existing_allowed + ["*"]
                await set_bonus(referrer_uid, new_amount, existing_allowed)
                await add_referral_earning(referrer_uid, commission, buyer_uid, order_id)
                try:
                    await bot.send_message(
                        referrer_uid,
                        f"{pem('gift')} <b>✦ Referral Bonus Earned! ✦</b>\n{_SEP}\n"
                        f"  Your referral just made a purchase! 🎉\n"
                        f"{_LINE}\n"
                        f"  {pem('money')} Bonus Added ‣ <b>${commission:.2f}</b>\n"
                        f"  ‣ Use it as a discount on your next purchase!",
                    )
                except Exception:
                    pass
    except Exception as _ref_err:
        logger.warning("Referral commission failed: %s", _ref_err)


# ══════════════════════════════════════════════════════════════════
# DATABASE — Settings
# ══════════════════════════════════════════════════════════════════

_DEFAULT_SETTINGS = {
    "usd_rate": 125.0,
    "bkash_number": "", "nagad_number": "", "binance_uid": "",
    "bkash_min": 100.0, "nagad_min": 150.0, "binance_min": 5.0,
    "support_username": SUPPORT_USERNAME,
    "welcome_message": WELCOME_MSG,
    "force_join_channel": "",
    "force_join_channel_2": "",
    "low_stock_threshold": 5,
    "get_2fa_link": "",
    "shop_name": "Neroxa Shop",
    "proxy_data_options": "1 GB,5 GB,10 GB,50 GB",
    "stock_export_interval": 30,
    "referral_bonus_pct": 5.0,
    "maintenance_mode": "OFF",
    "maintenance_message": "\ud83d\udd27 Bot is under maintenance. Please try again later.",
    "backup_interval_hours": 24,
}

async def get_settings() -> dict:
    data = await db_get("settings")
    if not data:
        await db_set("settings", _DEFAULT_SETTINGS)
        return dict(_DEFAULT_SETTINGS)
    return {**_DEFAULT_SETTINGS, **data}

async def update_settings(updates: dict) -> None:
    await db_update("settings", updates)


# ══════════════════════════════════════════════════════════════════
# DATABASE — Products
# ══════════════════════════════════════════════════════════════════

async def get_all_products() -> Dict[str, dict]:
    return await db_get("products") or {}

async def get_product(pid: str) -> Optional[dict]:
    return await db_get(f"products/{pid}")

async def create_product(name: str, price: float, emoji: str = "", category: str = "mail",
                         delivery_mode: str = "manual", hidden: bool = False,
                         description: str = "") -> str:
    pid = await generate_id("PRD")
    await db_set(f"products/{pid}", {
        "name": name, "price": price, "emoji": emoji, "category": category,
        "delivery_mode": delivery_mode, "hidden": hidden, "description": description,
        "stock_count": 0, "created_at": int(time.time()), "total_sold": 0,
    })
    return pid

async def update_product(pid: str, updates: dict) -> None:
    await db_update(f"products/{pid}", updates)

async def delete_product(pid: str) -> None:
    await db_delete(f"products/{pid}")
    await db_delete(f"stocks/{pid}")

async def get_service_products(category: str) -> Dict[str, dict]:
    all_p = await get_all_products()
    return {k: v for k, v in all_p.items() if v.get("category") == category and not v.get("hidden")}


# ══════════════════════════════════════════════════════════════════
# DATABASE — Stock  (BUG FIX: item reassignment inside loop)
# ══════════════════════════════════════════════════════════════════

async def add_stock_items(pid: str, items: List[str], bot=None) -> int:
    """Add items to stock. Returns number of items actually added."""
    existing = await db_get(f"stocks/{pid}") or {}
    before = len(existing)
    was_empty = before == 0
    for raw_item in items:
        cleaned = raw_item.strip()
        if cleaned:
            existing[uuid.uuid4().hex[:16]] = cleaned
    await db_set(f"stocks/{pid}", existing)
    count = len(existing)
    # Always unhide the product when stock is added
    update_data = {"stock_count": count}
    if count > 0:
        update_data["hidden"] = False
    await db_update(f"products/{pid}", update_data)
    added = count - before
    # Notify restock subscribers if product was out of stock
    if was_empty and added > 0 and bot:
        asyncio.create_task(_notify_restock_subscribers(pid, bot))
    return added  # Return actually added count, not total


async def _notify_restock_subscribers(pid: str, bot) -> None:
    """Notify users who subscribed to restock notifications for this product."""
    try:
        product = await get_product(pid)
        if not product:
            return
        subscribers = await get_restock_subscribers(pid)
        if not subscribers:
            return
        name = product.get("name", "Unknown")
        emoji = product.get("emoji", "")
        stock = product.get("stock_count", 0)
        for uid in subscribers:
            try:
                await bot.send_message(
                    uid,
                    f"{pem('bell')} <b>✦ Back In Stock! ✦</b>\n{_SEP}\n"
                    f"  {emoji} <b>{name}</b> is now available again!\n"
                    f"{_LINE}\n"
                    f"  {pem('num')} Units Available ‣ <b>{stock}</b>\n"
                    f"  ⚡ Limited stock — order now before it sells out!",
                )
            except Exception:
                pass
        await clear_restock_subscribers(pid)
    except Exception as e:
        logger.warning("Restock notification failed: %s", e)

async def pop_stock_items(pid: str, qty: int) -> List[str]:
    existing = await db_get(f"stocks/{pid}") or {}
    keys = list(existing.keys())[:qty]
    popped = [existing[k] for k in keys]
    for k in keys:
        del existing[k]
    await db_set(f"stocks/{pid}", existing)
    new_count = len(existing)
    await db_update(f"products/{pid}", {"stock_count": new_count})
    return popped

async def clear_stock(pid: str) -> None:
    await db_delete(f"stocks/{pid}")
    await db_update(f"products/{pid}", {"stock_count": 0})

async def get_stock_count(pid: str) -> int:
    data = await db_get(f"stocks/{pid}")
    return len(data) if data else 0


# ══════════════════════════════════════════════════════════════════
# DATABASE — Activity Logs (FEAT-002)
# ══════════════════════════════════════════════════════════════════

async def log_admin_action(admin_id: int, action: str, details: str = "") -> None:
    """Log an admin action to activity_logs/."""
    await db_push("activity_logs", {
        "admin_id": admin_id,
        "action": action,
        "details": details,
        "timestamp": int(time.time()),
    })


async def get_activity_logs(limit: int = 20, offset: int = 0) -> List[dict]:
    """Get recent activity logs sorted by timestamp descending."""
    data = await db_get("activity_logs") or {}
    logs = [{**v, "log_id": k} for k, v in data.items()]
    logs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return logs[offset:offset + limit]


# ══════════════════════════════════════════════════════════════════
# DATABASE — Admin Roles (FEAT-002)
# ══════════════════════════════════════════════════════════════════

async def get_admin_role(uid: int) -> str:
    """Get admin role. Returns 'owner'for ADMIN_IDS, checks the database for others."""
    if uid in ADMIN_IDS:
        role = await db_get(f"admin_roles/{uid}")
        if role:
            return role.get("role", "owner") if isinstance(role, dict) else str(role)
        return "owner"
    role_data = await db_get(f"admin_roles/{uid}")
    if role_data:
        return role_data.get("role", "none") if isinstance(role_data, dict) else str(role_data)
    return "none"


async def set_admin_role(uid: int, role: str) -> None:
    """Set admin role in the database."""
    await db_set(f"admin_roles/{uid}", {"role": role, "updated_at": int(time.time())})


async def get_all_admin_roles() -> Dict[str, dict]:
    """Get all admin roles from the database."""
    return await db_get("admin_roles") or {}


def check_role_permission(role: str, action: str) -> bool:
    """Check if a role has permission for an action.
    owner: full access
    admin: full access except role management
    moderator: view-only, no destructive actions
    """
    if role == "owner":
        return True
    if role == "admin":
        return action != "manage_roles"
    if role == "moderator":
        return action in ("view_dashboard", "view_analytics", "view_users",
                          "view_orders", "view_logs", "view_products")
    return False


# ══════════════════════════════════════════════════════════════════
# DATABASE — Orders
# ══════════════════════════════════════════════════════════════════

async def create_order(uid: int, pid: str, product_name: str,
                       qty: int, total_price: float, items: List[str]) -> str:
    oid = await generate_id("ORD")
    await db_set(f"orders/{oid}", {
        "user_id": uid, "product_id": pid, "product_name": product_name,
        "qty": qty, "total_price": total_price, "items": items,
        "status": "delivered", "created_at": int(time.time()),
    })
    u = await get_user(uid) or {}
    await db_update(f"users/{uid}", {
        "total_spent": round((u.get("total_spent") or 0) + total_price, 4),
        "order_count": (u.get("order_count") or 0) + 1,
    })
    prod = await get_product(pid) or {}
    await db_update(f"products/{pid}", {
        "total_sold": (prod.get("total_sold") or 0) + qty,
    })
    return oid

async def get_user_orders(uid: int) -> List[dict]:
    data = await db_get("orders")
    if not data:
        return []
    return sorted(
        [{**v, "order_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# DATABASE — VPN Orders
# ══════════════════════════════════════════════════════════════════

async def create_vpn_order(uid: int, username: str, pid: str,
                           product_name: str, duration_days: int, price: float) -> str:
    u = await get_user(uid) or {}
    await db_update(f"users/{uid}", {
        "total_spent": round((u.get("total_spent") or 0) + price, 4),
        "order_count": (u.get("order_count") or 0) + 1,
    })
    prod = await get_product(pid) or {}
    await db_update(f"products/{pid}", {
        "total_sold": (prod.get("total_sold") or 0) + 1,
    })
    oid = await generate_id("VPN")
    await db_set(f"vpn_orders/{oid}", {
        "user_id": uid, "username": username, "product_id": pid,
        "product_name": product_name, "duration_days": duration_days,
        "price": price, "status": "pending", "created_at": int(time.time()),
    })
    return oid

async def update_vpn_order(oid: str, updates: dict) -> None:
    await db_update(f"vpn_orders/{oid}", updates)

async def get_pending_vpn_orders() -> List[dict]:
    data = await db_get("vpn_orders")
    if not data:
        return []
    return [{**v, "order_id": k} for k, v in data.items() if v.get("status") == "pending"]

async def get_user_vpn_orders(uid: int) -> List[dict]:
    data = await db_get("vpn_orders")
    if not data:
        return []
    return sorted(
        [{**v, "order_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# DATABASE — Proxy Orders
# ══════════════════════════════════════════════════════════════════

async def create_proxy_order(uid: int, username: str, pid: str,
                             product_name: str, duration_days, price: float,
                             items: Optional[List[str]] = None) -> str:
    delivery_mode = "auto"if items else "manual"
    status        = "delivered"if delivery_mode == "auto"else "pending"
    u = await get_user(uid) or {}
    await db_update(f"users/{uid}", {
        "total_spent": round((u.get("total_spent") or 0) + price, 4),
        "order_count": (u.get("order_count") or 0) + 1,
    })
    prod = await get_product(pid) or {}
    await db_update(f"products/{pid}", {
        "total_sold": (prod.get("total_sold") or 0) + 1,
    })
    oid = await generate_id("PXY")
    await db_set(f"proxy_orders/{oid}", {
        "user_id": uid, "username": username, "product_id": pid,
        "product_name": product_name, "duration_days": duration_days,
        "price": price, "status": status, "delivery_mode": delivery_mode,
        "items": items or [], "created_at": int(time.time()),
    })
    return oid

async def update_proxy_order(oid: str, updates: dict) -> None:
    await db_update(f"proxy_orders/{oid}", updates)

async def get_pending_proxy_orders() -> List[dict]:
    data = await db_get("proxy_orders")
    if not data:
        return []
    return [{**v, "order_id": k} for k, v in data.items() if v.get("status") == "pending"]

async def get_user_proxy_orders(uid: int) -> List[dict]:
    data = await db_get("proxy_orders")
    if not data:
        return []
    return sorted(
        [{**v, "order_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# DATABASE — Deposits
# ══════════════════════════════════════════════════════════════════

async def create_deposit(uid: int, username: str, method: str,
                         amount_bdt: float, amount_usd: float,
                         trx_id: str, screenshot_url: str) -> str:
    return await db_push("deposits", {
        "user_id": uid, "username": username, "method": method,
        "amount_bdt": amount_bdt, "amount_usd": amount_usd,
        "trx_id": trx_id, "screenshot_url": screenshot_url,
        "status": "pending", "created_at": int(time.time()),
    })

async def get_deposit(dep_id: str) -> Optional[dict]:
    return await db_get(f"deposits/{dep_id}")

async def update_deposit(dep_id: str, updates: dict) -> None:
    await db_update(f"deposits/{dep_id}", updates)

async def get_pending_deposits() -> List[dict]:
    data = await db_get("deposits")
    if not data:
        return []
    return sorted(
        [{**v, "deposit_id": k} for k, v in data.items() if v.get("status") == "pending"],
        key=lambda x: x.get("created_at", 0),
    )

async def check_trx_duplicate(trx_id: str) -> bool:
    data = await db_get("deposits")
    if not data:
        return False
    return any(v.get("trx_id") == trx_id for v in data.values())

async def get_user_deposits(uid: int) -> List[dict]:
    data = await db_get("deposits")
    if not data:
        return []
    return sorted(
        [{**v, "deposit_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# DATABASE — Coupons
# ══════════════════════════════════════════════════════════════════

async def get_coupon(code: str) -> Optional[dict]:
    data = await db_get("coupons")
    if not data:
        return None
    for k, v in data.items():
        if v.get("code", "").upper() == code.upper():
            return {**v, "coupon_id": k}
    return None

async def create_coupon(code: str, discount_pct: float, max_uses: int, expires_at: int) -> str:
    return await db_push("coupons", {
        "code": code.upper(), "discount_pct": discount_pct,
        "max_uses": max_uses, "used_count": 0, "expires_at": expires_at, "active": True,
    })

async def use_coupon(coupon_id: str) -> None:
    c = await db_get(f"coupons/{coupon_id}")
    used = (c.get("used_count") or 0) + 1
    await db_update(f"coupons/{coupon_id}", {
        "used_count": used,
        "active": used < c.get("max_uses", 1),
    })

async def get_all_coupons() -> List[dict]:
    data = await db_get("coupons")
    return [{**v, "coupon_id": k} for k, v in data.items()] if data else []

async def delete_coupon(coupon_id: str) -> None:
    await db_delete(f"coupons/{coupon_id}")


# ══════════════════════════════════════════════════════════════════
# DATABASE — VIP System
# ══════════════════════════════════════════════════════════════════

_VIP_TIERS = [
    (500, "Diamond", pem("diamond")),
    (200, "Gold", pem("gold")),
    (50, "Silver", pem("silver")),
    (10, "Bronze", pem("bronze")),
]


def get_vip_tier(total_spent: float) -> Tuple[str, str]:
    """Return (tier_name, emoji) based on total_spent. Returns ('', '') if no tier."""
    for threshold, name, emoji in _VIP_TIERS:
        if total_spent >= threshold:
            return name, emoji
    return "", ""


def get_vip_progress(total_spent: float) -> Tuple[str, float, float]:
    """Return (next_tier_name, current_spent, next_threshold) for progress display."""
    for i, (threshold, name, _emoji) in enumerate(_VIP_TIERS):
        if total_spent >= threshold:
            if i == 0:
                return "Max", total_spent, threshold
            prev_threshold = _VIP_TIERS[i - 1][0]
            return _VIP_TIERS[i - 1][1], total_spent, prev_threshold
    return "Bronze", total_spent, 10.0


# ══════════════════════════════════════════════════════════════════
# DATABASE — Favorites
# ══════════════════════════════════════════════════════════════════

async def get_user_favorites(uid: int) -> List[str]:
    """Return list of product IDs favorited by user."""
    data = await db_get(f"users/{uid}/favorites")
    if not data:
        return []
    if isinstance(data, dict):
        return list(data.keys())
    return list(data) if isinstance(data, list) else []


async def add_user_favorite(uid: int, pid: str) -> None:
    await db_set(f"users/{uid}/favorites/{pid}", True)


async def remove_user_favorite(uid: int, pid: str) -> None:
    await db_delete(f"users/{uid}/favorites/{pid}")


# ══════════════════════════════════════════════════════════════════
# DATABASE — Restock Notifications
# ══════════════════════════════════════════════════════════════════

async def subscribe_restock(pid: str, uid: int) -> None:
    await db_set(f"restock_subs/{pid}/{uid}", int(time.time()))


async def unsubscribe_restock(pid: str, uid: int) -> None:
    await db_delete(f"restock_subs/{pid}/{uid}")


async def get_restock_subscribers(pid: str) -> List[int]:
    data = await db_get(f"restock_subs/{pid}")
    if not data:
        return []
    return [int(uid) for uid in data.keys()]


async def clear_restock_subscribers(pid: str) -> None:
    await db_delete(f"restock_subs/{pid}")


# ══════════════════════════════════════════════════════════════════
# DATABASE — Stats & Storage
# ══════════════════════════════════════════════════════════════════

async def get_dashboard_stats() -> dict:
    users, orders, vpn, proxy, deposits = await asyncio.gather(
        db_get("users"), db_get("orders"),
        db_get("vpn_orders"), db_get("proxy_orders"), db_get("deposits"),
    )
    rev = (
        sum(v.get("total_price", 0) for v in (orders or {}).values()) +
        sum(v.get("price", 0) for v in (vpn or {}).values() if v.get("status") == "delivered") +
        sum(v.get("price", 0) for v in (proxy or {}).values() if v.get("status") == "delivered")
    )
    return {
        "total_users":      len(users) if users else 0,
        "total_revenue":    round(rev, 2),
        "total_sales":      len(orders or {}),
        "pending_deposits": sum(1 for v in (deposits or {}).values() if v.get("status") == "pending"),
        "pending_orders":   (
            sum(1 for v in (vpn or {}).values() if v.get("status") == "pending") +
            sum(1 for v in (proxy or {}).values() if v.get("status") == "pending")
        ),
    }


async def get_analytics_data() -> dict:
    users, orders, vpn, proxy, products = await asyncio.gather(
        db_get("users"), db_get("orders"),
        db_get("vpn_orders"), db_get("proxy_orders"), db_get("products"),
    )
    orders = orders or {}
    vpn = vpn or {}
    proxy = proxy or {}
    users = users or {}
    products = products or {}

    now = int(time.time())
    today_start = now - (now % 86400)
    week_start = now - 7 * 86400
    month_start = now - 30 * 86400

    all_orders = []
    for v in orders.values():
        all_orders.append((v.get("created_at", 0), v.get("total_price", 0)))
    for v in vpn.values():
        if v.get("status") == "delivered":
            all_orders.append((v.get("created_at", 0), v.get("price", 0)))
    for v in proxy.values():
        if v.get("status") == "delivered":
            all_orders.append((v.get("created_at", 0), v.get("price", 0)))

    today_rev = 0.0
    today_count = 0
    week_rev = 0.0
    week_count = 0
    month_rev = 0.0
    month_count = 0

    for created_at, price in all_orders:
        if created_at >= today_start:
            today_rev += price
            today_count += 1
        if created_at >= week_start:
            week_rev += price
            week_count += 1
        if created_at >= month_start:
            month_rev += price
            month_count += 1

    top_products = sorted(
        [(k, v.get("name", k), v.get("total_sold", 0)) for k, v in products.items()],
        key=lambda x: x[2], reverse=True,
    )[:5]

    top_buyers = sorted(
        [(uid, u.get("username", ""), u.get("total_spent", 0)) for uid, u in users.items()],
        key=lambda x: x[2], reverse=True,
    )[:5]

    return {
        "today_rev": round(today_rev, 2),
        "today_count": today_count,
        "week_rev": round(week_rev, 2),
        "week_count": week_count,
        "month_rev": round(month_rev, 2),
        "month_count": month_count,
        "top_products": top_products,
        "top_buyers": top_buyers,
    }


# ══════════════════════════════════════════════════════════════════
# STOCK FILE PARSER  (BUG FIX: robust xlsx parsing)
# ══════════════════════════════════════════════════════════════════

def _norm(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if ","in line and ":"not in line:
        parts = line.split(",", 1)
        return ":".join(p.strip() for p in parts)
    return line


def parse_stock_file(content: bytes, filename: str) -> List[str]:
    fname = (filename or "").lower()

    if fname.endswith(".xlsx"):
        items: List[str] = []
        try:
            wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            ws = wb.active
            if ws is None:
                logger.warning("XLSX: no active sheet found")
                return []
            first_row = True
            for row in ws.iter_rows(values_only=True):
                # FIX: filter None, convert to str, strip whitespace
                cols = [str(c).strip() for c in row if c is not None and str(c).strip() not in ("", "None")]
                # Skip header row
                if first_row:
                    first_row = False
                    if any(c.lower() in ("email", "password", "account", "mail", "#", "no.", "number", "pass", "username", "login") for c in cols):
                        continue
                if len(cols) >= 2:
                    items.append(f"{cols[0]}:{cols[1]}")
                elif len(cols) == 1:
                    items.append(cols[0])
            wb.close()
        except Exception as e:
            logger.error("XLSX parse error: %s", e)
            raise ValueError(f"Cannot read xlsx file: {e}") from e
        return [i for i in items if i.strip()]

    if fname.endswith(".csv"):
        items = []
        try:
            text = content.decode("utf-8-sig", errors="replace")  # FIX: handle BOM
        except Exception:
            text = content.decode("latin-1", errors="replace")
        first_row = True
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            parts = [p for p in parts if p]
            # Skip header row
            if first_row:
                first_row = False
                if any(p.lower() in ("email", "password", "account", "mail", "#", "no.", "number", "pass", "username", "login") for p in parts):
                    continue
            if len(parts) >= 2:
                items.append(f"{parts[0]}:{parts[1]}")
            elif len(parts) == 1:
                items.append(parts[0])
        return [i for i in items if i]

    # Plain text (.txt or unknown)
    try:
        text = content.decode("utf-8-sig", errors="replace")
    except Exception:
        text = content.decode("latin-1", errors="replace")
    _header_kw = ("email", "password", "account", "mail", "#", "no.", "number", "pass", "username", "login")
    items = []
    first_row = True
    for ln in text.splitlines():
        normed = _norm(ln)
        if not normed:
            continue
        if first_row:
            first_row = False
            parts = [p.strip().lower() for p in normed.replace(":", ",").split(",") if p.strip()]
            if any(p in _header_kw for p in parts):
                continue
        items.append(normed)
    return items


# ══════════════════════════════════════════════════════════════════
# DONGVAN MAIL API — Service detection & helpers
# ══════════════════════════════════════════════════════════════════

_DV_SERVICE_KEYWORDS: Dict[str, List[str]] = {
    "FACEBOOK":  ["security@facebookmail.com", "facebook", "fb"],
    "INSTAGRAM": ["instagram", "mail@instagram.com"],
    "TWITTER":   ["twitter", "x.com", "notify@twitter.com"],
    "GOOGLE":    ["google", "gmail", "youtube", "no-reply@google.com"],
    "APPLE":     ["apple", "icloud", "no-reply@apple.com"],
    "TIKTOK":    ["tiktok", "douyin"],
    "AMAZON":    ["amazon", "shipment-tracking@amazon.com"],
    "SHOPEE":    ["shopee"],
    "TELEGRAM":  ["telegram"],
    "KAKAOTALK": ["kakao"],
    "LAZADA":    ["lazada"],
    "WECHAT":    ["wechat", "weixin"],
    "OUTLOOK":   ["outlook", "microsoft", "hotmail", "no-reply@microsoft.com"],
    "LINKEDIN":  ["linkedin"],
    "NETFLIX":   ["netflix"],
    "DISCORD":   ["discord"],
    "SNAPCHAT":  ["snapchat"],
    "GARENA":    ["garena", "account@garena.com"],
    "COINBASE":  ["coinbase"],
    "BINANCE":   ["binance"],
}
_DV_SERVICE_LIST = list(_DV_SERVICE_KEYWORDS.keys())


def _dv_determine_service(subject: str = "", sender_name: str = "", sender_address: str = "") -> str:
    text = f"{subject} {sender_name} {sender_address}".lower()
    for svc, keywords in _DV_SERVICE_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            return svc
    return "UNKNOWN"


def _dv_extract_codes(messages_data: Optional[dict]) -> List[dict]:
    found: List[dict] = []
    if not messages_data or not messages_data.get("status") or not messages_data.get("messages"):
        return found
    _CODE_PATTERNS = [
        r'(\d{4,8})\s+is your',
        r'[Cc]ode[:\s]+(\d{4,8})',
        r'[Cc]onfirmation code[:\s]*(\d{4,8})',
        r'[Vv]erification code[:\s]*(\d{4,8})',
        r'OTP[:\s]*(\d{4,8})',
        r'mã xác nhận[:\s]*(\d{4,8})',
        r'is\s+(\d{4,8})\s',
        r'security code[:\s]*(\d{4,8})',
    ]
    for msg in messages_data["messages"]:
        subject  = msg.get("subject", "") or ""
        body     = msg.get("message", "") or ""
        from_f   = msg.get("from")
        sname    = from_f[0].get("name", "") if from_f and isinstance(from_f, list) and from_f else ""
        saddr    = from_f[0].get("address", "") if from_f and isinstance(from_f, list) and from_f else ""
        code     = msg.get("code", "") or ""
        if not code:
            combined = subject + " " + body[:2000]
            for pattern in _CODE_PATTERNS:
                m = re.search(pattern, combined)
                if m:
                    code = m.group(1)
                    break
        if code:
            found.append({
                "code": code, "service": _dv_determine_service(subject, sname, saddr),
                "sender": sname, "address": saddr, "subject": subject,
                "date": msg.get("date", "") or "", "uid": msg.get("uid", "") or "",
            })
    return found


def _dv_parse_input(text: str) -> dict:
    parts = text.strip().split("|")
    result = {"email": None, "password": None, "refresh_token": None, "client_id": None, "has_oauth2": False}
    if len(parts) >= 2:
        result["email"]    = parts[0].strip()
        result["password"] = parts[1].strip()
    if len(parts) >= 4:
        result["refresh_token"] = parts[2].strip()
        result["client_id"]     = parts[3].strip()
        result["has_oauth2"]    = True
    return result


async def _dv_oauth2(email: str, password: str) -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_OAUTH2_URL, json={"email": email, "password": password, "apikey": DONGVAN_API_KEY}, timeout=30)
            d = r.json()
            if d.get("status") and "oauth2"in d:
                parts = d["oauth2"].split("|")
                if len(parts) >= 2:
                    return {"refresh_token": parts[0], "client_id": parts[1]}
        except Exception as e:
            logger.error("DV oauth2 error: %s", e)
        return None
    return await _run(_call)


async def _dv_get_messages(email: str, rt: str, cid: str) -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_GET_MSGS_URL, json={"email": email, "refresh_token": rt, "client_id": cid, "list_mail": "all"}, timeout=30)
            return r.json()
        except Exception as e:
            logger.error("DV get_messages error: %s", e)
            return None
    return await _run(_call)


async def _dv_get_code(email: str, rt: str, cid: str, code_type: str = "all") -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_GET_CODE_URL, json={"email": email, "refresh_token": rt, "client_id": cid, "type": code_type}, timeout=30)
            return r.json()
        except Exception as e:
            logger.error("DV get_code error: %s", e)
            return None
    return await _run(_call)


async def _dv_graph_messages(email: str, rt: str, cid: str) -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_GRAPH_MSGS_URL, json={"email": email, "refresh_token": rt, "client_id": cid, "list_mail": "all"}, timeout=30)
            return r.json()
        except Exception as e:
            logger.error("DV graph_messages error: %s", e)
            return None
    return await _run(_call)


async def _dv_process_mailbox(session: dict) -> List[dict]:
    email, rt, cid = session["email"], session["refresh_token"], session["client_id"]
    msgs = await _dv_get_messages(email, rt, cid)
    if msgs and msgs.get("status") and msgs.get("messages"):
        return _dv_extract_codes(msgs)
    msgs = await _dv_graph_messages(email, rt, cid)
    if msgs and msgs.get("status") and msgs.get("messages"):
        return _dv_extract_codes(msgs)
    return []


def _dv_build_codes_display(messages: List[dict]) -> str:
    if not messages:
        return "No codes found in mailbox."
    by_svc: Dict[str, List[dict]] = {}
    for m in messages:
        by_svc.setdefault(m["service"], []).append(m)
    out = f"{_SEP}\n{pem('mail')} <b>CODES FOUND</b>\n{_SEP}\n\n"
    for svc, msgs in by_svc.items():
        out += f"<b>{svc}</b>\n"
        for m in msgs:
            out += f"├─ <code>{html_lib.escape(m['code'])}</code>\n"
            out += f"└─ {html_lib.escape(m['subject'][:60])}\n"
        out += "\n"
    out += f"{_SEP}\n{pem('file')} <b>COPY:</b>\n"
    for svc, msgs in by_svc.items():
        for m in msgs:
            out += f"<code>{svc} → {html_lib.escape(m['code'])}</code>\n"
    return out


def _dv_build_mailbox_display(messages: List[dict], filter_service: Optional[str] = None) -> str:
    filtered = [m for m in messages if m["service"] == filter_service.upper()] if filter_service else messages
    title    = f"{pem('search')} Filter: <b>{filter_service.upper()}</b>" if filter_service else f"{pem('mail')} <b>Mailbox</b>"
    if not filtered:
        return f"{title}\n{_SEP}\n No messages found."
    out = f"{title}\n{_SEP}\n Total: <b>{len(filtered)}</b> message(s)\n{_SEP}\n\n"
    for i, m in enumerate(filtered[:20], 1):
        code_display = f"<b>{html_lib.escape(m['code'])}</b>"if m.get("code") else "No code"
        out += f"<b>#{i}</b> <b>[{m['service']}]</b> {code_display}\n"
        out += f"└─  {html_lib.escape(m['subject'][:80])}\n"
        out += f"└─  {html_lib.escape(m.get('sender',''))}\n"
        if m.get("date"):
            out += f"└─  {str(m['date'])[:19]}\n"
        out += "\n"
    if len(filtered) > 20:
        out += f"<i>... and {len(filtered) - 20} more</i>\n\n"
    codes_with_code = [m for m in filtered if m.get("code")]
    if codes_with_code:
        out += f"{_SEP}\n <b>CODES:</b>\n"
        for m in codes_with_code:
            out += f"<code>{m['service']} → {html_lib.escape(m['code'])}</code>\n"
    return out


# ══════════════════════════════════════════════════════════════════
# FORMATTERS
# ══════════════════════════════════════════════════════════════════

TZ    = pytz.UTC
_SEP  = "┄" * 24
_LINE = "· · · · · · · · · · · ·"

# ══════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════


def _progress_bar(current: float, maximum: float, width: int = 10) -> str:
    """Visual progress bar using block characters."""
    if maximum <= 0:
        ratio = 0.0
    else:
        ratio = min(current / maximum, 1.0)
    filled = int(ratio * width)
    empty = width - filled
    bar = "\u2588" * filled + "\u2591" * empty
    pct = int(ratio * 100)
    return f"[{bar}] {pct}%"


def _mini_chart(values: list) -> str:
    """Sparkline text chart from a list of numeric values."""
    if not values:
        return ""
    spark_chars = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
    mn = min(values)
    mx = max(values)
    rng = mx - mn if mx != mn else 1
    return "".join(spark_chars[min(int((v - mn) / rng * 7), 7)] for v in values)


def _status_dot(is_online: bool) -> str:
    """Green/red circle emoji for status indication."""
    return pem("online") if is_online else pem("offline")


def _quick_actions_inline(actions: list) -> InlineKeyboardMarkup:
    """Generate quick-action button rows from list of (text, callback_data) tuples."""
    rows = []
    row = []
    for i, (txt, cb) in enumerate(actions):
        row.append(InlineKeyboardButton(text=txt, callback_data=cb))
        if len(row) == 3 or i == len(actions) - 1:
            rows.append(row)
            row = []
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _dt(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=TZ).strftime("%d %b %Y, %H:%M UTC")


def fmt_welcome(shop_name: str, welcome: str, first_name: str, balance: float,
                user: dict = None) -> str:
    tier_name, tier_emoji = ("", "")
    total_spent = 0
    order_count = 0
    if user:
        total_spent = user.get("total_spent", 0)
        order_count = user.get("order_count", 0)
        tier_name, tier_emoji = get_vip_tier(total_spent)
    vip_badge = f" {tier_emoji} {tier_name}" if tier_name else ""
    return (
        f"{pem('hi')} <b>✦ {shop_name} ✦</b>\n{_SEP}\n"
        f"<i>{welcome}</i>\n\n"
        f"╔══ {pem('user')} <b>{first_name}</b>{vip_badge}\n"
        f"║ {pem('diamond')} Balance ‣ <code>${balance:.2f}</code>\n"
        f"║ {pem('buy')} Orders ‣ <b>{order_count}</b>  {pem('money')} Spent ‣ <b>${total_spent:.2f}</b>\n"
        f"╚══ Status: {pem('ok')} <b>Active</b>\n"
        f"{_SEP}"
    )

def fmt_balance_screen(user: dict) -> str:
    banned = f"{pem('no')} <b>Banned</b>" if user.get("is_banned") else f"{pem('ok')} <b>Active</b>"
    bonus = user.get("bonus")
    bonus_line = ""
    if bonus and bonus.get("amount", 0) > 0:
        bonus_line = f"  {pem('gift')} Bonus Balance ‣ <code>${bonus['amount']:.2f}</code>\n"
    total_spent = user.get("total_spent", 0)
    tier_name, tier_emoji = get_vip_tier(total_spent)
    next_tier, current, threshold = get_vip_progress(total_spent)
    vip_line = f"  {tier_emoji} VIP Status ‣ <b>{tier_name}</b>\n" if tier_name else ""
    progress = _progress_bar(current, threshold) if next_tier != "Max" else _progress_bar(1, 1)
    member_since = _dt(user.get("joined_at", int(time.time())))
    return (
        f"{pem('diamond')} <b>✦ My Wallet ✦</b>\n{_SEP}\n"
        f"  {pem('user')} <b>{user.get('full_name', 'User')}</b>\n"
        f"  <code>{user.get('user_id', '?')}</code>  ‣  @{user.get('username') or 'N/A'}\n"
        f"{vip_line}"
        f"{_LINE}\n"
        f"  {pem('money')} Balance ‣ <code>${user.get('balance', 0):.2f}</code>\n"
        f"{bonus_line}"
        f"  {pem('buy')} Total Spent ‣ <b>${total_spent:.2f}</b>\n"
        f"  {pem('history')} Total Orders ‣ <b>{user.get('order_count', 0)}</b>\n"
        f"{_LINE}\n"
        f"  {pem('chart')} Progress ‣ {progress}\n"
        f"  Next Tier ‣ <b>{next_tier}</b>  (${threshold:.0f} needed)\n"
        f"{_LINE}\n"
        f"  {pem('date')} Member Since ‣ {member_since}\n"
        f"  Status ‣ {banned}"
    )

def fmt_product_list_header(category_name: str, count: int) -> str:
    return (
        f"{pem('package')} <b>✦ {category_name} ✦</b>\n{_SEP}\n"
        f"  {pem('star')} <b>{count}</b> premium product(s) available\n"
        f"{_LINE}\n"
        f"  ‣ Select your desired product below:"
    )

def fmt_product_detail(product: dict, stock: int) -> str:
    desc = product.get("description", "").strip()
    desc_line = f"  <i>{desc}</i>\n" if desc else ""
    status = _status_dot(stock > 0)
    stock_bar = _progress_bar(stock, max(stock, 50), width=8)
    return (
        f"{pem('package')} <b>✦ {product['name']} ✦</b>\n{_SEP}\n"
        f"{desc_line}"
        f"  {status} Availability ‣ <b>{'In Stock' if stock > 0 else 'Out of Stock'}</b>\n"
        f"  {pem('money')} Unit Price ‣ <code>${product['price']:.2f}</code> / account\n"
        f"  {pem('num')} Stock Level ‣ <b>{stock}</b> units  {stock_bar}\n"
        f"{_LINE}\n"
        f"  {pem('pin')} <b>Enter the quantity you want to purchase:</b>"
    )

def fmt_service_detail(product: dict, duration_days: int) -> str:
    price = round(product["price"] * duration_days, 4)
    desc = product.get("description", "").strip()
    desc_line = f"  <i>{desc}</i>\n" if desc else ""
    return (
        f"{pem('world')} <b>✦ {product['name']} ✦</b>\n{_SEP}\n"
        f"{desc_line}"
        f"  {pem('money')} Daily Rate ‣ <code>${product['price']:.2f}</code> / day\n"
        f"  {pem('time')} Duration ‣ <b>{duration_days} day(s)</b>\n"
        f"  {pem('card')} Total Cost ‣ <code>${price:.2f}</code>\n"
        f"{_LINE}\n"
        f"  ‣ Press {pem('confirm')} <b>Confirm Purchase</b> to place your order."
    )

def fmt_order_summary(product: dict, qty: int, total: float,
                      balance: float, discount_pct: float = 0) -> str:
    disc_line = f"  {pem('coupon')} Coupon Discount ‣ <b>-{discount_pct:.0f}%</b>\n" if discount_pct else ""
    afford = "✅" if balance >= total else "⚠️"
    return (
        f"{pem('history')} <b>✦ Order Summary ✦</b>\n{_SEP}\n"
        f"  {pem('package')} Product ‣ <b>{product['name']}</b>\n"
        f"  {pem('num')} Quantity ‣ <b>{qty}</b> unit(s)\n"
        f"  {pem('money')} Unit Price ‣ <b>${product['price']:.2f}</b> × {qty}\n"
        f"{disc_line}"
        f"  {pem('card')} Order Total ‣ <b>${total:.2f}</b>\n"
        f"{_LINE}\n"
        f"  {pem('diamond')} Your Balance ‣ <b>${balance:.2f}</b>  {afford}\n"
        f"{_SEP}\n"
        f"  💡 Have a coupon? Enter it below,\n"
        f"  or press {pem('confirm')} <b>Confirm Purchase</b> to proceed."
    )

def fmt_confirm_service(category: str, product: dict, days: int,
                        price: float, balance: float) -> str:
    afford = "✅" if balance >= price else "⚠️"
    return (
        f"{pem('history')} <b>✦ Order Summary ✦</b>\n{_SEP}\n"
        f"  {pem('world')} Service ‣ <b>{product['name']}</b>\n"
        f"  {pem('time')} Duration ‣ <b>{days} day(s)</b>\n"
        f"  {pem('card')} Total Cost ‣ <b>${price:.2f}</b>\n"
        f"{_LINE}\n"
        f"  {pem('diamond')} Your Balance ‣ <b>${balance:.2f}</b>  {afford}\n"
        f"{_SEP}\n"
        f"  ‣ Press {pem('confirm')} <b>Confirm Purchase</b> to place your order."
    )

def fmt_order_receipt(oid: str, product_name: str, qty: int,
                      total: float, items: List[str], new_balance: float) -> str:
    preview = "\n".join(items[:5])
    more = f"\n<i>  ··· and {len(items) - 5} more accounts</i>" if len(items) > 5 else ""
    return (
        f"{pem('approval')} <b>✦ Order Successful! ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} Order ID ‣ <code>{oid}</code>\n"
        f"  {pem('package')} Product ‣ <b>{product_name}</b> × {qty}\n"
        f"  {pem('card')} Amount Paid ‣ <b>${total:.2f}</b>\n"
        f"  {pem('diamond')} New Balance ‣ <b>${new_balance:.2f}</b>\n"
        f"{_SEP}\n"
        f"  {pem('key')} <b>Your Accounts:</b>\n"
        f"{_LINE}\n"
        f"<code>{preview}{more}</code>"
    )

def fmt_service_order_placed(cat_emoji: str, cat_name: str,
                              oid: str, product_name: str, days: int, price: float) -> str:
    return (
        f"{pem('approval')} <b>✦ {cat_name} Order Placed! ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} Order ID ‣ <code>{oid}</code>\n"
        f"  {pem('package')} Service ‣ <b>{product_name}</b>\n"
        f"  {pem('time')} Duration ‣ <b>{days} day(s)</b>\n"
        f"  {pem('card')} Amount Paid ‣ <b>${price:.2f}</b>\n"
        f"{_SEP}\n"
        f"  {pem('warn')} Status ‣ <b>Pending Delivery</b>\n"
        f"  ‣ Our team is processing your order.\n"
        f"  ‣ You will be notified upon delivery. 🔔"
    )

def fmt_deposit_info(method_label: str, number: str, rate: float, min_amt: float, is_usd: bool = False) -> str:
    if is_usd:
        return (
            f"{pem('payment')} <b>✦ Deposit via {method_label} ✦</b>\n{_SEP}\n"
            f"  {pem('pin')} Binance UID ‣ <code>{number or 'Not configured'}</code>\n"
            f"  {pem('money')} Minimum ‣ <b>${min_amt:.2f} USD</b>\n"
            f"{_LINE}\n"
            f"  ‣ Enter the <b>USD amount</b> you are sending:"
        )
    return (
        f"{pem('payment')} <b>✦ Deposit via {method_label} ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} Send To ‣ <code>{number or 'Not configured'}</code>\n"
        f"  {pem('graph')} Exchange Rate ‣ <b>1 USD = {rate:.0f} BDT</b>\n"
        f"  {pem('money')} Minimum ‣ <b>{min_amt:.0f} BDT</b>\n"
        f"{_LINE}\n"
        f"  ‣ Enter the <b>BDT amount</b> you are sending:"
    )

def fmt_deposit_confirm(method: str, amount_bdt: float, amount_usd: float, is_usd: bool = False) -> str:
    amt_str = f"${amount_usd:.2f} USD" if is_usd else f"{amount_bdt:.0f} BDT  ≈  ${amount_usd:.2f} USD"
    return (
        f"{pem('payment')} <b>✦ Deposit Summary ✦</b>\n{_SEP}\n"
        f"  {pem('card')} Method ‣ <b>{method}</b>\n"
        f"  {pem('money')} Amount ‣ <b>{amt_str}</b>\n"
        f"{_LINE}\n"
        f"  ‣ Now send your <b>Transaction ID / Reference No:</b>"
    )

def fmt_deposit_submitted(dep_id: str, method: str, amount_bdt: float, amount_usd: float, is_usd: bool = False) -> str:
    amt_str = f"${amount_usd:.2f} USD" if is_usd else f"{amount_bdt:.0f} BDT  ≈  ${amount_usd:.2f} USD"
    return (
        f"{pem('approval')} <b>✦ Deposit Request Submitted! ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} Reference ID ‣ <code>{dep_id[:12]}</code>\n"
        f"  {pem('payment')} Method ‣ <b>{method}</b>\n"
        f"  {pem('money')} Amount ‣ <b>{amt_str}</b>\n"
        f"{_SEP}\n"
        f"  {pem('warn')} Status ‣ <b>Pending Review</b>\n"
        f"  ‣ Balance credited after admin verification.\n"
        f"  ‣ Processing time: <b>5 – 30 minutes</b> ⏱"
    )

def fmt_order_history(orders: list, vpn: list, proxy: list) -> str:
    if not orders and not vpn and not proxy:
        return (
            f"{pem('history')} <b>✦ Order History ✦</b>\n{_SEP}\n"
            f"  📭 No orders found yet.\n"
            f"{_LINE}\n"
            f"  ‣ Browse our products and place your first order!"
        )
    lines = []
    if orders:
        lines.append(f"  {pem('mail')} <b>Mail Orders</b>")
        for o in orders[:8]:
            lines.append(f"  ‣ <code>{o['order_id']}</code>  {o['product_name']} ×{o['qty']}  <b>${o['total_price']:.2f}</b>")
    if vpn:
        lines.append("")
        lines.append(f"  {pem('shield')} <b>VPN Orders</b>")
        for o in vpn[:8]:
            s = {"delivered": pem("ok"), "cancelled": pem("no")}.get(o["status"], pem("time"))
            lines.append(f"  ‣ <code>{o['order_id']}</code>  {o['product_name']} {o['duration_days']}d  <b>${o['price']:.2f}</b>  {s}")
    if proxy:
        lines.append("")
        lines.append(f"  {pem('world')} <b>Proxy Orders</b>")
        for o in proxy[:8]:
            s = {"delivered": pem("ok"), "cancelled": pem("no")}.get(o["status"], pem("time"))
            data_lbl = o.get("duration_days", "-")
            lines.append(f"  ‣ <code>{o['order_id']}</code>  {o['product_name']} {data_lbl}  <b>${o['price']:.2f}</b>  {s}")
    total_orders = len(orders) + len(vpn) + len(proxy)
    return (
        f"{pem('history')} <b>✦ Order History ✦</b>\n{_SEP}\n"
        + "\n".join(lines)
        + f"\n{_SEP}\n  {pem('chart')} Total Orders ‣ <b>{total_orders}</b>"
    )

def fmt_deposit_history(deposits: list) -> str:
    if not deposits:
        return (
            f"{pem('payment')} <b>✦ Deposit History ✦</b>\n{_SEP}\n"
            f"  📭 No deposit records found.\n"
            f"{_LINE}\n"
            f"  ‣ Make your first deposit to get started!"
        )
    lines = []
    for d in deposits[:12]:
        s = {"approved": pem("ok"), "rejected": pem("no")}.get(d["status"], pem("time"))
        lines.append(f"  {s} <code>{d['deposit_id'][:8]}</code>  {d['method']}  <b>{d['amount_bdt']:.0f} BDT</b>  ${d['amount_usd']:.2f}")
    return (
        f"{pem('payment')} <b>✦ Deposit History ✦</b>\n{_SEP}\n"
        + "\n".join(lines)
    )

def fmt_admin_dashboard(stats: dict) -> str:
    pending_dep = stats.get('pending_deposits', 0)
    pending_ord = stats.get('pending_orders', 0)
    alert = ""
    if pending_dep > 0 or pending_ord > 0:
        alert = (
            f"\n{_SEP}\n"
            f"  {pem('bell')} <b>⚡ ACTION REQUIRED</b>\n"
            f"  ‣ {pending_dep} deposit(s) awaiting approval\n"
            f"  ‣ {pending_ord} order(s) pending fulfillment"
        )
    return (
        f"{pem('admin')} <b>✦ Admin Dashboard ✦</b>\n{_SEP}\n"
        f"  {pem('user')} Total Users ‣ <b>{stats['total_users']}</b>\n"
        f"  {pem('money')} Total Revenue ‣ <code>${stats['total_revenue']:.2f}</code>\n"
        f"  {pem('buy')} Total Sales ‣ <b>{stats['total_sales']}</b>\n"
        f"{_LINE}\n"
        f"  {pem('payment')} Pending Deposits ‣ <b>{pending_dep}</b>\n"
        f"  {pem('package')} Pending Orders ‣ <b>{pending_ord}</b>"
        f"{alert}"
    )

def fmt_analytics(data: dict) -> str:
    body_lines = [
        f"  📅 <b>Today</b>",
        f"  ‣ Revenue ‣ <code>${data['today_rev']:.2f}</code>  ·  Orders ‣ <b>{data['today_count']}</b>",
        "",
        f"  📆 <b>This Week</b>  <i>(7 days)</i>",
        f"  ‣ Revenue ‣ <code>${data['week_rev']:.2f}</code>  ·  Orders ‣ <b>{data['week_count']}</b>",
        "",
        f"  🗓 <b>This Month</b>  <i>(30 days)</i>",
        f"  ‣ Revenue ‣ <code>${data['month_rev']:.2f}</code>  ·  Orders ‣ <b>{data['month_count']}</b>",
    ]
    top_products_lines = [f"\n{_LINE}\n  {pem('trending')} <b>Top 5 Products</b>"]
    if data["top_products"]:
        medals = ["🥇","🥈","🥉","④","⑤"]
        for i, (_, name, sold) in enumerate(data["top_products"], 1):
            medal = medals[i-1] if i <= len(medals) else f"{i}."
            top_products_lines.append(f"  {medal} {name} ‣ <b>{sold}</b> sold")
    else:
        top_products_lines.append("  No data yet.")
    top_buyers_lines = [f"\n{_LINE}\n  {pem('crown')} <b>Top 5 Buyers</b>"]
    if data["top_buyers"]:
        medals = ["🥇","🥈","🥉","④","⑤"]
        for i, (uid, uname, spent) in enumerate(data["top_buyers"], 1):
            display = f"@{uname}" if uname else f"<code>{uid}</code>"
            medal = medals[i-1] if i <= len(medals) else f"{i}."
            top_buyers_lines.append(f"  {medal} {display} ‣ <b>${spent:.2f}</b>")
    else:
        top_buyers_lines.append("  No data yet.")
    body = "\n".join(body_lines + top_products_lines + top_buyers_lines)
    return (
        f"{pem('chart')} <b>✦ Sales Analytics ✦</b>\n{_SEP}\n"
        f"{body}"
    )


def fmt_admin_deposit_review(d: dict) -> str:
    return (
        f"{pem('payment')} <b>✦ Deposit Request ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} Ref ID ‣ <code>{d['deposit_id']}</code>\n"
        f"  {pem('user')} User ‣ @{d.get('username','—')}  (<code>{d['user_id']}</code>)\n"
        f"  {pem('card')} Method ‣ <b>{d['method']}</b>\n"
        f"  {pem('money')} Amount ‣ <b>{d['amount_bdt']:.0f} BDT</b>  ≈  <b>${d['amount_usd']:.2f}</b>\n"
        f"  {pem('key')} TRX ID ‣ <code>{d.get('trx_id','—')}</code>\n"
        f"{_LINE}\n"
        f"  {pem('date')} Submitted ‣ {_dt(d['created_at'])}"
    )

def fmt_admin_vpn_order(o: dict) -> str:
    return (
        f"{pem('shield')} <b>✦ New VPN Order ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} Order ID ‣ <code>{o['order_id']}</code>\n"
        f"  {pem('user')} Customer ‣ @{o.get('username','—')}  (<code>{o['user_id']}</code>)\n"
        f"  {pem('package')} Product ‣ <b>{o['product_name']}</b>\n"
        f"  {pem('time')} Duration ‣ <b>{o['duration_days']} day(s)</b>\n"
        f"  {pem('card')} Amount ‣ <b>${o['price']:.2f}</b>\n"
        f"{_LINE}\n"
        f"  {pem('date')} Placed ‣ {_dt(o['created_at'])}"
    )

def fmt_admin_proxy_order(o: dict) -> str:
    data_lbl = o.get("duration_days", "—")
    return (
        f"{pem('world')} <b>✦ New Proxy Order ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} Order ID ‣ <code>{o['order_id']}</code>\n"
        f"  {pem('user')} Customer ‣ @{o.get('username','—')}  (<code>{o['user_id']}</code>)\n"
        f"  {pem('package')} Product ‣ <b>{o['product_name']}</b>\n"
        f"  {pem('num')} Data ‣ <b>{data_lbl}</b>\n"
        f"  {pem('card')} Amount ‣ <b>${o['price']:.2f}</b>\n"
        f"{_LINE}\n"
        f"  {pem('date')} Placed ‣ {_dt(o['created_at'])}"
    )

def fmt_user_info(user: dict, mail_orders: int = 0, vpn_orders: int = 0, proxy_orders: int = 0) -> str:
    banned = f"{pem('no')} <b>Banned</b>" if user.get("is_banned") else f"{pem('ok')} <b>Active</b>"
    bonus = user.get("bonus")
    bonus_section = ""
    if bonus and bonus.get("amount", 0) > 0:
        allowed = bonus.get("allowed_products", [])
        prods = ", ".join(allowed) if allowed else "All Products"
        bonus_section = (
            f"\n{_LINE}\n"
            f"  {pem('gift')} <b>Bonus Balance</b>\n"
            f"  ‣ Amount ‣ <b>${bonus['amount']:.2f}</b>\n"
            f"  ‣ Valid For ‣ <code>{prods}</code>\n"
        )
    order_section = ""
    if mail_orders or vpn_orders or proxy_orders:
        order_section = (
            f"\n{_LINE}\n"
            f"  {pem('history')} <b>Order Breakdown</b>\n"
            f"  ‣ Mail ‣ <b>{mail_orders}</b>\n"
            f"  ‣ VPN ‣ <b>{vpn_orders}</b>\n"
            f"  ‣ Proxy ‣ <b>{proxy_orders}</b>\n"
        )
    return (
        f"{pem('user')} <b>✦ User Profile ✦</b>\n{_SEP}\n"
        f"  {pem('pin')} ID ‣ <code>{user['user_id']}</code>\n"
        f"  {pem('user')} Username ‣ @{user.get('username') or 'N/A'}\n"
        f"  {pem('star')} Name ‣ <b>{user.get('full_name') or 'N/A'}</b>\n"
        f"{_LINE}\n"
        f"  {pem('money')} Balance ‣ <b>${user.get('balance', 0):.2f}</b>\n"
        f"  {pem('buy')} Total Spent ‣ <b>${user.get('total_spent', 0):.2f}</b>\n"
        f"{bonus_section}"
        f"{_LINE}\n"
        f"  {pem('history')} Total Orders ‣ <b>{user.get('order_count', 0)}</b>\n"
        f"  {pem('date')} Joined ‣ {_dt(user.get('joined_at', 0))}\n"
        f"  {pem('online')} Status ‣ {banned}"
        f"{order_section}"
    )

def fmt_settings(s: dict) -> str:
    ch1  = s.get('force_join_channel') or '—'
    ch2  = s.get('force_join_channel_2') or '—'
    bkno = s.get('bkash_number') or '—'
    ngno = s.get('nagad_number') or '—'
    bnid = s.get('binance_uid') or '—'
    return (
        f"{pem('gear')} <b>✦ Bot Configuration ✦</b>\n{_SEP}\n"
        f"  {pem('star')} Shop ‣ <b>{s.get('shop_name') or 'Shop'}</b>\n"
        f"  {pem('graph')} Rate ‣ <b>1 USD = {s.get('usd_rate', 125):.0f} BDT</b>\n"
        f"  {pem('warn')} Low Stock Alert ‣ <b>{s.get('low_stock_threshold', 5)} units</b>\n"
        f"\n"
        f"  {pem('payment')} <b>── Payment Methods ──</b>\n"
        f"  {pem('bkash')} bKash ‣ <code>{bkno}</code>  · min <b>{s.get('bkash_min', 100):.0f} BDT</b>\n"
        f"  {pem('nagad')} Nagad ‣ <code>{ngno}</code>  · min <b>{s.get('nagad_min', 150):.0f} BDT</b>\n"
        f"  {pem('binance')} Binance ‣ <code>{bnid}</code>  · min <b>${s.get('binance_min', 5):.2f}</b>\n"
        f"\n"
        f"  {pem('link')} <b>── Channel Links ──</b>\n"
        f"  ‣ Ch1 ‣ <b>{ch1}</b>\n"
        f"  ‣ Ch2 ‣ <b>{ch2}</b>\n"
        f"  ‣ Support ‣ <b>{s.get('support_username') or '—'}</b>\n"
        f"  ‣ 2FA Link ‣ <b>{s.get('get_2fa_link') or '—'}</b>\n"
        f"\n"
        f"  {pem('world')} <b>── Proxy Settings ──</b>\n"
        f"  ‣ Data Options ‣ <code>{s.get('proxy_data_options', '1 GB,5 GB,10 GB,50 GB')}</code>\n"
        f"\n"
        f"  {pem('gear')} <b>── System ──</b>\n"
        f"  ‣ Stock Export ‣ <b>{s.get('stock_export_interval', 30):.0f} min</b>\n"
        f"  ‣ Referral Bonus ‣ <b>{s.get('referral_bonus_pct', 5.0):.1f}%</b>\n"
        f"  ‣ Maintenance ‣ <b>{str(s.get('maintenance_mode', 'OFF')).upper()}</b>\n"
        f"  ‣ Auto Backup ‣ <b>{'every ' + str(int(s.get('backup_interval_hours', 24))) + 'h' if s.get('backup_interval_hours', 24) > 0 else 'Disabled'}</b>"
    )

# ══════════════════════════════════════════════════════════════════
# VALIDATORS
# ══════════════════════════════════════════════════════════════════

def validate_quantity(text: str, max_stock: int) -> Tuple[Optional[int], Optional[str]]:
    try:
        qty = int(text.strip())
    except ValueError:
        return None, "Please enter a valid number."
    if qty <= 0:
        return None, "Quantity must be at least 1."
    if qty > max_stock:
        return None, f"Only <b>{max_stock}</b> in stock."
    return qty, None

def validate_amount_bdt(text: str, minimum: float) -> Tuple[Optional[float], Optional[str]]:
    try:
        amount = float(text.strip())
    except ValueError:
        return None, "Please enter a valid amount."
    if amount <= 0:
        return None, "Amount must be positive."
    if amount < minimum:
        return None, f"Minimum deposit is <b>{minimum:.0f} BDT</b>"
    return amount, None

def validate_custom_days(text: str) -> Tuple[Optional[int], Optional[str]]:
    try:
        days = int(text.strip())
    except ValueError:
        return None, "Enter a valid number of days."
    if days < 1:
        return None, "Minimum 1 day."
    if days > 365:
        return None, "Maximum 365 days."
    return days, None

def validate_coupon(coupon: dict) -> Tuple[bool, Optional[str]]:
    # NOTE: Coupon usage is tracked globally (used_count), not per-user.
    # A single user can use the same coupon multiple times until max_uses is reached.
    if not coupon.get("active"):
        return False, "Coupon is no longer active."
    if coupon.get("expires_at", 0) < int(time.time()):
        return False, "Coupon has expired."
    if coupon.get("used_count", 0) >= coupon.get("max_uses", 1):
        return False, "Coupon usage limit reached."
    return True, None

def validate_price(text: str) -> Tuple[Optional[float], Optional[str]]:
    try:
        p = float(text.strip())
    except ValueError:
        return None, "Enter a valid price."
    if p < 0:
        return None, "Price cannot be negative."
    return p, None

def validate_discount(text: str) -> Tuple[Optional[float], Optional[str]]:
    try:
        pct = float(text.strip())
    except ValueError:
        return None, "Enter a valid percentage."
    if not (0 < pct <= 100):
        return None, "Must be between 1 and 100."
    return pct, None


# ══════════════════════════════════════════════════════════════════
# FSM STATES
# ══════════════════════════════════════════════════════════════════

class UserFlow(StatesGroup):
    mail_product   = State()
    mail_qty       = State()
    mail_coupon       = State()
    mail_coupon_input = State()
    mail_confirm      = State()
    set_totp_key      = State()
    vpn_product      = State()
    vpn_duration     = State()
    vpn_custom       = State()
    vpn_coupon       = State()
    vpn_coupon_input = State()
    vpn_confirm      = State()
    proxy_product           = State()
    proxy_duration          = State()
    proxy_custom            = State()
    proxy_coupon            = State()
    proxy_coupon_input      = State()
    proxy_confirm           = State()
    proxy_auto_qty          = State()
    proxy_auto_coupon       = State()
    proxy_auto_coupon_input = State()
    proxy_auto_confirm      = State()
    dep_method     = State()
    dep_amount     = State()
    dep_trx        = State()
    dep_screenshot = State()
    # Get Code / Mailbox flow
    get_code_menu   = State()
    get_code_set    = State()
    get_code_filter = State()
    # Temp Mail flow
    temp_mail_menu   = State()
    temp_mail_domain = State()
    # User Panel Enhancements
    favorites_menu       = State()
    search_services      = State()
    order_tracking       = State()
    user_stats           = State()
    more_menu            = State()
    # AI Support flow
    ai_support           = State()
    ai_support_ask       = State()

class AdminFlow(StatesGroup):
    menu              = State()
    products_list     = State()
    product_detail    = State()
    product_edit      = State()
    product_add_name  = State()
    product_add_emoji = State()
    product_add_price = State()
    product_add_cat   = State()
    product_add_desc  = State()
    stock_list        = State()
    stock_detail      = State()
    stock_uploading   = State()
    stock_manual      = State()
    stock_import_all  = State()
    user_search       = State()
    user_menu         = State()
    user_detail       = State()
    user_add_bal      = State()
    user_remove_bal   = State()
    user_bonus_amount = State()
    user_bonus_products = State()
    coupons_list      = State()
    coupon_detail     = State()
    coupon_code       = State()
    coupon_discount   = State()
    coupon_max_uses   = State()
    coupon_expiry     = State()
    broadcast         = State()
    settings_menu     = State()
    settings_edit     = State()
    vpn_fulfill       = State()
    proxy_fulfill     = State()
    dep_reject_reason = State()
    products_import   = State()
    bonus_all_amount  = State()
    bonus_all_products = State()
    bonus_top10_amount = State()
    bonus_top10_products = State()
    proxy_pkg_list    = State()
    proxy_pkg_add     = State()
    order_lookup      = State()
    # FEAT-002: Admin Panel Enhancements
    analytics_detail  = State()
    low_stock_alerts  = State()
    price_sync        = State()
    auto_import       = State()
    roles_menu        = State()
    roles_assign      = State()
    advanced_search   = State()
    export_transactions = State()
    export_tx_dates   = State()
    service_status    = State()
    profit_calc       = State()
    profit_set_cost   = State()
    activity_logs     = State()
    # Sub-menu states
    orders_submenu    = State()
    reports_submenu   = State()
    tools_submenu     = State()


# ══════════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════════

PREMIUM_EMOJI_IDS = {
    "bot_reply": "6311845322150652183",
    "close": "6311965254817423602",
    "payment": "6312344027983257537",
    "approval": "6311983130471308119",
    "delete": "6314398126157340467",
    "fire": "6314080118188808371",
    "buy": "6312234398943026185",
    "add": "6312260233171312151",
    "date": "6314128625549450770",
    "okay": "6314082948572256406",
    "1": "5866189817481531778",
    "2": "6089331218392813822",
    "3": "5866206774012416141",
    "4": "5866324451821358773",
    "5": "5866474230215873258",
    "6": "5866354903139487976",
    "7": "5866208942970901081",
    "8": "5866395366026384460",
    "down": "6053169517905845173",
    "mail": "6053193097276298985",
    "telegram": "6109560346853251750",
    "confirm": "6311983130471308119",
    "time": "6336809269802833182",
    "button_click": "6233136657722251031",
    "stock_off": "5100657930429006538",
    "binance": "6237610939902858402",
    "bkash": "6237975191784266396",
    "nogod": "6235336389647407554",
    # User added premium emojis
    "express": "5814184382071574423",
    "ipvanish": "5816876665141202258",
    "nord_vpn": "5816931709442068156",
    "hotspot_shield": "5816437229857280693",
    "surfshark": "5816864355764932607",
    "admin": "6089346083274626176",
    "balance_low": "5454125707300978880",
    "gift": "6312301920123887895",
    "live": "6312004025487204067",
    "help_q": "6312235051778056164",
    "2fa_2": "6089331218392813822",
    "2fa_f": "6086887764253480137",
}

SET_USD_RATE        = _b("USD Rate")
SET_BKASH_NUM       = _b("bKash Number")
SET_BKASH_MIN       = _b("bKash Min Deposit")
SET_NAGAD_NUM       = _b("Nagad Number")
SET_NAGAD_MIN       = _b("Nagad Min Deposit")
SET_BINANCE_UID     = _b("Binance UID")
SET_BINANCE_MIN     = _b("Binance Min Deposit")
SET_FORCE_JOIN_1    = _b("Force Join #1")
SET_FORCE_JOIN_2    = _b("Force Join #2")
SET_SUPPORT_LINK    = _b("Support Link")
SET_GET_2FA_LINK    = _b("Get 2FA Link")
SET_SHOP_NAME       = _b("Shop Name")
SET_WELCOME_MSG     = _b("Welcome Message")
SET_LOW_STOCK       = _b("Low Stock Alert")
SET_PROXY_OPTS      = _b("Proxy Data Options")
SET_STOCK_EXPORT    = _b("Stock Export Interval")
SET_REF_BONUS       = _b("Referral Bonus %")
SET_MAINT_MODE      = _b("Maintenance Mode")
SET_MAINT_MSG       = _b("Maintenance Msg")
SET_BACKUP_INT      = _b("Backup Interval")

BTN_SET_PAYMENT  = _b("Payment")
BTN_SET_CHANNELS = _b("Channels")
BTN_SET_SHOP     = _b("Shop")
BTN_SET_SYSTEM   = _b("System")
BTN_PROXY_DATA_CUSTOM = _b("Custom Amount")

BUTTON_CUSTOM_EMOJIS: Dict[str, str] = {
    # Navigation
    HOME_BTN: PREMIUM_EMOJI_IDS["telegram"],
    BACK_BTN: PREMIUM_EMOJI_IDS["close"],
    CANCEL_BTN: PREMIUM_EMOJI_IDS["close"],

    # User Main Menu
    BTN_BALANCE: PREMIUM_EMOJI_IDS["payment"],
    BTN_DEPOSIT: PREMIUM_EMOJI_IDS["payment"],
    BTN_GET_MAIL: PREMIUM_EMOJI_IDS["mail"],
    BTN_TEMP_MAIL: PREMIUM_EMOJI_IDS["mail"],
    BTN_BUY_VPN: PREMIUM_EMOJI_IDS["buy"],
    BTN_BUY_PROXY: PREMIUM_EMOJI_IDS["buy"],
    BTN_GET_CODE: PREMIUM_EMOJI_IDS["button_click"],
    BTN_GET_2FA: PREMIUM_EMOJI_IDS["2fa_2"],
    BTN_HISTORY: PREMIUM_EMOJI_IDS["date"],
    BTN_REFERRAL: PREMIUM_EMOJI_IDS["gift"],
    BTN_MORE: PREMIUM_EMOJI_IDS["button_click"],
    BTN_SUPPORT: PREMIUM_EMOJI_IDS["telegram"],
    BTN_AI_SUPPORT: PREMIUM_EMOJI_IDS["bot_reply"],

    # Get Code Submenu
    BTN_GC_SET_MAIL: PREMIUM_EMOJI_IDS["mail"],
    BTN_GC_CODES: PREMIUM_EMOJI_IDS["button_click"],
    BTN_GC_INBOX: PREMIUM_EMOJI_IDS["mail"],
    BTN_GC_REFRESH: PREMIUM_EMOJI_IDS["bot_reply"],
    BTN_GC_FILTER: PREMIUM_EMOJI_IDS["mail"],
    BTN_GC_CHANGE: PREMIUM_EMOJI_IDS["bot_reply"],

    # More Submenu
    BTN_TRENDING: PREMIUM_EMOJI_IDS["fire"],
    BTN_FAVORITES: PREMIUM_EMOJI_IDS["gift"],
    BTN_SEARCH: PREMIUM_EMOJI_IDS["button_click"],
    BTN_MY_STATS: PREMIUM_EMOJI_IDS["payment"],

    # AI Support FAQ
    BTN_AI_HOW_BUY: PREMIUM_EMOJI_IDS["buy"],
    BTN_AI_HOW_DEPOSIT: PREMIUM_EMOJI_IDS["payment"],
    BTN_AI_STOCK: PREMIUM_EMOJI_IDS["balance_low"],
    BTN_AI_REFERRAL: PREMIUM_EMOJI_IDS["gift"],
    BTN_AI_ORDERS: PREMIUM_EMOJI_IDS["date"],
    BTN_AI_2FA: PREMIUM_EMOJI_IDS["2fa_2"],
    BTN_AI_MAIL: PREMIUM_EMOJI_IDS["mail"],
    BTN_AI_ASK: PREMIUM_EMOJI_IDS["help_q"],

    # Duration & Packages
    BTN_1DAY: PREMIUM_EMOJI_IDS["1"],
    BTN_7DAYS: PREMIUM_EMOJI_IDS["7"],
    BTN_30DAYS: PREMIUM_EMOJI_IDS["date"],
    BTN_90DAYS: PREMIUM_EMOJI_IDS["date"],
    BTN_CUSTOM: PREMIUM_EMOJI_IDS["time"],
    BTN_PROXY_DATA_CUSTOM: PREMIUM_EMOJI_IDS["time"],

    # Payment Methods
    BTN_BKASH: PREMIUM_EMOJI_IDS["bkash"],
    BTN_NAGAD: PREMIUM_EMOJI_IDS["nogod"],
    BTN_BINANCE: PREMIUM_EMOJI_IDS["binance"],

    # Action Confirmation
    BTN_CONFIRM: PREMIUM_EMOJI_IDS["confirm"],
    BTN_COUPON: PREMIUM_EMOJI_IDS["gift"],

    # Admin Main Menu
    BTN_ADM_DASHBOARD: PREMIUM_EMOJI_IDS["admin"],
    BTN_ADM_PRODUCTS: PREMIUM_EMOJI_IDS["buy"],
    BTN_ADM_STOCK: PREMIUM_EMOJI_IDS["balance_low"],
    BTN_ADM_USERS: PREMIUM_EMOJI_IDS["telegram"],
    BTN_ADM_DEPOSITS: PREMIUM_EMOJI_IDS["payment"],
    BTN_ADM_VPN_ORDERS: PREMIUM_EMOJI_IDS["buy"],
    BTN_ADM_PROXY_ORDERS: PREMIUM_EMOJI_IDS["buy"],
    BTN_ADM_COUPONS: PREMIUM_EMOJI_IDS["gift"],
    BTN_ADM_BROADCAST: PREMIUM_EMOJI_IDS["telegram"],
    BTN_ADM_SETTINGS: PREMIUM_EMOJI_IDS["button_click"],
    BTN_ADM_EXPORT: PREMIUM_EMOJI_IDS["down"],
    BTN_ADM_PROXY_PKGS: PREMIUM_EMOJI_IDS["buy"],
    BTN_ADM_ORDER_LOOKUP: PREMIUM_EMOJI_IDS["button_click"],
    BTN_ADM_ANALYTICS: PREMIUM_EMOJI_IDS["date"],
    BTN_PKG_ADD: PREMIUM_EMOJI_IDS["add"],

    # Admin Submenus
    BTN_ADM_ORDERS_MENU: PREMIUM_EMOJI_IDS["date"],
    BTN_ADM_REPORTS_MENU: PREMIUM_EMOJI_IDS["date"],
    BTN_ADM_TOOLS_MENU: PREMIUM_EMOJI_IDS["button_click"],

    # Admin Tools Enhancements
    BTN_ADM_LOW_STOCK: PREMIUM_EMOJI_IDS["balance_low"],
    BTN_ADM_ROLES: PREMIUM_EMOJI_IDS["admin"],
    BTN_ADM_EXPORT_TX: PREMIUM_EMOJI_IDS["down"],
    BTN_ADM_STATUS_MGR: PREMIUM_EMOJI_IDS["bot_reply"],
    BTN_ADM_PROFIT: PREMIUM_EMOJI_IDS["payment"],
    BTN_ADM_LOGS: PREMIUM_EMOJI_IDS["date"],
    BTN_ADM_PRICE_SYNC: PREMIUM_EMOJI_IDS["bot_reply"],
    BTN_ADM_AUTO_IMPORT: PREMIUM_EMOJI_IDS["add"],

    # Admin Product Actions
    BTN_EDIT_NAME: PREMIUM_EMOJI_IDS["button_click"],
    BTN_EDIT_PRICE: PREMIUM_EMOJI_IDS["payment"],
    BTN_EDIT_EMOJI: PREMIUM_EMOJI_IDS["bot_reply"],
    BTN_EDIT_DESC: PREMIUM_EMOJI_IDS["button_click"],
    BTN_HIDE_PROD: PREMIUM_EMOJI_IDS["stock_off"],
    BTN_SHOW_PROD: PREMIUM_EMOJI_IDS["okay"],
    BTN_DELETE: PREMIUM_EMOJI_IDS["delete"],
    BTN_ADD_PRODUCT: PREMIUM_EMOJI_IDS["add"],
    BTN_DOWNLOAD_PRODUCTS: PREMIUM_EMOJI_IDS["down"],
    BTN_IMPORT_PRODUCTS: PREMIUM_EMOJI_IDS["add"],
    BTN_ADD_STOCK: PREMIUM_EMOJI_IDS["add"],

    # Admin Stock Actions
    BTN_UPLOAD_FILE: PREMIUM_EMOJI_IDS["add"],
    BTN_MANUAL_ADD: PREMIUM_EMOJI_IDS["add"],
    BTN_CLEAR_STOCK: PREMIUM_EMOJI_IDS["delete"],
    BTN_GET_TEMPLATE: PREMIUM_EMOJI_IDS["down"],
    BTN_DOWNLOAD_STOCK: PREMIUM_EMOJI_IDS["down"],
    BTN_DOWNLOAD_ALL_STOCK: PREMIUM_EMOJI_IDS["down"],
    BTN_IMPORT_ALL_STOCK: PREMIUM_EMOJI_IDS["add"],

    # Admin User Actions
    BTN_BAN_USER: PREMIUM_EMOJI_IDS["close"],
    BTN_UNBAN_USER: PREMIUM_EMOJI_IDS["okay"],
    BTN_ADD_BAL: PREMIUM_EMOJI_IDS["add"],
    BTN_REMOVE_BAL: PREMIUM_EMOJI_IDS["delete"],
    BTN_ADD_BONUS: PREMIUM_EMOJI_IDS["add"],
    BTN_REMOVE_BONUS: PREMIUM_EMOJI_IDS["delete"],
    BTN_BONUS_ALL_USERS: PREMIUM_EMOJI_IDS["fire"],
    BTN_BONUS_TOP10: PREMIUM_EMOJI_IDS["fire"],
    BTN_SEARCH_USER: PREMIUM_EMOJI_IDS["button_click"],

    # Admin Coupon Actions
    BTN_DELETE_COUPON: PREMIUM_EMOJI_IDS["delete"],
    BTN_CREATE_COUPON: PREMIUM_EMOJI_IDS["add"],

    # Settings Categories
    BTN_SET_PAYMENT: PREMIUM_EMOJI_IDS["payment"],
    BTN_SET_CHANNELS: PREMIUM_EMOJI_IDS["telegram"],
    BTN_SET_SHOP: PREMIUM_EMOJI_IDS["buy"],
    BTN_SET_SYSTEM: PREMIUM_EMOJI_IDS["button_click"],

    # Settings Keys
    SET_USD_RATE: PREMIUM_EMOJI_IDS["payment"],
    SET_BKASH_NUM: PREMIUM_EMOJI_IDS["bkash"],
    SET_BKASH_MIN: PREMIUM_EMOJI_IDS["bkash"],
    SET_NAGAD_NUM: PREMIUM_EMOJI_IDS["nogod"],
    SET_NAGAD_MIN: PREMIUM_EMOJI_IDS["nogod"],
    SET_BINANCE_UID: PREMIUM_EMOJI_IDS["binance"],
    SET_BINANCE_MIN: PREMIUM_EMOJI_IDS["binance"],
    SET_FORCE_JOIN_1: PREMIUM_EMOJI_IDS["telegram"],
    SET_FORCE_JOIN_2: PREMIUM_EMOJI_IDS["telegram"],
    SET_SUPPORT_LINK: PREMIUM_EMOJI_IDS["telegram"],
    SET_GET_2FA_LINK: PREMIUM_EMOJI_IDS["bot_reply"],
    SET_SHOP_NAME: PREMIUM_EMOJI_IDS["buy"],
    SET_WELCOME_MSG: PREMIUM_EMOJI_IDS["bot_reply"],
    SET_LOW_STOCK: PREMIUM_EMOJI_IDS["balance_low"],
    SET_PROXY_OPTS: PREMIUM_EMOJI_IDS["buy"],
    SET_STOCK_EXPORT: PREMIUM_EMOJI_IDS["time"],
    SET_REF_BONUS: PREMIUM_EMOJI_IDS["fire"],
    SET_MAINT_MODE: PREMIUM_EMOJI_IDS["stock_off"],
    SET_MAINT_MSG: PREMIUM_EMOJI_IDS["bot_reply"],
    SET_BACKUP_INT: PREMIUM_EMOJI_IDS["time"],
}

# ══════════════════════════════════════════════════════════════════
# BUTTON COLOR PALETTE MAPPING
# ══════════════════════════════════════════════════════════════════
BUTTON_EXPLICIT_STYLES = {
    # ── Navigation ──
    HOME_BTN: "primary",         # 🔵 Home (Blue)
    BACK_BTN: "danger",          # 🔴 Back (Red)
    CANCEL_BTN: "danger",        # 🔴 Cancel (Red)

    # ── User Main Menu ──
    BTN_BALANCE: "primary",      # 🔵 Balance (Blue - ব্যালেন্স)
    BTN_DEPOSIT: "primary",      # 🔵 Deposit (Blue - ডিপোজিট)
    BTN_GET_MAIL: "danger",      # 🔴 Get Mail (Red - মেইল ক্রয়)
    BTN_TEMP_MAIL: "danger",     # 🔴 Temp Mail (Red - টেম্প মেইল)
    BTN_BUY_VPN: "danger",       # 🔴 Buy VPN (Red - ভিপিএন ক্রয়)
    BTN_BUY_PROXY: "danger",     # 🔴 Buy Proxy (Red - প্রক্সি ক্রয়)
    BTN_GET_CODE: "primary",     # 🔵 Get Code (Blue)
    BTN_GET_2FA: "success",      # 🟢 Get 2FA (Green)
    BTN_HISTORY: "primary",      # 🔵 Order History (Blue)
    BTN_REFERRAL: "success",     # 🟢 Referral (Green)
    BTN_MORE: "primary",         # 🔵 More (Blue)
    BTN_SUPPORT: "primary",      # 🔵 Support (Blue)
    BTN_AI_SUPPORT: "success",   # 🟢 AI Support (Green)

    # ── Get Code Sub-menu ──
    BTN_GC_SET_MAIL: "primary",  # 🔵 Set Mail
    BTN_GC_CODES: "primary",     # 🔵 Get Codes
    BTN_GC_INBOX: "primary",     # 🔵 Read Inbox
    BTN_GC_REFRESH: "primary",   # 🔵 Refresh Inbox
    BTN_GC_FILTER: "primary",    # 🔵 Filter Mail
    BTN_GC_CHANGE: "danger",     # 🔴 Change Mail

    # ── Deposit Methods (নীল / প্রাইমারি) ──
    BTN_BKASH: "danger",         # 🔴 bKash (Pink/Red)
    BTN_NAGAD: "primary",        # 🔵 Nagad (Blue)
    BTN_BINANCE: "primary",      # 🔵 Binance (Blue)

    # ── AI Support FAQ Topics ──
    BTN_AI_HOW_BUY: "danger",      # 🔴 How to Buy (Red)
    BTN_AI_HOW_DEPOSIT: "primary", # 🔵 How to Deposit (Blue)
    BTN_AI_STOCK: "danger",        # 🔴 Check Stock (Red)
    BTN_AI_REFERRAL: "success",    # 🟢 Referral Info (Green)
    BTN_AI_ORDERS: "primary",      # 🔵 My Orders (Blue)
    BTN_AI_2FA: "success",         # 🟢 2FA Help (Green)
    BTN_AI_MAIL: "danger",         # 🔴 Mail Codes (Red)
    BTN_AI_ASK: "success",         # 🟢 Ask a Question (Green)

    # ── Purchase Actions (লাল / ডেঞ্জার) ──
    BTN_CONFIRM: "danger",       # 🔴 Confirm Purchase (Red)
    BTN_COUPON: "success",       # 🟢 Apply Coupon (Green)

    # ── Duration & Packages ──
    BTN_1DAY: "danger",          # 🔴 1 Day
    BTN_7DAYS: "danger",         # 🔴 7 Days
    BTN_30DAYS: "danger",        # 🔴 30 Days
    BTN_90DAYS: "danger",        # 🔴 90 Days
    BTN_CUSTOM: "danger",        # 🔴 Custom

    # ── User Panel Enhancement ──
    BTN_TRENDING: "danger",      # 🔴 Trending
    BTN_FAVORITES: "success",    # 🟢 Favorites
    BTN_SEARCH: "primary",       # 🔵 Search
    BTN_MY_STATS: "primary",     # 🔵 My Stats

    # ── Categories (লাল / ক্রয় অপশন) ──
    BTN_CAT_MAIL: "danger",      # 🔴 Mail
    BTN_CAT_VPN: "danger",       # 🔴 VPN
    BTN_CAT_PROXY: "danger",     # 🔴 Proxy

    # ── Admin Main Menu ──
    BTN_ADM_DASHBOARD: "primary",    # 🔵 Dashboard
    BTN_ADM_PRODUCTS: "danger",      # 🔴 Products
    BTN_ADM_STOCK: "danger",         # 🔴 Stock
    BTN_ADM_USERS: "primary",        # 🔵 Users
    BTN_ADM_DEPOSITS: "primary",     # 🔵 Deposits
    BTN_ADM_VPN_ORDERS: "danger",    # 🔴 VPN Orders
    BTN_ADM_PROXY_ORDERS: "danger",  # 🔴 Proxy Orders
    BTN_ADM_COUPONS: "success",      # 🟢 Coupons
    BTN_ADM_BROADCAST: "primary",    # 🔵 Broadcast
    BTN_ADM_SETTINGS: "primary",     # 🔵 Settings
    BTN_ADM_EXPORT: "primary",       # 🔵 Export Mail Orders
    BTN_ADM_PROXY_PKGS: "danger",    # 🔴 Data Packages
    BTN_ADM_ORDER_LOOKUP: "primary", # 🔵 Order Lookup
    BTN_ADM_ANALYTICS: "primary",    # 🔵 Analytics

    # ── Admin Sub-menus ──
    BTN_ADM_ORDERS_MENU: "primary",  # 🔵 Orders
    BTN_ADM_REPORTS_MENU: "primary", # 🔵 Reports
    BTN_ADM_TOOLS_MENU: "primary",   # 🔵 Tools

    # ── Admin Actions ──
    BTN_ADD_PRODUCT: "danger",       # 🔴 Add Product
    BTN_ADD_STOCK: "danger",         # 🔴 Add Stock
    BTN_PKG_ADD: "danger",           # 🔴 Add Package
    BTN_EDIT_NAME: "primary",        # 🔵 Edit Name
    BTN_EDIT_PRICE: "primary",       # 🔵 Edit Price
    BTN_EDIT_EMOJI: "primary",       # 🔵 Edit Emoji
    BTN_EDIT_DESC: "primary",        # 🔵 Edit Description
    BTN_HIDE_PROD: "danger",         # 🔴 Hide Product
    BTN_SHOW_PROD: "success",        # 🟢 Show Product
    BTN_DELETE: "danger",            # 🔴 Delete
    BTN_CLEAR_STOCK: "danger",       # 🔴 Clear Stock
    BTN_UPLOAD_FILE: "primary",      # 🔵 Upload File
    BTN_MANUAL_ADD: "danger",        # 🔴 Manual Add
    BTN_GET_TEMPLATE: "primary",     # 🔵 Template
    BTN_DOWNLOAD_STOCK: "primary",   # 🔵 Download Stock
    BTN_DOWNLOAD_ALL_STOCK: "primary", # 🔵 Download All
    BTN_IMPORT_ALL_STOCK: "danger",  # 🔴 Import All
    BTN_DOWNLOAD_PRODUCTS: "primary",# 🔵 Download Products
    BTN_IMPORT_PRODUCTS: "danger",   # 🔴 Import Products
    BTN_DELETE_COUPON: "danger",     # 🔴 Delete Coupon
    BTN_CREATE_COUPON: "success",    # 🟢 Create Coupon

    # ── Admin User Actions ──
    BTN_BAN_USER: "danger",          # 🔴 Ban User
    BTN_UNBAN_USER: "success",       # 🟢 Unban User
    BTN_ADD_BAL: "primary",          # 🔵 Add Balance (Blue)
    BTN_REMOVE_BAL: "danger",        # 🔴 Remove Balance
    BTN_ADD_BONUS: "success",        # 🟢 Add Bonus
    BTN_REMOVE_BONUS: "danger",      # 🔴 Remove Bonus
    BTN_BONUS_ALL_USERS: "success",  # 🟢 Bonus All
    BTN_BONUS_TOP10: "primary",      # 🔵 Top 10
    BTN_SEARCH_USER: "primary",      # 🔵 Search User

    # ── Admin FEAT-002 ──
    BTN_ADM_LOW_STOCK: "danger",     # 🔴 Low Stock Alerts
    BTN_ADM_ROLES: "primary",        # 🔵 Admin Roles
    BTN_ADM_EXPORT_TX: "primary",    # 🔵 Export Transactions
    BTN_ADM_STATUS_MGR: "primary",   # 🔵 Service Status
    BTN_ADM_PROFIT: "primary",       # 🔵 Profit Calculator
    BTN_ADM_LOGS: "primary",         # 🔵 Activity Logs
    BTN_ADM_PRICE_SYNC: "primary",   # 🔵 Price Sync
    BTN_ADM_AUTO_IMPORT: "danger",   # 🔴 Auto Import
}

def find_button_style(text: str) -> str:
    if not text:
        return "primary"

    # 1. Direct match in explicit palette dictionary
    if text in BUTTON_EXPLICIT_STYLES:
        return BUTTON_EXPLICIT_STYLES[text]

    clean_text = _unb(text).strip()
    # Check ASCII / plain version in explicit styles
    for btn_k, style_val in BUTTON_EXPLICIT_STYLES.items():
        if _unb(btn_k).strip() == clean_text:
            return style_val

    t = clean_text.lower()

    # 🔴 লাল বাটন (Danger) — মেইল, ভিপিএন, প্রক্সি ক্রয়, Buy, Confirm, Cancel, Delete, Back
    danger_keywords = [
        "buy", "কিনুন", "kinbo", "purchase", "order",
        "mail", "মেইল", "gmail", "vpn", "ভিপিএন", "proxy", "প্রক্সি",
        "confirm", "নিশ্চিত", "cancel", "বাতিল", "reject", "রিজেক্ট",
        "remove", "delete", "ডিলিট", "stop", "exit", "close",
        "back", "পিছনে", "❌", "🔴", "ban", "clear", "hide", "off", "refund",
        "cut", "demote", "custom", "কাস্টম", "stock", "স্টক",
    ]
    if any(k in t for k in danger_keywords):
        return "danger"

    # 🟢 সবুজ বাটন (Success) — 2FA, Referral, Bonus, Coupon, Unban, AI Support
    success_keywords = [
        "2fa", "totp", "authenticator", "referral", "রেফার",
        "bonus", "বোনাস", "coupon", "কুপন", "unban", "approve", "অ্যাপ্রুভ",
        "favorite", "star", "ai support", "ask", "প্রশ্ন", "✅", "🟢",
    ]
    if any(k in t for k in success_keywords):
        return "success"

    # 🔵 নীল বাটন (Primary) — ব্যালেন্স, ডিপোজিট, ওয়ালেট, সার্চ, ইনফো, হিস্ট্রি, মেনু (Default)
    return "primary"

def find_button_emoji(text: str) -> Optional[str]:
    if not text:
        return None
    if text in BUTTON_CUSTOM_EMOJIS:
        return BUTTON_CUSTOM_EMOJIS[text]
    clean_text = _unb(text).strip()
    for btn_k, emoji_val in BUTTON_CUSTOM_EMOJIS.items():
        if _unb(btn_k).strip() == clean_text:
            return emoji_val
    t = clean_text.lower()
    if "express" in t:
        return PREMIUM_EMOJI_IDS["express"]
    if "ipvanish" in t:
        return PREMIUM_EMOJI_IDS["ipvanish"]
    if "nord" in t:
        return PREMIUM_EMOJI_IDS["nord_vpn"]
    if "hotspot" in t or "shield" in t:
        return PREMIUM_EMOJI_IDS["hotspot_shield"]
    if "surfshark" in t:
        return PREMIUM_EMOJI_IDS["surfshark"]
    if "confirm" in t or "নিশ্চিত" in t:
        return PREMIUM_EMOJI_IDS["confirm"]
    if "delete" in t or "ডিলিট" in t:
        return PREMIUM_EMOJI_IDS["delete"]
    if "close" in t or "cancel" in t or "বাতিল" in t or "back" in t:
        return PREMIUM_EMOJI_IDS["close"]
    if "gift" in t or "refer" in t or "bonus" in t or "coupon" in t:
        return PREMIUM_EMOJI_IDS["gift"]
    if "live" in t:
        return PREMIUM_EMOJI_IDS["live"]
    if "admin" in t:
        return PREMIUM_EMOJI_IDS["admin"]
    if "low" in t and "stock" in t:
        return PREMIUM_EMOJI_IDS["balance_low"]
    return None

_orig_kb_init = KeyboardButton.__init__
def _patched_kb_init(self, *args, **kwargs):
    text = kwargs.get("text") or (args[0] if args else "")
    if "style" not in kwargs or not kwargs["style"]:
        kwargs["style"] = find_button_style(text)
    if "icon_custom_emoji_id" not in kwargs or not kwargs["icon_custom_emoji_id"]:
        emoji_id = find_button_emoji(text)
        if emoji_id:
            kwargs["icon_custom_emoji_id"] = str(emoji_id)
    _orig_kb_init(self, *args, **kwargs)
KeyboardButton.__init__ = _patched_kb_init

_orig_inline_init = InlineKeyboardButton.__init__
def _patched_inline_init(self, *args, **kwargs):
    text = kwargs.get("text") or (args[0] if args else "")
    if "style" not in kwargs or not kwargs["style"]:
        kwargs["style"] = find_button_style(text)
    if "icon_custom_emoji_id" not in kwargs or not kwargs["icon_custom_emoji_id"]:
        emoji_id = find_button_emoji(text)
        if emoji_id:
            kwargs["icon_custom_emoji_id"] = str(emoji_id)
    _orig_inline_init(self, *args, **kwargs)
InlineKeyboardButton.__init__ = _patched_inline_init

def _kb(*rows, resize: bool = True, one_time: bool = False) -> ReplyKeyboardMarkup:
    keyboard = []
    for row in rows:
        btn_row = []
        for item in row:
            if isinstance(item, KeyboardButton):
                btn_row.append(item)
            elif isinstance(item, str):
                emoji_id = find_button_emoji(item)
                btn_style = find_button_style(item)
                if emoji_id:
                    btn_row.append(KeyboardButton(text=item, icon_custom_emoji_id=str(emoji_id), style=btn_style))
                else:
                    btn_row.append(KeyboardButton(text=item, style=btn_style))
        keyboard.append(btn_row)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize,
        one_time_keyboard=one_time,
    )

def main_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_BALANCE,   BTN_DEPOSIT],
        [BTN_GET_MAIL,  BTN_TEMP_MAIL],
        [BTN_BUY_VPN,   BTN_BUY_PROXY],
        [BTN_GET_CODE,  BTN_GET_2FA],
        [BTN_HISTORY,   BTN_REFERRAL],
        [BTN_MORE],
        [BTN_SUPPORT,   BTN_AI_SUPPORT],
    )

def banned_user_kb() -> ReplyKeyboardMarkup:
    return _kb([BTN_SUPPORT])

def more_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_TRENDING,  BTN_FAVORITES],
        [BTN_SEARCH,    BTN_MY_STATS],
        [BACK_BTN, HOME_BTN],
    )

def ai_support_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_AI_HOW_BUY,     BTN_AI_HOW_DEPOSIT],
        [BTN_AI_STOCK,       BTN_AI_REFERRAL],
        [BTN_AI_ORDERS,      BTN_AI_2FA],
        [BTN_AI_MAIL,        BTN_AI_ASK],
        [BACK_BTN, HOME_BTN],
    )

def _nav_row() -> List[str]:
    return [BACK_BTN, HOME_BTN]

def is_back_btn(text: str) -> bool:
    if not text:
        return False
    clean = _unb(text).strip().lower()
    return text == BACK_BTN or clean in ("back", "পিছনে", "🔙")

def is_home_btn(text: str) -> bool:
    if not text:
        return False
    clean = _unb(text).strip().lower()
    return text == HOME_BTN or clean in ("home", "হোম", "মেনু", "🏠")

def is_cancel_btn(text: str) -> bool:
    if not text:
        return False
    clean = _unb(text).strip().lower()
    return text == CANCEL_BTN or clean in ("cancel", "বাতিল", "❌")

def resolve_selection_id(text: str, dm: dict) -> Optional[str]:
    """Finds product ID or item ID from user text against a display_map (dm).
    Supports:
    - Exact match
    - Leading/trailing whitespace strip
    - Normalized whitespace match (collapsing multiple spaces)
    - Unicode bold/italic decoded match (_unb)
    - Item index / number selection (e.g. '1', '2', '#1', '1.')
    - Product name / keyword match in key
    """
    if not text or not dm:
        return None
    
    # 1. Exact match
    if text in dm:
        return dm[text]
    
    clean_text = text.strip()
    if clean_text in dm:
        return dm[clean_text]
        
    # 2. Case-insensitive / whitespace normalized match
    norm_text = re.sub(r"\s+", " ", clean_text)
    unb_text = _unb(clean_text).strip()
    unb_norm = re.sub(r"\s+", " ", unb_text).lower()
    
    for k, v in dm.items():
        k_strip = k.strip()
        if k_strip == clean_text:
            return v
        k_norm = re.sub(r"\s+", " ", k_strip)
        if k_norm == norm_text:
            return v
        k_unb = re.sub(r"\s+", " ", _unb(k_strip)).lower()
        if k_unb == unb_norm:
            return v

    # 3. Numeric selection by position (e.g., "1", "2", "#1", "1.")
    num_match = re.match(r"^#?(\d+)\.?$", unb_text)
    if num_match:
        idx = int(num_match.group(1)) - 1
        keys = list(dm.keys())
        if 0 <= idx < len(keys):
            return dm[keys[idx]]

    # 4. Partial substring or product name match
    if unb_norm:
        for k, v in dm.items():
            k_clean = re.sub(r"\s+", " ", _unb(k).strip()).lower()
            if unb_norm in k_clean or k_clean in unb_norm:
                return v

    return None

def products_kb(display_map: dict) -> ReplyKeyboardMarkup:
    rows = [[k] for k in display_map.keys()]
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

DURATION_MAP = {
    BTN_1DAY: 1, BTN_7DAYS: 7,
    BTN_30DAYS: 30, BTN_90DAYS: 90,
    BTN_CUSTOM: -1,
}

def duration_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_1DAY,   BTN_7DAYS],
        [BTN_30DAYS, BTN_90DAYS],
        [BTN_CUSTOM],
        [BACK_BTN, HOME_BTN],
    )

def parse_proxy_data_options(options_str: str) -> List[str]:
    return [o.strip() for o in options_str.split(",") if o.strip()]

def proxy_data_kb(options_str: str = "1 GB,5 GB,10 GB,50 GB") -> ReplyKeyboardMarkup:
    opts = parse_proxy_data_options(options_str)
    rows = []
    for i in range(0, len(opts), 2):
        row = [_b(opts[i])]
        if i + 1 < len(opts):
            row.append(_b(opts[i + 1]))
        rows.append(row)
    rows.append([BTN_PROXY_DATA_CUSTOM])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def parse_data_amount(text: str) -> Tuple[Optional[float], Optional[str]]:
    raw = text.strip()
    clean = raw.upper().replace("GB", "").replace("MB", "").strip()
    try:
        amount = float(clean)
    except ValueError:
        return None, "Valid number লিখুন (e.g. 5 GB বা 500 MB)."
    if amount <= 0:
        return None, "Amount must be positive."
    if amount > 100000:
        return None, "Maximum 100000 GB/MB."
    return amount, None

def confirm_kb() -> ReplyKeyboardMarkup:
    """First confirmation — includes Apply Coupon button (mail flow only)."""
    return _kb([BTN_CONFIRM], [BTN_COUPON], [BACK_BTN, HOME_BTN])

def confirm_final_kb() -> ReplyKeyboardMarkup:
    """Final confirmation — no coupon button (used for 2nd mail confirm, VPN, Proxy)."""
    return _kb([BTN_CONFIRM], [BACK_BTN, HOME_BTN])

def input_kb() -> ReplyKeyboardMarkup:
    return _kb([CANCEL_BTN, HOME_BTN])

def tfa_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh Code", callback_data="tfa_refresh", icon_custom_emoji_id=PREMIUM_EMOJI_IDS["bot_reply"])],
        [
            InlineKeyboardButton(text="⏱️ Timer", callback_data="tfa_timer", icon_custom_emoji_id=PREMIUM_EMOJI_IDS["time"]),
            InlineKeyboardButton(text="🔑 Change Key", callback_data="tfa_setkey", icon_custom_emoji_id=PREMIUM_EMOJI_IDS["bot_reply"]),
        ],
    ])

def tfa_nokey_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Set My Key", callback_data="tfa_setkey", icon_custom_emoji_id=PREMIUM_EMOJI_IDS["bot_reply"])],
    ])

def _totp_secs() -> int:
    return 30 - (int(time.time()) % 30)

def _totp_bar(secs: int) -> str:
    filled = round(secs / 30 * 10)
    return "█" * filled + "░" * (10 - filled)

def _valid_totp_key(key: str) -> bool:
    try:
        pyotp.TOTP(key).now()
        return True
    except Exception:
        return False

def _fmt_totp(code: str) -> str:
    secs = _totp_secs()
    bar  = _totp_bar(secs)
    tfa_title = f"{pem('2fa_2', '2')}{pem('2fa_f', 'F')}A Code"
    urgency = "🔴" if secs <= 8 else ("🟡" if secs <= 16 else "🟢")
    return (
        f"{pem('lock')} <b>✦ Your {tfa_title} ✦</b>\n{_SEP}\n"
        f"  <b><code>  {code[:3]}  {code[3:]}  </code></b>\n"
        f"{_LINE}\n"
        f"  {urgency} Expires in ‣ <b>{secs}s</b>\n"
        f"  [{bar}]"
    )

DEPOSIT_MAP = {
    BTN_BKASH:   "bkash",
    BTN_NAGAD:   "nagad",
    BTN_BINANCE: "binance",
}

def deposit_method_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_BKASH,   BTN_NAGAD],
        [BTN_BINANCE],
        [BACK_BTN, HOME_BTN],
    )

def admin_main_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_ADM_DASHBOARD],
        [BTN_ADM_PRODUCTS,     BTN_ADM_STOCK],
        [BTN_ADM_USERS,        BTN_ADM_DEPOSITS],
        [BTN_ADM_ORDERS_MENU,  BTN_ADM_REPORTS_MENU],
        [BTN_ADM_TOOLS_MENU,   BTN_ADM_SETTINGS],
        [HOME_BTN],
    )

def admin_orders_submenu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_ADM_VPN_ORDERS,   BTN_ADM_PROXY_ORDERS],
        [BTN_ADM_ORDER_LOOKUP, BTN_ADM_EXPORT],
        [BACK_BTN, HOME_BTN],
    )

def admin_reports_submenu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_ADM_ANALYTICS,    BTN_ADM_PROFIT],
        [BTN_ADM_EXPORT_TX,    BTN_ADM_LOGS],
        [BACK_BTN, HOME_BTN],
    )

def admin_tools_submenu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_ADM_LOW_STOCK,    BTN_ADM_STATUS_MGR],
        [BTN_ADM_PRICE_SYNC,   BTN_ADM_AUTO_IMPORT],
        [BTN_ADM_ROLES,        BTN_ADM_BROADCAST],
        [BTN_ADM_COUPONS,      BTN_ADM_PROXY_PKGS],
        [BACK_BTN, HOME_BTN],
    )

def proxy_pkg_manage_kb(options: list) -> ReplyKeyboardMarkup:
    rows = [[_b(o)] for o in options]
    rows.append([BTN_PKG_ADD])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

SETTINGS_MAP = {
    SET_USD_RATE:     ("usd_rate",             float, "Enter BDT per 1 USD (e.g. 125):"),
    SET_BKASH_NUM:    ("bkash_number",          str,   "Enter bKash number:"),
    SET_BKASH_MIN:    ("bkash_min",             float, "Enter minimum bKash deposit in BDT (e.g. 100):"),
    SET_NAGAD_NUM:    ("nagad_number",          str,   "Enter Nagad number:"),
    SET_NAGAD_MIN:    ("nagad_min",             float, "Enter minimum Nagad deposit in BDT (e.g. 150):"),
    SET_BINANCE_UID:  ("binance_uid",           str,   "Enter Binance Pay UID:"),
    SET_BINANCE_MIN:  ("binance_min",           float, "Enter minimum Binance deposit in USD (e.g. 5):"),
    SET_FORCE_JOIN_1: ("force_join_channel",    str,   "Enter channel (e.g. @mychannel) or blank to disable:"),
    SET_FORCE_JOIN_2: ("force_join_channel_2",  str,   "Enter 2nd channel or blank to disable:"),
    SET_SUPPORT_LINK: ("support_username",      str,   "Enter support username (e.g. @support):"),
    SET_GET_2FA_LINK: ("get_2fa_link",          str,   "Enter the Get 2FA URL:"),
    SET_SHOP_NAME:    ("shop_name",             str,   "Enter shop display name:"),
    SET_WELCOME_MSG:  ("welcome_message",       str,   "Enter welcome message text:"),
    SET_LOW_STOCK:    ("low_stock_threshold",   float, "Enter low stock threshold (number):"),
    SET_PROXY_OPTS:   ("proxy_data_options",    str,   "Enter data options separated by commas (e.g. 1 GB,5 GB,10 GB,50 GB).\nAdmin can set any GB/MB values here:"),
    SET_STOCK_EXPORT: ("stock_export_interval", float, "Enter interval in minutes for auto stock export to group (e.g. 30):"),
    SET_REF_BONUS:    ("referral_bonus_pct",    float, "Enter referral bonus % (0-100):"),
    SET_MAINT_MODE:   ("maintenance_mode",      str,   "Enter ON or OFF:"),
    SET_MAINT_MSG:    ("maintenance_message",   str,   "Enter maintenance message text:"),
    SET_BACKUP_INT:   ("backup_interval_hours", float, "Enter backup interval in hours (e.g. 24 for daily, 0 to disable):"),
}

SETTINGS_CATEGORIES = {
    BTN_SET_PAYMENT: [
        SET_USD_RATE, SET_BKASH_NUM, SET_BKASH_MIN,
        SET_NAGAD_NUM, SET_NAGAD_MIN,
        SET_BINANCE_UID, SET_BINANCE_MIN,
    ],
    BTN_SET_CHANNELS: [
        SET_FORCE_JOIN_1, SET_FORCE_JOIN_2, SET_SUPPORT_LINK,
    ],
    BTN_SET_SHOP: [
        SET_SHOP_NAME, SET_WELCOME_MSG, SET_GET_2FA_LINK,
        SET_REF_BONUS, SET_PROXY_OPTS,
    ],
    BTN_SET_SYSTEM: [
        SET_LOW_STOCK, SET_STOCK_EXPORT,
        SET_MAINT_MODE, SET_MAINT_MSG, SET_BACKUP_INT,
    ],
}

def admin_settings_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_SET_PAYMENT, BTN_SET_CHANNELS],
        [BTN_SET_SHOP, BTN_SET_SYSTEM],
        [BACK_BTN, HOME_BTN],
    )

def settings_category_kb(keys: list) -> ReplyKeyboardMarkup:
    rows = [keys[i:i+2] for i in range(0, len(keys), 2)]
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

CATEGORY_MAP = {
    BTN_CAT_MAIL:  "mail",
    BTN_CAT_VPN:   "vpn",
    BTN_CAT_PROXY: "proxy",
}

def admin_category_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_CAT_MAIL],
        [BTN_CAT_VPN],
        [BTN_CAT_PROXY],
        [CANCEL_BTN, HOME_BTN],
    )

def admin_products_kb(products: dict) -> ReplyKeyboardMarkup:
    rows = [
        [f"{p.get('emoji', '🛍️')} {p['name']} {' [HIDDEN]' if p.get('hidden') else ''} [{p.get('category','mail').upper()}] — ${p['price']:.2f}"]
        for pid, p in products.items()
    ]
    rows.append([BTN_ADD_PRODUCT])
    rows.append([BTN_DOWNLOAD_PRODUCTS, BTN_IMPORT_PRODUCTS])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def build_admin_products_dm(products: dict) -> dict:
    return {
        f"{p.get('emoji', '🛍️')} {p['name']} {' [HIDDEN]' if p.get('hidden') else ''} [{p.get('category','mail').upper()}] — ${p['price']:.2f}": pid
        for pid, p in products.items()
    }

def admin_product_actions_kb(hidden: bool, category: str = "mail", delivery_mode: str = "manual") -> ReplyKeyboardMarkup:
    toggle = BTN_SHOW_PROD if hidden else BTN_HIDE_PROD
    rows: list = [
        [BTN_EDIT_NAME,  BTN_EDIT_PRICE],
        [BTN_EDIT_EMOJI, toggle],
        [BTN_EDIT_DESC],
    ]
    if category == "mail" or (category == "proxy" and delivery_mode == "auto"):
        rows.append([BTN_ADD_STOCK])
    if category == "proxy":
        mode_btn = BTN_TOGGLE_MANUAL if delivery_mode == "auto" else BTN_TOGGLE_AUTO
        rows.append([mode_btn])
    rows.append([BTN_DELETE, BACK_BTN])
    rows.append([HOME_BTN])
    return _kb(*rows)

def admin_stock_products_kb(products: dict) -> ReplyKeyboardMarkup:
    rows = [[f"{p.get('emoji', '📦')} {p['name']} · {p.get('stock_count',0)} left"] for p in products.values()]
    rows.append([BTN_DOWNLOAD_ALL_STOCK, BTN_IMPORT_ALL_STOCK])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def build_admin_stock_dm(products: dict) -> dict:
    return {
        f"{p.get('emoji', '📦')} {p['name']} · {p.get('stock_count',0)} left": pid
        for pid, p in products.items()
    }

def admin_stock_actions_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_GET_TEMPLATE, BTN_DOWNLOAD_STOCK],
        [BTN_UPLOAD_FILE, BTN_MANUAL_ADD],
        [BTN_CLEAR_STOCK],
        [BACK_BTN, HOME_BTN],
    )

def admin_user_actions_kb(is_banned: bool) -> ReplyKeyboardMarkup:
    ban_btn = BTN_UNBAN_USER if is_banned else BTN_BAN_USER
    return _kb(
        [ban_btn],
        [BTN_ADD_BAL, BTN_REMOVE_BAL],
        [BTN_ADD_BONUS, BTN_REMOVE_BONUS],
        [BACK_BTN, HOME_BTN],
    )

def admin_users_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_SEARCH_USER],
        [BTN_BONUS_ALL_USERS, BTN_BONUS_TOP10],
        [BACK_BTN, HOME_BTN],
    )


async def _show_user_menu(target: Message, state: FSMContext):
    await state.set_state(AdminFlow.user_menu)
    all_users = await get_all_users()
    adv_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Advanced Search", callback_data="adm_adv_search")]
    ])
    await target.answer(
        f"<b>User Management</b>\n{_SEP}\n"
        f"Total Users: <b>{len(all_users)}</b>\n\nSelect an option:",
        reply_markup=admin_users_menu_kb(),
    )
    await target.answer("Or use advanced search:", reply_markup=adv_kb)


def get_code_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_GC_SET_MAIL,  BTN_GC_CHANGE],
        [BTN_GC_CODES,     BTN_GC_INBOX],
        [BTN_GC_REFRESH,   BTN_GC_FILTER],
        [BACK_BTN, HOME_BTN],
    )

def get_code_filter_kb() -> ReplyKeyboardMarkup:
    rows = []
    row: List[str] = []
    for svc in _DV_SERVICE_LIST:
        row.append(svc)
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def admin_coupons_kb(coupons: list) -> ReplyKeyboardMarkup:
    rows = [[f"🎟️ {c['code']} · {c['discount_pct']:.0f}% · ({c['used_count']}/{c['max_uses']})"] for c in coupons]
    rows.append([BTN_CREATE_COUPON])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def build_coupons_dm(coupons: list) -> dict:
    return {
        f"🎟️ {c['code']} · {c['discount_pct']:.0f}% · ({c['used_count']}/{c['max_uses']})": c["coupon_id"]
        for c in coupons
    }

def admin_coupon_actions_kb() -> ReplyKeyboardMarkup:
    return _kb([BTN_DELETE_COUPON], [BACK_BTN, HOME_BTN])

# In-memory pending state: admin_id → context dict
_pending_fulfill: Dict[int, Dict] = {}   # VPN/Proxy credentials input
_pending_reject:  Dict[int, Dict] = {}   # Deposit reject reason input

def deposit_review_inline(dep_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Approve",      callback_data=f"dep_ok:{dep_id}"),
        InlineKeyboardButton(text="❌ Reject + Reason", callback_data=f"dep_no:{dep_id}"),
    ]])

def order_review_inline(oid: str, kind: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📤 Send Credentials", callback_data=f"{kind}_ok:{oid}"),
        InlineKeyboardButton(text="❌ Cancel & Refund",   callback_data=f"{kind}_no:{oid}"),
    ]])


# ══════════════════════════════════════════════════════════════════
# MIDDLEWARE — Anti-Spam
# ══════════════════════════════════════════════════════════════════

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self):
        self._last: Dict[int, float] = {}
        self._hist: Dict[int, deque] = defaultdict(deque)

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        uid = event.from_user.id if event.from_user else None
        if uid is None or is_admin(uid):
            return await handler(event, data)
        now = time.time()
        if now - self._last.get(uid, 0) < SPAM_COOLDOWN:
            await event.answer(f"Slow down! Wait {SPAM_COOLDOWN:.0f}s between messages.")
            return
        hist = self._hist[uid]
        while hist and now - hist[0] > SPAM_WINDOW:
            hist.popleft()
        if len(hist) >= SPAM_MAX_MSGS:
            await event.answer("Too many messages. Please wait a moment.")
            return
        hist.append(now)
        self._last[uid] = now
        return await handler(event, data)


# ══════════════════════════════════════════════════════════════════
# MIDDLEWARE — Auth  (BUG FIX: also handle CallbackQuery)
# ══════════════════════════════════════════════════════════════════

_maintenance_cache: Dict[str, Any] = {"value": None, "ts": 0.0}

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if not user:
            return await handler(event, data)

        db_user = await create_or_update_user(user.id, user.username or "", user.full_name or "")
        data["db_user"] = db_user

        if db_user.get("is_banned") and not is_admin(user.id):
            # Allow banned users to reach Support handler
            if isinstance(event, Message) and event.text == BTN_SUPPORT:
                return await handler(event, data)
            msg = (
                "<b>Account Banned</b>\n\n"
                "Your account has been banned from this shop.\n"
                "Contact support if you think this is a mistake."
            )
            if isinstance(event, Message):
                await event.answer(msg, reply_markup=banned_user_kb())
            elif isinstance(event, CallbackQuery):
                await event.answer("Account banned.", show_alert=True)
            return

        # Maintenance mode check for non-admin users
        if not is_admin(user.id):
            now = time.time()
            if now - _maintenance_cache["ts"] > 30:
                _settings = await get_settings()
                _maintenance_cache["value"] = _settings
                _maintenance_cache["ts"] = now
            else:
                _settings = _maintenance_cache["value"]
            if str(_settings.get("maintenance_mode", "OFF")).strip().upper() == "ON":
                maint_msg = _settings.get("maintenance_message") or "Bot is under maintenance. Please try again later."
                if isinstance(event, Message):
                    await event.answer(maint_msg)
                elif isinstance(event, CallbackQuery):
                    await event.answer("Bot is under maintenance.", show_alert=True)
                return

        # Force-join check for non-admin users (skip for Support button)
        if not is_admin(user.id):
            if isinstance(event, Message) and event.text == BTN_SUPPORT:
                pass  # Allow support access without force-join
            else:
                try:
                    passed, failed_channels = await check_force_join(data.get("bot") or event.bot, user.id)
                    if not passed:
                        links = []
                        for ch in failed_channels:
                            url = _channel_to_url(ch)
                            links.append(f"  • <a href='{url}'>{ch}</a>"if url else f"  • {ch}")
                        channels_text = "\n".join(links)
                        msg = (
                            f"<b>Join Required!</b>\n\n"
                            f"You must join the following channel(s) to use this bot:\n{channels_text}\n\n"
                            f"After joining, try again."
                        )
                        if isinstance(event, Message):
                            await event.answer(msg, disable_web_page_preview=True)
                        elif isinstance(event, CallbackQuery):
                            await event.answer("Please join required channels first.", show_alert=True)
                        return
                except Exception as e:
                    logger.warning("Force-join check failed: %s", e)

        return await handler(event, data)


# ══════════════════════════════════════════════════════════════════
# HELPER — Force-Join check  (BUG FIX: handle https:// links)
# ══════════════════════════════════════════════════════════════════

def _parse_channel(raw: str) -> str:
    """Convert any channel format to @username or numeric ID."""
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("https://t.me/"):
        handle = raw.split("https://t.me/")[-1].strip("/")
        if handle:
            return f"@{handle}"
    if raw.startswith("@"):
        return raw
    if raw.lstrip("-").isdigit():
        return raw
    return f"@{raw}"


def _channel_to_url(raw: str) -> str:
    """Return a clickable https://t.me/ URL from any channel format."""
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("https://t.me/"):
        return raw
    username = raw.lstrip("@")
    return f"https://t.me/{username}"


def _channel_display_name(raw: str) -> str:
    """Return a short human-readable name for a channel."""
    raw = raw.strip()
    if raw.startswith("https://t.me/"):
        return raw.split("https://t.me/")[-1].strip("/")
    return raw.lstrip("@")


async def check_force_join(bot: Bot, uid: int) -> Tuple[bool, List[str]]:
    settings = await get_settings()
    failed = []
    for key in ("force_join_channel", "force_join_channel_2"):
        raw_ch = (settings.get(key) or "").strip()
        if not raw_ch:
            continue
        ch = _parse_channel(raw_ch)
        if not ch:
            continue
        try:
            m = await bot.get_chat_member(ch, uid)
            if m.status in ("left", "kicked"):
                failed.append(raw_ch)
        except Exception as e:
            logger.warning("Force-join check failed for %s: %s", ch, e)
    return len(failed) == 0, failed


async def send_main_menu(message: Message, state: FSMContext, text: Optional[str] = None, user_id: Optional[int] = None) -> None:
    await state.clear()
    settings = await get_settings()
    uid = user_id or message.from_user.id
    user = await get_user(uid) or {}
    shop_name = settings.get("shop_name", "Neroxa Shop")
    welcome   = settings.get("welcome_message", WELCOME_MSG)
    balance   = user.get("balance", 0)
    first_name = user.get("first_name", message.from_user.first_name)
    display = text or fmt_welcome(shop_name, welcome, first_name, balance, user)
    await message.answer(display, reply_markup=main_menu_kb())


# ══════════════════════════════════════════════════════════════════
# GLOBAL ROUTER — Home (works from ANY state)
# ══════════════════════════════════════════════════════════════════

router_global = Router()

@router_global.message(F.text == HOME_BTN)
async def go_home(message: Message, state: FSMContext):
    # If admin is in admin flow, send them to admin panel instead
    current_state = await state.get_state()
    if is_admin(message.from_user.id) and current_state and current_state.startswith("AdminFlow:"):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    await send_main_menu(message, state)


# ══════════════════════════════════════════════════════════════════
# TEMP MAIL — API Helpers & In-memory store
# ══════════════════════════════════════════════════════════════════

_TEMPMAIL_API = "https://api.internal.temp-mail.io/api/v3"

# In-memory store: uid -> {email, token, seen_ids: set, messages: {short_id: msg_dict}, msg_index: int}
_tempmail_sessions: Dict[int, dict] = {}


def _tempmail_request(url: str, payload: Optional[dict] = None) -> dict:
    headers = {"Content-Type": "application/json", "User-Agent": "NeroxaShopBot/1.0"}
    data = json.dumps(payload).encode() if payload else None
    try:
        req = _urllib_request.Request(url, data=data, headers=headers)
        with _urllib_request.urlopen(req, timeout=12) as res:
            return json.loads(res.read())
    except Exception as e:
        logger.error("TempMail request error: %s", e)
        return {}


_TEMPMAIL_DOMAIN = "bltiwd.com"

async def _tm_get_domains() -> List[str]:
    def _extract(raw) -> List[str]:
        """Recursively extract domain name strings from any API response shape."""
        if isinstance(raw, str):
            return [raw] if raw else []
        if isinstance(raw, dict):
            # {"domains": [...]}  or  {"name": "bltiwd.com"}
            if "name"in raw:
                return [str(raw["name"])]
            for key in ("domains", "data", "list"):
                if key in raw:
                    return _extract(raw[key])
            return []
        if isinstance(raw, list):
            result = []
            for item in raw:
                result.extend(_extract(item))
            return result
        return []

    def _call():
        try:
            url = f"{_TEMPMAIL_API}/domains"
            req = _urllib_request.Request(url, headers={"User-Agent": "NeroxaShopBot/1.0"})
            with _urllib_request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read())
                names = [d for d in _extract(data) if d]
                return names if names else [_TEMPMAIL_DOMAIN]
        except Exception as e:
            logger.error("TempMail domains error: %s", e)
        return [_TEMPMAIL_DOMAIN]
    return await _run(_call)

async def _tm_create_email(domain: str = _TEMPMAIL_DOMAIN) -> Tuple[Optional[str], Optional[str]]:
    def _call():
        r = _tempmail_request(f"{_TEMPMAIL_API}/email/new", {
            "min_name_length": 10,
            "max_name_length": 10,
            "domain": domain,
        })
        return r.get("email"), r.get("token")
    return await _run(_call)


async def _tm_get_inbox(email: str) -> List[dict]:
    def _call():
        url = f"{_TEMPMAIL_API}/email/{email}/messages"
        headers = {"accept": "application/json", "User-Agent": "NeroxaShopBot/1.0"}
        try:
            req = _urllib_request.Request(url, headers=headers)
            with _urllib_request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read())
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error("TempMail inbox error: %s", e)
            return []
    return await _run(_call)


def _tm_strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    for ent, ch in [("&amp;","&"),("&lt;","<"),("&gt;",">"),("&quot;",'"'),("&nbsp;"," "),("&#39;","'")]:
        text = text.replace(ent, ch)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _tm_extract_otp(body: str) -> Optional[str]:
    patterns = [
        r'\b(\d{4,8})\s+is your',
        r'[Cc]ode[:\s]+(\d{4,8})',
        r'OTP[:\s]*(\d{4,8})',
        r'[Vv]erification code[:\s]*(\d{4,8})',
        r'\b([A-Z0-9]{6,10})\b',
    ]
    for pat in patterns:
        m = re.search(pat, body[:1000])
        if m:
            return m.group(1)
    return None


def _tm_format_body(body_text: str, body_html: str) -> str:
    body = (body_text or "").strip() or _tm_strip_html(body_html or "")
    if not body:
        return "<i>No content</i>"
    otp = _tm_extract_otp(body)
    preview = body[:2000]
    result = f"<pre>{html_lib.escape(preview)}</pre>"
    if len(body) > 2000:
        result += "\n<i>… truncated</i>"
    if otp:
        result += f"\n\n <b>Code detected:</b> <code>{html_lib.escape(otp)}</code>"
    return result


def _tm_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [_TM_GEN],
        [_TM_INB, _TM_REF],
        [_TM_MY,  _TM_DEL],
        [_TM_DOM, _TM_RND],
        [BACK_BTN, HOME_BTN],
    )

def _tm_domain_kb(domains: List[str]) -> ReplyKeyboardMarkup:
    rows = [[_TM_RND]]                                         # Random at top
    rows += [domains[i:i+2] for i in range(0, min(len(domains), 16), 2)]
    rows.append([BACK_BTN])
    return _kb(*rows)


# ══════════════════════════════════════════════════════════════════
# ROUTER — Start & Main Menu
# ══════════════════════════════════════════════════════════════════

router_start = Router()


@router_start.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    if is_admin(message.from_user.id):
        await state.set_state(AdminFlow.menu)
        await message.answer(
            f"{pem('admin')} <b>✦ Admin Control Panel ✦</b>\n{_SEP}\n  Welcome back, Administrator! 🔐",
            reply_markup=admin_main_kb(),
        )
        return
    # Note: Middleware also checks force-join, but /start provides richer onboarding UX with inline join buttons
    passed, failed_channels = await check_force_join(message.bot, message.from_user.id)
    if not passed:
        try:
            bot_info = await message.bot.get_me()
            bot_username = bot_info.username
        except Exception:
            bot_username = None
        buttons = [
            [InlineKeyboardButton(
                text=f" {_channel_display_name(ch)} — Join Now",
                url=_channel_to_url(ch),
            )]
            for ch in failed_channels
        ]
        if bot_username:
            buttons.append([InlineKeyboardButton(
                text="I Joined — Check Again",
                url=f"https://t.me/{bot_username}?start=check",
            )])
        await message.answer(
            f"{pem('warn')} <b>✦ Channel Membership Required ✦</b>\n{_SEP}\n"
            f"  You must join our official channel(s) to access the shop.\n"
            f"{_LINE}\n"
            f"  ‣ Join the channel(s) below, then press\n"
            f"  <b>I Joined — Check Again ✅</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return
    # ── Handle referral deep link ──
    args = message.text.split(maxsplit=1)
    ref_uid = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            ref_uid = int(args[1][4:])
        except (ValueError, IndexError):
            ref_uid = None
    if ref_uid and ref_uid != message.from_user.id:
        existing_user = await get_user(message.from_user.id)
        if existing_user is None:
            await create_or_update_user(
                message.from_user.id,
                message.from_user.username or "",
                message.from_user.full_name or "",
            )
            referrer = await get_user(ref_uid)
            if referrer:
                ref_info = await get_referral_info(message.from_user.id)
                if not ref_info.get("referred_by"):
                    await set_referrer(message.from_user.id, ref_uid)
    await send_main_menu(message, state)


@router_start.message(F.text == BTN_BALANCE)
async def show_balance(message: Message):
    user = await get_user(message.from_user.id) or {}
    await message.answer(fmt_balance_screen(user), reply_markup=main_menu_kb())


@router_start.message(F.text == BTN_REFERRAL)
async def show_referral(message: Message):
    uid = message.from_user.id
    ref_info = await get_referral_info(uid)
    try:
        bot_info = await message.bot.get_me()
        bot_username = bot_info.username
    except Exception:
        bot_username = "bot"
    link = f"https://t.me/{bot_username}?start=ref_{uid}"
    await message.answer(
        f"{pem('gift')} <b>✦ Referral Program ✦</b>\n{_SEP}\n"
        f"  Share your link & earn Bonus Balance on every purchase!\n"
        f"  <i>Bonus Balance can be used as a discount on future purchases.</i>\n"
        f"{_LINE}\n"
        f"  {pem('link')} Your Referral Link:\n"
        f"  <code>{link}</code>\n"
        f"{_LINE}\n"
        f"  {pem('user')} Total Referred ‣ <b>{ref_info.get('referred_count', 0)}</b>\n"
        f"  {pem('money')} Bonus Earned ‣ <b>${ref_info.get('total_earned', 0.0):.2f}</b>",
        reply_markup=main_menu_kb(),
    )


@router_start.message(F.text == BTN_GET_CODE)
async def get_code(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    status  = f"<code>{html_lib.escape(session['email'])}</code>"if session else "No mail set"
    await state.set_state(UserFlow.get_code_menu)
    await message.answer(
        f"<b>Get Code — Mail Inbox</b>\n{_SEP}\n"
        f"Current mail: {status}\n\n"
        f"Use the buttons below to manage your mailbox.",
        reply_markup=get_code_menu_kb(),
    )


# ── Get Code sub-menu handlers ─────────────────────────────────────

@router_start.message(UserFlow.get_code_menu, F.text == BACK_BTN)
async def gc_back(message: Message, state: FSMContext):
    await send_main_menu(message, state)


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_SET_MAIL)
async def gc_set_mail(message: Message, state: FSMContext):
    await state.set_state(UserFlow.get_code_set)
    await message.answer(
        f"<b>Set Mail</b>\n{_SEP}\n"
        f"Send your account data in format:\n\n"
        f"<code>email|password|refresh_token|client_id</code>\n\n"
        f"Or just:\n<code>email|password</code>\n\n"
        f"(OAuth2 will be auto-fetched if not provided)\n\n"
        f"Press {BACK_BTN} to cancel.",
        reply_markup=input_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_CHANGE)
async def gc_change_mail(message: Message, state: FSMContext):
    uid = message.from_user.id
    if uid in _mail_sessions:
        del _mail_sessions[uid]
    await state.set_state(UserFlow.get_code_set)
    await message.answer(
        f"<b>Change Mail</b>\n{_SEP}\n"
        f"Session cleared! Send new account data:\n\n"
        f"<code>email|password|refresh_token|client_id</code>\n\n"
        f"Press {BACK_BTN} to cancel.",
        reply_markup=input_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_CODES)
async def gc_get_codes(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(
            f"<b>No mail set!</b>\n{_SEP}\nPress <b> Set Mail</b> first.",
            reply_markup=get_code_menu_kb(),
        )
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"<b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"<code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Your mail was auto-set but OAuth2 token is missing.\n"
            f"Press <b> Set Mail</b> and enter:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    wait = await message.answer(f"Fetching codes for <code>{html_lib.escape(session['email'])}</code>…")
    all_msgs: List[dict] = []
    code_data = await _dv_get_code(session["email"], session["refresh_token"], session["client_id"], "all")
    if code_data and code_data.get("status") and code_data.get("code"):
        svc = _dv_determine_service(code_data.get("content", ""), "", "")
        all_msgs.append({"code": code_data["code"], "service": svc,
                         "subject": code_data.get("content", ""), "sender": "",
                         "date": code_data.get("date", ""), "address": ""})
    msgs = await _dv_get_messages(session["email"], session["refresh_token"], session["client_id"])
    if msgs and msgs.get("status"):
        existing = {m["code"] for m in all_msgs}
        for c in _dv_extract_codes(msgs):
            if c["code"] not in existing:
                all_msgs.append(c)
                existing.add(c["code"])
    if not all_msgs:
        msgs2 = await _dv_graph_messages(session["email"], session["refresh_token"], session["client_id"])
        if msgs2 and msgs2.get("status"):
            all_msgs = _dv_extract_codes(msgs2)
    display = _dv_build_codes_display(all_msgs)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(f"<code>{html_lib.escape(session['email'])}</code>\n{display}"),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_INBOX)
async def gc_read_inbox(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(f"<b>No mail set!</b>\n{_SEP}\nPress <b> Set Mail</b> first.", reply_markup=get_code_menu_kb())
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"<b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"<code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Press <b> Set Mail</b> and enter full credentials:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    wait = await message.answer(f"Reading <code>{html_lib.escape(session['email'])}</code>…")
    messages = await _dv_process_mailbox(session)
    display  = _dv_build_mailbox_display(messages)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(
            f"<code>{html_lib.escape(session['email'])}</code>\n"
            f"<code>{html_lib.escape(session['password'])}</code>\n{display}"
        ),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_REFRESH)
async def gc_refresh(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(f"<b>No mail set!</b>\n{_SEP}\nPress <b> Set Mail</b> first.", reply_markup=get_code_menu_kb())
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"<b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"<code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Press <b> Set Mail</b> and enter full credentials:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    wait = await message.answer(f"Refreshing <code>{html_lib.escape(session['email'])}</code>…")
    messages = await _dv_process_mailbox(session)
    display  = _dv_build_mailbox_display(messages)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(f"<b>Refreshed!</b>\n\n <code>{html_lib.escape(session['email'])}</code>\n{display}"),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_FILTER)
async def gc_show_filter(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(f"<b>No mail set!</b>\n{_SEP}\nPress <b> Set Mail</b> first.", reply_markup=get_code_menu_kb())
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"<b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"<code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Press <b> Set Mail</b> and enter full credentials:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    await state.set_state(UserFlow.get_code_filter)
    await state.update_data(gc_email=session["email"])
    await message.answer(
        f"<b>Filter by Service</b>\n{_SEP}\n <code>{html_lib.escape(session['email'])}</code>\n\nSelect a service:",
        reply_markup=get_code_filter_kb(),
    )


@router_start.message(UserFlow.get_code_set)
async def gc_receive_mail_data(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.set_state(UserFlow.get_code_menu)
        uid     = message.from_user.id
        session = _mail_sessions.get(uid)
        status  = f"<code>{html_lib.escape(session['email'])}</code>"if session else "No mail set"
        await message.answer(
            f"<b>Get Code — Mail Inbox</b>\n{_SEP}\nCurrent mail: {status}",
            reply_markup=get_code_menu_kb(),
        )
        return
    text = message.text or ""
    if "|"not in text:
        await message.answer("Invalid format. Use: <code>email|password|refresh_token|client_id</code>", reply_markup=input_kb())
        return
    parsed = _dv_parse_input(text)
    if not parsed["email"]:
        await message.answer("Invalid format. Use: <code>email|password</code>", reply_markup=input_kb())
        return
    wait = await message.answer(f"Processing <code>{html_lib.escape(parsed['email'])}</code>…")
    if not parsed["has_oauth2"]:
        oauth2 = await _dv_oauth2(parsed["email"], parsed["password"])
        if not oauth2:
            await _safe_delete(wait)
            await message.answer(
                f"Failed to get OAuth2 for <code>{html_lib.escape(parsed['email'])}</code>\n\n"
                f"Check credentials or top up your Dongvan balance.\nTry again:",
                reply_markup=input_kb(),
            )
            return
        parsed["refresh_token"] = oauth2["refresh_token"]
        parsed["client_id"]     = oauth2["client_id"]
    uid = message.from_user.id
    _mail_sessions[uid] = {
        "email": parsed["email"], "password": parsed["password"],
        "refresh_token": parsed["refresh_token"], "client_id": parsed["client_id"],
    }
    msgs    = await _dv_process_mailbox(_mail_sessions[uid])
    display = _dv_build_mailbox_display(msgs)
    cid_raw = parsed["client_id"] or ""
    cid_p   = cid_raw[:20] + "…"if len(cid_raw) > 20 else cid_raw
    await _safe_delete(wait)
    await state.set_state(UserFlow.get_code_menu)
    await message.answer(
        _truncate_msg(
            f"<b>Mail Set Successfully!</b>\n{_SEP}\n"
            f"<code>{html_lib.escape(parsed['email'])}</code>\n"
            f"<code>{html_lib.escape(cid_p)}</code>\n\n{display}"
        ),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_filter)
async def gc_filter_selected(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(UserFlow.get_code_menu)
        uid     = message.from_user.id
        session = _mail_sessions.get(uid)
        status  = f"<code>{html_lib.escape(session['email'])}</code>"if session else "No mail set"
        await message.answer(f"<b>Get Code — Mail Inbox</b>\n{_SEP}\nCurrent mail: {status}", reply_markup=get_code_menu_kb())
        return
    filter_svc = message.text.strip().upper()
    if filter_svc not in _DV_SERVICE_KEYWORDS:
        await message.answer("Select a service from the keyboard.", reply_markup=get_code_filter_kb())
        return
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await state.set_state(UserFlow.get_code_menu)
        await message.answer("Session expired. Please set mail again.", reply_markup=get_code_menu_kb())
        return
    wait     = await message.answer(f"Filtering <b>{filter_svc}</b> in <code>{html_lib.escape(session['email'])}</code>…")
    messages = await _dv_process_mailbox(session)
    display  = _dv_build_mailbox_display(messages, filter_svc)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(f"<code>{html_lib.escape(session['email'])}</code>\n{display}"),
        reply_markup=get_code_filter_kb(),
    )


async def _show_2fa(message: Message) -> None:
    """Shared logic for BTN_GET_2FA button and /get2fa command."""
    uid    = message.from_user.id
    secret = await get_totp_secret(uid)
    if not secret:
        await message.answer(
            f"{pem('lock')} <b>✦ 2FA Code Generator ✦</b>\n{_SEP}\n"
            f"  You haven't set a secret key yet.\n"
            f"{_LINE}\n"
            f"  ‣ Press <b>Set My Key</b> below to add your TOTP secret.",
            reply_markup=tfa_nokey_kb(),
        )
        return
    try:
        code = pyotp.TOTP(secret).now()
    except Exception:
        await message.answer(
            f"<b>Invalid Key</b>\n{_SEP}\n"
            f"Your saved key appears invalid. Please reset it.",
            reply_markup=tfa_nokey_kb(),
        )
        return
    await message.answer(_fmt_totp(code), reply_markup=tfa_inline_kb())


@router_start.message(F.text == BTN_GET_2FA)
async def get_2fa_btn(message: Message, state: FSMContext):
    await _show_2fa(message)


@router_start.message(Command("get2fa"))
async def get_2fa_cmd(message: Message, state: FSMContext):
    await _show_2fa(message)


@router_start.message(Command("setkey"))
async def cmd_setkey(message: Message, state: FSMContext):
    await state.set_state(UserFlow.set_totp_key)
    await message.answer(
        f"{pem('lock')} <b>✦ Set Your 2FA Secret Key ✦</b>\n{_SEP}\n"
        f"  Enter your <b>Base32 TOTP secret key</b>:\n"
        f"{_LINE}\n"
        f"  Example ‣ <code>JBSWY3DPEHPK3PXP</code>\n\n"
        f"  🔒 Your key is stored securely and used only for code generation.",
        reply_markup=input_kb(),
    )


@router_start.message(Command("timer"))
async def cmd_timer(message: Message):
    secs = _totp_secs()
    bar  = _totp_bar(secs)
    await message.answer(
        f"<b>2FA Timer</b>\n{_SEP}\n"
        f"Current code expires in: <b>{secs} seconds</b>\n"
        f"[{bar}]"
    )


@router_start.message(UserFlow.set_totp_key)
async def receive_totp_key(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.clear()
        await send_main_menu(message, state)
        return
    key = message.text.strip().upper().replace(" ", "")
    if not _valid_totp_key(key):
        await message.answer(
            f"{pem('warn')} <b>✦ Invalid Key ✦</b>\n{_SEP}\n"
            f"  That doesn't appear to be a valid Base32 TOTP secret.\n"
            f"{_LINE}\n"
            f"  ‣ Must contain letters A–Z and digits 2–7 only.\n"
            f"  ‣ Try again or press Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    await set_totp_secret(message.from_user.id, key)
    code = pyotp.TOTP(key).now()
    await state.clear()
    await message.answer(
        f"{pem('ok')} <b>✦ Key Saved Successfully! ✦</b>\n{_SEP}\n"
        f"  🔒 Your 2FA key is stored securely.\n"
        f"{_LINE}\n"
        + _fmt_totp(code),
        reply_markup=tfa_inline_kb(),
    )
    await message.answer("⬇ Use the buttons below or press  Home.", reply_markup=main_menu_kb())


# ── 2FA Callback Queries ──────────────────────────────────────────

@router_start.callback_query(F.data == "tfa_refresh")
async def tfa_cb_refresh(call: CallbackQuery):
    uid    = call.from_user.id
    secret = await get_totp_secret(uid)
    if not secret:
        await call.answer("No key set. Press  Set My Key.", show_alert=True)
        return
    try:
        code = pyotp.TOTP(secret).now()
    except Exception:
        await call.answer("Invalid key. Please reset.", show_alert=True)
        return
    try:
        await call.message.edit_text(_fmt_totp(code), reply_markup=tfa_inline_kb())
    except Exception:
        pass
    await call.answer("Refreshed!")


@router_start.callback_query(F.data == "tfa_timer")
async def tfa_cb_timer(call: CallbackQuery):
    secs = _totp_secs()
    bar  = _totp_bar(secs)
    await call.answer(f" {secs}s remaining\n[{bar}]", show_alert=True)


@router_start.callback_query(F.data == "tfa_setkey")
async def tfa_cb_setkey(call: CallbackQuery, state: FSMContext):
    await state.set_state(UserFlow.set_totp_key)
    await call.message.answer(
        f"{pem('lock')} <b>✦ Set Your 2FA Secret Key ✦</b>\n{_SEP}\n"
        f"  Enter your <b>Base32 TOTP secret key</b>:\n"
        f"{_LINE}\n"
        f"  Example ‣ <code>JBSWY3DPEHPK3PXP</code>\n\n"
        f"  🔒 Your key is stored securely and used only for code generation.",
        reply_markup=input_kb(),
    )
    await call.answer()


@router_start.message(F.text == BTN_SUPPORT)
async def show_support(message: Message):
    settings = await get_settings()
    support = (settings.get("support_username") or SUPPORT_USERNAME).strip()
    support_url = _channel_to_url(support)
    display = _channel_display_name(support)
    await message.answer(
        f"<b>Support</b>\n{_SEP}\n"
        f"Need help? Our support team is ready!\n\n"
        f"Click the button below to open a chat with us. ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Contact {display}", url=support_url)]
        ]),
    )


# ══════════════════════════════════════════════════════════════════
# AI SUPPORT HANDLER
# ══════════════════════════════════════════════════════════════════
# AI SUPPORT HANDLER & SMART KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════

_AI_FAQ = {
    BTN_AI_HOW_BUY: (
        "<b>How to Buy / কেনার নিয়ম</b>\n" + _SEP + "\n"
        "1. মেইন মেনু থেকে ক্যাটাগরি বেছে নিন (Get Mail, Buy VPN, Buy Proxy)।\n"
        "2. আপনার পছন্দের প্রডাক্ট সিলেক্ট করুন।\n"
        "3. কত পিস কিনতে চান সংখ্যা লিখুন।\n"
        "4. কুপন কোড থাকলে দিন অথবা স্কিপ করুন।\n"
        "5. Confirm Purchase বাটনে চাপুন।\n"
        "6. সাথে সাথে প্রডাক্ট আপনার ইনবক্সে ডেলিভারি হয়ে যাবে!\n\n"
        "<i>Note: কেনার পূর্বে আপনার একাউন্টে পর্যাপ্ত ব্যালেন্স আছে কিনা দেখে নিন।</i>"
    ),
    BTN_AI_HOW_DEPOSIT: (
        "<b>How to Deposit / টাকা জমা করার নিয়ম</b>\n" + _SEP + "\n"
        "1. মেইন মেনু থেকে <b>Deposit</b> বাটনে চাপুন।\n"
        "2. পেমেন্ট মেথড সিলেক্ট করুন (bKash, Nagad, অথবা Binance)।\n"
        "3. স্ক্রিনে দেখানো নাম্বারে টাকা বা ডলার সেন্ড মানি করুন।\n"
        "4. আপনি কত টাকা পাঠিয়েছেন সেই পরিমাণ লিখুন।\n"
        "5. আপনার Transaction ID (TrxID) দিন এবং স্ক্রিনশট পাঠান।\n"
        "6. এডমিন চেক করে ৫-১৫ মিনিটের মধ্যে আপনার ব্যালেন্স যুক্ত করে দেবে।"
    ),
    BTN_AI_STOCK: (
        "<b>Check Stock / স্টক চেক</b>\n" + _SEP + "\n"
        "প্রডাক্ট স্টক দেখার নিয়ম:\n"
        "1. Get Mail, Buy VPN অথবা Buy Proxy-তে যান।\n"
        "2. প্রডাক্ট সিলেক্ট করলে রিয়েল-টাইম স্টক সংখ্যা দেখতে পাবেন।\n"
        "3. স্টক 0 হলে প্রডাক্টটি সাময়িকভাবে অফলাইন থাকে।\n\n"
        "এডমিন স্টক রিস্টক করার সাথে সাথে বট স্বয়ংক্রিয়ভাবে আপডেট করে দেয়।"
    ),
    BTN_AI_REFERRAL: (
        "<b>Referral Program / বন্ধুদের ইনভাইট</b>\n" + _SEP + "\n"
        "আপনার রেফারেল লিংক শেয়ার করে ইনকাম করুন:\n"
        "1. মেইন মেনুর <b>Referral</b> বাটনে চাপুন।\n"
        "2. আপনার নিজস্ব রেফারেল লিংকটি কপি করুন।\n"
        "3. বন্ধুদের সাথে শেয়ার করুন।\n"
        "4. আপনার লিংকে যোগ দিয়ে কেনাকাটা করলেই আপনি লাইফটাইম কমিশন বোনাস পাবেন!"
    ),
    BTN_AI_ORDERS: (
        "<b>Order History / আগের অর্ডার</b>\n" + _SEP + "\n"
        "আপনার সব অর্ডার ইতিহাস দেখতে:\n"
        "1. মেইন মেনুর <b>Order History</b> বাটনে চাপুন।\n"
        "2. আপনার সমস্ত Mail, VPN এবং Proxy ক্রয়ের তালিকা দেখতে পাবেন।\n"
        "3. প্রতিটি অর্ডারের ট্রানজেকশন ও ডেলিভারি স্ট্যাটাস দেখা যাবে।"
    ),
    BTN_AI_2FA: (
        "<b>2FA Code Help / টু-ফ্যাক্টর অথেনটিকেশন</b>\n" + _SEP + "\n"
        "টেলিগ্রামেই 2FA কোড পাওয়ার নিয়ম:\n"
        "1. মেইন মেনু থেকে <b>Get 2FA</b> সিলেক্ট করুন।\n"
        "2. আপনার Secret Key বা TOTP Key দিন।\n"
        "3. বট আপনাকে তাৎক্ষণিক ৬ ডিজিটের ভেরিফিকেশন কোড ও টাইমার দেখাবে!\n\n"
        "এটি গুগল অথেনটিকেটরের মতোই ৩০ সেকেন্ড পর পর নতুন কোড জেনারেট করে।"
    ),
    BTN_AI_MAIL: (
        "<b>Mail Codes & Temp Mail / মেইল ও কোড</b>\n" + _SEP + "\n"
        "মেইল ভেরিফিকেশন কোড পাওয়ার নিয়ম:\n"
        "1. মেইন মেনু থেকে <b>Get Code</b> বাটনে চাপুন।\n"
        "2. <b>Set Mail</b> চেপে আপনার মেইল ও পাসওয়ার্ড সেট করুন।\n"
        "3. <b>Get Codes</b> দিয়ে নতুন কোড চেক করুন অথবা <b>Read Inbox</b> দিয়ে মেসেজ পড়ুন।\n"
        "4. অস্থায়ী মেইলের জন্য মেইন মেনুর <b>Temp Mail</b> অপশন ব্যবহার করুন।"
    ),
}

_SMART_AI_RULES = [
    {
        "keys": ["buy", "kinbo", "kivabe", "kinte", "order", "purchase", "kena", "কেনার", "কিনব", "কিনতে", "অর্ডার", "পণ্য", "প্রডাক্ট", "নেব"],
        "answer": (
            "<b>🛍️ How to Buy / কেনার সহজ উপায়:</b>\n" + _SEP + "\n"
            "• মেইন মেনু থেকে আপনার কাঙ্ক্ষিত ক্যাটাগরি (Get Mail / Buy VPN / Buy Proxy) বেছে নিন।\n"
            "• প্রডাক্ট ও পরিমাণ সিলেক্ট করে Confirm Purchase-এ চাপুন।\n"
            "• ব্যালেন্স পর্যাপ্ত থাকলে তাৎক্ষণিক ডেলিভারি পেয়ে যাবেন!"
        )
    },
    {
        "keys": ["deposit", "diposit", "payment", "pay", "taka", "add money", "recharge", "bkash", "nagad", "binance", "টাকা", "ডিপোজিট", "পেমেন্ট", "বিকাশ", "নগদ", "বাইন্যান্স", "ব্যালেন্স", "এড মানি"],
        "answer": (
            "<b>💳 Deposit / টাকা জমার নিয়ম:</b>\n" + _SEP + "\n"
            "• মেইন মেনুর <b>Deposit</b> বাটনে ক্লিক করুন।\n"
            "• bKash, Nagad বা Binance সিলেক্ট করে প্রদত্ত নাম্বারে টাকা পাঠান।\n"
            "• কত টাকা পাঠিয়েছেন এবং TrxID বটের কাছে সাবমিট করুন।\n"
            "• এডমিন যাচাই করে দ্রুত আপনার একাউন্টে ব্যালেন্স যুক্ত করে দেবেন।"
        )
    },
    {
        "keys": ["stock", "available", "restock", "maal", "ache", "স্টক", "মাল", "আছে", "কবে আসবে", "এভেইলেবল"],
        "answer": (
            "<b>📦 Stock Info / স্টক সংক্রান্ত তথ্য:</b>\n" + _SEP + "\n"
            "• Get Mail, Buy VPN বা Buy Proxy-তে গিয়ে যেকোনো প্রডাক্ট সিলেক্ট করলেই বর্তমান স্টক লাইভ দেখা যায়।\n"
            "• স্টক শেষ হলে খুব দ্রুত নতুন স্টক আপলোড করা হয়।"
        )
    },
    {
        "keys": ["mail", "email", "gmail", "outlook", "code", "inbox", "otp", "temp", "মেইল", "জিমেইল", "কোড", "ওটিপি", "ইনবক্স", "টেম্প"],
        "answer": (
            "<b>📧 Mail & Code Help:</b>\n" + _SEP + "\n"
            "• মেইল থেকে কোড আনতে <b>Get Code</b> মেনুতে গিয়ে <b>Set Mail</b> করুন, তারপর <b>Get Codes</b> চাপুন।\n"
            "• অস্থায়ী ওটিপির জন্য <b>Temp Mail</b> বাটন ব্যবহার করতে পারেন।"
        )
    },
    {
        "keys": ["2fa", "totp", "auth", "authenticator", "key", "টু এফ এ", "২এফএ", "অথেনটিকেটর", "সিক্রেট"],
        "answer": (
            "<b>🔑 2FA Authenticator Help:</b>\n" + _SEP + "\n"
            "• মেইন মেনু থেকে <b>Get 2FA</b> বাটন চাপুন।\n"
            "• আপনার 2FA Secret Key পাঠালে সাথে সাথে লাইভ ৬ ডিজিটের ওটিপি কোড পাবেন।"
        )
    },
    {
        "keys": ["vpn", "ভিপিএন"],
        "answer": (
            "<b>🛡️ VPN Services:</b>\n" + _SEP + "\n"
            "• মেইন মেনুর <b>Buy VPN</b> চাপুন, মেয়াদ (১ দিন, ৭ দিন, ৩০ দিন ইত্যাদি) পছন্দ করুন এবং অর্ডার করুন।"
        )
    },
    {
        "keys": ["proxy", "প্রক্সি", "socks5", "http", "residential", "gb", "mb"],
        "answer": (
            "<b>🌐 Proxy Services:</b>\n" + _SEP + "\n"
            "• মেইন মেনুর <b>Buy Proxy</b> অপশনে গিয়ে আপনার প্রয়োজনীয় ডাটা প্যাকেজ সিলেক্ট করে ক্রয় করুন।"
        )
    },
    {
        "keys": ["referral", "refer", "invite", "bonus", "রেফার", "রেফারেল", "বোনাস", "ইনভাইট", "কমিশন"],
        "answer": (
            "<b>🎁 Referral Bonus:</b>\n" + _SEP + "\n"
            "• মেইন মেনু থেকে <b>Referral</b> চেপে আপনার লিংক নিন এবং বন্ধুদের ইনভাইট করে বোনাস উপার্জন করুন।"
        )
    },
    {
        "keys": ["coupon", "discount", "promo", "voucher", "কুপন", "ছাড়", "ডিসকাউন্ট", "প্রোমো"],
        "answer": (
            "<b>🎟️ Coupon & Discount:</b>\n" + _SEP + "\n"
            "• প্রডাক্ট কেনার সময় <b>Apply Coupon</b> বাটনে চাপ দিয়ে এডমিন প্রদত্ত কুপন কোড ব্যবহার করে ছাড় পেতে পারেন।"
        )
    },
    {
        "keys": ["admin", "support", "human", "contact", "help", "এডমিন", "সাপোর্ট", "সাহায্য", "যোগাযোগ", "কথা"],
        "answer": (
            "<b>💬 Support & Helpdesk:</b>\n" + _SEP + "\n"
            "• যেকোনো ব্যক্তিগত সমস্যা বা এডমিনের সাথে কথা বলতে মেইন মেনুর <b>Support</b> বাটন ব্যবহার করুন।"
        )
    },
    {
        "keys": ["hi", "hello", "salam", "assalam", "হাই", "হ্যালো", "সালাম", "আসসালামু"],
        "answer": (
            "<b>👋 Welcome! / স্বাগতম!</b>\n" + _SEP + "\n"
            "আমি আপনার শপ অ্যাসিস্ট্যান্ট এআই। কেনাকাটা, ডিপোজিট, মেইল কোড বা যেকোনো বিষয়ে আপনার প্রশ্ন টাইপ করতে পারেন অথবা নিচের বিষয়গুলো বেছে নিতে পারেন।"
        )
    }
]

def _smart_ai_match(query: str) -> Optional[str]:
    q = query.lower().strip()
    for rule in _SMART_AI_RULES:
        for k in rule["keys"]:
            if k in q:
                return rule["answer"]
    return None


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()  # Railway Variables-এ দিন

async def _ask_gemini_ai(user_question: str) -> Optional[str]:
    """Tries to answer using Gemini API, returns None if API fails."""
    if not GEMINI_API_KEY:
        return None
    prompt = (
        "You are an intelligent, friendly AI Support Assistant for a Telegram Digital Shop Bot. "
        "The shop sells: Gmail, Temp Mail, Mail Code checking, VPNs, Proxies, and 2FA TOTP tools. "
        "Deposit methods: bKash, Nagad, Binance. "
        "Always respond politely and concisely in Bengali (with English key terms). "
        "Do not invent false payment numbers. Keep responses under 100 words.\n\n"
        f"User question: {user_question}"
    )
    for model in ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-2.5-flash", "gemini-flash-latest"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
            }
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        if text:
                            return text.strip()
        except Exception:
            continue
    return None


@router_start.message(F.text == BTN_AI_SUPPORT)
async def show_ai_support(message: Message, state: FSMContext):
    await state.set_state(UserFlow.ai_support)
    await message.answer(
        f"<b>🤖 AI Smart Support</b>\n{_SEP}\n"
        f"যেকোনো তথ্যের জন্য নিচের বাটনে চাপুন অথবা সরাসরি আপনার প্রশ্নটি লিখে পাঠান:\n",
        reply_markup=ai_support_kb(),
    )


@router_start.message(UserFlow.ai_support, F.text.in_([BACK_BTN, HOME_BTN]))
async def ai_support_nav_back(message: Message, state: FSMContext):
    await send_main_menu(message, state)


@router_start.message(UserFlow.ai_support_ask, F.text.in_([BACK_BTN, HOME_BTN]))
async def ai_support_ask_nav_back(message: Message, state: FSMContext):
    await state.set_state(UserFlow.ai_support)
    await message.answer(
        f"<b>🤖 AI Support</b>\n{_SEP}\n"
        f"Choose a topic below or type your question:",
        reply_markup=ai_support_kb(),
    )


@router_start.message(UserFlow.ai_support, F.text == BTN_AI_ASK)
async def ai_ask_question(message: Message, state: FSMContext):
    await state.set_state(UserFlow.ai_support_ask)
    await message.answer(
        f"<b>❓ Ask a Question</b>\n{_SEP}\n"
        f"আপনার প্রশ্নটি বাংলায় বা ইংরেজিতে নিচে টাইপ করে পাঠান:\n\n"
        f"<i>যেমন: \"কীভাবে কিনব?\", \"ডিপোজিট নিয়ম\", \"2FA কোড কিভাবে বের করব?\"</i>",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


@router_start.message(UserFlow.ai_support)
async def ai_support_smart_input(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        return

    # Check exact FAQ buttons
    for btn_key, faq_text in _AI_FAQ.items():
        if text in (btn_key, btn_key.strip(), _b(btn_key.replace("<b>", "").replace("</b>", ""))):
            await message.answer(faq_text, reply_markup=ai_support_kb())
            return

    # 1. Smart local knowledge matching
    matched_answer = _smart_ai_match(text)
    if matched_answer:
        await message.answer(matched_answer, reply_markup=ai_support_kb())
        return

    # 2. Try Gemini AI
    gemini_resp = await _ask_gemini_ai(text)
    if gemini_resp:
        await message.answer(f"<b>🤖 AI Assistant:</b>\n{_SEP}\n{gemini_resp}", reply_markup=ai_support_kb())
        return

    # 3. Fallback to live human support
    settings = await get_settings()
    support = (settings.get("support_username") or SUPPORT_USERNAME).strip()
    support_url = _channel_to_url(support)
    kb_inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Live Human Support", url=support_url)]
    ]) if support_url else None
    await message.answer(
        f"<b>🤖 AI Support Assistant</b>\n{_SEP}\n"
        f"আপনার প্রশ্নটি পুরোপুরি বুঝতে পারিনি। আপনি নিচের মেনু থেকে কোনো বিষয় বেছে নিতে পারেন, "
        f"অথবা সরাসরি আমাদের সাপোর্ট টিমের সাথে কথা বলতে পারেন:",
        reply_markup=kb_inline or ai_support_kb(),
    )


@router_start.message(UserFlow.ai_support_ask)
async def ai_free_question(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        return

    matched_answer = _smart_ai_match(text)
    if matched_answer:
        await message.answer(matched_answer, reply_markup=ai_support_kb())
        await state.set_state(UserFlow.ai_support)
        return

    gemini_resp = await _ask_gemini_ai(text)
    if gemini_resp:
        await message.answer(f"<b>🤖 AI Assistant:</b>\n{_SEP}\n{gemini_resp}", reply_markup=ai_support_kb())
        await state.set_state(UserFlow.ai_support)
        return

    settings = await get_settings()
    support = (settings.get("support_username") or SUPPORT_USERNAME).strip()
    support_url = _channel_to_url(support)
    kb_inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Live Human Support", url=support_url)]
    ]) if support_url else None
    await message.answer(
        f"<b>🤖 AI Support Assistant</b>\n{_SEP}\n"
        f"আপনার প্রশ্নটির নির্দিষ্ট উত্তর খুঁজে পাওয়া যায়নি। অনুগ্রহ করে সহজ ভাষায় আবার লিখে দেখুন অথবা সরাসরি সাপোর্ট লিংকে যোগাযোগ করুন:",
        reply_markup=kb_inline or _kb([BACK_BTN, HOME_BTN]),
    )


@router_start.message(F.text == BTN_HISTORY)
async def order_history(message: Message):
    uid = message.from_user.id
    mail_o, vpn_o, proxy_o = await asyncio.gather(
        get_user_orders(uid), get_user_vpn_orders(uid), get_user_proxy_orders(uid),
    )
    await message.answer(fmt_order_history(mail_o, vpn_o, proxy_o), reply_markup=main_menu_kb())
    deposits = await get_user_deposits(uid)
    if deposits:
        await message.answer(fmt_deposit_history(deposits))


# ══════════════════════════════════════════════════════════════════
# HELPER — Low Stock Alert (shared by mail and proxy flows)
# ══════════════════════════════════════════════════════════════════

async def _check_low_stock_alert(bot: Bot, pid: str, product_name: str) -> None:
    """Send low stock or out-of-stock alert to all admins."""
    try:
        remaining = await get_stock_count(pid)
        settings  = await get_settings()
        threshold = int(settings.get("low_stock_threshold", 5))
        if remaining == 0:
            for adm in ADMIN_IDS:
                try:
                    await bot.send_message(
                        adm,
                        f"{pem('stock_off')} <b>✦ Out of Stock! ✦</b>\n{_SEP}\n"
                        f"  {pem('package')} Product ‣ <b>{product_name}</b>\n"
                        f"  {pem('num')} Remaining ‣ <b>0 units</b>\n"
                        f"{_LINE}\n"
                        f"  ⚠️ Product automatically hidden from users.",
                    )
                except Exception:
                    pass
        elif 0 < remaining <= threshold:
            for adm in ADMIN_IDS:
                try:
                    await bot.send_message(
                        adm,
                        f"{pem('warn')} <b>✦ Low Stock Alert ✦</b>\n{_SEP}\n"
                        f"  {pem('package')} Product ‣ <b>{product_name}</b>\n"
                        f"  {pem('num')} Remaining ‣ <b>{remaining}</b> unit(s)\n"
                        f"{_LINE}\n"
                        f"  ⚡ Please restock soon!",
                    )
                except Exception:
                    pass
    except Exception as _se:
        logger.warning("Low stock alert failed: %s", _se)


# ══════════════════════════════════════════════════════════════════
# ROUTER — User Panel Enhancements
# ══════════════════════════════════════════════════════════════════

router_user_panel = Router()


# ── VIP Badge display helper ──────────────────────────────────────

def _vip_badge_line(total_spent: float) -> str:
    tier_name, tier_emoji = get_vip_tier(total_spent)
    if not tier_name:
        return ""
    return f"{tier_emoji} VIP: <b>{tier_name}</b>"


# ── More Menu ──────────────────────────────────────────────────────

@router_user_panel.message(F.text == BTN_MORE)
async def more_menu_handler(message: Message, state: FSMContext):
    await state.set_state(UserFlow.more_menu)
    await message.answer("<b>More Options</b>", reply_markup=more_menu_kb())


@router_user_panel.message(UserFlow.more_menu, F.text == BACK_BTN)
async def more_menu_back(message: Message, state: FSMContext):
    await state.clear()
    await send_main_menu(message, state)


# ── Trending Services ─────────────────────────────────────────────

@router_user_panel.message(F.text == BTN_TRENDING)
async def show_trending(message: Message):
    orders_data, vpn_data, proxy_data, products = await asyncio.gather(
        db_get("orders"), db_get("vpn_orders"), db_get("proxy_orders"), get_all_products(),
    )
    now = int(time.time())
    week_ago = now - 7 * 86400
    purchase_counts: Dict[str, int] = defaultdict(int)
    for v in (orders_data or {}).values():
        if v.get("created_at", 0) >= week_ago:
            pid = v.get("product_id", "")
            if pid:
                purchase_counts[pid] += v.get("qty", 1)
    for v in (vpn_data or {}).values():
        if v.get("created_at", 0) >= week_ago and v.get("status") != "cancelled":
            pid = v.get("product_id", "")
            if pid:
                purchase_counts[pid] += 1
    for v in (proxy_data or {}).values():
        if v.get("created_at", 0) >= week_ago and v.get("status") != "cancelled":
            pid = v.get("product_id", "")
            if pid:
                purchase_counts[pid] += 1
    if not purchase_counts:
        await message.answer(
            f"<b>Trending Services</b>\n{_SEP}\n"
            f"No trending data yet this week.\nCheck back soon!",
            reply_markup=main_menu_kb(),
        )
        return
    top5 = sorted(purchase_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    lines = [f"<b>Trending Services</b> (Last 7 Days)\n{_SEP}"]
    for rank, (pid, count) in enumerate(top5, 1):
        p = products.get(pid, {})
        name = p.get("name", "Unknown")
        emoji = p.get("emoji", "")
        status_dot = ""if p.get("status", "online") == "online"else ""
        price = p.get("price", 0)
        lines.append(f"\n{rank}. {status_dot} {emoji} <b>{name}</b>")
        lines.append(f"    ${price:.2f} |  {count} purchases")
    await message.answer("\n".join(lines), reply_markup=main_menu_kb())


# ── Favorites ─────────────────────────────────────────────────────

@router_user_panel.message(F.text == BTN_FAVORITES)
async def show_favorites(message: Message, state: FSMContext):
    uid = message.from_user.id
    fav_pids = await get_user_favorites(uid)
    if not fav_pids:
        await message.answer(
            f"\u2B50 <b>My Favorites</b>\n{_SEP}\n"
            f"You have no favorite products yet.\n\n"
            f"Browse products to add favorites!",
            reply_markup=main_menu_kb(),
        )
        return
    products = await get_all_products()
    lines = [f"\u2B50 <b>My Favorites</b>\n{_SEP}"]
    found = False
    for pid in fav_pids:
        p = products.get(pid)
        if not p:
            continue
        found = True
        status_dot = ""if p.get("status", "online") == "online"else ""
        stock = p.get("stock_count", 0)
        emoji = p.get("emoji", "")
        lines.append(f"\n{status_dot} {emoji} <b>{p['name']}</b>")
        lines.append(f"    ${p['price']:.2f} |  {stock} in stock")
    if not found:
        await message.answer(
            f"\u2B50 <b>My Favorites</b>\n{_SEP}\n"
            f"Your favorited products are no longer available.",
            reply_markup=main_menu_kb(),
        )
        return
    await message.answer("\n".join(lines), reply_markup=main_menu_kb())


# ── Advanced Service Search ───────────────────────────────────────

@router_user_panel.message(F.text == BTN_SEARCH)
async def search_start(message: Message, state: FSMContext):
    await state.set_state(UserFlow.search_services)
    await message.answer(
        f"<b>Search Services</b>\n{_SEP}\n"
        f"Type a product name to search.\n"
        f"Example: <i>Gmail, VPN, Proxy</i>\n\n"
        f"Press {HOME_BTN} to cancel.",
        reply_markup=input_kb(),
    )


@router_user_panel.message(UserFlow.search_services)
async def search_query(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.clear()
        await send_main_menu(message, state)
        return
    query = message.text.strip().lower()
    if not query or len(query) < 2:
        await message.answer("Please enter at least 2 characters to search.", reply_markup=input_kb())
        return
    products = await get_all_products()
    results = []
    for pid, p in products.items():
        if p.get("hidden"):
            continue
        name = p.get("name", "").lower()
        desc = p.get("description", "").lower()
        if query in name or query in desc:
            results.append((pid, p))
    if not results:
        await message.answer(
            f"No results for '<b>{html_lib.escape(query)}</b>'\n\nTry a different keyword.",
            reply_markup=input_kb(),
        )
        return
    lines = [f"<b>Search Results</b> for '{html_lib.escape(query)}'\n{_SEP}"]
    for pid, p in results[:10]:
        status_dot = ""if p.get("status", "online") == "online"else ""
        stock = p.get("stock_count", 0)
        emoji = p.get("emoji", "")
        lines.append(f"\n{status_dot} {emoji} <b>{p['name']}</b>")
        lines.append(f"    ${p['price']:.2f} |  {stock} in stock")
    await message.answer("\n".join(lines), reply_markup=main_menu_kb())


# ── Live User Statistics Dashboard ────────────────────────────────

@router_user_panel.message(F.text == BTN_MY_STATS)
async def show_user_stats(message: Message):
    uid = message.from_user.id
    user = await get_user(uid) or {}
    total_spent = user.get("total_spent", 0)
    order_count = user.get("order_count", 0)
    balance = user.get("balance", 0)
    # VIP info
    tier_name, tier_emoji = get_vip_tier(total_spent)
    next_tier, current, next_threshold = get_vip_progress(total_spent)
    # VIP progress bar
    if next_tier == "Max":
        vip_bar = "▓▓▓▓▓▓▓▓▓▓ MAX"
    else:
        pct = min(current / next_threshold, 1.0) if next_threshold > 0 else 0
        filled = round(pct * 10)
        vip_bar = "▓" * filled + "░" * (10 - filled) + f" ${current:.0f}/${next_threshold:.0f}"
    vip_line = f"{tier_emoji} <b>{tier_name}</b>"if tier_name else "No VIP tier yet"
    # Weekly spending
    orders_data, vpn_data, proxy_data = await asyncio.gather(
        db_get("orders"), db_get("vpn_orders"), db_get("proxy_orders"),
    )
    now = int(time.time())
    this_week = now - 7 * 86400
    last_week_start = now - 14 * 86400
    week_spend = 0.0
    last_week_spend = 0.0
    for v in (orders_data or {}).values():
        if v.get("user_id") != uid:
            continue
        ts = v.get("created_at", 0)
        amt = v.get("total_price", 0)
        if ts >= this_week:
            week_spend += amt
        elif ts >= last_week_start:
            last_week_spend += amt
    for src in (vpn_data or {}, proxy_data or {}):
        for v in src.values():
            if v.get("user_id") != uid or v.get("status") == "cancelled":
                continue
            ts = v.get("created_at", 0)
            amt = v.get("price", 0)
            if ts >= this_week:
                week_spend += amt
            elif ts >= last_week_start:
                last_week_spend += amt
    if last_week_spend > 0:
        trend = ((week_spend - last_week_spend) / last_week_spend) * 100
        trend_str = f"{''if trend >= 0 else ''} {trend:+.0f}% vs last week"
    else:
        trend_str = "No comparison data"
    # Favorite category
    cat_counts: Dict[str, int] = defaultdict(int)
    for v in (orders_data or {}).values():
        if v.get("user_id") == uid:
            cat_counts["mail"] += 1
    for v in (vpn_data or {}).values():
        if v.get("user_id") == uid:
            cat_counts["vpn"] += 1
    for v in (proxy_data or {}).values():
        if v.get("user_id") == uid:
            cat_counts["proxy"] += 1
    fav_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "None"
    cat_emojis = {"mail": "", "vpn": "", "proxy": "", "None": ""}
    text = (
        f"<b>My Statistics</b>\n{_SEP}\n\n"
        f"<b>{user.get('full_name', 'User')}</b>\n"
        f"VIP Status: {vip_line}\n"
        f"[{vip_bar}]\n"
        f"{_LINE}\n"
        f"Balance: <b>${balance:.2f}</b>\n"
        f"Total Spent: <b>${total_spent:.2f}</b>\n"
        f"Total Orders: <b>{order_count}</b>\n"
        f"{_LINE}\n"
        f"This Week: <b>${week_spend:.2f}</b>\n"
        f"{trend_str}\n"
        f"{_LINE}\n"
        f"{cat_emojis.get(fav_cat, '')} Favorite Category: <b>{fav_cat.title()}</b>\n"
        f"Member Since: {_dt(user.get('joined_at', int(time.time())))}"
    )
    await message.answer(text, reply_markup=main_menu_kb())


# ══════════════════════════════════════════════════════════════════
# ROUTER — Mail (auto-delivery)
# ══════════════════════════════════════════════════════════════════

router_mail = Router()


@router_mail.message(F.text == BTN_GET_MAIL)
async def mail_start(message: Message, state: FSMContext):
    products = await get_all_products()
    dm = {
        f"{(p.get('emoji') or '📧').strip()} {p['name'].strip()}  ·  ${p['price']:.2f}  ·  {p.get('stock_count',0)} left": pid
        for pid, p in products.items()
        if p.get("category", "mail") == "mail" and not p.get("hidden")
    }
    if not dm:
        await message.answer(
            f"<b>Mail Products</b>\n{_SEP}\n No mail products available right now.\nCheck back later!",
            reply_markup=main_menu_kb(),
        )
        return
    await state.update_data(dm=dm)
    await state.set_state(UserFlow.mail_product)
    await message.answer(fmt_product_list_header("Mail Products", len(dm)), reply_markup=products_kb(dm))


@router_mail.message(UserFlow.mail_product)
async def mail_product_selected(message: Message, state: FSMContext):
    if is_back_btn(message.text) or is_home_btn(message.text):
        await send_main_menu(message, state)
        return
    data = await state.get_data()
    dm   = data.get("dm", {})
    pid  = resolve_selection_id(message.text, dm)
    if not pid:
        # Fallback: re-fetch products in case dm is empty in state
        all_prods = await get_all_products()
        fresh_dm = {
            f"{(p.get('emoji') or '📧').strip()} {p['name'].strip()}  ·  ${p['price']:.2f}  ·  {p.get('stock_count',0)} left": p_id
            for p_id, p in all_prods.items()
            if p.get("category", "mail") == "mail" and not p.get("hidden")
        }
        pid = resolve_selection_id(message.text, fresh_dm)
        if pid:
            dm = fresh_dm
            await state.update_data(dm=dm)
    if not pid:
        await message.answer("Please select a product from the keyboard.", reply_markup=products_kb(dm))
        return
    product = await get_product(pid)
    if not product:
        await message.answer("Product not found.")
        return
    stock = await get_stock_count(pid)
    if stock == 0:
        emoji = product.get("emoji", "")
        await message.answer(
            f"{pem('stock_off')} <b>✦ Out of Stock ✦</b>\n{_SEP}\n"
            f"  {emoji} <b>{product['name']}</b> is currently unavailable.\n"
            f"{_LINE}\n"
            f"  ‣ Please check back later or browse other products.",
            reply_markup=main_menu_kb(),
        )
        await state.clear()
        return
    await state.update_data(pid=pid, product=product, stock=stock)
    await state.set_state(UserFlow.mail_qty)
    await message.answer(fmt_product_detail(product, stock), reply_markup=input_kb())


@router_mail.message(UserFlow.mail_qty)
async def mail_qty_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data = await state.get_data()
        dm = data.get("dm", {})
        await state.set_data({"dm": dm})
        await state.set_state(UserFlow.mail_product)
        await message.answer(
            fmt_product_list_header("Mail Products", len(dm)),
            reply_markup=products_kb(dm),
        )
        return
    data = await state.get_data()
    qty, err = validate_quantity(message.text, data.get("stock", 0))
    if err:
        await message.answer(err)
        return
    pid     = data.get("pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("product", {})
    await state.update_data(product=product)
    total   = round(qty * product.get("price", 0), 4)
    user    = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await state.update_data(qty=qty, total=total, coupon_id=None, discount_pct=0)
    await state.set_state(UserFlow.mail_coupon)
    await message.answer(fmt_order_summary(product, qty, total, balance), reply_markup=confirm_kb())


@router_mail.message(UserFlow.mail_coupon)
async def mail_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data = await state.get_data()
        dm = data.get("dm", {})
        pid = data.get("pid")
        product = data.get("product", {})
        stock = data.get("stock", 0)
        await state.set_data({"dm": dm, "pid": pid, "product": product, "stock": stock})
        await state.set_state(UserFlow.mail_qty)
        await message.answer(fmt_product_detail(product, stock), reply_markup=input_kb())
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.mail_coupon_input)
        await message.answer(
            f"<b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "Please press <b> Confirm Purchase</b> to proceed, or <b> Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data    = await state.get_data()
    product = data.get("product", {})
    qty     = data.get("qty", 1)
    total   = data.get("total", 0)
    await state.set_state(UserFlow.mail_confirm)
    user    = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await message.answer(
        fmt_order_summary(product, qty, total, balance, data.get("discount_pct", 0)) +
        f"\n\n This will deduct <b>${total:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_mail.message(UserFlow.mail_coupon_input)
async def mail_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        dm      = data.get("dm", {})
        pid     = data.get("pid")
        product = data.get("product", {})
        stock   = data.get("stock", 0)
        qty     = data.get("qty", 1)
        total   = data.get("total", 0)
        user    = await get_user(message.from_user.id) or {}
        balance = user.get("balance", 0)
        await state.set_data({"dm": dm, "pid": pid, "product": product, "stock": stock,
                               "qty": qty, "total": total, "coupon_id": None, "discount_pct": 0})
        await state.set_state(UserFlow.mail_coupon)
        await message.answer(
            fmt_order_summary(product, qty, total, balance, 0),
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"Invalid coupon code: <code>{code}</code>\n\nTry again or press  Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press  Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("product", {})
    qty     = data.get("qty", 1)
    disc    = coupon["discount_pct"]
    total   = round(qty * product.get("price", 0) * (1 - disc / 100), 4)
    await state.update_data(coupon_id=coupon["coupon_id"], discount_pct=disc, total=total)
    user    = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await state.set_state(UserFlow.mail_coupon)
    await message.answer(
        f"{pem('ok')} <b>✦ Coupon Applied! ✦</b>\n{_SEP}\n"
        f"  {pem('coupon')} Code ‣ <code>{code.upper()}</code>\n"
        f"  {pem('gift')} Discount ‣ <b>{disc:.0f}% OFF</b>\n"
        f"  {pem('card')} New Total ‣ <b>${total:.2f}</b>\n"
        f"{_LINE}\n"
        f"  ‣ Press {pem('confirm')} <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_mail.message(UserFlow.mail_confirm)
async def mail_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data      = await state.get_data()
        dm        = data.get("dm", {})
        pid       = data.get("pid")
        product   = data.get("product", {})
        stock     = data.get("stock", 0)
        qty       = data.get("qty", 1)
        total     = data.get("total", 0)
        disc      = data.get("discount_pct", 0)
        coupon_id = data.get("coupon_id")
        user      = await get_user(message.from_user.id) or {}
        balance   = user.get("balance", 0)
        await state.set_data({"dm": dm, "pid": pid, "product": product, "stock": stock,
                               "qty": qty, "total": total, "coupon_id": coupon_id, "discount_pct": disc})
        await state.set_state(UserFlow.mail_coupon)
        await message.answer(
            fmt_order_summary(product, qty, total, balance, disc),
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("Press the Confirm Purchase button or Home to cancel.")
        return
    data    = await state.get_data()
    pid     = data.get("pid")
    product = data.get("product")
    qty     = data.get("qty")
    total   = data.get("total")
    if not pid or not product or qty is None or total is None:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    balance = user.get("balance", 0)

    # ── Bonus logic ──
    bonus = await get_bonus(uid)
    bonus_used, remaining_cost = compute_bonus_usage(bonus, pid, total)

    actual_deduct = remaining_cost

    if balance < actual_deduct:
        await state.clear()
        await message.answer(
            f"{pem('warn')} <b>✦ Insufficient Balance ✦</b>\n{_SEP}\n"
            f"  {pem('card')} Required ‣ <b>${total:.2f}</b>\n"
            + (f"  {pem('gift')} Bonus Applied ‣ <b>${bonus_used:.2f}</b>\n" if bonus_used > 0 else "")
            + f"  {pem('diamond')} Your Balance ‣ <b>${balance:.2f}</b>\n"
            f"  📉 Shortfall ‣ <b>${remaining_cost - balance:.2f}</b>\n"
            f"{_LINE}\n"
            f"  ‣ Please make a deposit to continue.",
            reply_markup=main_menu_kb(),
        )
        return
    stock = await get_stock_count(pid)
    if stock < qty:
        await state.clear()
        await message.answer(
            f"{pem('warn')} <b>✦ Stock Limit Reached ✦</b>\n{_SEP}\n"
            f"  Only <b>{stock}</b> unit(s) remaining.\n"
            f"  ‣ Please try a smaller quantity.",
            reply_markup=main_menu_kb(),
        )
        return
    items   = await pop_stock_items(pid, qty)
    # Deduct bonus first, then regular balance for remainder + hidden surcharge
    if bonus_used > 0:
        await use_bonus(uid, bonus_used)
    new_bal = await update_balance(uid, -actual_deduct)
    oid     = await create_order(uid, pid, product["name"], qty, total, items)
    if data.get("coupon_id"):
        await use_coupon(data["coupon_id"])
    # Append to persistent My_Mail_Shop_Orders.xlsx
    try:
        uname = (await get_user(uid) or {}).get("username", "")
        append_to_mail_shop_file(oid, uid, uname, product["name"], qty, total, items, int(time.time()))
    except Exception as _e:
        logger.warning("Mail shop file append failed: %s", _e)
    await state.clear()
    bonus_note = f"\n Paid from Bonus: <b>${bonus_used:.2f}</b>"if bonus_used > 0 else ""
    await message.answer(fmt_order_receipt(oid, product["name"], qty, total, items, new_bal) + bonus_note, reply_markup=main_menu_kb())

    # ── Referral commission ──
    await pay_referral_commission(message.bot, uid, total, oid)

    # ── Auto-set mail session when exactly 1 item is purchased ────────
    if qty == 1 and items:
        first_item = items[0]
        try:
            parsed = _dv_parse_input(first_item)
            if not parsed["email"] and ":"in first_item:
                p = first_item.split(":", 1)
                parsed["email"]    = p[0].strip()
                parsed["password"] = p[1].strip()

            if parsed["email"] and parsed["password"]:
                mail_email    = parsed["email"]
                mail_password = parsed["password"]

                # Attempt to get OAuth2 token automatically
                await message.answer(
                    f"<b>Setting up Get Code access…</b>\n"
                    f"<code>{html_lib.escape(mail_email)}</code>"
                )
                oauth2 = None
                if parsed.get("has_oauth2"):
                    oauth2 = {"refresh_token": parsed["refresh_token"], "client_id": parsed["client_id"]}
                else:
                    try:
                        oauth2 = await _dv_oauth2(mail_email, mail_password)
                    except Exception as _oe:
                        logger.warning("Auto OAuth2 failed: %s", _oe)

                if oauth2:
                    _mail_sessions[uid] = {
                        "email": mail_email, "password": mail_password,
                        "refresh_token": oauth2["refresh_token"],
                        "client_id": oauth2["client_id"],
                    }
                    # Pre-load inbox
                    try:
                        msgs    = await _dv_process_mailbox(_mail_sessions[uid])
                        display = _dv_build_mailbox_display(msgs)
                    except Exception:
                        display = ""
                    await message.answer(
                        _truncate_msg(
                            f"<b>Mail Auto-Set in Get Code!</b>\n{_SEP}\n"
                            f"<code>{html_lib.escape(mail_email)}</code>\n"
                            f"OAuth2:  Ready\n\n"
                            f"Press <b> Get Code</b> to read codes directly.\n"
                            + (f"\n{display}"if display else "")
                        ),
                        reply_markup=main_menu_kb(),
                    )
                else:
                    # Set without OAuth2 — user can complete setup manually
                    _mail_sessions[uid] = {
                        "email": mail_email, "password": mail_password,
                        "refresh_token": "", "client_id": "",
                    }
                    await message.answer(
                        f"<b>Mail Auto-Set!</b>\n{_SEP}\n"
                        f"<code>{html_lib.escape(mail_email)}</code>\n"
                        f"OAuth2:  Not available\n\n"
                        f"Press <b> Get Code</b> → <b> Set Mail</b> and re-enter the mail to activate full access.",
                        reply_markup=main_menu_kb(),
                    )
        except Exception as _ae:
            logger.warning("Auto-set mail session failed: %s", _ae)

    # Send purchased items as xlsx file to the user
    try:
        xlsx_bytes = make_user_order_xlsx(oid, product["name"], qty, total, items)
        date_str   = time.strftime("%Y%m%d_%H%M", time.gmtime())
        filename   = f"order_{oid}_{date_str}.xlsx"
        await message.answer_document(
            document=BufferedInputFile(xlsx_bytes, filename=filename),
            caption=(
                f"<b>Your Accounts File</b>\n{_SEP}\n"
                f" {product['name']} × {qty}\n"
                f"Order: <code>{oid}</code>\n\n"
                f"<i>Open this file to see all your accounts.</i>"
            ),
        )
    except Exception as _xe:
        logger.warning("Failed to send order xlsx to user: %s", _xe)

    # ── Low Stock Auto-Alert ───────────────────────────────────────
    await _check_low_stock_alert(message.bot, pid, product['name'])


# ══════════════════════════════════════════════════════════════════
# ROUTER — VPN
# ══════════════════════════════════════════════════════════════════

router_vpn = Router()


@router_vpn.message(F.text == BTN_BUY_VPN)
async def vpn_start(message: Message, state: FSMContext):
    products = await get_service_products("vpn")
    if not products:
        await message.answer(f"<b>VPN Products</b>\n{_SEP}\n No VPN products available.", reply_markup=main_menu_kb())
        return
    dm = {f"{p.get('emoji','')} {p['name']}  ·  ${p['price']:.2f}/day": pid for pid, p in products.items()}
    await state.update_data(vpn_dm=dm)
    await state.set_state(UserFlow.vpn_product)
    await message.answer(fmt_product_list_header("VPN Products", len(dm)), reply_markup=products_kb(dm))


@router_vpn.message(UserFlow.vpn_product)
async def vpn_product_selected(message: Message, state: FSMContext):
    if is_back_btn(message.text) or is_home_btn(message.text):
        await send_main_menu(message, state)
        return
    data   = await state.get_data()
    vpn_dm = data.get("vpn_dm", {})
    pid    = resolve_selection_id(message.text, vpn_dm)
    if not pid:
        products = await get_service_products("vpn")
        fresh_dm = {f"{(p.get('emoji') or '🛡️').strip()} {p['name'].strip()}  ·  ${p['price']:.2f}/day": p_id for p_id, p in products.items()}
        pid = resolve_selection_id(message.text, fresh_dm)
        if pid:
            vpn_dm = fresh_dm
            await state.update_data(vpn_dm=vpn_dm)
    if not pid:
        await message.answer("Select a product from the keyboard.", reply_markup=products_kb(vpn_dm))
        return
    product = await get_product(pid)
    await state.update_data(vpn_pid=pid, vpn_product=product)
    await state.set_state(UserFlow.vpn_duration)
    await message.answer(
        f"<b>{product['name']}</b>\n{_SEP}\n"
        f"Price: <b>${product['price']:.2f}</b> per day\n\nSelect duration:",
        reply_markup=duration_kb(),
    )


@router_vpn.message(UserFlow.vpn_duration)
async def vpn_duration_selected(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        data   = await state.get_data()
        vpn_dm = data.get("vpn_dm", {})
        await state.set_data({"vpn_dm": vpn_dm})
        await state.set_state(UserFlow.vpn_product)
        await message.answer(fmt_product_list_header("VPN Products", len(vpn_dm)), reply_markup=products_kb(vpn_dm))
        return
    if message.text == BTN_CUSTOM:
        await state.set_state(UserFlow.vpn_custom)
        await message.answer(f"<b>Custom Duration</b>\n{_SEP}\nEnter number of days (1–365):", reply_markup=input_kb())
        return
    days = DURATION_MAP.get(message.text)
    if not days:
        await message.answer("Select a duration from the keyboard.")
        return
    await _vpn_confirm(message, state, days)


@router_vpn.message(UserFlow.vpn_custom)
async def vpn_custom_days(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data    = await state.get_data()
        vpn_dm  = data.get("vpn_dm", {})
        vpn_pid = data.get("vpn_pid")
        prod    = data.get("vpn_product", {})
        await state.set_data({"vpn_dm": vpn_dm, "vpn_pid": vpn_pid, "vpn_product": prod})
        await state.set_state(UserFlow.vpn_duration)
        await message.answer(f"<b>{prod.get('name','')}</b>\n{_SEP}\nSelect duration:", reply_markup=duration_kb())
        return
    days, err = validate_custom_days(message.text)
    if err:
        await message.answer(err)
        return
    await _vpn_confirm(message, state, days)


async def _vpn_confirm(message: Message, state: FSMContext, days: int):
    data    = await state.get_data()
    pid     = data.get("vpn_pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("vpn_product", {})
    await state.update_data(vpn_product=product)
    price   = round(product["price"] * days, 4)
    await state.update_data(vpn_days=days, vpn_price=price, vpn_coupon_id=None, vpn_discount_pct=0)
    await state.set_state(UserFlow.vpn_coupon)
    user = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await message.answer(
        f"<b>Order Summary</b>\n{_SEP}\n"
        f" {product['name']}\n"
        f"Duration: <b>{days} day(s)</b>\n"
        f"Price/day: <b>${product['price']:.2f}</b>\n"
        f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"Your Balance: <b>${balance:.2f}</b>\n\n"
        f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
        reply_markup=confirm_kb(),
    )


@router_vpn.message(UserFlow.vpn_coupon)
async def vpn_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data    = await state.get_data()
        vpn_dm  = data.get("vpn_dm", {})
        vpn_pid = data.get("vpn_pid")
        prod    = data.get("vpn_product", {})
        await state.set_data({"vpn_dm": vpn_dm, "vpn_pid": vpn_pid, "vpn_product": prod})
        await state.set_state(UserFlow.vpn_duration)
        await message.answer(
            f"<b>{prod.get('name', 'VPN')}</b>\n{_SEP}\n"
            f"Price/day: <b>${prod.get('price', 0):.2f}</b>\n\nSelect duration:",
            reply_markup=duration_kb(),
        )
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.vpn_coupon_input)
        await message.answer(
            f"<b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "Please press <b> Confirm Purchase</b> to proceed, or <b> Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data         = await state.get_data()
    product      = data.get("vpn_product", {})
    days         = data.get("vpn_days", 0)
    price        = data.get("vpn_price", 0)
    if not product or not days:
        await send_main_menu(message, state)
        return
    discount_pct = data.get("vpn_discount_pct", 0)
    user         = await get_user(message.from_user.id) or {}
    balance      = user.get("balance", 0)
    disc_line    = f"Coupon: <b>-{discount_pct:.0f}%</b>\n"if discount_pct else ""
    await state.set_state(UserFlow.vpn_confirm)
    await message.answer(
        f"<b>Order Summary</b>\n{_SEP}\n"
        f" {product['name']}\n"
        f"Duration: <b>{days} day(s)</b>\n"
        f"Price/day: <b>${product['price']:.2f}</b>\n"
        f"{disc_line}"
        f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"Your Balance: <b>${balance:.2f}</b>\n\n"
        f"This will deduct <b>${price:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_vpn.message(UserFlow.vpn_coupon_input)
async def vpn_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        vpn_dm  = data.get("vpn_dm", {})
        vpn_pid = data.get("vpn_pid")
        product = data.get("vpn_product", {})
        days    = data.get("vpn_days", 0)
        price   = data.get("vpn_price", 0)
        user    = await get_user(message.from_user.id) or {}
        disc    = 0
        disc_line = ""
        await state.set_data({"vpn_dm": vpn_dm, "vpn_pid": vpn_pid, "vpn_product": product,
                               "vpn_days": days, "vpn_price": price,
                               "vpn_coupon_id": None, "vpn_discount_pct": 0})
        await state.set_state(UserFlow.vpn_coupon)
        await message.answer(
            f"<b>Order Summary</b>\n{_SEP}\n"
            f" {product['name']}\n"
            f"Duration: <b>{days} day(s)</b>\n"
            f"Price/day: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"Invalid coupon code: <code>{code}</code>\n\nTry again or press  Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press  Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("vpn_product", {})
    days    = data.get("vpn_days", 0)
    disc    = coupon["discount_pct"]
    price   = round(product.get("price", 0) * days * (1 - disc / 100), 4)
    await state.update_data(vpn_coupon_id=coupon["coupon_id"], vpn_discount_pct=disc, vpn_price=price)
    user    = await get_user(message.from_user.id) or {}
    await state.set_state(UserFlow.vpn_coupon)
    await message.answer(
        f"<b>Coupon Applied!</b>\n{_SEP}\n"
        f"Code: <code>{code.upper()}</code>\n"
        f"Discount: <b>{disc:.0f}%</b>\n"
        f"New Total: <b>${price:.2f}</b>\n\n"
        f"Press  <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_vpn.message(UserFlow.vpn_confirm)
async def vpn_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data    = await state.get_data()
        product = data.get("vpn_product", {})
        days    = data.get("vpn_days", 0)
        price   = data.get("vpn_price", 0)
        disc    = data.get("vpn_discount_pct", 0)
        disc_line = f"Coupon: <b>-{disc:.0f}%</b>\n"if disc else ""
        user    = await get_user(message.from_user.id) or {}
        await state.set_state(UserFlow.vpn_coupon)
        await message.answer(
            f"<b>Order Summary</b>\n{_SEP}\n"
            f" {product['name']}\n"
            f"Duration: <b>{days} day(s)</b>\n"
            f"Price/day: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("Press the Confirm Purchase button or go back.")
        return
    data    = await state.get_data()
    product = data.get("vpn_product")
    days    = data.get("vpn_days")
    price   = data.get("vpn_price")
    vpn_pid = data.get("vpn_pid")
    if not product or days is None or price is None or not vpn_pid:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    balance = user.get("balance") or 0

    # ── Bonus logic ──
    bonus = await get_bonus(uid)
    bonus_used, remaining_cost = compute_bonus_usage(bonus, vpn_pid, price)

    actual_deduct = remaining_cost

    if balance < actual_deduct:
        await state.clear()
        await message.answer(
            f"<b>Insufficient Balance</b>\n{_SEP}\nRequired: <b>${price:.2f}</b>"
            + (f"  ·   Bonus: <b>${bonus_used:.2f}</b>"if bonus_used > 0 else "")
            + f"  ·  Yours: <b>${balance:.2f}</b>",
            reply_markup=main_menu_kb(),
        )
        return
    if bonus_used > 0:
        await use_bonus(uid, bonus_used)
    await update_balance(uid, -actual_deduct)
    if data.get("vpn_coupon_id"):
        await use_coupon(data["vpn_coupon_id"])
    oid = await create_vpn_order(uid, user.get("username",""), vpn_pid, product["name"], days, price)
    await state.clear()
    bonus_note = f"\n Paid from Bonus: ${bonus_used:.2f}"if bonus_used > 0 else ""
    await message.answer(fmt_service_order_placed("", "VPN", oid, product["name"], days, price) + bonus_note, reply_markup=main_menu_kb())
    # ── Referral commission ──
    await pay_referral_commission(message.bot, uid, price, oid)
    for adm in ADMIN_IDS:
        try:
            await message.bot.send_message(
                adm,
                fmt_admin_vpn_order({"order_id": oid, "user_id": uid, "username": user.get("username",""),
                                     "product_name": product["name"], "duration_days": days,
                                     "price": price, "created_at": int(time.time())}),
                reply_markup=order_review_inline(oid, "vpn"),
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
# ROUTER — Proxy
# ══════════════════════════════════════════════════════════════════

router_proxy = Router()


@router_proxy.message(F.text == BTN_BUY_PROXY)
async def proxy_start(message: Message, state: FSMContext):
    products = await get_service_products("proxy")
    if not products:
        await message.answer(f"<b>Proxy Products</b>\n{_SEP}\n No proxy products available.", reply_markup=main_menu_kb())
        return
    dm = {}
    for pid, p in products.items():
        mode = p.get("delivery_mode", "manual")
        if mode == "auto":
            stock = p.get("stock_count", 0)
            label = f"{p.get('emoji','')} {p['name']}    {stock}  ·  ${p['price']:.2f}"
        else:
            label = f"{p.get('emoji','')} {p['name']}    ·  ${p['price']:.2f}/GB"
        dm[label] = pid
    await state.update_data(proxy_dm=dm)
    await state.set_state(UserFlow.proxy_product)
    await message.answer(fmt_product_list_header("Proxy Products", len(dm)), reply_markup=products_kb(dm))


@router_proxy.message(UserFlow.proxy_product)
async def proxy_product_selected(message: Message, state: FSMContext):
    if is_back_btn(message.text) or is_home_btn(message.text):
        await send_main_menu(message, state)
        return
    data     = await state.get_data()
    proxy_dm = data.get("proxy_dm", {})
    pid      = resolve_selection_id(message.text, proxy_dm)
    if not pid:
        products = await get_service_products("proxy")
        fresh_dm = {}
        for p_id, p in products.items():
            mode = p.get("delivery_mode", "manual")
            if mode == "auto":
                stock = p.get("stock_count", 0)
                label = f"{(p.get('emoji') or '🌐').strip()} {p['name'].strip()}  ·  ${p['price']:.2f}  ·  {stock} left"
            else:
                label = f"{(p.get('emoji') or '🌐').strip()} {p['name'].strip()}  ·  ${p['price']:.2f}/GB"
            fresh_dm[label] = p_id
        pid = resolve_selection_id(message.text, fresh_dm)
        if pid:
            proxy_dm = fresh_dm
            await state.update_data(proxy_dm=proxy_dm)
    if not pid:
        await message.answer("Select a product from the keyboard.", reply_markup=products_kb(proxy_dm))
        return
    product = await get_product(pid)
    await state.update_data(proxy_pid=pid, proxy_product=product)

    if product.get("delivery_mode", "manual") == "auto":
        # ── Auto delivery: ask for quantity like Mail ──────────────
        stock = await get_stock_count(pid)
        if stock == 0:
            await message.answer(
                f"<b>{product['name']}</b>\n{_SEP}\n Out of stock. Try another product.",
                reply_markup=products_kb(data.get("proxy_dm", {})),
            )
            return
        await state.update_data(proxy_stock=stock)
        await state.set_state(UserFlow.proxy_auto_qty)
        await message.answer(
            f"<b>{product['name']}</b>\n{_SEP}\n"
            f"Price: <b>${product['price']:.2f}</b> per item\n"
            f"In Stock: <b>{stock}</b>\n\n"
            f"How many do you want? (1–{stock}):",
            reply_markup=input_kb(),
        )
    else:
        # ── Manual delivery: data amount selection ─────────────────
        settings = await get_settings()
        data_opts = settings.get("proxy_data_options", "1 GB,5 GB,10 GB,50 GB")
        await state.update_data(proxy_data_opts=data_opts)
        await state.set_state(UserFlow.proxy_duration)
        await message.answer(
            f"<b>{product['name']}</b>\n{_SEP}\n"
            f"Price: <b>${product['price']:.2f}</b> per GB\n\nSelect data amount:",
            reply_markup=proxy_data_kb(data_opts),
        )


# ── AUTO PROXY — qty & confirm ──────────────────────────────────────

@router_proxy.message(UserFlow.proxy_auto_qty)
async def proxy_auto_qty_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data     = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts})
        await state.set_state(UserFlow.proxy_product)
        await message.answer(fmt_product_list_header("Proxy Products", len(proxy_dm)), reply_markup=products_kb(proxy_dm))
        return
    data  = await state.get_data()
    stock = data.get("proxy_stock", 0)
    qty, err = validate_quantity(message.text, stock)
    if err:
        await message.answer(err)
        return
    pid     = data.get("proxy_pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("proxy_product", {})
    await state.update_data(proxy_product=product)
    total   = round(qty * product.get("price", 0), 4)
    user    = await get_user(message.from_user.id) or {}
    await state.update_data(proxy_qty=qty, proxy_price=total, proxy_auto_coupon_id=None, proxy_auto_discount_pct=0)
    await state.set_state(UserFlow.proxy_auto_coupon)
    await message.answer(
        f"<b>Order Summary</b>\n{_SEP}\n"
        f" {product['name']}\n"
        f"Quantity: <b>{qty}</b>\n"
        f"Price: <b>${product['price']:.2f}</b> × {qty}\n"
        f"Total: <b>${total:.2f}</b>\n{_LINE}\n"
        f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
        f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_auto_coupon)
async def proxy_auto_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN, HOME_BTN):
        data     = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid = data.get("proxy_pid")
        prod     = data.get("proxy_product", {})
        stock    = data.get("proxy_stock", 0)
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": prod, "proxy_stock": stock})
        await state.set_state(UserFlow.proxy_auto_qty)
        await message.answer(
            fmt_product_detail(prod, stock) if prod else fmt_product_list_header("Proxy Products", len(proxy_dm)),
            reply_markup=input_kb() if prod else products_kb(proxy_dm),
        )
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.proxy_auto_coupon_input)
        await message.answer(
            f"<b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "Please press <b> Confirm Purchase</b> to proceed, or <b> Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data         = await state.get_data()
    product      = data.get("proxy_product", {})
    qty          = data.get("proxy_qty", 1)
    total        = data.get("proxy_price", 0)
    discount_pct = data.get("proxy_auto_discount_pct", 0)
    user         = await get_user(message.from_user.id) or {}
    disc_line    = f"Coupon: <b>-{discount_pct:.0f}%</b>\n"if discount_pct else ""
    await state.set_state(UserFlow.proxy_auto_confirm)
    await message.answer(
        f"<b>Order Summary</b>\n{_SEP}\n"
        f" {product['name']}\n"
        f"Quantity: <b>{qty}</b>\n"
        f"Price: <b>${product['price']:.2f}</b> × {qty}\n"
        f"{disc_line}"
        f"Total: <b>${total:.2f}</b>\n{_LINE}\n"
        f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
        f"This will deduct <b>${total:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_proxy.message(UserFlow.proxy_auto_coupon_input)
async def proxy_auto_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid = data.get("proxy_pid")
        product = data.get("proxy_product", {})
        stock   = data.get("proxy_stock", 0)
        qty     = data.get("proxy_qty", 1)
        total   = data.get("proxy_price", 0)
        user    = await get_user(message.from_user.id) or {}
        disc    = 0
        disc_line = ""
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": product, "proxy_stock": stock,
                               "proxy_qty": qty, "proxy_price": total,
                               "proxy_auto_coupon_id": None, "proxy_auto_discount_pct": 0})
        await state.set_state(UserFlow.proxy_auto_coupon)
        await message.answer(
            f"<b>Order Summary</b>\n{_SEP}\n"
            f" {product['name']}\n"
            f"Quantity: <b>{qty}</b>\n"
            f"Price: <b>${product['price']:.2f}</b> × {qty}\n"
            f"{disc_line}"
            f"Total: <b>${total:.2f}</b>\n{_LINE}\n"
            f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"Invalid coupon code: <code>{code}</code>\n\nTry again or press  Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press  Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("proxy_product", {})
    qty     = data.get("proxy_qty", 1)
    disc    = coupon["discount_pct"]
    total   = round(qty * product.get("price", 0) * (1 - disc / 100), 4)
    await state.update_data(proxy_auto_coupon_id=coupon["coupon_id"], proxy_auto_discount_pct=disc, proxy_price=total)
    user    = await get_user(message.from_user.id) or {}
    await state.set_state(UserFlow.proxy_auto_coupon)
    await message.answer(
        f"{pem('ok')} <b>✦ Coupon Applied! ✦</b>\n{_SEP}\n"
        f"  {pem('coupon')} Code ‣ <code>{code.upper()}</code>\n"
        f"  {pem('gift')} Discount ‣ <b>{disc:.0f}% OFF</b>\n"
        f"  {pem('card')} New Total ‣ <b>${total:.2f}</b>\n"
        f"{_LINE}\n"
        f"  ‣ Press {pem('confirm')} <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_auto_confirm)
async def proxy_auto_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN, HOME_BTN):
        data     = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid = data.get("proxy_pid")
        product  = data.get("proxy_product", {})
        stock    = data.get("proxy_stock", 0)
        qty      = data.get("proxy_qty", 1)
        total    = data.get("proxy_price", 0)
        disc     = data.get("proxy_auto_discount_pct", 0)
        disc_line = f"Coupon: <b>-{disc:.0f}%</b>\n"if disc else ""
        user     = await get_user(message.from_user.id) or {}
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": product, "proxy_stock": stock,
                               "proxy_qty": qty, "proxy_price": total,
                               "proxy_auto_coupon_id": data.get("proxy_auto_coupon_id"),
                               "proxy_auto_discount_pct": disc})
        await state.set_state(UserFlow.proxy_auto_coupon)
        await message.answer(
            f"<b>Order Summary</b>\n{_SEP}\n"
            f" {product.get('name', '')}\n"
            f"Quantity: <b>{qty}</b>\n"
            f"Price: <b>${product.get('price', 0):.2f}</b> × {qty}\n"
            f"{disc_line}"
            f"Total: <b>${total:.2f}</b>\n{_LINE}\n"
            f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("Press the Confirm Purchase button or go back.", reply_markup=confirm_final_kb())
        return
    data    = await state.get_data()
    pid     = data.get("proxy_pid")
    product = data.get("proxy_product", {})
    qty     = data.get("proxy_qty", 1)
    total   = data.get("proxy_price", 0)
    if not pid or not product:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    balance = user.get("balance", 0)

    # ── Bonus logic ──
    bonus = await get_bonus(uid)
    bonus_used, remaining_cost = compute_bonus_usage(bonus, pid, total)

    actual_deduct = remaining_cost

    if balance < actual_deduct:
        await state.clear()
        await message.answer(
            f"{pem('warn')} <b>✦ Insufficient Balance ✦</b>\n{_SEP}\n"
            f"  {pem('card')} Required ‣ <b>${total:.2f}</b>\n"
            + (f"  {pem('gift')} Bonus Applied ‣ <b>${bonus_used:.2f}</b>\n" if bonus_used > 0 else "")
            + f"  {pem('diamond')} Your Balance ‣ <b>${balance:.2f}</b>\n"
            f"  📉 Shortfall ‣ <b>${remaining_cost - balance:.2f}</b>\n"
            f"{_LINE}\n"
            f"  ‣ Please make a deposit to continue.",
            reply_markup=main_menu_kb(),
        )
        return
    stock = await get_stock_count(pid)
    if stock < qty:
        await state.clear()
        await message.answer(
            f"{pem('warn')} <b>✦ Stock Limit Reached ✦</b>\n{_SEP}\n"
            f"  Only <b>{stock}</b> unit(s) remaining.\n"
            f"  ‣ Please try a smaller quantity.",
            reply_markup=main_menu_kb(),
        )
        return

    items   = await pop_stock_items(pid, qty)
    if bonus_used > 0:
        await use_bonus(uid, bonus_used)
    new_bal = await update_balance(uid, -actual_deduct)
    if data.get("proxy_auto_coupon_id"):
        await use_coupon(data["proxy_auto_coupon_id"])
    oid     = await create_proxy_order(uid, user.get("username", ""), pid, product["name"], "Auto", total, items=items)
    await state.clear()

    preview = "\n".join(items[:5])
    more    = f"\n<i>... and {len(items) - 5} more</i>"if len(items) > 5 else ""
    bonus_note = f"\n Paid from Bonus: <b>${bonus_used:.2f}</b>"if bonus_used > 0 else ""
    await message.answer(
        f"<b>Proxy Order Delivered!</b>\n{_SEP}\n"
        f"Order: <code>{oid}</code>\n"
        f" {product['name']} × {qty}\n"
        f"Paid: <b>${total:.2f}</b>\n"
        f"Balance left: <b>${new_bal:.2f}</b>\n{bonus_note}{_SEP}\n"
        f"<b>Your Proxies:</b>\n<code>{preview}{more}</code>",
        reply_markup=main_menu_kb(),
    )

    # Send purchased items as xlsx file to the user
    try:
        xlsx_bytes = make_user_order_xlsx(oid, product["name"], qty, total, items)
        date_str = time.strftime("%Y%m%d_%H%M", time.gmtime())
        filename = f"order_{oid}_{date_str}.xlsx"
        await message.answer_document(
            document=BufferedInputFile(xlsx_bytes, filename=filename),
            caption=(
                f"<b>Your Proxies File</b>\n{_SEP}\n"
                f" {product['name']} \u00d7 {qty}\n"
                f"Order: <code>{oid}</code>\n\n"
                f"<i>Open this file to see all your proxy details.</i>"
            ),
        )
    except Exception as _xe:
        logger.warning("Failed to send proxy order xlsx to user: %s", _xe)

    # Low stock alert
    await _check_low_stock_alert(message.bot, pid, product['name'])

    # ── Referral commission ──
    await pay_referral_commission(message.bot, uid, total, oid)


# ── MANUAL PROXY — duration & confirm ──────────────────────────────

@router_proxy.message(UserFlow.proxy_duration)
async def proxy_duration_selected(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        data            = await state.get_data()
        proxy_dm        = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts})
        await state.set_state(UserFlow.proxy_product)
        await message.answer(fmt_product_list_header("Proxy Products", len(proxy_dm)), reply_markup=products_kb(proxy_dm))
        return
    if message.text == BTN_PROXY_DATA_CUSTOM:
        await state.set_state(UserFlow.proxy_custom)
        await message.answer(f"<b>Custom Data Amount</b>\n{_SEP}\nEnter data amount (e.g. 3 GB, 500 MB):", reply_markup=input_kb())
        return
    data = await state.get_data()
    data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
    all_opts_bold = [f"📦 {_b(o)}" for o in parse_proxy_data_options(data_opts)]
    if message.text not in all_opts_bold:
        await message.answer("Select a data option from the keyboard.")
        return
    raw_label = parse_proxy_data_options(data_opts)[all_opts_bold.index(message.text)]
    await _proxy_confirm(message, state, raw_label)


@router_proxy.message(UserFlow.proxy_custom)
async def proxy_custom_days(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data            = await state.get_data()
        proxy_dm        = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid       = data.get("proxy_pid")
        prod            = data.get("proxy_product", {})
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": prod})
        await state.set_state(UserFlow.proxy_duration)
        await message.answer(f"<b>{prod.get('name','')}</b>\n{_SEP}\nSelect data amount:", reply_markup=proxy_data_kb(proxy_data_opts))
        return
    amount, err = parse_data_amount(message.text)
    if err:
        await message.answer(err)
        return
    raw = message.text.strip()
    unit = "MB"if "MB"in raw.upper() else "GB"
    label = f"{amount:.0f} {unit}"if amount == int(amount) else f"{amount} {unit}"
    await _proxy_confirm(message, state, label)


async def _proxy_confirm(message: Message, state: FSMContext, data_label: str):
    data    = await state.get_data()
    pid     = data.get("proxy_pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("proxy_product", {})
    await state.update_data(proxy_product=product)
    amount, _ = parse_data_amount(data_label)
    amount = amount or 1.0
    price   = round(product.get("price", 0) * amount, 4)
    await state.update_data(proxy_days=data_label, proxy_price=price, proxy_coupon_id=None, proxy_discount_pct=0)
    await state.set_state(UserFlow.proxy_coupon)
    user = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await message.answer(
        f"<b>Order Summary</b>\n{_SEP}\n"
        f" {product['name']}\n"
        f"Data: <b>{data_label}</b>\n"
        f"Price/GB: <b>${product['price']:.2f}</b>\n"
        f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"Your Balance: <b>${balance:.2f}</b>\n\n"
        f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_coupon)
async def proxy_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data            = await state.get_data()
        proxy_dm        = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid       = data.get("proxy_pid")
        prod            = data.get("proxy_product", {})
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": prod})
        await state.set_state(UserFlow.proxy_duration)
        await message.answer(
            f"<b>{prod.get('name', 'Proxy')}</b>\n{_SEP}\n"
            f"Price/GB: <b>${prod.get('price', 0):.2f}</b>\n\nSelect data amount:",
            reply_markup=proxy_data_kb(proxy_data_opts),
        )
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.proxy_coupon_input)
        await message.answer(
            f"<b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "Please press <b> Confirm Purchase</b> to proceed, or <b> Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data         = await state.get_data()
    product      = data.get("proxy_product", {})
    days         = data.get("proxy_days", "")
    price        = data.get("proxy_price", 0)
    if not product or not days:
        await send_main_menu(message, state)
        return
    discount_pct = data.get("proxy_discount_pct", 0)
    user         = await get_user(message.from_user.id) or {}
    balance      = user.get("balance", 0)
    disc_line    = f"Coupon: <b>-{discount_pct:.0f}%</b>\n"if discount_pct else ""
    await state.set_state(UserFlow.proxy_confirm)
    await message.answer(
        f"<b>Order Summary</b>\n{_SEP}\n"
        f" {product['name']}\n"
        f"Data: <b>{days}</b>\n"
        f"Price/GB: <b>${product['price']:.2f}</b>\n"
        f"{disc_line}"
        f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"Your Balance: <b>${balance:.2f}</b>\n\n"
        f"This will deduct <b>${price:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_proxy.message(UserFlow.proxy_coupon_input)
async def proxy_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        product = data.get("proxy_product", {})
        days    = data.get("proxy_days", "")
        price   = data.get("proxy_price", 0)
        user    = await get_user(message.from_user.id) or {}
        disc    = data.get("proxy_discount_pct", 0)
        disc_line = f"Coupon: <b>-{disc:.0f}%</b>\n"if disc else ""
        await state.set_state(UserFlow.proxy_coupon)
        await message.answer(
            f"<b>Order Summary</b>\n{_SEP}\n"
            f" {product['name']}\n"
            f"Data: <b>{days}</b>\n"
            f"Price/GB: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"Invalid coupon code: <code>{code}</code>\n\nTry again or press  Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press  Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("proxy_product", {})
    days    = data.get("proxy_days", "")
    disc    = coupon["discount_pct"]
    amt, _  = parse_data_amount(days)
    amt     = amt or 1.0
    price   = round(product.get("price", 0) * amt * (1 - disc / 100), 4)
    await state.update_data(proxy_coupon_id=coupon["coupon_id"], proxy_discount_pct=disc, proxy_price=price)
    user    = await get_user(message.from_user.id) or {}
    await state.set_state(UserFlow.proxy_coupon)
    await message.answer(
        f"<b>Coupon Applied!</b>\n{_SEP}\n"
        f"Code: <code>{code.upper()}</code>\n"
        f"Discount: <b>{disc:.0f}%</b>\n"
        f"New Total: <b>${price:.2f}</b>\n\n"
        f"Press  <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_confirm)
async def proxy_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data    = await state.get_data()
        product = data.get("proxy_product", {})
        days    = data.get("proxy_days", "")
        price   = data.get("proxy_price", 0)
        disc    = data.get("proxy_discount_pct", 0)
        disc_line = f"Coupon: <b>-{disc:.0f}%</b>\n"if disc else ""
        user    = await get_user(message.from_user.id) or {}
        await state.set_state(UserFlow.proxy_coupon)
        await message.answer(
            f"<b>Order Summary</b>\n{_SEP}\n"
            f" {product['name']}\n"
            f"Data: <b>{days}</b>\n"
            f"Price/GB: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press  Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("Press the Confirm Purchase button or go back.", reply_markup=confirm_final_kb())
        return
    data    = await state.get_data()
    product = data.get("proxy_product", {})
    days    = data.get("proxy_days", "")
    price   = data.get("proxy_price", 0)
    if not product or not days:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    balance = user.get("balance") or 0
    proxy_pid = data.get("proxy_pid", "")

    # ── Bonus logic ──
    bonus = await get_bonus(uid)
    bonus_used, remaining_cost = compute_bonus_usage(bonus, proxy_pid, price)

    actual_deduct = remaining_cost

    if balance < actual_deduct:
        await state.clear()
        await message.answer(
            f"<b>Insufficient Balance</b>\n{_SEP}\nRequired: <b>${price:.2f}</b>"
            + (f"  ·   Bonus: <b>${bonus_used:.2f}</b>"if bonus_used > 0 else "")
            + f"  ·  Yours: <b>${balance:.2f}</b>",
            reply_markup=main_menu_kb(),
        )
        return
    if bonus_used > 0:
        await use_bonus(uid, bonus_used)
    await update_balance(uid, -actual_deduct)
    if data.get("proxy_coupon_id"):
        await use_coupon(data.get("proxy_coupon_id"))
    oid = await create_proxy_order(uid, user.get("username",""), proxy_pid, product.get("name",""), days, price)
    await state.clear()
    bonus_note = f"\n Paid from Bonus: <b>${bonus_used:.2f}</b>"if bonus_used > 0 else ""
    await message.answer(
        f"<b>Proxy Order Placed!</b>\n{_SEP}\n"
        f"Order: <code>{oid}</code>\n"
        f" {product['name']}\n"
        f"Data: <b>{days}</b>\n"
        f"Paid: <b>${price:.2f}</b>\n{bonus_note}{_SEP}\n"
        f"Status: <b>Pending</b>\n"
        f"Our team will deliver your order shortly.\n"
        f"You'll receive a notification when ready. ",
        reply_markup=main_menu_kb()
    )
    # ── Referral commission ──
    await pay_referral_commission(message.bot, uid, price, oid)
    for adm in ADMIN_IDS:
        try:
            await message.bot.send_message(
                adm,
                f"<b>New Proxy Order</b>\n{_SEP}\n"
                f"<code>{oid}</code>\n"
                f" {uid}  @{user.get('username','')}\n"
                f" {product['name']}\n"
                f"Data: <b>{days}</b>\n"
                f" ${price:.2f}\n"
                f" {_dt(int(time.time()))}",
                reply_markup=order_review_inline(oid, "proxy"),
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
# ROUTER — Deposit
# ══════════════════════════════════════════════════════════════════

router_deposit = Router()


@router_deposit.message(F.text == BTN_DEPOSIT)
async def deposit_start(message: Message, state: FSMContext):
    await state.set_state(UserFlow.dep_method)
    user = await get_user(message.from_user.id) or {}
    await message.answer(
        f"{pem('payment')} <b>✦ Add Funds ✦</b>\n{_SEP}\n"
        f"  {pem('diamond')} Current Balance ‣ <b>${user.get('balance',0):.2f}</b>\n"
        f"{_LINE}\n"
        f"  ‣ Choose your preferred payment method:",
        reply_markup=deposit_method_kb(),
    )


@router_deposit.message(UserFlow.dep_method)
async def deposit_method_chosen(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        await send_main_menu(message, state)
        return
    method_key = DEPOSIT_MAP.get(message.text)
    if not method_key:
        await message.answer("Select a payment method from the keyboard.")
        return
    settings = await get_settings()
    if method_key == "bkash":
        number  = settings.get("bkash_number", "")
        min_amt = settings.get("bkash_min", 100)
        label   = "bKash"
    elif method_key == "nagad":
        number  = settings.get("nagad_number", "")
        min_amt = settings.get("nagad_min", 150)
        label   = "Nagad"
    else:
        number  = settings.get("binance_uid", "")
        min_amt = settings.get("binance_min", 5)
        label   = "Binance"
    rate   = settings.get("usd_rate", 125)
    is_usd = (method_key == "binance")
    await state.update_data(method_key=method_key, method_label=label, min_amt=min_amt, rate=rate, is_usd=is_usd, pay_number=number)
    await state.set_state(UserFlow.dep_amount)
    await message.answer(fmt_deposit_info(label, number, rate, min_amt, is_usd), reply_markup=input_kb())


@router_deposit.message(UserFlow.dep_amount)
async def deposit_amount_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        await state.set_state(UserFlow.dep_method)
        await message.answer("Select payment method:", reply_markup=deposit_method_kb())
        return
    data   = await state.get_data()
    is_usd = data.get("is_usd", False)
    if is_usd:
        amount_usd, err = validate_price(message.text)
        if err:
            await message.answer(err)
            return
        if amount_usd <= 0:
            await message.answer("Amount must be positive.")
            return
        if amount_usd < data.get("min_amt", 0):
            await message.answer(f"Minimum Binance deposit is <b>${data.get('min_amt', 0):.2f} USD</b>")
            return
        rate       = data.get("rate") or 125
        amount_bdt = round(amount_usd * rate, 2)
    else:
        amount_bdt, err = validate_amount_bdt(message.text, data.get("min_amt", 0))
        if err:
            await message.answer(err)
            return
        rate = data.get("rate") or 0
        if rate <= 0:
            await message.answer("Exchange rate is not configured. Contact admin.")
            return
        amount_usd = round(amount_bdt / rate, 4)
    await state.update_data(amount_bdt=amount_bdt, amount_usd=amount_usd)
    await state.set_state(UserFlow.dep_trx)
    await message.answer(fmt_deposit_confirm(data.get("method_label", ""), amount_bdt, amount_usd, is_usd), reply_markup=input_kb())


@router_deposit.message(UserFlow.dep_trx)
async def deposit_trx_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data = await state.get_data()
        await state.set_state(UserFlow.dep_amount)
        await message.answer(fmt_deposit_info(data.get("method_label", ""), data.get("pay_number", ""), data.get("rate", 0), data.get("min_amt", 0), data.get("is_usd", False)), reply_markup=input_kb())
        return
    trx = message.text.strip()
    if await check_trx_duplicate(trx):
        await message.answer(
            f"{pem('warn')} <b>✦ Duplicate Transaction ✦</b>\n{_SEP}\n"
            f"  This Transaction ID has already been submitted.\n"
            f"{_LINE}\n"
            f"  ‣ Contact support if you believe this is an error."
        )
        return
    await state.update_data(trx_id=trx)
    await state.set_state(UserFlow.dep_screenshot)
    await message.answer(
        f"{pem('upload')} <b>✦ Upload Payment Screenshot ✦</b>\n{_SEP}\n"
        f"  Please send a <b>clear screenshot</b> of your payment.\n"
        f"{_LINE}\n"
        f"  📸 This helps our team verify your deposit faster.",
        reply_markup=input_kb(),
    )


@router_deposit.message(UserFlow.dep_screenshot)
async def deposit_screenshot(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data = await state.get_data()
        await state.set_state(UserFlow.dep_trx)
        await message.answer(
            f"<b>Transaction ID</b>\n{_SEP}\nPlease enter your TRX ID / Transaction reference:",
            reply_markup=input_kb(),
        )
        return
    if not message.photo:
        await message.answer("Please send a photo/screenshot of your payment.")
        return
    data      = await state.get_data()
    uid       = message.from_user.id
    user      = await get_user(uid) or {}
    photo     = message.photo[-1]
    file_id   = photo.file_id          # Telegram file_id is stored with the deposit

    # Screenshot is kept as the Telegram file_id (permanent for this bot, no external storage)
    screenshot_url = file_id

    method_label = data.get("method_label", "")
    amount_bdt   = data.get("amount_bdt", 0)
    amount_usd   = data.get("amount_usd", 0)
    trx_id       = data.get("trx_id", "")
    dep_id = await create_deposit(
        uid, user.get("username", ""), method_label,
        amount_bdt, amount_usd, trx_id, screenshot_url,
    )
    await state.clear()
    await message.answer(
        fmt_deposit_submitted(dep_id, method_label, amount_bdt, amount_usd, data.get("is_usd", False)),
        reply_markup=main_menu_kb(),
    )
    for adm in ADMIN_IDS:
        try:
            dep = {
                "deposit_id": dep_id, "user_id": uid, "username": user.get("username", ""),
                "method": method_label, "amount_bdt": amount_bdt,
                "amount_usd": amount_usd, "trx_id": trx_id,
                "screenshot_url": screenshot_url, "created_at": int(time.time()),
            }
            text      = fmt_admin_deposit_review(dep)
            kb_inline = deposit_review_inline(dep_id)
            # Send the photo using its Telegram file_id
            await message.bot.send_photo(adm, photo=file_id, caption=text, reply_markup=kb_inline)
        except Exception as ex:
            logger.warning("Admin deposit notify error (uid=%s): %s", adm, ex)
            try:
                await message.bot.send_message(adm, text, reply_markup=kb_inline)
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════
# ROUTER — Temp Mail
# ══════════════════════════════════════════════════════════════════

router_tempmail = Router()

_TM_GEN  = f"⚡ {_b('Generate Email')}"
_TM_INB  = f"📥 {_b('Check Inbox')}"
_TM_REF  = f"🔄 {_b('Refresh')}"
_TM_MY   = f"📧 {_b('My Email')}"
_TM_DEL  = f"🗑️ {_b('Delete Email')}"
_TM_DOM  = f"🌐 {_b('Change Domain')}"
_TM_RND  = f"🎲 {_b('Random Domain')}"
_TM_BTNS = {_TM_GEN, _TM_INB, _TM_REF, _TM_MY, _TM_DEL, _TM_DOM, _TM_RND}


@router_tempmail.message(F.text == BTN_TEMP_MAIL)
async def tempmail_entry(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.set_state(UserFlow.temp_mail_menu)
    sess = _tempmail_sessions.get(uid)
    if sess:
        email = sess.get("email", "")
        txt = (
            f"<b>Temp Mail</b>\n{_SEP}\n"
            f"Active email:\n<code>{html_lib.escape(email)}</code>\n\n"
            f"Choose an action:"
        )
    else:
        txt = (
            f"<b>Temp Mail</b>\n{_SEP}\n"
            f"Get a free disposable email address instantly.\n\n"
            f"Press <b> Generate Email</b> to create one."
        )
    await message.answer(txt, reply_markup=_tm_menu_kb())


@router_tempmail.message(UserFlow.temp_mail_menu, F.text.in_({BACK_BTN, HOME_BTN}))
async def tempmail_back(message: Message, state: FSMContext):
    await send_main_menu(message, state)


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_GEN)
async def tempmail_generate(message: Message, state: FSMContext):
    uid = message.from_user.id
    # use domain saved in session, or default
    chosen_domain = (_tempmail_sessions.get(uid) or {}).get("chosen_domain", _TEMPMAIL_DOMAIN)
    await message.answer(f"Generating email on <b>@{chosen_domain}</b>…")
    email, token = await _tm_create_email(chosen_domain)
    if not email:
        await message.answer("Failed to generate email. Please try again.", reply_markup=_tm_menu_kb())
        return
    _tempmail_sessions[uid] = {
        "email": email, "token": token,
        "chosen_domain": chosen_domain,
        "seen_ids": set(), "messages": {}, "msg_index": 0,
    }
    ts = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    await message.answer(
        f"<b>Email Generated!</b>\n{_SEP}\n"
        f"<code>{html_lib.escape(email)}</code>\n\n"
        f"<i>Tap the address above to copy it</i>\n"
        f"Created: {ts}",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_MY)
async def tempmail_myemail(message: Message, state: FSMContext):
    uid  = message.from_user.id
    sess = _tempmail_sessions.get(uid)
    if not sess:
        await message.answer("No active email. Press <b> Generate Email</b> first.", reply_markup=_tm_menu_kb())
        return
    await message.answer(
        f"<b>Your current email:</b>\n{_SEP}\n"
        f"<code>{html_lib.escape(sess['email'])}</code>\n\n"
        f"<i>Tap to copy</i>",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.message(UserFlow.temp_mail_menu, F.text.in_({_TM_INB, _TM_REF}))
async def tempmail_inbox(message: Message, state: FSMContext):
    uid     = message.from_user.id
    refresh = message.text == _TM_REF
    sess    = _tempmail_sessions.get(uid)
    if not sess:
        await message.answer("No email found. Generate one first.", reply_markup=_tm_menu_kb())
        return

    email = sess["email"]
    await message.answer(f"Checking inbox for <code>{html_lib.escape(email)}</code>…")
    messages = await _tm_get_inbox(email)

    if not messages:
        await message.answer("<b>Inbox is empty.</b>\n\n<i>Emails may take a moment to arrive.</i>", reply_markup=_tm_menu_kb())
        return

    seen     = sess.get("seen_ids", set())
    new_msgs = [m for m in messages if str(m.get("id", "")) not in seen]

    if refresh and not new_msgs:
        await message.answer(
            f"No new messages. Total: <b>{len(messages)}</b> email(s).",
            reply_markup=_tm_menu_kb(),
        )
        return

    show_msgs = new_msgs if new_msgs else messages

    stored   = sess.get("messages", {})
    mi       = sess.get("msg_index", 0)
    id_map: Dict[str, str] = {}

    for msg in messages:
        full_id  = str(msg.get("id", ""))
        existing = next((k for k, v in stored.items() if str(v.get("id", "")) == full_id), None)
        if existing:
            id_map[full_id] = existing
        else:
            short_id = f"m{mi}"
            mi += 1
            stored[short_id] = msg
            id_map[full_id]  = short_id

    _tempmail_sessions[uid]["messages"]  = stored
    _tempmail_sessions[uid]["msg_index"] = mi

    for i, msg in enumerate(show_msgs[:10]):
        full_id     = str(msg.get("id", ""))
        short_id    = id_map.get(full_id, f"m{i}")
        sender      = html_lib.escape(str(msg.get("from", "Unknown"))[:60])
        subject     = html_lib.escape(str(msg.get("subject", "(No Subject)"))[:80])
        received    = str(msg.get("created_at", ""))[:19]
        raw_preview = (msg.get("body_text") or "")[:100].replace("\n", " ")
        preview     = html_lib.escape(raw_preview)

        card = (
            f"<b>Mail #{i+1}</b>\n"
            f"<b>From:</b> {sender}\n"
            f"<b>Subject:</b> {subject}\n"
        )
        if received:
            card += f" {received}\n"
        if preview:
            card += f"\n<i>{preview}…</i>"

        inline_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Read Full Email", callback_data=f"tm_read:{uid}:{short_id}")
        ]])
        await message.answer(card, reply_markup=inline_kb)
        seen.add(full_id)
        await asyncio.sleep(0.3)

    _tempmail_sessions[uid]["seen_ids"] = seen
    label = "new"if new_msgs else "total"
    await message.answer(
        f"Showing <b>{len(show_msgs)}</b> {label} email(s).",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.callback_query(F.data.startswith("tm_read:"))
async def tempmail_read_callback(call: CallbackQuery):
    await call.answer()
    parts = call.data.split(":", 2)
    if len(parts) < 3:
        await call.answer("Invalid.", show_alert=True)
        return
    uid_str, short_id = parts[1], parts[2]
    try:
        uid = int(uid_str)
    except ValueError:
        return
    sess = _tempmail_sessions.get(uid)
    if not sess:
        await call.message.answer("Session expired. Please generate a new email.")
        return
    msg = sess.get("messages", {}).get(short_id)
    if not msg:
        await call.message.answer("Email not found. Try checking inbox again.")
        return

    sender   = html_lib.escape(str(msg.get("from", "Unknown")))
    subject  = html_lib.escape(str(msg.get("subject", "(No Subject)")))
    received = str(msg.get("created_at", ""))[:19]

    header = (
        f"<b>Full Email</b>\n{_SEP}\n"
        f"<b>From:</b> {sender}\n"
        f"<b>Subject:</b> {subject}\n"
    )
    if received:
        header += f"<b>Received:</b> {received}\n"
    header += _SEP

    await call.message.answer(header)

    body_formatted = _tm_format_body(
        msg.get("body_text", ""),
        msg.get("body_html", ""),
    )
    chunk_size = 3800
    chunks = [body_formatted[i:i+chunk_size] for i in range(0, len(body_formatted), chunk_size)]
    for chunk in chunks:
        if chunk.strip():
            await call.message.answer(chunk)
            await asyncio.sleep(0.2)


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_DEL)
async def tempmail_delete(message: Message, state: FSMContext):
    uid  = message.from_user.id
    sess = _tempmail_sessions.pop(uid, None)
    if sess:
        deleted = html_lib.escape(sess["email"])
        await message.answer(
            f"<b>Email deleted.</b>\n{_SEP}\n"
            f"<code>{deleted}</code>\n\n"
            f"<i>Generate a new one anytime.</i>",
            reply_markup=_tm_menu_kb(),
        )
    else:
        await message.answer("No active email to delete.", reply_markup=_tm_menu_kb())


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_DOM)
async def tempmail_change_domain(message: Message, state: FSMContext):
    uid = message.from_user.id
    current = (_tempmail_sessions.get(uid) or {}).get("chosen_domain", _TEMPMAIL_DOMAIN)
    await message.answer("Fetching available domains…")
    domains = await _tm_get_domains()
    if _TEMPMAIL_DOMAIN not in domains:
        domains.insert(0, _TEMPMAIL_DOMAIN)
    await state.set_state(UserFlow.temp_mail_domain)
    await state.update_data(tm_domains=domains)
    await message.answer(
        f"<b>Choose Domain</b>\n{_SEP}\n"
        f"Current: <code>@{current}</code>\n\n"
        f"Select a domain for your next email.\n"
        f"<i>({len(domains)} domains available)</i>",
        reply_markup=_tm_domain_kb(domains),
    )


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_RND)
async def tempmail_random_domain(message: Message, state: FSMContext):
    """Pick a random domain from the API list instantly from the main menu."""
    uid = message.from_user.id
    await message.answer("Picking a random domain…")
    domains = await _tm_get_domains()
    if not domains:
        domains = [_TEMPMAIL_DOMAIN]
    chosen = random.choice(domains)
    sess = _tempmail_sessions.get(uid) or {}
    sess["chosen_domain"] = chosen
    _tempmail_sessions[uid] = sess
    await message.answer(
        f"<b>Random domain selected:</b> <code>@{chosen}</code>\n\n"
        f"Press  <b>Generate Email</b> to create a new address with this domain.",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.message(UserFlow.temp_mail_domain)
async def tempmail_domain_selected(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN, CANCEL_BTN):
        await state.set_state(UserFlow.temp_mail_menu)
        uid = message.from_user.id
        current = (_tempmail_sessions.get(uid) or {}).get("chosen_domain", _TEMPMAIL_DOMAIN)
        await message.answer(
            f"<b>Temp Mail</b>\n{_SEP}\nDomain unchanged: <code>@{current}</code>",
            reply_markup=_tm_menu_kb(),
        )
        return
    data    = await state.get_data()
    domains = data.get("tm_domains", [_TEMPMAIL_DOMAIN])
    uid     = message.from_user.id
    # Handle random button inside domain chooser screen too
    if message.text == _TM_RND:
        chosen = random.choice(domains)
        sess = _tempmail_sessions.get(uid) or {}
        sess["chosen_domain"] = chosen
        _tempmail_sessions[uid] = sess
        await state.set_state(UserFlow.temp_mail_menu)
        await message.answer(
            f"<b>Random domain selected:</b> <code>@{chosen}</code>\n\n"
            f"Press  <b>Generate Email</b> to use it.",
            reply_markup=_tm_menu_kb(),
        )
        return
    chosen = message.text.strip().lstrip("@")
    if chosen not in domains:
        await message.answer("Please select a domain from the list.")
        return
    # save chosen domain; preserve existing session data if present
    sess = _tempmail_sessions.get(uid) or {}
    sess["chosen_domain"] = chosen
    _tempmail_sessions[uid] = sess
    await state.set_state(UserFlow.temp_mail_menu)
    await message.answer(
        f"<b>Domain set to</b> <code>@{chosen}</code>\n\n"
        f"Press  <b>Generate Email</b> to create a new address with this domain.",
        reply_markup=_tm_menu_kb(),
    )


# ══════════════════════════════════════════════════════════════════
# ROUTER — Admin Panel
# ══════════════════════════════════════════════════════════════════

router_admin = Router()


@router_admin.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.")
        return
    await state.clear()
    await state.set_state(AdminFlow.menu)
    await message.answer(f"<b>Admin Panel</b>\n{_SEP}\nWelcome back, admin!", reply_markup=admin_main_kb())


# ── Sub-menu navigation ────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_ORDERS_MENU)
async def admin_orders_submenu(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.orders_submenu)
    await message.answer("<b>Orders Management</b>", reply_markup=admin_orders_submenu_kb())

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_REPORTS_MENU)
async def admin_reports_submenu(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.reports_submenu)
    await message.answer("<b>Reports & Analytics</b>", reply_markup=admin_reports_submenu_kb())

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_TOOLS_MENU)
async def admin_tools_submenu(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.tools_submenu)
    await message.answer("<b>Tools & Automation</b>", reply_markup=admin_tools_submenu_kb())

@router_admin.message(AdminFlow.orders_submenu, F.text == BACK_BTN)
async def admin_orders_back(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.menu)
    await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())

@router_admin.message(AdminFlow.reports_submenu, F.text == BACK_BTN)
async def admin_reports_back(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.menu)
    await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())

@router_admin.message(AdminFlow.tools_submenu, F.text == BACK_BTN)
async def admin_tools_back(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.menu)
    await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())


# ── Dashboard ──────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_DASHBOARD)
async def admin_dashboard(message: Message):
    stats = await get_dashboard_stats()
    await message.answer(fmt_admin_dashboard(stats), reply_markup=admin_main_kb())
    # Admin quick-action inline buttons
    admin_actions = _quick_actions_inline([
        ("Analytics", "adm_quick:analytics"),
        ("Stock", "adm_quick:stock"),
        ("Deposits", "adm_quick:deposits"),
    ])
    await message.answer("<b>Quick Actions</b>", reply_markup=admin_actions)
    # Auto-check low stock alerts
    settings = await get_settings()
    threshold = int(settings.get("low_stock_threshold", 5))
    products = await get_all_products()
    low_items = []
    _pkg_emoji = ""
    for pid, p in products.items():
        if p.get("hidden"):
            continue
        count = p.get("stock_count", 0)
        if count <= threshold:
            stock_dot = _status_dot(count > 0)
            emoji = p.get("emoji", _pkg_emoji)
            low_items.append(f"  {stock_dot} {emoji} {p.get('name', pid)}: <b>{count}</b>")
    if low_items:
        alert_text = f"<b>Low Stock Alert</b>\n{_SEP}\nThreshold: {threshold}\n" + "\n".join(low_items[:10])
        await message.answer(alert_text)


# ── Admin Quick Action Callbacks ───────────────────────────────────

@router_admin.callback_query(F.data == "adm_quick:analytics")
async def adm_quick_analytics_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Denied", show_alert=True)
        return
    await state.set_state(AdminFlow.menu)
    await callback.message.answer("Opening analytics...", reply_markup=admin_main_kb())
    await callback.answer()


@router_admin.callback_query(F.data == "adm_quick:stock")
async def adm_quick_stock_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Denied", show_alert=True)
        return
    products = await get_all_products()
    lines = []
    _pkg_e = ""
    for pid, p in products.items():
        if p.get("hidden"):
            continue
        count = p.get("stock_count", 0)
        dot = _status_dot(count > 0)
        bar = _progress_bar(count, max(count, 50), width=6)
        emoji = p.get("emoji", _pkg_e)
        lines.append(f"{dot} {emoji} {p.get('name', pid)}: <b>{count}</b> {bar}")
    body = "\n".join(lines[:15]) if lines else "No products."
    await callback.message.answer(f"<b>Stock Overview</b>\n{_SEP}\n{body}")
    await callback.answer()


@router_admin.callback_query(F.data == "adm_quick:deposits")
async def adm_quick_deposits_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Denied", show_alert=True)
        return
    await callback.message.answer("Check pending deposits in the Admin menu.", reply_markup=admin_main_kb())
    await callback.answer()


# ── Deposit inline callbacks ───────────────────────────────────────

@router_admin.callback_query(F.data.startswith("dep_ok:"))
async def approve_deposit(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    dep_id = call.data.split(":", 1)[1]
    dep    = await get_deposit(dep_id)
    if not dep or dep.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    await update_deposit(dep_id, {"status": "approved"})
    new_bal = await update_balance(dep["user_id"], dep["amount_usd"])
    await log_admin_action(call.from_user.id, "approve_deposit", f"ID:{dep_id} User:{dep['user_id']} ${dep['amount_usd']:.2f}")
    try:
        await call.message.edit_caption((call.message.caption or "") + "\n\n APPROVED", reply_markup=None)
    except Exception:
        try:
            await call.message.edit_text((call.message.text or "") + "\n\n APPROVED", reply_markup=None)
        except Exception:
            pass
    await call.answer("Approved")
    try:
        await call.bot.send_message(
            dep["user_id"],
            f"{pem('ok')} <b>✦ Deposit Approved! ✦</b>\n{_SEP}\n"
            f"  {pem('money')} Amount Credited ‣ <b>${dep['amount_usd']:.2f}</b>\n"
            f"  {pem('diamond')} New Balance ‣ <b>${new_bal:.2f}</b>\n"
            f"{_LINE}\n"
            f"  ‣ Thank you for your deposit! 🎉",
        )
    except Exception:
        pass


@router_admin.callback_query(F.data.startswith("dep_no:"))
async def reject_deposit(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    dep_id = call.data.split(":", 1)[1]
    dep    = await get_deposit(dep_id)
    if not dep or dep.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    _pending_reject[call.from_user.id] = {"dep_id": dep_id, "dep": dep, "msg": call.message}
    await state.set_state(AdminFlow.dep_reject_reason)
    await call.answer("Enter reject reason")
    await call.message.answer(
        f"<b>Reject Deposit</b>\n{_SEP}\n"
        f"User: @{dep.get('username','—')}  |  Amount: <b>${dep['amount_usd']:.2f}</b>\n\n"
        f"<b>Type the rejection reason to send to the user:</b>\n"
        f"<i>(e.g. Wrong TRX ID, screenshot unclear)</i>\n\n"
        f"Press /cancel to abort.",
    )


# ── Deposits list ──────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_DEPOSITS)
async def admin_deposits(message: Message):
    pending = await get_pending_deposits()
    if not pending:
        await message.answer("No pending deposits.", reply_markup=admin_main_kb())
        return
    await message.answer(f"<b>{len(pending)} Pending Deposit(s)</b>", reply_markup=admin_main_kb())
    for dep in pending[:10]:
        try:
            text      = fmt_admin_deposit_review(dep)
            kb_inline = deposit_review_inline(dep["deposit_id"])
            ss        = dep.get("screenshot_url", "")
            if ss:  # Telegram file_id (or an old http URL)
                await message.answer_photo(photo=ss, caption=text, reply_markup=kb_inline)
            else:
                await message.answer(text, reply_markup=kb_inline)
        except Exception as e:
            logger.warning("Deposit display error: %s", e)


# ── VPN order callbacks ────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_VPN_ORDERS)
@router_admin.message(AdminFlow.orders_submenu, F.text == BTN_ADM_VPN_ORDERS)
async def admin_vpn_orders(message: Message):
    pending = await get_pending_vpn_orders()
    if not pending:
        await message.answer("No pending VPN orders.", reply_markup=admin_main_kb())
        return
    await message.answer(f"<b>{len(pending)} Pending VPN Order(s)</b>", reply_markup=admin_main_kb())
    for o in pending[:10]:
        await message.answer(fmt_admin_vpn_order(o), reply_markup=order_review_inline(o["order_id"], "vpn"))


@router_admin.callback_query(F.data.startswith("vpn_ok:"))
async def deliver_vpn(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"vpn_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    _pending_fulfill[call.from_user.id] = {"oid": oid, "uid": o["user_id"], "kind": "vpn",
                                            "product_name": o["product_name"], "days": o["duration_days"]}
    await state.set_state(AdminFlow.vpn_fulfill)
    await call.answer("Enter credentials now")
    await call.message.answer(
        f"<b>VPN Credentials</b>\n{_SEP}\n"
        f"Order: <code>{oid}</code>\n"
        f"Product: <b>{o['product_name']}</b>  ·  {o['duration_days']} days\n\n"
        f"<b>Type the credentials to send to the user:</b>\n"
        f"<i>(e.g. username, password, server info)</i>\n\n"
        f"Press /cancel to abort.",
    )


@router_admin.callback_query(F.data.startswith("vpn_no:"))
async def cancel_vpn(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"vpn_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    uid   = o.get("user_id")
    price = o.get("price", 0)
    await update_vpn_order(oid, {"status": "cancelled"})
    if uid:
        await update_balance(uid, price)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer("Cancelled & refunded")
    try:
        await call.bot.send_message(
            uid,
            f"<b>VPN Order Cancelled</b>\n{_SEP}\n"
            f" {o.get('product_name','?')} order was cancelled.\n"
            f"Refund: <b>${price:.2f}</b> added to your balance.",
        )
    except Exception:
        pass


# ── Proxy order callbacks ──────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PROXY_ORDERS)
@router_admin.message(AdminFlow.orders_submenu, F.text == BTN_ADM_PROXY_ORDERS)
async def admin_proxy_orders(message: Message):
    pending = await get_pending_proxy_orders()
    if not pending:
        await message.answer("No pending proxy orders.", reply_markup=admin_main_kb())
        return
    await message.answer(f"<b>{len(pending)} Pending Proxy Order(s)</b>", reply_markup=admin_main_kb())
    for o in pending[:10]:
        await message.answer(fmt_admin_proxy_order(o), reply_markup=order_review_inline(o["order_id"], "proxy"))


@router_admin.callback_query(F.data.startswith("proxy_ok:"))
async def deliver_proxy(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"proxy_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    _pending_fulfill[call.from_user.id] = {"oid": oid, "uid": o["user_id"], "kind": "proxy",
                                            "product_name": o["product_name"], "days": o["duration_days"]}
    await state.set_state(AdminFlow.proxy_fulfill)
    await call.answer("Enter credentials now")
    await call.message.answer(
        f"<b>Proxy Credentials</b>\n{_SEP}\n"
        f"Order: <code>{oid}</code>\n"
        f"Product: <b>{o['product_name']}</b>  ·   {o.get('duration_days', '—')}\n\n"
        f"<b>Type the proxy details to send to the user:</b>\n"
        f"<i>(e.g. IP:Port, username, password)</i>\n\n"
        f"Press /cancel to abort.",
    )


@router_admin.callback_query(F.data.startswith("proxy_no:"))
async def cancel_proxy(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"proxy_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    uid   = o.get("user_id")
    price = o.get("price", 0)
    await update_proxy_order(oid, {"status": "cancelled"})
    if uid:
        await update_balance(uid, price)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer("Cancelled & refunded")
    try:
        await call.bot.send_message(
            uid,
            f"<b>Proxy Order Cancelled</b>\n{_SEP}\n"
            f" {o.get('product_name','?')} order was cancelled.\n"
            f"Refund: <b>${price:.2f}</b> added to your balance.",
        )
    except Exception:
        pass


# ── VPN Credentials Fulfillment ────────────────────────────────────

@router_admin.message(AdminFlow.vpn_fulfill)
async def vpn_credentials_received(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN) or (message.text and message.text.lower() == "/cancel"):
        _pending_fulfill.pop(message.from_user.id, None)
        await state.set_state(AdminFlow.menu)
        await message.answer("Cancelled.", reply_markup=admin_main_kb())
        return
    if not message.text:
        await message.answer("Please send the credentials as <b>text</b> (no files or photos).")
        return
    ctx = _pending_fulfill.pop(message.from_user.id, None)
    if not ctx:
        await state.set_state(AdminFlow.menu)
        await message.answer("Session expired.", reply_markup=admin_main_kb())
        return
    await update_vpn_order(ctx["oid"], {"status": "delivered"})
    await state.set_state(AdminFlow.menu)
    await message.answer(
        "<b>Delivered!</b> Credentials sent to user.",
        reply_markup=admin_main_kb(),
    )
    try:
        await message.bot.send_message(
            ctx["uid"],
            f"<b>VPN Order Delivered!</b>\n{_SEP}\n"
            f"<b>{ctx['product_name']}</b>  ·  {ctx['days']} day(s)\n\n"
            f"<b>Your Credentials:</b>\n<pre>{message.text}</pre>",
        )
    except Exception:
        pass


# ── Proxy Credentials Fulfillment ──────────────────────────────────

@router_admin.message(AdminFlow.proxy_fulfill)
async def proxy_credentials_received(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN) or (message.text and message.text.lower() == "/cancel"):
        _pending_fulfill.pop(message.from_user.id, None)
        await state.set_state(AdminFlow.menu)
        await message.answer("Cancelled.", reply_markup=admin_main_kb())
        return
    if not message.text:
        await message.answer("Please send the proxy details as <b>text</b> (no files or photos).")
        return
    ctx = _pending_fulfill.pop(message.from_user.id, None)
    if not ctx:
        await state.set_state(AdminFlow.menu)
        await message.answer("Session expired.", reply_markup=admin_main_kb())
        return
    await update_proxy_order(ctx["oid"], {"status": "delivered"})
    await state.set_state(AdminFlow.menu)
    await message.answer(
        "<b>Delivered!</b> Proxy details sent to user.",
        reply_markup=admin_main_kb(),
    )
    try:
        await message.bot.send_message(
            ctx["uid"],
            f"<b>Proxy Order Delivered!</b>\n{_SEP}\n"
            f"<b>{ctx['product_name']}</b>  ·   {ctx['days']}\n\n"
            f"<b>Your Proxy Details:</b>\n<pre>{message.text}</pre>",
        )
    except Exception:
        pass


# ── Deposit Reject Reason ───────────────────────────────────────────

@router_admin.message(AdminFlow.dep_reject_reason)
async def deposit_reject_reason_received(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN) or (message.text and message.text.lower() == "/cancel"):
        _pending_reject.pop(message.from_user.id, None)
        await state.set_state(AdminFlow.menu)
        await message.answer("Cancelled.", reply_markup=admin_main_kb())
        return
    ctx = _pending_reject.pop(message.from_user.id, None)
    if not ctx:
        await state.set_state(AdminFlow.menu)
        await message.answer("Session expired.", reply_markup=admin_main_kb())
        return
    dep_id = ctx["dep_id"]
    dep    = ctx["dep"]
    reason = message.text or "No reason given."
    await update_deposit(dep_id, {"status": "rejected", "reject_reason": reason})
    await log_admin_action(message.from_user.id, "reject_deposit", f"ID:{dep_id} User:{dep['user_id']} Reason:{reason[:50]}")
    orig_msg = ctx["msg"]
    try:
        await orig_msg.edit_caption(
            (orig_msg.caption or "") + f"\n\n REJECTED\nReason: {reason}", reply_markup=None
        )
    except Exception:
        try:
            await orig_msg.edit_text(
                (orig_msg.text or "") + f"\n\n REJECTED\nReason: {reason}", reply_markup=None
            )
        except Exception:
            pass
    await state.set_state(AdminFlow.menu)
    await message.answer("Deposit rejected.", reply_markup=admin_main_kb())
    try:
        await message.bot.send_message(
            dep["user_id"],
            f"<b>Deposit Rejected</b>\n{_SEP}\n"
            f"Amount: <b>${dep['amount_usd']:.2f}</b> was not credited.\n\n"
            f"<b>Reason:</b> {reason}\n\n"
            f"Contact support if you think this is an error.",
        )
    except Exception:
        pass


# ── Products ───────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PRODUCTS)
async def admin_products(message: Message, state: FSMContext):
    products = await get_all_products()
    dm = build_admin_products_dm(products)
    await state.update_data(products=products, dm=dm)
    await state.set_state(AdminFlow.products_list)
    await message.answer(
        f"<b>Products</b>\n{_SEP}\n{len(products)} product(s) total.\nSelect one to manage:",
        reply_markup=admin_products_kb(products),
    )


@router_admin.message(AdminFlow.products_list)
async def admin_products_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_ADD_PRODUCT:
        await state.set_state(AdminFlow.product_add_name)
        await message.answer("Enter product name:", reply_markup=input_kb())
        return
    if message.text == BTN_DOWNLOAD_PRODUCTS:
        products = await get_all_products()
        if not products:
            await message.answer("No products found.")
            return
        all_stocks = {}
        for pid in products:
            all_stocks[pid] = await db_get(f"stocks/{pid}") or {}
        xlsx_bytes = make_products_xlsx(products, all_stocks)
        date_str   = time.strftime("%Y%m%d_%H%M", time.gmtime())
        total_items = sum(len(v) for v in all_stocks.values())
        await message.answer_document(
            document=BufferedInputFile(xlsx_bytes, filename=f"products_{date_str}.xlsx"),
            caption=(
                f"<b>All Products</b>\n{_SEP}\n"
                f"Total: <b>{len(products)}</b> product(s)\n"
                f"Stock Items: <b>{total_items}</b>\n\n"
                f"<i>Edit this file and upload it via  Import Products to add new products in bulk.</i>"
            ),
        )
        return
    if message.text == BTN_IMPORT_PRODUCTS:
        await state.set_state(AdminFlow.products_import)
        await message.answer(
            f"<b>Import Products</b>\n{_SEP}\n"
            f"Send an <b>.xlsx</b> file to import products in bulk.\n\n"
            f"<b>Required columns:</b>\n"
            f"• <b>Name</b> — product name\n"
            f"• <b>Emoji</b> — icon (e.g.   )\n"
            f"• <b>Category</b> — mail / vpn / proxy\n"
            f"• <b>Price (USD)</b> — price per unit\n"
            f"• <b>Delivery Mode</b> — manual / auto (proxy only)\n"
            f"• <b>Hidden</b> — yes / no\n\n"
            f"Tip: Download the current products file first to use it as a template.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    data = await state.get_data()
    dm   = data.get("dm", {})
    pid  = resolve_selection_id(message.text, dm)
    if not pid:
        await message.answer("Select a product from the keyboard.")
        return
    product = await get_product(pid)
    await state.update_data(pid=pid, product=product)
    await state.set_state(AdminFlow.product_detail)
    hidden        = product.get("hidden", False)
    category      = product.get("category", "mail")
    delivery_mode = product.get("delivery_mode", "manual")
    desc          = product.get("description", "").strip()
    mode_label = ""
    if category == "proxy":
        mode_label = f"\n Delivery: <b>{'Auto (Stock)'if delivery_mode == 'auto'else 'Manual (Admin)'}</b>"
    desc_line = f"\n <i>{desc}</i>"if desc else "\n <i>No description</i>"
    await message.answer(
        f"{product.get('emoji','')} <b>{product['name']}</b>\n{_SEP}\n"
        f"Price: ${product['price']:.2f}\n"
        f"Stock: {product.get('stock_count',0)}\n"
        f"Category: {category.upper()}{mode_label}\n"
        f"Visible: {'No 'if hidden else 'Yes '}\n"
        f"Sold: {product.get('total_sold',0)}"
        f"{desc_line}",
        reply_markup=admin_product_actions_kb(hidden, category, delivery_mode),
    )


@router_admin.message(AdminFlow.product_detail)
async def admin_product_detail_action(message: Message, state: FSMContext):
    data    = await state.get_data()
    pid     = data.get("pid")
    product = data.get("product", {})
    if message.text in (BACK_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    if message.text in (BTN_HIDE_PROD, BTN_SHOW_PROD):
        new_h   = not product.get("hidden", False)
        await update_product(pid, {"hidden": new_h})
        updated = await get_product(pid)
        await state.update_data(product=updated)
        await message.answer(
            f"Product is now {'hidden 'if new_h else 'visible '}.",
            reply_markup=admin_product_actions_kb(
                updated.get("hidden", False),
                updated.get("category", "mail"),
                updated.get("delivery_mode", "manual"),
            ),
        )
        return
    if message.text in (BTN_TOGGLE_AUTO, BTN_TOGGLE_MANUAL):
        if product.get("category", "mail") != "proxy":
            await message.answer("Only proxy products have a delivery mode.")
            return
        new_mode = "auto"if message.text == BTN_TOGGLE_AUTO else "manual"
        await update_product(pid, {"delivery_mode": new_mode})
        updated = await get_product(pid)
        await state.update_data(product=updated)
        label = "Auto (Stock)"if new_mode == "auto"else "Manual (Admin)"
        await message.answer(
            f"Delivery mode → <b>{label}</b>",
            reply_markup=admin_product_actions_kb(updated.get("hidden", False), "proxy", new_mode),
        )
        return
    if message.text == BTN_ADD_STOCK:
        cat  = product.get("category", "mail")
        dmode = product.get("delivery_mode", "manual")
        if not (cat == "mail"or (cat == "proxy"and dmode == "auto")):
            await message.answer("Stock management is only for Mail or Auto-Proxy products.")
            return
        stock = await get_stock_count(pid)
        settings = await get_settings()
        warn = "\n <b>Low Stock Alert!</b>"if stock <= settings.get("low_stock_threshold", 5) else ""
        await state.update_data(stock_pid=pid, stock_product=product)
        await state.set_state(AdminFlow.stock_detail)
        await message.answer(
            f"<b>{product['name']}</b>\n{_SEP}\n"
            f"Current Stock: <b>{stock}</b>{warn}\n\nChoose an action:",
            reply_markup=admin_stock_actions_kb(),
        )
        return
    if message.text == BTN_DELETE:
        await delete_product(pid)
        await message.answer("Deleted.")
        await _back_to_products(message, state)
        return
    field_map = {
        BTN_EDIT_NAME:  "name",
        BTN_EDIT_PRICE: "price",
        BTN_EDIT_EMOJI: "emoji",
        BTN_EDIT_DESC:  "description",
    }
    field = field_map.get(message.text)
    if field:
        await state.update_data(edit_field=field)
        await state.set_state(AdminFlow.product_edit)
        prompts = {
            "name":        "Enter new product name:",
            "price":       "Enter new price (USD):",
            "emoji":       "Enter new emoji:",
            "description": "Enter new description (or send — to remove it):",
        }
        await message.answer(prompts[field], reply_markup=input_kb())
        return
    await message.answer("Select from keyboard.")


@router_admin.message(AdminFlow.product_edit)
async def receive_product_edit(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    data  = await state.get_data()
    field = data.get("edit_field", "name")
    pid   = data.get("pid")
    value = message.text.strip()
    if field == "price":
        price, err = validate_price(value)
        if err:
            await message.answer(err)
            return
        await update_product(pid, {"price": price})
    elif field == "description":
        # "—"or "-"means remove description
        new_desc = ""if value in ("—", "-") else value
        await update_product(pid, {"description": new_desc})
    else:
        await update_product(pid, {field: value})
    updated = await get_product(pid)
    await state.update_data(product=updated)
    await state.set_state(AdminFlow.product_detail)
    field_label = "Description"if field == "description"else field.capitalize()
    await message.answer(
        f"<b>{field_label} updated!</b>\n{updated.get('emoji','')} {updated['name']} — ${updated['price']:.2f}",
        reply_markup=admin_product_actions_kb(
            updated.get("hidden", False),
            updated.get("category", "mail"),
            updated.get("delivery_mode", "manual"),
        ),
    )


@router_admin.message(AdminFlow.products_import)
async def admin_products_import(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    if not message.document:
        await message.answer(
            "Please send an <b>.xlsx</b> file.\n\nPress  Cancel to go back.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    fname = message.document.file_name or ""
    if not fname.lower().endswith(".xlsx"):
        await message.answer(
            f"Unsupported file type: <code>{fname}</code>\nOnly <b>.xlsx</b> files are supported.\n\nPress  Cancel to go back.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    try:
        file       = await message.bot.get_file(message.document.file_id)
        file_bytes = (await message.bot.download_file(file.file_path)).read()
    except Exception as e:
        await message.answer(f"Failed to download file: {e}", reply_markup=_kb([CANCEL_BTN, HOME_BTN]))
        return
    parsed = parse_products_xlsx(file_bytes)
    if not parsed:
        await message.answer(
            "No valid products found in the file.\n\n"
            "Make sure the file has <b>Name</b> and <b>Price (USD)</b> columns.\n\n"
            "Press  Cancel to go back.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    created = 0
    skipped = 0
    stock_added = 0
    for p in parsed:
        try:
            pid = await create_product(p["name"], p["price"], p["emoji"], p["category"],
                                  p.get("delivery_mode", "manual"), p.get("hidden", False))
            created += 1
            # Import stock items if present
            if p.get("stock_items"):
                added = await add_stock_items(pid, p["stock_items"], bot=message.bot)
                stock_added += added
        except Exception:
            skipped += 1
    await _back_to_products(message, state)
    lines = [f"  • {p['emoji']} {p['name']} [{p['category'].upper()}] — ${p['price']:.2f}"for p in parsed[:10]]
    preview = "\n".join(lines) + (f"\n  <i>... and {len(parsed) - 10} more</i>"if len(parsed) > 10 else "")
    stock_line = f"\n Stock imported: <b>{stock_added}</b> item(s)"if stock_added > 0 else ""
    await message.answer(
        f"<b>Import Complete!</b>\n{_SEP}\n"
        f"Created: <b>{created}</b> product(s)\n"
        f"Skipped: <b>{skipped}</b>{stock_line}\n\n"
        f"<b>Imported products:</b>\n{preview}\n\n"
        f"<i>ℹ Note: Import always creates new products. It does not update existing ones.</i>",
    )


@router_admin.message(AdminFlow.product_add_name)
async def add_product_name(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    await state.update_data(pname=message.text.strip())
    await state.set_state(AdminFlow.product_add_emoji)
    await message.answer("Enter emoji (e.g.   ):", reply_markup=input_kb())


@router_admin.message(AdminFlow.product_add_emoji)
async def add_product_emoji(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    await state.update_data(pemoji=message.text.strip())
    await state.set_state(AdminFlow.product_add_price)
    await message.answer("Enter price in USD:", reply_markup=input_kb())


@router_admin.message(AdminFlow.product_add_price)
async def add_product_price(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    price, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    await state.update_data(pprice=price)
    await state.set_state(AdminFlow.product_add_cat)
    await message.answer("Select category:", reply_markup=admin_category_kb())


@router_admin.message(AdminFlow.product_add_cat)
async def add_product_category(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    cat = CATEGORY_MAP.get(message.text)
    if not cat:
        await message.answer("Select from keyboard.", reply_markup=admin_category_kb())
        return
    await state.update_data(pcat=cat)
    await state.set_state(AdminFlow.product_add_desc)
    await message.answer(
        "<b>Product Description</b> (optional)\n\n"
        "Enter a short description shown to users when they view this product.\n"
        "<i>Example: Fast residential proxies, 99% uptime guarantee</i>\n\n"
        "Or press <b> Skip</b> to leave it blank.",
        reply_markup=_kb(["Skip"], [CANCEL_BTN]),
    )


@router_admin.message(AdminFlow.product_add_desc)
async def add_product_desc(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    data = await state.get_data()
    desc = ""if message.text.strip() in ("Skip", "skip", "-") else message.text.strip()
    await create_product(
        data.get("pname", ""), data.get("pprice", 0.0),
        data.get("pemoji", ""), data.get("pcat", "mail"),
        description=desc,
    )
    desc_preview = f"\n {desc}"if desc else ""
    await message.answer(
        f"<b>Product Created!</b>\n{_SEP}\n"
        f"{data.get('pemoji','')} {data.get('pname','')} — ${data.get('pprice',0):.2f} [{data.get('pcat','mail').upper()}]"
        f"{desc_preview}"
    )
    await _back_to_products(message, state)


async def _back_to_products(message: Message, state: FSMContext):
    products = await get_all_products()
    dm = build_admin_products_dm(products)
    await state.update_data(products=products, dm=dm)
    await state.set_state(AdminFlow.products_list)
    await message.answer("<b>Products</b>", reply_markup=admin_products_kb(products))


# ── Stock ──────────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_STOCK)
async def admin_stock(message: Message, state: FSMContext):
    products = await get_all_products()
    stockable = {
        k: v for k, v in products.items()
        if v.get("category") == "mail"
        or (v.get("category") == "proxy"and v.get("delivery_mode") == "auto")
    }
    if not stockable:
        await message.answer(
            "No stockable products yet.\nCreate Mail products or Auto-Proxy products first.",
            reply_markup=admin_main_kb(),
        )
        return
    dm = build_admin_stock_dm(stockable)
    await state.update_data(stock_products=stockable, stock_dm=dm)
    await state.set_state(AdminFlow.stock_list)
    await message.answer(
        f"<b>Stock Management</b>\n{_SEP}\n"
        f"Mail &  Auto-Proxy products:\nSelect a product:",
        reply_markup=admin_stock_products_kb(stockable),
    )


@router_admin.message(AdminFlow.stock_list)
async def admin_stock_list_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_DOWNLOAD_ALL_STOCK:
        data     = await state.get_data()
        products = data.get("stock_products", {})
        if not products:
            await message.answer("No stockable products found.", reply_markup=admin_main_kb())
            return
        await message.answer("Exporting all stock, please wait…")
        try:
            all_stocks = {}
            for pid_key in products:
                all_stocks[pid_key] = await db_get(f"stocks/{pid_key}") or {}
            total_items = sum(len(v) for v in all_stocks.values())
            xlsx_bytes  = make_all_stock_export_xlsx(products, all_stocks)
            date_str    = time.strftime("%Y%m%d_%H%M", time.gmtime())
            await message.answer_document(
                document=BufferedInputFile(xlsx_bytes, filename=f"all_stock_{date_str}.xlsx"),
                caption=(
                    f"<b>All Stock Export</b>\n{_SEP}\n"
                    f"Products: <b>{len(products)}</b>\n"
                    f"Total Items: <b>{total_items}</b>\n\n"
                    f"<i>Each product has its own sheet. Column D (Raw) is the original account string for re-importing.</i>"
                ),
            )
        except Exception as e:
            logger.error("All-stock export error: %s", e)
            await message.answer(f"Export failed: {e}")
        return
    if message.text == BTN_IMPORT_ALL_STOCK:
        await state.set_state(AdminFlow.stock_import_all)
        await message.answer(
            f"<b>Import All Stock</b>\n{_SEP}\n"
            f"Send a <b>.xlsx</b> file exported by <b>Download All Stock</b>.\n\n"
            f"<i>Each sheet name will be matched to a product. "
            f"Column D (Raw) is used for import.</i>",
            reply_markup=input_kb(),
        )
        return
    data     = await state.get_data()
    stock_dm = data.get("stock_dm", {})
    pid      = resolve_selection_id(message.text, stock_dm)
    if not pid:
        await message.answer("Select from keyboard.")
        return
    product  = await get_product(pid)
    stock    = await get_stock_count(pid)
    settings = await get_settings()
    warn     = "\n <b>Low Stock Alert!</b>"if stock <= settings.get("low_stock_threshold", 5) else ""
    await state.update_data(stock_pid=pid, stock_product=product)
    await state.set_state(AdminFlow.stock_detail)
    await message.answer(
        f"<b>{product['name']}</b>\n{_SEP}\n"
        f"Current Stock: <b>{stock}</b>{warn}\n\nChoose an action:",
        reply_markup=admin_stock_actions_kb(),
    )


@router_admin.message(AdminFlow.stock_detail)
async def admin_stock_detail_action(message: Message, state: FSMContext):
    data    = await state.get_data()
    pid     = data.get("stock_pid")
    product = data.get("stock_product", {})
    if message.text == BACK_BTN:
        mail_p = data.get("stock_products", {})
        await state.set_state(AdminFlow.stock_list)
        await message.answer("<b>Stock Management</b>", reply_markup=admin_stock_products_kb(mail_p))
        return
    if message.text == HOME_BTN:
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_GET_TEMPLATE:
        try:
            tmpl = make_stock_template_xlsx(product["name"])
            safe_name = product["name"].replace(" ", "_")[:20]
            await message.answer_document(
                document=BufferedInputFile(tmpl, filename=f"stock_template_{safe_name}.xlsx"),
                caption=(
                    f"<b>Stock Template — {product['name']}</b>\n{_SEP}\n"
                    f"1⃣  Open this file in Excel / Google Sheets\n"
                    f"2⃣  Delete the 3 example rows (green)\n"
                    f"3⃣  Fill in real accounts: Email in <b>column A</b>, Password in <b>column B</b>\n"
                    f"4⃣  Save and upload back with <b> Upload File</b>"
                ),
                reply_markup=admin_stock_actions_kb(),
            )
        except Exception as _te:
            logger.warning("Template send failed: %s", _te)
            await message.answer("Failed to generate template.", reply_markup=admin_stock_actions_kb())
        return
    if message.text == BTN_DOWNLOAD_STOCK:
        stock_data = await db_get(f"stocks/{pid}") or {}
        if not stock_data:
            await message.answer(
                f"<b>No stock found</b>\n{_SEP}\n"
                f"Product <b>{product['name']}</b> has no stock items yet.",
                reply_markup=admin_stock_actions_kb(),
            )
            return
        try:
            xlsx_bytes = make_stock_export_xlsx(product["name"], stock_data)
            safe_name  = re.sub(r"[^\w]", "_", product["name"])[:20]
            date_str   = time.strftime("%Y%m%d_%H%M", time.gmtime())
            await message.answer_document(
                document=BufferedInputFile(xlsx_bytes, filename=f"stock_{safe_name}_{date_str}.xlsx"),
                caption=(
                    f"<b>Stock Export — {product['name']}</b>\n{_SEP}\n"
                    f"Total Items: <b>{len(stock_data)}</b>\n\n"
                    f"<i>Column D (Raw) is the original account string — use it when re-importing via  Upload File.</i>"
                ),
                reply_markup=admin_stock_actions_kb(),
            )
        except Exception as e:
            logger.error("Stock export error: %s", e)
            await message.answer(f"Failed to generate stock file: {e}", reply_markup=admin_stock_actions_kb())
        return
    if message.text == BTN_UPLOAD_FILE:
        await state.set_state(AdminFlow.stock_uploading)
        await message.answer(
            f"<b>Upload Stock</b>\n{_SEP}\n"
            f"Product: <b>{product['name']}</b>\n\n"
            f"Send a <b>.txt</b> / <b>.csv</b> / <b>.xlsx</b> file\n"
            f"Format: <code>email:password</code> (one per row/line)\n\n"
            f"<i>For xlsx: put email in column A, password in column B</i>",
            reply_markup=input_kb(),
        )
        return
    if message.text == BTN_MANUAL_ADD:
        await state.set_state(AdminFlow.stock_manual)
        await message.answer(
            f"<b>Manual Add</b>\n{_SEP}\n"
            f"Product: <b>{product['name']}</b>\n\n"
            f"Type accounts one per line:\n<code>email@gmail.com:password</code>",
            reply_markup=input_kb(),
        )
        return
    if message.text == BTN_CLEAR_STOCK:
        await clear_stock(pid)
        await message.answer(
            f"Stock cleared for <b>{product['name']}</b>.",
            reply_markup=admin_stock_actions_kb(),
        )
        return
    await message.answer("Select from keyboard.")


@router_admin.message(AdminFlow.stock_uploading, F.document)
async def receive_stock_file(message: Message, state: FSMContext):
    data    = await state.get_data()
    pid     = data.get("stock_pid")
    product = data.get("stock_product", {})
    doc: Document = message.document

    # Check file type before downloading
    fname = (doc.file_name or "file.txt").lower()
    if not (fname.endswith(".txt") or fname.endswith(".csv") or fname.endswith(".xlsx")):
        await message.answer(
            f"Unsupported file type: <b>{doc.file_name}</b>\n"
            f"Please send a <b>.txt</b>, <b>.csv</b>, or <b>.xlsx</b> file.",
            reply_markup=admin_stock_actions_kb(),
        )
        await state.set_state(AdminFlow.stock_detail)
        return

    await message.answer("Processing file…")
    try:
        file = await message.bot.get_file(doc.file_id)
        raw  = (await message.bot.download_file(file.file_path)).read()
    except Exception as e:
        await message.answer(f"Failed to download file: {e}", reply_markup=admin_stock_actions_kb())
        await state.set_state(AdminFlow.stock_detail)
        return

    try:
        items = parse_stock_file(raw, doc.file_name or "file.txt")
    except Exception as e:
        await message.answer(f"Parse error: {e}", reply_markup=admin_stock_actions_kb())
        await state.set_state(AdminFlow.stock_detail)
        return

    if not items:
        await message.answer(
            "No valid accounts found in the file.\n"
            "Make sure the file has email:password format.",
            reply_markup=admin_stock_actions_kb(),
        )
        await state.set_state(AdminFlow.stock_detail)
        return

    added     = await add_stock_items(pid, items, bot=message.bot)
    new_count = await get_stock_count(pid)
    await log_admin_action(message.from_user.id, "add_stock", f"Product:{product.get('name', pid)} +{added} items")
    await state.set_state(AdminFlow.stock_detail)
    await message.answer(
        f"<b>{added} accounts added</b> ({len(items)} lines read)\n{_SEP}\n"
        f"Product: <b>{product['name']}</b>\n Total Stock: <b>{new_count}</b>",
        reply_markup=admin_stock_actions_kb(),
    )


@router_admin.message(AdminFlow.stock_uploading)
async def stock_not_file(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.stock_detail)
        await message.answer("Cancelled.", reply_markup=admin_stock_actions_kb())
        return
    await message.answer("Please send a <b>.txt</b>, <b>.csv</b> or <b>.xlsx</b> file — not a text message.")


@router_admin.message(AdminFlow.stock_import_all, F.document)
async def receive_import_all_stock_file(message: Message, state: FSMContext):
    doc = message.document
    fname = (doc.file_name or "").lower()
    if not fname.endswith(".xlsx"):
        await message.answer(
            "Please send a <b>.xlsx</b> file (the format exported by Download All Stock).",
            reply_markup=input_kb(),
        )
        return

    await message.answer("Importing stock from all sheets, please wait...")
    try:
        file = await message.bot.get_file(doc.file_id)
        raw  = (await message.bot.download_file(file.file_path)).read()
    except Exception as e:
        data = await state.get_data()
        products = data.get("stock_products", {})
        await state.set_state(AdminFlow.stock_list)
        await message.answer(f"Failed to download file: {e}", reply_markup=admin_stock_products_kb(products))
        return

    try:
        wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    except Exception as e:
        data = await state.get_data()
        products = data.get("stock_products", {})
        await state.set_state(AdminFlow.stock_list)
        await message.answer(f"Cannot read xlsx file: {e}", reply_markup=admin_stock_products_kb(products))
        return

    data = await state.get_data()
    products = data.get("stock_products", {})

    # Build lookup: normalized product name (truncated to 28 chars) -> pid
    name_to_pid = {}
    for pid, p in products.items():
        pname = p.get("name", "")
        safe_title = re.sub(r"[\\/*?:\[\]]", "", pname)[:28].lower().strip()
        name_to_pid[safe_title] = pid

    results = []
    total_imported = 0
    matched_sheets = 0

    for sheet_name in wb.sheetnames:
        if sheet_name.lower() == "summary":
            continue

        # Match sheet name to product (case-insensitive, trimmed to 28 chars)
        lookup_key = sheet_name.lower().strip()
        pid = name_to_pid.get(lookup_key)
        if not pid:
            # Try partial match: sheet name might be truncated
            for norm_name, candidate_pid in name_to_pid.items():
                if norm_name.startswith(lookup_key) or lookup_key.startswith(norm_name):
                    pid = candidate_pid
                    break

        if not pid:
            results.append(f"<b>{sheet_name}</b>: no matching product found")
            continue

        ws = wb[sheet_name]
        items = []
        first_row = True
        for row in ws.iter_rows(values_only=True):
            if first_row:
                first_row = False
                continue  # Skip header row
            # Prefer column D (Raw), fallback to columns B:C (Email:Password)
            cols = list(row)
            raw_val = cols[3] if len(cols) > 3 else None
            if raw_val and str(raw_val).strip() and str(raw_val).strip().lower() != "none":
                items.append(str(raw_val).strip())
            elif len(cols) >= 3:
                email = str(cols[1]).strip() if cols[1] else ""
                password = str(cols[2]).strip() if cols[2] else ""
                if email and email.lower() != "none":
                    if password and password.lower() != "none":
                        items.append(f"{email}:{password}")
                    else:
                        items.append(email)

        if items:
            added = await add_stock_items(pid, items, bot=message.bot)
            total_imported += added
            matched_sheets += 1
            product_name = products[pid].get("name", pid)
            results.append(f"<b>{product_name}</b>: {added} items imported")
        else:
            product_name = products[pid].get("name", pid)
            results.append(f"<b>{product_name}</b>: no items found in sheet")

    wb.close()

    # Refresh products for updated stock counts
    all_products = await get_all_products()
    stockable = {pid: p for pid, p in all_products.items() if p.get("category") in ("mail", "proxy")}
    for pid in stockable:
        stockable[pid]["stock_count"] = await get_stock_count(pid)
    await state.update_data(stock_products=stockable, stock_dm=build_admin_stock_dm(stockable))

    report = "\n".join(results) if results else "No sheets processed."
    await state.set_state(AdminFlow.stock_list)
    await message.answer(
        f"<b>Import All Stock - Complete</b>\n{_SEP}\n"
        f"Sheets matched: <b>{matched_sheets}</b>\n"
        f"Total items imported: <b>{total_imported}</b>\n\n"
        f"{report}",
        reply_markup=admin_stock_products_kb(stockable),
    )


@router_admin.message(AdminFlow.stock_import_all)
async def stock_import_all_not_file(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data = await state.get_data()
        products = data.get("stock_products", {})
        await state.set_state(AdminFlow.stock_list)
        await message.answer("Cancelled.", reply_markup=admin_stock_products_kb(products))
        return
    await message.answer("Please send a <b>.xlsx</b> file exported by <b>Download All Stock</b>.")


@router_admin.message(AdminFlow.stock_manual)
async def receive_manual_stock(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.stock_detail)
        await message.answer("Cancelled.", reply_markup=admin_stock_actions_kb())
        return
    data    = await state.get_data()
    pid     = data.get("stock_pid")
    product = data.get("stock_product", {})
    lines   = [ln.strip() for ln in message.text.splitlines() if ln.strip()]
    if not lines:
        await message.answer("No valid lines found.")
        return
    added     = await add_stock_items(pid, lines, bot=message.bot)
    new_count = await get_stock_count(pid)
    await state.set_state(AdminFlow.stock_detail)
    await message.answer(
        f"<b>{added} accounts added</b>\n{_SEP}\nProduct: <b>{product['name']}</b>\n Total Stock: <b>{new_count}</b>",
        reply_markup=admin_stock_actions_kb(),
    )


# ── Users ──────────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_USERS)
async def admin_users(message: Message, state: FSMContext):
    await _show_user_menu(message, state)


@router_admin.message(AdminFlow.user_menu)
async def admin_user_menu(message: Message, state: FSMContext):
    if message.text == BACK_BTN or message.text == HOME_BTN:
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_SEARCH_USER:
        await state.set_state(AdminFlow.user_search)
        await message.answer("Enter a Telegram User ID to look up:", reply_markup=_kb([BACK_BTN, HOME_BTN]))
        return
    if message.text == BTN_BONUS_ALL_USERS:
        await state.set_state(AdminFlow.bonus_all_amount)
        await message.answer("<b>Bonus All Users</b>\n\nEnter bonus amount (USD):", reply_markup=input_kb())
        return
    if message.text == BTN_BONUS_TOP10:
        await state.set_state(AdminFlow.bonus_top10_amount)
        await message.answer("<b>Bonus Top 10 Active Users</b>\n\nEnter bonus amount (USD):", reply_markup=input_kb())
        return
    await message.answer("Select from keyboard.")


@router_admin.message(AdminFlow.user_search)
async def admin_search_user(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await _show_user_menu(message, state)
        return
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("Enter a valid numeric user ID.")
        return
    user = await get_user(uid)
    if not user:
        await message.answer("User not found.")
        return
    mail_orders, vpn_orders, proxy_orders = await asyncio.gather(
        get_user_orders(uid),
        get_user_vpn_orders(uid),
        get_user_proxy_orders(uid),
    )
    await state.update_data(target_uid=uid, target_user=user)
    await state.set_state(AdminFlow.user_detail)
    await message.answer(
        fmt_user_info(user, len(mail_orders), len(vpn_orders), len(proxy_orders)),
        reply_markup=admin_user_actions_kb(user.get("is_banned", False)),
    )


@router_admin.message(AdminFlow.user_detail)
async def admin_user_action(message: Message, state: FSMContext):
    data = await state.get_data()
    uid  = data.get("target_uid")
    user = data.get("target_user", {})
    if message.text == BACK_BTN:
        await _show_user_menu(message, state)
        return
    if message.text == HOME_BTN:
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text in (BTN_BAN_USER, BTN_UNBAN_USER):
        new_b   = not user.get("is_banned", False)
        await ban_user(uid, new_b)
        await log_admin_action(message.from_user.id, "ban_user"if new_b else "unban_user", f"User:{uid}")
        updated = await get_user(uid)
        await state.update_data(target_user=updated)
        await message.answer(
            f"User <code>{uid}</code> {'banned 'if new_b else 'unbanned '}",
            reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
        )
        try:
            await message.bot.send_message(
                uid,
                "Your account has been banned."if new_b else "Your account has been unbanned.",
            )
        except Exception:
            pass
        return
    if message.text == BTN_ADD_BAL:
        await state.set_state(AdminFlow.user_add_bal)
        await message.answer(f"Enter USD amount to add to <code>{uid}</code>:", reply_markup=input_kb())
        return
    if message.text == BTN_REMOVE_BAL:
        await state.set_state(AdminFlow.user_remove_bal)
        await message.answer(f"Enter USD amount to remove from <code>{uid}</code>:", reply_markup=input_kb())
        return
    if message.text == BTN_ADD_BONUS:
        await state.set_state(AdminFlow.user_bonus_amount)
        current_bonus = await get_bonus(uid)
        if current_bonus["amount"] > 0:
            await message.answer(
                f"User already has a bonus: <b>${current_bonus['amount']:.2f}</b>\n"
                f"Setting a new bonus will replace it."
            )
        await message.answer(f"Enter bonus amount (USD) for <code>{uid}</code>:", reply_markup=input_kb())
        return
    if message.text == BTN_REMOVE_BONUS:
        current_bonus = await get_bonus(uid)
        if current_bonus["amount"] <= 0:
            await message.answer("User has no bonus to remove.")
            return
        await db_delete(f"users/{uid}/bonus")
        updated = await get_user(uid)
        await state.update_data(target_user=updated)
        await message.answer(
            f"Bonus removed from user <code>{uid}</code>.\n"
            f"Previous bonus was: <b>${current_bonus['amount']:.2f}</b>",
            reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
        )
        try:
            await message.bot.send_message(
                uid,
                f"<b>Bonus Removed</b>\n{_SEP}\n"
                f"Your bonus of <b>${current_bonus['amount']:.2f}</b> has been removed by admin.",
            )
        except Exception:
            pass
        return
    await message.answer("Select from keyboard.")


@router_admin.message(AdminFlow.user_add_bal)
async def admin_add_bal(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data = await state.get_data()
        user = data.get("target_user", {})
        await state.set_state(AdminFlow.user_detail)
        await message.answer(fmt_user_info(user), reply_markup=admin_user_actions_kb(user.get("is_banned", False)))
        return
    amount, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    data    = await state.get_data()
    uid     = data.get("target_uid")
    new_bal = await update_balance(uid, amount)
    updated = await get_user(uid)
    await state.update_data(target_user=updated)
    await state.set_state(AdminFlow.user_detail)
    await message.answer(
        f"Added <b>${amount:.2f}</b> → New Balance: <b>${new_bal:.2f}</b>",
        reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
    )
    try:
        await message.bot.send_message(
            uid,
            f"<b>Balance Added!</b>\n{_SEP}\n ${amount:.2f}\n New Balance: ${new_bal:.2f}",
        )
    except Exception:
        pass


@router_admin.message(AdminFlow.user_remove_bal)
async def admin_remove_bal(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data = await state.get_data()
        user = data.get("target_user", {})
        await state.set_state(AdminFlow.user_detail)
        await message.answer(fmt_user_info(user), reply_markup=admin_user_actions_kb(user.get("is_banned", False)))
        return
    amount, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    data    = await state.get_data()
    uid     = data.get("target_uid")
    target_user = data.get("target_user", {})
    new_bal = await update_balance(uid, -amount)
    updated = await get_user(uid)
    await state.update_data(target_user=updated)
    await state.set_state(AdminFlow.user_detail)
    warning = ""
    if new_bal < 0:
        warning = "\n\n\ufe0f <b>Warning:</b> Balance went negative!"
    await message.answer(
        f"Removed <b>${amount:.2f}</b> \u2192 New Balance: <b>${new_bal:.2f}</b>{warning}",
        reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
    )


# ── Admin Bonus ────────────────────────────────────────────────────

@router_admin.message(AdminFlow.user_bonus_amount)
async def admin_bonus_amount(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data = await state.get_data()
        user = data.get("target_user", {})
        await state.set_state(AdminFlow.user_detail)
        await message.answer(fmt_user_info(user), reply_markup=admin_user_actions_kb(user.get("is_banned", False)))
        return
    amount, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    if amount <= 0:
        await message.answer("Bonus amount must be greater than 0.")
        return
    await state.update_data(bonus_amount=amount, bonus_selected_products=[])
    products = await get_all_products()
    if not products:
        await message.answer("No products found. Add products first.")
        data = await state.get_data()
        user = data.get("target_user", {})
        await state.set_state(AdminFlow.user_detail)
        await message.answer(fmt_user_info(user), reply_markup=admin_user_actions_kb(user.get("is_banned", False)))
        return
    buttons = []
    for pid, prod in products.items():
        buttons.append([InlineKeyboardButton(
            text=f"{prod.get('emoji', '')} {prod['name']}",
            callback_data=f"bonus_prod:{pid}",
        )])
    buttons.append([InlineKeyboardButton(text="Done", callback_data="bonus_done")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(AdminFlow.user_bonus_products)
    await message.answer(
        f"Bonus: <b>${amount:.2f}</b>\n\n"
        f"Select which products this bonus can be used on:\n"
        f"(Tap to toggle selection, then press Done)",
        reply_markup=kb,
    )


@router_admin.callback_query(F.data.startswith("bonus_prod:"))
async def admin_bonus_toggle_product(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Not authorized", show_alert=True)
        return
    current_state = await state.get_state()
    if current_state != AdminFlow.user_bonus_products.state:
        await call.answer()
        return
    pid = call.data.split(":", 1)[1]
    data = await state.get_data()
    selected = data.get("bonus_selected_products", [])
    if pid in selected:
        selected.remove(pid)
    else:
        selected.append(pid)
    await state.update_data(bonus_selected_products=selected)
    products = await get_all_products()
    buttons = []
    for p_id, prod in products.items():
        check = " "if p_id in selected else ""
        buttons.append([InlineKeyboardButton(
            text=f"{check}{prod.get('emoji', '')} {prod['name']}",
            callback_data=f"bonus_prod:{p_id}",
        )])
    buttons.append([InlineKeyboardButton(text="Done", callback_data="bonus_done")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()


@router_admin.callback_query(F.data == "bonus_done")
async def admin_bonus_done(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Not authorized", show_alert=True)
        return
    current_state = await state.get_state()
    if current_state != AdminFlow.user_bonus_products.state:
        await call.answer()
        return
    data = await state.get_data()
    uid = data.get("target_uid")
    amount = data.get("bonus_amount", 0)
    selected = data.get("bonus_selected_products", [])
    if not selected:
        await call.answer("Please select at least one product.", show_alert=True)
        return
    # Validate that selected product IDs still exist
    products = await get_all_products()
    valid_selected = [p for p in selected if p in products]
    if not valid_selected:
        await call.answer("Selected products no longer exist. Please re-select.", show_alert=True)
        return
    await set_bonus(uid, amount, valid_selected)
    updated = await get_user(uid)
    await state.update_data(target_user=updated)
    await state.set_state(AdminFlow.user_detail)
    prod_names = [products[p]["name"] for p in valid_selected if p in products]
    await call.message.edit_text(
        f"Bonus set!\n"
        f"Amount: <b>${amount:.2f}</b>\n"
        f"Products: {', '.join(prod_names)}"
    )
    await call.message.answer(
        fmt_user_info(updated),
        reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
    )
    try:
        await call.bot.send_message(
            uid,
            f"<b>Bonus Added!</b>\n{_SEP}\n"
            f"Amount: <b>${amount:.2f}</b>\n"
            f"Eligible Products: {', '.join(prod_names)}\n\n"
            f"Use this bonus to purchase the above products!",
        )
    except Exception:
        pass
    await call.answer()


# ── Bonus All Users ────────────────────────────────────────────────

@router_admin.message(AdminFlow.bonus_all_amount)
async def admin_bonus_all_amount(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await _show_user_menu(message, state)
        return
    amount, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    if amount <= 0:
        await message.answer("Bonus amount must be greater than 0.")
        return
    await state.update_data(bonus_all_amount=amount, bonusall_selected_products=[])
    products = await get_all_products()
    if not products:
        await message.answer("No products found. Add products first.")
        await _show_user_menu(message, state)
        return
    buttons = []
    for pid, prod in products.items():
        buttons.append([InlineKeyboardButton(
            text=f"{prod.get('emoji', '')} {prod['name']}",
            callback_data=f"bonusall_prod:{pid}",
        )])
    buttons.append([InlineKeyboardButton(text="Done", callback_data="bonusall_done")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(AdminFlow.bonus_all_products)
    await message.answer(
        f"Bonus All Users: <b>${amount:.2f}</b>\n\n"
        f"Select which products this bonus can be used on:\n"
        f"(Tap to toggle selection, then press Done)",
        reply_markup=kb,
    )


@router_admin.callback_query(F.data.startswith("bonusall_prod:"))
async def admin_bonusall_toggle_product(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Not authorized", show_alert=True)
        return
    current_state = await state.get_state()
    if current_state != AdminFlow.bonus_all_products.state:
        await call.answer()
        return
    pid = call.data.split(":", 1)[1]
    data = await state.get_data()
    selected = data.get("bonusall_selected_products", [])
    if pid in selected:
        selected.remove(pid)
    else:
        selected.append(pid)
    await state.update_data(bonusall_selected_products=selected)
    products = await get_all_products()
    buttons = []
    for p_id, prod in products.items():
        check = " "if p_id in selected else ""
        buttons.append([InlineKeyboardButton(
            text=f"{check}{prod.get('emoji', '')} {prod['name']}",
            callback_data=f"bonusall_prod:{p_id}",
        )])
    buttons.append([InlineKeyboardButton(text="Done", callback_data="bonusall_done")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()


@router_admin.callback_query(F.data == "bonusall_done")
async def admin_bonusall_done(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Not authorized", show_alert=True)
        return
    current_state = await state.get_state()
    if current_state != AdminFlow.bonus_all_products.state:
        await call.answer()
        return
    data = await state.get_data()
    amount = data.get("bonus_all_amount", 0)
    selected = data.get("bonusall_selected_products", [])
    if not selected:
        await call.answer("Please select at least one product.", show_alert=True)
        return
    products = await get_all_products()
    valid_selected = [p for p in selected if p in products]
    if not valid_selected:
        await call.answer("Selected products no longer exist. Please re-select.", show_alert=True)
        return
    await call.answer()
    all_users = await get_all_users()
    count = 0
    for uid_str in all_users:
        try:
            uid_int = int(uid_str)
            await set_bonus(uid_int, amount, valid_selected)
            count += 1
            try:
                prod_names = [products[p]["name"] for p in valid_selected if p in products]
                await call.bot.send_message(
                    uid_int,
                    f"<b>Bonus Added!</b>\n{_SEP}\n"
                    f"Amount: <b>${amount:.2f}</b>\n"
                    f"Eligible Products: {', '.join(prod_names)}\n\n"
                    f"Use this bonus to purchase the above products!",
                )
            except Exception:
                pass
            await asyncio.sleep(0.05)
        except Exception:
            pass
    prod_names = [products[p]["name"] for p in valid_selected if p in products]
    await call.message.edit_text(
        f"Bonus set for <b>{count}</b> user(s)!\n"
        f"Amount: <b>${amount:.2f}</b>\n"
        f"Products: {', '.join(prod_names)}"
    )
    await _show_user_menu(call.message, state)


# ── Bonus Top 10 ──────────────────────────────────────────────────

@router_admin.message(AdminFlow.bonus_top10_amount)
async def admin_bonus_top10_amount(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await _show_user_menu(message, state)
        return
    amount, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    if amount <= 0:
        await message.answer("Bonus amount must be greater than 0.")
        return
    await state.update_data(bonus_top10_amount=amount, bonustop_selected_products=[])
    products = await get_all_products()
    if not products:
        await message.answer("No products found. Add products first.")
        await _show_user_menu(message, state)
        return
    buttons = []
    for pid, prod in products.items():
        buttons.append([InlineKeyboardButton(
            text=f"{prod.get('emoji', '')} {prod['name']}",
            callback_data=f"bonustop_prod:{pid}",
        )])
    buttons.append([InlineKeyboardButton(text="Done", callback_data="bonustop_done")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(AdminFlow.bonus_top10_products)
    await message.answer(
        f"Bonus Top 10: <b>${amount:.2f}</b>\n\n"
        f"Select which products this bonus can be used on:\n"
        f"(Tap to toggle selection, then press Done)",
        reply_markup=kb,
    )


@router_admin.callback_query(F.data.startswith("bonustop_prod:"))
async def admin_bonustop_toggle_product(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Not authorized", show_alert=True)
        return
    current_state = await state.get_state()
    if current_state != AdminFlow.bonus_top10_products.state:
        await call.answer()
        return
    pid = call.data.split(":", 1)[1]
    data = await state.get_data()
    selected = data.get("bonustop_selected_products", [])
    if pid in selected:
        selected.remove(pid)
    else:
        selected.append(pid)
    await state.update_data(bonustop_selected_products=selected)
    products = await get_all_products()
    buttons = []
    for p_id, prod in products.items():
        check = " "if p_id in selected else ""
        buttons.append([InlineKeyboardButton(
            text=f"{check}{prod.get('emoji', '')} {prod['name']}",
            callback_data=f"bonustop_prod:{p_id}",
        )])
    buttons.append([InlineKeyboardButton(text="Done", callback_data="bonustop_done")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()


@router_admin.callback_query(F.data == "bonustop_done")
async def admin_bonustop_done(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Not authorized", show_alert=True)
        return
    current_state = await state.get_state()
    if current_state != AdminFlow.bonus_top10_products.state:
        await call.answer()
        return
    data = await state.get_data()
    amount = data.get("bonus_top10_amount", 0)
    selected = data.get("bonustop_selected_products", [])
    if not selected:
        await call.answer("Please select at least one product.", show_alert=True)
        return
    products = await get_all_products()
    valid_selected = [p for p in selected if p in products]
    if not valid_selected:
        await call.answer("Selected products no longer exist. Please re-select.", show_alert=True)
        return
    await call.answer()
    all_users = await get_all_users()
    # Sort by order_count descending, take top 10
    sorted_users = sorted(
        all_users.items(),
        key=lambda x: x[1].get("order_count", 0) if isinstance(x[1], dict) else 0,
        reverse=True,
    )[:10]
    count = 0
    for uid_str, u_data in sorted_users:
        try:
            uid_int = int(uid_str)
            await set_bonus(uid_int, amount, valid_selected)
            count += 1
            try:
                prod_names = [products[p]["name"] for p in valid_selected if p in products]
                await call.bot.send_message(
                    uid_int,
                    f"<b>Bonus Added!</b>\n{_SEP}\n"
                    f"You are one of the top 10 active users!\n"
                    f"Amount: <b>${amount:.2f}</b>\n"
                    f"Eligible Products: {', '.join(prod_names)}\n\n"
                    f"Use this bonus to purchase the above products!",
                )
            except Exception:
                pass
            await asyncio.sleep(0.05)
        except Exception:
            pass
    prod_names = [products[p]["name"] for p in valid_selected if p in products]
    await call.message.edit_text(
        f"Bonus set for top <b>{count}</b> active user(s)!\n"
        f"Amount: <b>${amount:.2f}</b>\n"
        f"Products: {', '.join(prod_names)}"
    )
    await _show_user_menu(call.message, state)


# ── Coupons ────────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_COUPONS)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_COUPONS)
async def admin_coupons(message: Message, state: FSMContext):
    coupons = await get_all_coupons()
    dm = build_coupons_dm(coupons)
    await state.update_data(coupons=coupons, coupons_dm=dm)
    await state.set_state(AdminFlow.coupons_list)
    await message.answer(f"<b>Coupons</b>\n{_SEP}\n{len(coupons)} coupon(s) total.", reply_markup=admin_coupons_kb(coupons))


@router_admin.message(AdminFlow.coupons_list)
async def admin_coupons_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_CREATE_COUPON:
        await state.set_state(AdminFlow.coupon_code)
        await message.answer("Enter coupon code (alphanumeric, e.g. SAVE20):", reply_markup=input_kb())
        return
    data       = await state.get_data()
    coupons_dm = data.get("coupons_dm", {})
    cid        = resolve_selection_id(message.text, coupons_dm)
    if not cid:
        await message.answer("Select from keyboard.")
        return
    coupons = data.get("coupons", [])
    coupon  = next((c for c in coupons if c["coupon_id"] == cid), None)
    if not coupon:
        await message.answer("Not found.")
        return
    expires = time.strftime("%d %b %Y", time.gmtime(coupon.get("expires_at", 0)))
    await state.update_data(selected_cid=cid)
    await state.set_state(AdminFlow.coupon_detail)
    await message.answer(
        f"<b>{coupon['code']}</b>\n{_SEP}\n"
        f"Discount: <b>{coupon['discount_pct']:.0f}%</b>\n"
        f"Used: <b>{coupon['used_count']}/{coupon['max_uses']}</b>\n"
        f"Expires: <b>{expires}</b>\n"
        f"Status: {'Active'if coupon.get('active') else 'Inactive'}",
        reply_markup=admin_coupon_actions_kb(),
    )


@router_admin.message(AdminFlow.coupon_detail)
async def admin_coupon_action(message: Message, state: FSMContext):
    data = await state.get_data()
    cid  = data.get("selected_cid")
    if message.text in (BACK_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    if message.text == BTN_DELETE_COUPON:
        await delete_coupon(cid)
        await _back_to_coupons(message, state)
        return
    await message.answer("Select from keyboard.")


@router_admin.message(AdminFlow.coupon_code)
async def coupon_create_code(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    code = message.text.strip().upper()
    if not code.isalnum():
        await message.answer("Alphanumeric only (letters and numbers).")
        return
    await state.update_data(c_code=code)
    await state.set_state(AdminFlow.coupon_discount)
    await message.answer("Enter discount % (1–100):", reply_markup=input_kb())


@router_admin.message(AdminFlow.coupon_discount)
async def coupon_create_discount(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    pct, err = validate_discount(message.text)
    if err:
        await message.answer(err)
        return
    await state.update_data(c_pct=pct)
    await state.set_state(AdminFlow.coupon_max_uses)
    await message.answer("Enter max number of uses:", reply_markup=input_kb())


@router_admin.message(AdminFlow.coupon_max_uses)
async def coupon_create_max_uses(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    try:
        max_uses = int(message.text.strip())
        assert max_uses > 0
    except (ValueError, AssertionError):
        await message.answer("Enter a positive integer.")
        return
    await state.update_data(c_max=max_uses)
    await state.set_state(AdminFlow.coupon_expiry)
    await message.answer("Enter validity in days (e.g. 30):", reply_markup=input_kb())


@router_admin.message(AdminFlow.coupon_expiry)
async def coupon_create_expiry(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    try:
        days = int(message.text.strip())
        assert days > 0
    except (ValueError, AssertionError):
        await message.answer("Enter a positive number of days.")
        return
    data       = await state.get_data()
    expires_at = int(time.time()) + days * 86400
    c_code = data.get("c_code", "")
    c_pct  = data.get("c_pct", 0)
    c_max  = data.get("c_max", 1)
    await create_coupon(c_code, c_pct, c_max, expires_at)
    await message.answer(
        f"<b>Coupon Created!</b>\n{_SEP}\n"
        f"Code: <code>{c_code}</code>\n"
        f"Discount: <b>{c_pct:.0f}%</b>\n"
        f"Max Uses: <b>{c_max}</b>\n"
        f"Valid for: <b>{days} days</b>",
    )
    await _back_to_coupons(message, state)


async def _back_to_coupons(message: Message, state: FSMContext):
    coupons = await get_all_coupons()
    dm = build_coupons_dm(coupons)
    await state.update_data(coupons=coupons, coupons_dm=dm)
    await state.set_state(AdminFlow.coupons_list)
    await message.answer("<b>Coupons</b>", reply_markup=admin_coupons_kb(coupons))


# ── Analytics ──────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_ANALYTICS)
@router_admin.message(AdminFlow.reports_submenu, F.text == BTN_ADM_ANALYTICS)
async def admin_analytics(message: Message):
    data = await get_analytics_data()
    detail_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Detailed Breakdown", callback_data="adm_analytics_detail")]
    ])
    await message.answer(fmt_analytics(data), reply_markup=detail_kb)


# ── Order Lookup ───────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_ORDER_LOOKUP)
@router_admin.message(AdminFlow.orders_submenu, F.text == BTN_ADM_ORDER_LOOKUP)
async def admin_order_lookup_start(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.order_lookup)
    await message.answer(
        f"<b>Order Lookup</b>\n{_SEP}\n"
        f"Enter an Order ID to search:\n"
        f"<i>(e.g. ORD-0001, VPN-0001, PXY-0001)</i>",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


@router_admin.message(AdminFlow.order_lookup)
async def admin_order_lookup_search(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    oid = (message.text or "").strip()
    if not oid:
        await message.answer("Please enter a valid Order ID.")
        return
    # Validate format to prevent path injection
    if not re.match(r'^[A-Z]{2,4}-\d{3,4}$', oid):
        await message.answer(
            "Invalid Order ID format.\n"
            "Use format like: ORD-0001, VPN-0001, PXY-0001"
        )
        return
    # Prefix-aware routing to reduce redundant database lookups
    if oid.startswith("ORD-"):
        order = await db_get(f"orders/{oid}")
        if order:
            user = await get_user(order.get("user_id", 0)) or {}
            items_preview = ""
            items_list = order.get("items", [])
            if items_list:
                preview = "\n".join(str(i) for i in items_list[:5])
                more = f"\n<i>... +{len(items_list) - 5} more</i>"if len(items_list) > 5 else ""
                items_preview = f"\n <b>Items:</b>\n<code>{preview}{more}</code>"
            await message.answer(
                f"<b>Mail Order Details</b>\n{_SEP}\n"
                f"Order: <code>{oid}</code>\n"
                f"User: @{user.get('username', '—')} (<code>{order.get('user_id')}</code>)\n"
                f"Product: <b>{order.get('product_name', '—')}</b>\n"
                f"Qty: <b>{order.get('qty', 0)}</b>\n"
                f"Total: <b>${order.get('total_price', 0):.2f}</b>\n"
                f"Status: <b>{order.get('status', '—')}</b>\n"
                f"Date: {_dt(order.get('created_at', 0))}"
                f"{items_preview}",
                reply_markup=_kb([BACK_BTN, HOME_BTN]),
            )
            return
    elif oid.startswith("VPN-"):
        vpn_order = await db_get(f"vpn_orders/{oid}")
        if vpn_order:
            user = await get_user(vpn_order.get("user_id", 0)) or {}
            await message.answer(
                f"<b>VPN Order Details</b>\n{_SEP}\n"
                f"Order: <code>{oid}</code>\n"
                f"User: @{user.get('username', '—')} (<code>{vpn_order.get('user_id')}</code>)\n"
                f"Product: <b>{vpn_order.get('product_name', '—')}</b>\n"
                f"Duration: <b>{vpn_order.get('duration_days', 0)} day(s)</b>\n"
                f"Price: <b>${vpn_order.get('price', 0):.2f}</b>\n"
                f"Status: <b>{vpn_order.get('status', '—')}</b>\n"
                f"Date: {_dt(vpn_order.get('created_at', 0))}",
                reply_markup=_kb([BACK_BTN, HOME_BTN]),
            )
            return
    elif oid.startswith("PXY-"):
        proxy_order = await db_get(f"proxy_orders/{oid}")
        if proxy_order:
            user = await get_user(proxy_order.get("user_id", 0)) or {}
            items_preview = ""
            items_list = proxy_order.get("items", [])
            if items_list:
                preview = "\n".join(str(i) for i in items_list[:5])
                more = f"\n<i>... +{len(items_list) - 5} more</i>"if len(items_list) > 5 else ""
                items_preview = f"\n <b>Items:</b>\n<code>{preview}{more}</code>"
            await message.answer(
                f"<b>Proxy Order Details</b>\n{_SEP}\n"
                f"Order: <code>{oid}</code>\n"
                f"User: @{user.get('username', '—')} (<code>{proxy_order.get('user_id')}</code>)\n"
                f"Product: <b>{proxy_order.get('product_name', '—')}</b>\n"
                f"Duration: <b>{proxy_order.get('duration_days', '—')}</b>\n"
                f"Price: <b>${proxy_order.get('price', 0):.2f}</b>\n"
                f"Status: <b>{proxy_order.get('status', '—')}</b>\n"
                f"Date: {_dt(proxy_order.get('created_at', 0))}"
                f"{items_preview}",
                reply_markup=_kb([BACK_BTN, HOME_BTN]),
            )
            return
    else:
        # Fallback for legacy or unknown prefix: search all collections
        order = await db_get(f"orders/{oid}")
        if order:
            user = await get_user(order.get("user_id", 0)) or {}
            items_preview = ""
            items_list = order.get("items", [])
            if items_list:
                preview = "\n".join(str(i) for i in items_list[:5])
                more = f"\n<i>... +{len(items_list) - 5} more</i>"if len(items_list) > 5 else ""
                items_preview = f"\n <b>Items:</b>\n<code>{preview}{more}</code>"
            await message.answer(
                f"<b>Mail Order Details</b>\n{_SEP}\n"
                f"Order: <code>{oid}</code>\n"
                f"User: @{user.get('username', '—')} (<code>{order.get('user_id')}</code>)\n"
                f"Product: <b>{order.get('product_name', '—')}</b>\n"
                f"Qty: <b>{order.get('qty', 0)}</b>\n"
                f"Total: <b>${order.get('total_price', 0):.2f}</b>\n"
                f"Status: <b>{order.get('status', '—')}</b>\n"
                f"Date: {_dt(order.get('created_at', 0))}"
                f"{items_preview}",
                reply_markup=_kb([BACK_BTN, HOME_BTN]),
            )
            return
        vpn_order = await db_get(f"vpn_orders/{oid}")
        if vpn_order:
            user = await get_user(vpn_order.get("user_id", 0)) or {}
            await message.answer(
                f"<b>VPN Order Details</b>\n{_SEP}\n"
                f"Order: <code>{oid}</code>\n"
                f"User: @{user.get('username', '—')} (<code>{vpn_order.get('user_id')}</code>)\n"
                f"Product: <b>{vpn_order.get('product_name', '—')}</b>\n"
                f"Duration: <b>{vpn_order.get('duration_days', 0)} day(s)</b>\n"
                f"Price: <b>${vpn_order.get('price', 0):.2f}</b>\n"
                f"Status: <b>{vpn_order.get('status', '—')}</b>\n"
                f"Date: {_dt(vpn_order.get('created_at', 0))}",
                reply_markup=_kb([BACK_BTN, HOME_BTN]),
            )
            return
        proxy_order = await db_get(f"proxy_orders/{oid}")
        if proxy_order:
            user = await get_user(proxy_order.get("user_id", 0)) or {}
            items_preview = ""
            items_list = proxy_order.get("items", [])
            if items_list:
                preview = "\n".join(str(i) for i in items_list[:5])
                more = f"\n<i>... +{len(items_list) - 5} more</i>"if len(items_list) > 5 else ""
                items_preview = f"\n <b>Items:</b>\n<code>{preview}{more}</code>"
            await message.answer(
                f"<b>Proxy Order Details</b>\n{_SEP}\n"
                f"Order: <code>{oid}</code>\n"
                f"User: @{user.get('username', '—')} (<code>{proxy_order.get('user_id')}</code>)\n"
                f"Product: <b>{proxy_order.get('product_name', '—')}</b>\n"
                f"Duration: <b>{proxy_order.get('duration_days', '—')}</b>\n"
                f"Price: <b>${proxy_order.get('price', 0):.2f}</b>\n"
                f"Status: <b>{proxy_order.get('status', '—')}</b>\n"
                f"Date: {_dt(proxy_order.get('created_at', 0))}"
                f"{items_preview}",
                reply_markup=_kb([BACK_BTN, HOME_BTN]),
            )
            return
    await message.answer(
        f"<b>Order Not Found</b>\n{_SEP}\n"
        f"No order found with ID: <code>{oid}</code>\n"
        f"Please check the ID and try again.",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


# ── Export Mail Orders ─────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_EXPORT)
@router_admin.message(AdminFlow.orders_submenu, F.text == BTN_ADM_EXPORT)
async def admin_export_orders(message: Message):
    _init_mail_shop_file()

    if not MAIL_SHOP_FILE.exists():
        await message.answer("No mail orders file found yet.", reply_markup=admin_main_kb())
        return

    wb = openpyxl.load_workbook(str(MAIL_SHOP_FILE))
    ws = wb.active
    total_rows = ws.max_row - 1  # subtract header

    if total_rows <= 0:
        await message.answer("No mail orders recorded yet.", reply_markup=admin_main_kb())
        return

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    await message.answer_document(
        document=BufferedInputFile(buf.read(), filename="My_Mail_Shop_Orders.xlsx"),
        caption=(
            f"<b>My Mail Shop Orders</b>\n{_SEP}\n"
            f"Total Orders: <b>{total_rows}</b>\n"
            f"Updated: {time.strftime('%d %b %Y %H:%M')} UTC"
        ),
        reply_markup=admin_main_kb(),
    )


# ── Broadcast ──────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_BROADCAST)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_BROADCAST)
async def admin_broadcast_start(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.broadcast)
    await message.answer(
        f"<b>Broadcast</b>\n{_SEP}\n"
        f"Send a text message or photo+caption.\nIt will be sent to ALL users.\n\n"
        f"Press {BACK_BTN} to cancel.",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


@router_admin.message(AdminFlow.broadcast)
async def receive_broadcast(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("Cancelled.", reply_markup=admin_main_kb())
        return
    if not message.text and not message.photo:
        await message.answer("Send text or a photo with caption.")
        return
    await state.set_state(AdminFlow.menu)
    users  = await get_all_users()
    uids   = list(users.keys())
    status = await message.answer(f"Broadcasting to <b>{len(uids)}</b> users…")
    sent = failed = 0
    for uid_str in uids:
        try:
            uid = int(uid_str)
            if message.photo:
                await message.bot.send_photo(uid, photo=message.photo[-1].file_id, caption=message.caption or "")
            else:
                await message.bot.send_message(uid, message.text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    try:
        await status.edit_text(
            f"<b>Broadcast Complete!</b>\n{_SEP}\n Sent: <b>{sent}</b>\n Failed: <b>{failed}</b>"
        )
    except Exception:
        await message.answer(
            f"<b>Broadcast Complete!</b>\n{_SEP}\n Sent: <b>{sent}</b>\n Failed: <b>{failed}</b>"
        )
    await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())


# ── Settings ───────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_SETTINGS)
async def admin_settings(message: Message, state: FSMContext):
    settings = await get_settings()
    await state.set_state(AdminFlow.settings_menu)
    await message.answer(fmt_settings(settings), reply_markup=admin_settings_kb())


@router_admin.message(AdminFlow.settings_menu)
async def admin_settings_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        data = await state.get_data()
        if data.get("settings_category"):
            # Back from sub-category -> show categories
            await state.update_data(settings_category=None)
            settings = await get_settings()
            await message.answer(fmt_settings(settings), reply_markup=admin_settings_kb())
            return
        # Back from categories -> admin main
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    # Check if it's a category button
    if message.text in SETTINGS_CATEGORIES:
        keys = SETTINGS_CATEGORIES[message.text]
        await state.update_data(settings_category=message.text)
        await message.answer(f"<b>{message.text}</b>", reply_markup=settings_category_kb(keys))
        return
    # Check if it's a setting item
    info = SETTINGS_MAP.get(message.text)
    if not info:
        await message.answer("Select from keyboard.")
        return
    key, type_, prompt = info
    await state.update_data(s_key=key, s_type=type_.__name__)
    await state.set_state(AdminFlow.settings_edit)
    await message.answer(
        f"<b>{message.text}</b>\n{_SEP}\n{prompt}\n\n<i>Send blank to clear this value.</i>",
        reply_markup=input_kb(),
    )


@router_admin.message(AdminFlow.settings_edit)
async def receive_setting(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data = await state.get_data()
        cat = data.get("settings_category")
        await state.set_state(AdminFlow.settings_menu)
        if cat and cat in SETTINGS_CATEGORIES:
            await message.answer(f"<b>{cat}</b>", reply_markup=settings_category_kb(SETTINGS_CATEGORIES[cat]))
        else:
            settings = await get_settings()
            await message.answer(fmt_settings(settings), reply_markup=admin_settings_kb())
        return
    data      = await state.get_data()
    key       = data.get("s_key", "")
    type_name = data.get("s_type", "str")
    raw       = message.text.strip()
    if type_name == "float"and raw:
        try:
            value: Any = float(raw)
        except ValueError:
            await message.answer("Enter a valid number.")
            return
        if key == "usd_rate"and value <= 0:
            await message.answer("USD rate must be greater than 0.")
            return
        if key in ("bkash_min", "nagad_min", "binance_min") and value < 0:
            await message.answer("Minimum deposit cannot be negative.")
            return
        if key == "referral_bonus_pct"and not (0 <= value <= 100):
            await message.answer("Bonus % must be between 0 and 100.")
            return
        if key == "backup_interval_hours"and value < 0:
            await message.answer("Backup interval cannot be negative. Use 0 to disable.")
            return
    else:
        value = raw
        if key == "maintenance_mode":
            normalized = raw.strip().upper()
            if normalized in ("ON", "1", "TRUE", "YES"):
                value = "ON"
            elif normalized in ("OFF", "0", "FALSE", "NO"):
                value = "OFF"
            else:
                await message.answer("Invalid value. Enter ON or OFF (also accepts yes/no, true/false, 1/0).")
                return
    await update_settings({key: value})
    settings = await get_settings()
    await state.set_state(AdminFlow.settings_menu)
    data = await state.get_data()
    cat = data.get("settings_category")
    if cat and cat in SETTINGS_CATEGORIES:
        await message.answer(
            f"<b>Updated!</b>  {key} → <code>{value or '(cleared)'}</code>",
            reply_markup=settings_category_kb(SETTINGS_CATEGORIES[cat]),
        )
    else:
        await message.answer(
            f"<b>Updated!</b>  {key} → <code>{value or '(cleared)'}</code>\n\n" + fmt_settings(settings),
            reply_markup=admin_settings_kb(),
        )


# ══════════════════════════════════════════════════════════════════
# ADMIN — Proxy Data Packages Manager
# ══════════════════════════════════════════════════════════════════

def _pkg_options(settings: dict) -> list:
    raw = settings.get("proxy_data_options", "1 GB,5 GB,10 GB,50 GB")
    return [o.strip() for o in raw.split(",") if o.strip()]

def _pkg_summary(options: list) -> str:
    if not options:
        return "<i>No packages set. Add one below.</i>"
    lines = "\n".join(f"  • <b>{o}</b>"for o in options)
    return lines

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PROXY_PKGS)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_PROXY_PKGS)
async def admin_proxy_pkgs(message: Message, state: FSMContext):
    settings = await get_settings()
    opts = _pkg_options(settings)
    await state.set_state(AdminFlow.proxy_pkg_list)
    await message.answer(
        f"<b>Proxy Data Packages</b>\n{_SEP}\n"
        f"Current packages:\n{_pkg_summary(opts)}\n\n"
        f"Tap  <b>a package</b> to remove it, or  <b>Add Package</b> to add new.",
        reply_markup=proxy_pkg_manage_kb(opts),
    )


@router_admin.message(AdminFlow.proxy_pkg_list)
async def proxy_pkg_list_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return

    if message.text == BTN_PKG_ADD:
        await state.set_state(AdminFlow.proxy_pkg_add)
        await message.answer(
            f"<b>Add Data Package</b>\n{_SEP}\n"
            f"Enter the data size to add:\n"
            f"<i>Examples: 1 GB · 5 GB · 500 MB · 2.5 GB</i>",
            reply_markup=input_kb(),
        )
        return

    settings = await get_settings()
    opts = _pkg_options(settings)
    clicked_text = message.text.strip()
    matched = None
    for o in opts:
        if clicked_text in (o, _b(o), f"📦 {o}", f"📦 {_b(o)}"):
            matched = o
            break
    if matched:
        opts.remove(matched)
        await update_settings({"proxy_data_options": ",".join(opts)})
        settings = await get_settings()
        opts = _pkg_options(settings)
        await message.answer(
            f"<b>Removed:</b> {matched}\n\n"
            f"<b>Current packages:</b>\n{_pkg_summary(opts)}",
            reply_markup=proxy_pkg_manage_kb(opts),
        )
        return

    await message.answer("Tap a package to remove, or Add Package.")


@router_admin.message(AdminFlow.proxy_pkg_add)
async def proxy_pkg_add_input(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        settings = await get_settings()
        opts = _pkg_options(settings)
        await state.set_state(AdminFlow.proxy_pkg_list)
        await message.answer(
            f"<b>Proxy Data Packages</b>\n{_SEP}\n"
            f"Current packages:\n{_pkg_summary(opts)}",
            reply_markup=proxy_pkg_manage_kb(opts),
        )
        return

    raw = message.text.strip()
    amount, err = parse_data_amount(raw)
    if err or not amount:
        await message.answer(
            f"Invalid format.\nEnter like: <code>5 GB</code> or <code>500 MB</code>",
            reply_markup=input_kb(),
        )
        return

    unit = "MB"if "MB"in raw.upper() else "GB"
    label = f"{int(amount)} {unit}"if amount == int(amount) else f"{amount} {unit}"

    settings = await get_settings()
    opts = _pkg_options(settings)
    if label in opts:
        await message.answer(f"<b>{label}</b> is already in the list.", reply_markup=input_kb())
        return

    opts.append(label)
    await update_settings({"proxy_data_options": ",".join(opts)})
    settings = await get_settings()
    opts = _pkg_options(settings)
    await state.set_state(AdminFlow.proxy_pkg_list)
    await message.answer(
        f"<b>Added:</b> {label}\n\n"
        f"<b>Current packages:</b>\n{_pkg_summary(opts)}",
        reply_markup=proxy_pkg_manage_kb(opts),
    )




# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Enhanced Analytics (hourly, daily chart, conversion)
# ══════════════════════════════════════════════════════════════════

@router_admin.callback_query(F.data == "adm_analytics_detail")
async def admin_analytics_detail_cb(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    orders, vpn, proxy = await asyncio.gather(
        db_get("orders"), db_get("vpn_orders"), db_get("proxy_orders"),
    )
    orders = orders or {}
    vpn = vpn or {}
    proxy = proxy or {}
    now = int(time.time())
    today_start = now - (now % 86400)
    week_start = now - 7 * 86400

    # Hourly breakdown for today
    hourly = [0.0] * 24
    today_count = 0
    total_value = 0.0
    for v in orders.values():
        ts = v.get("created_at", 0)
        price = v.get("total_price", 0)
        if ts >= today_start:
            hour = ((ts - today_start) // 3600) % 24
            hourly[hour] += price
            today_count += 1
            total_value += price
    for v in vpn.values():
        ts = v.get("created_at", 0)
        price = v.get("price", 0)
        if ts >= today_start and v.get("status") == "delivered":
            hour = ((ts - today_start) // 3600) % 24
            hourly[hour] += price
            today_count += 1
            total_value += price
    for v in proxy.values():
        ts = v.get("created_at", 0)
        price = v.get("price", 0)
        if ts >= today_start and v.get("status") == "delivered":
            hour = ((ts - today_start) // 3600) % 24
            hourly[hour] += price
            today_count += 1
            total_value += price

    # Daily chart for past 7 days
    daily = [0.0] * 7
    daily_counts = [0] * 7
    all_sources = list(orders.values()) + \
        [v for v in vpn.values() if v.get("status") == "delivered"] + \
        [v for v in proxy.values() if v.get("status") == "delivered"]
    for v in all_sources:
        ts = v.get("created_at", 0)
        price = v.get("total_price") or v.get("price", 0)
        if ts >= week_start:
            day_idx = min(6, (now - ts) // 86400)
            daily[6 - day_idx] += price
            daily_counts[6 - day_idx] += 1

    # Conversion rate: orders / unique users who visited
    users = await db_get("users") or {}
    total_users = len(users)
    total_orders = len(orders) + len([v for v in vpn.values() if v.get("status") == "delivered"]) + \
        len([v for v in proxy.values() if v.get("status") == "delivered"])
    conversion = (total_orders / total_users * 100) if total_users > 0 else 0
    avg_value = (total_value / today_count) if today_count > 0 else 0

    # Format hourly
    max_h = max(hourly) if any(hourly) else 1
    hourly_lines = []
    for h in range(0, 24, 3):
        val = sum(hourly[h:h+3])
        bar_len = int((val / max_h) * 8) if max_h > 0 else 0
        bar = "█" * bar_len
        hourly_lines.append(f"  {h:02d}-{h+3:02d}h: {bar} ${val:.0f}")

    # Format daily chart
    max_d = max(daily) if any(daily) else 1
    daily_lines = []
    for i in range(7):
        day_ts = now - (6 - i) * 86400
        day_lbl = datetime.fromtimestamp(day_ts, tz=pytz.UTC).strftime("%a")
        bar_len = int((daily[i] / max_d) * 8) if max_d > 0 else 0
        bar = "█" * bar_len
        daily_lines.append(f"  {day_lbl}: {bar} ${daily[i]:.0f} ({daily_counts[i]})")

    text = (
        f"<b>Detailed Analytics</b>\n{_SEP}\n\n"
        f"<b>Hourly Breakdown (Today)</b>\n"
        + "\n".join(hourly_lines) + "\n\n"
        f"<b>Daily Revenue (7 days)</b>\n"
        + "\n".join(daily_lines) + "\n\n"
        f"{_SEP}\n"
        f"<b>Conversion Rate:</b> {conversion:.1f}%\n"
        f"<b>Avg Order Value (today):</b> ${avg_value:.2f}\n"
        f"<b>Total Orders (all time):</b> {total_orders}\n"
        f"<b>Total Users:</b> {total_users}"
    )
    await call.message.answer(text)
    await call.answer()


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Low Stock Alerts
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_LOW_STOCK)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_LOW_STOCK)
async def admin_low_stock_alerts(message: Message):
    if not is_admin(message.from_user.id):
        return
    settings = await get_settings()
    threshold = int(settings.get("low_stock_threshold", 5))
    products = await get_all_products()
    low_stock = []
    for pid, p in products.items():
        if p.get("hidden"):
            continue
        count = p.get("stock_count", 0)
        if count <= threshold:
            low_stock.append((pid, p.get("name", pid), p.get("emoji", ""), count))
    if not low_stock:
        await message.answer(
            f"<b>Low Stock Alerts</b>\n{_SEP}\n\n"
            f"All products have stock above threshold ({threshold}).",
            reply_markup=admin_main_kb(),
        )
        return
    low_stock.sort(key=lambda x: x[3])
    lines = [f"<b>Low Stock Alerts</b>\n{_SEP}\n"
             f"Threshold: <b>{threshold}</b> items\n"]
    buttons = []
    for pid, name, emoji, count in low_stock[:15]:
        status = "OUT"if count == 0 else f" {count}"
        lines.append(f"  {emoji} {name}: <b>{status}</b>")
        buttons.append([InlineKeyboardButton(
            text=f"Restock: {name}", callback_data=f"adm_restock:{pid}"
        )])
    text = "\n".join(lines)
    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await message.answer(text, reply_markup=kb)


@router_admin.callback_query(F.data.startswith("adm_restock:"))
async def admin_restock_cb(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    pid = call.data.split(":", 1)[1]
    product = await get_product(pid)
    if not product:
        await call.answer("Product not found", show_alert=True)
        return
    await state.update_data(stock_pid=pid)
    await state.set_state(AdminFlow.stock_detail)
    await call.message.answer(
        f"<b>Restock: {product.get('name', pid)}</b>\n{_SEP}\n"
        f"Current stock: <b>{product.get('stock_count', 0)}</b>\n\n"
        f"Send a .txt or .xlsx file with stock items, or type items line by line.",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )
    await call.answer()


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Auto Price Sync (category markup rules)
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PRICE_SYNC)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_PRICE_SYNC)
async def admin_price_sync(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    role = await get_admin_role(message.from_user.id)
    if not check_role_permission(role, "manage_settings"):
        await message.answer("Moderators cannot manage price sync.", reply_markup=admin_main_kb())
        return
    rules = await db_get("settings/price_rules") or {}
    lines = [f"<b>Auto Price Sync</b>\n{_SEP}\n"
             f"Set markup % per category. New products inherit the category markup.\n"]
    if rules:
        for cat, pct in rules.items():
            lines.append(f"<b>{cat}</b>: +{pct}%")
    else:
        lines.append("<i>No rules set yet.</i>")
    lines.append(f"\n{_SEP}\nSend: <code>category:percentage</code>\nExample: <code>mail:15</code>")
    lines.append("Send <code>remove:category</code> to delete a rule.")
    await state.set_state(AdminFlow.price_sync)
    await message.answer("\n".join(lines), reply_markup=_kb([BACK_BTN, HOME_BTN]))


@router_admin.message(AdminFlow.price_sync)
async def admin_price_sync_input(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    text = (message.text or "").strip()
    if text.lower().startswith("remove:"):
        cat = text.split(":", 1)[1].strip().lower()
        rules = await db_get("settings/price_rules") or {}
        if cat in rules:
            del rules[cat]
            await db_set("settings/price_rules", rules)
            await message.answer(f"Removed rule for <b>{cat}</b>.")
        else:
            await message.answer(f"No rule found for <b>{cat}</b>.")
        return
    if ":"not in text:
        await message.answer("Format: <code>category:percentage</code>\nExample: <code>mail:15</code>")
        return
    parts = text.split(":", 1)
    cat = parts[0].strip().lower()
    try:
        pct = float(parts[1].strip())
    except ValueError:
        await message.answer("Percentage must be a number.")
        return
    if pct < 0 or pct > 500:
        await message.answer("Percentage must be between 0 and 500.")
        return
    rules = await db_get("settings/price_rules") or {}
    rules[cat] = pct
    await db_set("settings/price_rules", rules)
    await log_admin_action(message.from_user.id, "price_sync", f"Set {cat} markup to {pct}%")
    await message.answer(f"Set <b>{cat}</b> markup to <b>+{pct}%</b>")


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Auto Product Import (batch JSON)
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_AUTO_IMPORT)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_AUTO_IMPORT)
async def admin_auto_import(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    role = await get_admin_role(message.from_user.id)
    if not check_role_permission(role, "manage_products"):
        await message.answer("Moderators cannot import products.", reply_markup=admin_main_kb())
        return
    await state.set_state(AdminFlow.auto_import)
    await message.answer(
        f"<b>Auto Product Import</b>\n{_SEP}\n\n"
        f"Paste a JSON array of products to import.\n\n"
        f"<b>Format:</b>\n<code>"
        '[\n  {"name": "Gmail", "price": 0.5, "category": "mail", "emoji": ""},\n'
        '  {"name": "Yahoo", "price": 0.3, "category": "mail"}\n]</code>\n\n'
        f"Required fields: <b>name, price</b>\n"
        f"Optional: category, emoji, description, hidden",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


@router_admin.message(AdminFlow.auto_import)
async def admin_auto_import_input(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    text = (message.text or "").strip()
    if not text:
        await message.answer("Please paste a JSON array of products.")
        return
    try:
        products_data = json.loads(text)
    except json.JSONDecodeError as e:
        await message.answer(f"Invalid JSON: {e}")
        return
    if not isinstance(products_data, list):
        await message.answer("Expected a JSON array (list of products).")
        return
    if len(products_data) > 50:
        await message.answer("Maximum 50 products per import.")
        return
    # Get price rules for auto markup
    price_rules = await db_get("settings/price_rules") or {}
    imported = 0
    errors = []
    for i, p in enumerate(products_data):
        if not isinstance(p, dict):
            errors.append(f"Item {i+1}: not a dict")
            continue
        name = p.get("name", "").strip()
        price = p.get("price")
        if not name:
            errors.append(f"Item {i+1}: missing name")
            continue
        if price is None:
            errors.append(f"Item {i+1}: missing price")
            continue
        try:
            price = float(price)
        except (ValueError, TypeError):
            errors.append(f"Item {i+1}: invalid price")
            continue
        if price < 0:
            errors.append(f"Item {i+1}: negative price")
            continue
        category = str(p.get("category", "mail")).strip().lower()
        # Apply price rule if exists
        if category in price_rules:
            price = round(price * (1 + price_rules[category] / 100), 2)
        emoji = p.get("emoji", "")
        desc = p.get("description", "")
        hidden = bool(p.get("hidden", False))
        await create_product(name, price, emoji, category, "manual", hidden, desc)
        imported += 1
    err_text = ""
    if errors:
        err_text = "\n\n<b>Errors:</b>\n" + "\n".join(f"  - {e}"for e in errors[:10])
    await log_admin_action(message.from_user.id, "auto_import", f"Imported {imported} products")
    await state.set_state(AdminFlow.menu)
    await message.answer(
        f"<b>Import Complete</b>\n{_SEP}\n"
        f"Imported: <b>{imported}</b> products\n"
        f"Errors: <b>{len(errors)}</b>{err_text}",
        reply_markup=admin_main_kb(),
    )


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Multiple Admin Roles
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_ROLES)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_ROLES)
async def admin_roles_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    role = await get_admin_role(message.from_user.id)
    if role != "owner":
        await message.answer("Only owners can manage roles.", reply_markup=admin_main_kb())
        return
    roles_data = await get_all_admin_roles()
    lines = [f"<b>Admin Roles</b>\n{_SEP}\n"
             f"<b>Role Hierarchy:</b> Owner > Admin > Moderator\n"]
    # Show existing ADMIN_IDS as owners
    for aid in ADMIN_IDS:
        lines.append(f"<code>{aid}</code> - <b>owner</b> (config)")
    # Show additional roles from the database
    for uid_str, rdata in roles_data.items():
        uid_int = int(uid_str) if uid_str.isdigit() else 0
        if uid_int in ADMIN_IDS:
            continue
        r = rdata.get("role", "none") if isinstance(rdata, dict) else str(rdata)
        if r != "none":
            emoji_r = ""if r == "admin"else ""
            lines.append(f"  {emoji_r} <code>{uid_str}</code> - <b>{r}</b>")
    lines.append(f"\n{_SEP}\nTo assign a role, send:\n<code>user_id:role</code>")
    lines.append("Roles: <b>admin</b>, <b>moderator</b>, <b>none</b> (remove)")
    await state.set_state(AdminFlow.roles_menu)
    await message.answer("\n".join(lines), reply_markup=_kb([BACK_BTN, HOME_BTN]))


@router_admin.message(AdminFlow.roles_menu)
async def admin_roles_input(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    text = (message.text or "").strip()
    if ":"not in text:
        await message.answer("Format: <code>user_id:role</code>\nExample: <code>123456789:admin</code>")
        return
    parts = text.split(":", 1)
    try:
        target_uid = int(parts[0].strip())
    except ValueError:
        await message.answer("Invalid user ID.")
        return
    role_val = parts[1].strip().lower()
    if role_val not in ("admin", "moderator", "none"):
        await message.answer("Valid roles: <b>admin</b>, <b>moderator</b>, <b>none</b>")
        return
    if target_uid in ADMIN_IDS and role_val != "owner":
        await message.answer("Cannot change role of config-defined admins (they are always owners).")
        return
    await set_admin_role(target_uid, role_val)
    await log_admin_action(message.from_user.id, "set_role", f"Set {target_uid} to {role_val}")
    emoji_r = ""if role_val == "owner"else (""if role_val == "admin"else (""if role_val == "moderator"else ""))
    await message.answer(
        f" {emoji_r} User <code>{target_uid}</code> role set to <b>{role_val}</b>",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Advanced User Search
# ══════════════════════════════════════════════════════════════════

@router_admin.callback_query(F.data == "adm_adv_search")
async def admin_advanced_search_cb(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    await state.set_state(AdminFlow.advanced_search)
    await call.message.answer(
        f"<b>Advanced User Search</b>\n{_SEP}\n\n"
        f"<b>Search options:</b>\n"
        f"  - Username: <code>@username</code>\n"
        f"  - User ID: <code>12345678</code>\n"
        f"  - Balance range: <code>bal:10-50</code>\n"
        f"  - Order count: <code>orders:5+</code>\n"
        f"  - All users: <code>all</code>\n\n"
        f"<i>Results shown as paginated inline list.</i>",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )
    await call.answer()


@router_admin.message(AdminFlow.advanced_search)
async def admin_advanced_search_input(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    query = (message.text or "").strip()
    if not query:
        await message.answer("Enter a search query.")
        return
    users = await get_all_users()
    results = []
    if query.startswith("@"):
        uname = query[1:].lower()
        for uid, u in users.items():
            if uname in (u.get("username") or "").lower():
                results.append((uid, u))
    elif query.isdigit():
        uid_search = query
        if uid_search in users:
            results.append((uid_search, users[uid_search]))
    elif query.lower().startswith("bal:"):
        range_str = query[4:].strip()
        try:
            if "-"in range_str:
                low, high = range_str.split("-", 1)
                low, high = float(low), float(high)
            else:
                low, high = float(range_str), 999999
        except ValueError:
            await message.answer("Invalid balance range. Use: <code>bal:10-50</code>")
            return
        for uid, u in users.items():
            bal = u.get("balance", 0)
            if low <= bal <= high:
                results.append((uid, u))
    elif query.lower().startswith("orders:"):
        count_str = query[7:].strip().rstrip("+")
        try:
            min_orders = int(count_str)
        except ValueError:
            await message.answer("Invalid order count. Use: <code>orders:5+</code>")
            return
        for uid, u in users.items():
            if (u.get("order_count") or 0) >= min_orders:
                results.append((uid, u))
    elif query.lower() == "all":
        results = list(users.items())[:50]
    else:
        # Fuzzy search by username or first name
        for uid, u in users.items():
            uname = (u.get("username") or "").lower()
            fname = (u.get("first_name") or "").lower()
            if query.lower() in uname or query.lower() in fname:
                results.append((uid, u))
    if not results:
        await message.answer("No users found matching your search.")
        return
    # Paginate as inline buttons (max 10 per page)
    results = results[:30]
    buttons = []
    for uid, u in results[:10]:
        uname = u.get("username") or "No username"
        bal = u.get("balance", 0)
        buttons.append([InlineKeyboardButton(
            text=f"@{uname} | ${bal:.2f} | ID:{uid}",
            callback_data=f"adm_uinfo:{uid}",
        )])
    if len(results) > 10:
        buttons.append([InlineKeyboardButton(
            text=f"... +{len(results) - 10} more results",
            callback_data="adm_search_more",
        )])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        f"<b>Search Results</b> ({len(results)} found)",
        reply_markup=kb,
    )


@router_admin.callback_query(F.data == "adm_search_more")
async def adm_search_more_cb(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    await call.answer(
        "Use more specific search terms to narrow results.",
        show_alert=True,
    )


@router_admin.callback_query(F.data.startswith("adm_uinfo:"))
async def admin_user_info_cb(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    uid_str = call.data.split(":", 1)[1]
    user = await db_get(f"users/{uid_str}")
    if not user:
        await call.answer("User not found", show_alert=True)
        return
    text = (
        f"<b>User Details</b>\n{_SEP}\n"
        f"ID: <code>{uid_str}</code>\n"
        f"Username: @{user.get('username', 'N/A')}\n"
        f"Name: {user.get('first_name', 'N/A')}\n"
        f"Balance: <b>${user.get('balance', 0):.2f}</b>\n"
        f"Orders: <b>{user.get('order_count', 0)}</b>\n"
        f"Total Spent: <b>${user.get('total_spent', 0):.2f}</b>\n"
        f"Banned: <b>{'Yes'if user.get('banned') else 'No'}</b>\n"
        f"Joined: {_dt(user.get('created_at', 0))}"
    )
    await call.message.answer(text)
    await call.answer()


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Transaction Export (CSV/Excel)
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_EXPORT_TX)
@router_admin.message(AdminFlow.reports_submenu, F.text == BTN_ADM_EXPORT_TX)
async def admin_export_transactions(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminFlow.export_transactions)
    await message.answer(
        f"<b>Transaction Export</b>\n{_SEP}\n\n"
        f"Export all transactions as Excel (.xlsx) with separate sheets.\n\n"
        f"<b>Options:</b>\n"
        f"  - Send <code>all</code> for all-time data\n"
        f"  - Send <code>7d</code> for last 7 days\n"
        f"  - Send <code>30d</code> for last 30 days\n"
        f"  - Send dates: <code>2024-01-01:2024-12-31</code>",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


@router_admin.message(AdminFlow.export_transactions)
async def admin_export_tx_input(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    text = (message.text or "").strip().lower()
    now = int(time.time())
    start_ts = 0
    end_ts = now
    if text == "all":
        start_ts = 0
    elif text == "7d":
        start_ts = now - 7 * 86400
    elif text == "30d":
        start_ts = now - 30 * 86400
    elif ":"in text:
        try:
            parts = text.split(":", 1)
            start_dt = datetime.strptime(parts[0].strip(), "%Y-%m-%d")
            end_dt = datetime.strptime(parts[1].strip(), "%Y-%m-%d")
            start_ts = int(start_dt.timestamp())
            end_ts = int(end_dt.timestamp()) + 86400
        except (ValueError, IndexError):
            await message.answer("Invalid date format. Use: <code>2024-01-01:2024-12-31</code>")
            return
    else:
        await message.answer("Send <code>all</code>, <code>7d</code>, <code>30d</code>, or <code>date:date</code>")
        return

    orders, vpn, proxy, deposits = await asyncio.gather(
        db_get("orders"), db_get("vpn_orders"),
        db_get("proxy_orders"), db_get("deposits"),
    )
    orders = orders or {}
    vpn = vpn or {}
    proxy = proxy or {}
    deposits = deposits or {}

    wb = openpyxl.Workbook()
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

    # Sheet 1: Mail Orders
    ws = wb.active
    ws.title = "Mail Orders"
    headers = ["Order ID", "User ID", "Product", "Qty", "Total ($)", "Status", "Date"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
    row = 2
    for oid, o in orders.items():
        ts = o.get("created_at", 0)
        if start_ts <= ts <= end_ts:
            ws.cell(row=row, column=1, value=oid)
            ws.cell(row=row, column=2, value=str(o.get("user_id", "")))
            ws.cell(row=row, column=3, value=o.get("product_name", ""))
            ws.cell(row=row, column=4, value=o.get("qty", 0))
            ws.cell(row=row, column=5, value=round(o.get("total_price", 0), 2))
            ws.cell(row=row, column=6, value=o.get("status", ""))
            ws.cell(row=row, column=7, value=_dt(ts))
            row += 1

    # Sheet 2: VPN Orders
    ws2 = wb.create_sheet("VPN Orders")
    headers2 = ["Order ID", "User ID", "Product", "Duration", "Price ($)", "Status", "Date"]
    for col, h in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
    row = 2
    for oid, o in vpn.items():
        ts = o.get("created_at", 0)
        if start_ts <= ts <= end_ts:
            ws2.cell(row=row, column=1, value=oid)
            ws2.cell(row=row, column=2, value=str(o.get("user_id", "")))
            ws2.cell(row=row, column=3, value=o.get("product_name", ""))
            ws2.cell(row=row, column=4, value=f"{o.get('duration_days', 0)} days")
            ws2.cell(row=row, column=5, value=round(o.get("price", 0), 2))
            ws2.cell(row=row, column=6, value=o.get("status", ""))
            ws2.cell(row=row, column=7, value=_dt(ts))
            row += 1

    # Sheet 3: Proxy Orders
    ws3 = wb.create_sheet("Proxy Orders")
    headers3 = ["Order ID", "User ID", "Product", "Data", "Price ($)", "Status", "Date"]
    for col, h in enumerate(headers3, 1):
        cell = ws3.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
    row = 2
    for oid, o in proxy.items():
        ts = o.get("created_at", 0)
        if start_ts <= ts <= end_ts:
            ws3.cell(row=row, column=1, value=oid)
            ws3.cell(row=row, column=2, value=str(o.get("user_id", "")))
            ws3.cell(row=row, column=3, value=o.get("product_name", ""))
            ws3.cell(row=row, column=4, value=str(o.get("duration_days", "")))
            ws3.cell(row=row, column=5, value=round(o.get("price", 0), 2))
            ws3.cell(row=row, column=6, value=o.get("status", ""))
            ws3.cell(row=row, column=7, value=_dt(ts))
            row += 1

    # Sheet 4: Deposits
    ws4 = wb.create_sheet("Deposits")
    headers4 = ["Deposit ID", "User ID", "Username", "Method", "BDT", "USD", "Status", "Date"]
    for col, h in enumerate(headers4, 1):
        cell = ws4.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
    row = 2
    for did, d in deposits.items():
        ts = d.get("created_at", 0)
        if start_ts <= ts <= end_ts:
            ws4.cell(row=row, column=1, value=did)
            ws4.cell(row=row, column=2, value=str(d.get("user_id", "")))
            ws4.cell(row=row, column=3, value=d.get("username", ""))
            ws4.cell(row=row, column=4, value=d.get("method", ""))
            ws4.cell(row=row, column=5, value=round(d.get("amount_bdt", 0), 2))
            ws4.cell(row=row, column=6, value=round(d.get("amount_usd", 0), 2))
            ws4.cell(row=row, column=7, value=d.get("status", ""))
            ws4.cell(row=row, column=8, value=_dt(ts))
            row += 1

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    date_str = time.strftime("%Y%m%d_%H%M", time.gmtime())
    await log_admin_action(message.from_user.id, "export_transactions", f"Filter: {text}")
    await state.set_state(AdminFlow.menu)
    await message.answer_document(
        document=BufferedInputFile(buf.read(), filename=f"transactions_{date_str}.xlsx"),
        caption=f"<b>Transaction Export</b>\n{_SEP}\nFilter: <b>{text}</b>",
        reply_markup=admin_main_kb(),
    )


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Service Status Manager
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_STATUS_MGR)
@router_admin.message(AdminFlow.tools_submenu, F.text == BTN_ADM_STATUS_MGR)
async def admin_service_status(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    products = await get_all_products()
    if not products:
        await message.answer("No products found.", reply_markup=admin_main_kb())
        return
    lines = [f"<b>Service Status Manager</b>\n{_SEP}\n"
             f"Toggle products online/offline with one tap.\n"]
    buttons = []
    for pid, p in sorted(products.items(), key=lambda x: x[1].get("name", "")):
        status = p.get("status", "online")
        icon = ""if status == "online"else ""
        name = p.get("name", pid)
        buttons.append([InlineKeyboardButton(
            text=f"{icon} {name} [{status}]",
            callback_data=f"adm_toggle:{pid}",
        )])
    buttons.append([InlineKeyboardButton(text="Bulk: All Online", callback_data="adm_bulk_on")])
    buttons.append([InlineKeyboardButton(text="Bulk: All Offline", callback_data="adm_bulk_off")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("\n".join(lines), reply_markup=kb)


@router_admin.callback_query(F.data.startswith("adm_toggle:"))
async def admin_toggle_status_cb(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    pid = call.data.split(":", 1)[1]
    product = await get_product(pid)
    if not product:
        await call.answer("Product not found", show_alert=True)
        return
    current = product.get("status", "online")
    new_status = "offline"if current == "online"else "online"
    await update_product(pid, {"status": new_status})
    icon = ""if new_status == "online"else ""
    await log_admin_action(call.from_user.id, "toggle_status", f"{product.get('name', pid)}: {new_status}")
    await call.answer(f"{icon} {product.get('name', pid)}: {new_status}")
    # Refresh the list
    products = await get_all_products()
    buttons = []
    for p_id, p in sorted(products.items(), key=lambda x: x[1].get("name", "")):
        status = p.get("status", "online")
        s_icon = ""if status == "online"else ""
        name = p.get("name", p_id)
        buttons.append([InlineKeyboardButton(
            text=f"{s_icon} {name} [{status}]",
            callback_data=f"adm_toggle:{p_id}",
        )])
    buttons.append([InlineKeyboardButton(text="Bulk: All Online", callback_data="adm_bulk_on")])
    buttons.append([InlineKeyboardButton(text="Bulk: All Offline", callback_data="adm_bulk_off")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        await call.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass


@router_admin.callback_query(F.data == "adm_bulk_on")
async def admin_bulk_online_cb(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    products = await get_all_products()
    for pid in products:
        await update_product(pid, {"status": "online"})
    await log_admin_action(call.from_user.id, "bulk_status", "All products set to online")
    await call.answer("All products set to ONLINE")
    # Refresh
    products = await get_all_products()
    buttons = []
    for p_id, p in sorted(products.items(), key=lambda x: x[1].get("name", "")):
        buttons.append([InlineKeyboardButton(
            text=f" {p.get('name', p_id)} [online]",
            callback_data=f"adm_toggle:{p_id}",
        )])
    buttons.append([InlineKeyboardButton(text="Bulk: All Online", callback_data="adm_bulk_on")])
    buttons.append([InlineKeyboardButton(text="Bulk: All Offline", callback_data="adm_bulk_off")])
    try:
        await call.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except Exception:
        pass


@router_admin.callback_query(F.data == "adm_bulk_off")
async def admin_bulk_offline_cb(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    products = await get_all_products()
    for pid in products:
        await update_product(pid, {"status": "offline"})
    await log_admin_action(call.from_user.id, "bulk_status", "All products set to offline")
    await call.answer("All products set to OFFLINE")
    products = await get_all_products()
    buttons = []
    for p_id, p in sorted(products.items(), key=lambda x: x[1].get("name", "")):
        buttons.append([InlineKeyboardButton(
            text=f" {p.get('name', p_id)} [offline]",
            callback_data=f"adm_toggle:{p_id}",
        )])
    buttons.append([InlineKeyboardButton(text="Bulk: All Online", callback_data="adm_bulk_on")])
    buttons.append([InlineKeyboardButton(text="Bulk: All Offline", callback_data="adm_bulk_off")])
    try:
        await call.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Profit Calculator
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PROFIT)
@router_admin.message(AdminFlow.reports_submenu, F.text == BTN_ADM_PROFIT)
async def admin_profit_calc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    products = await get_all_products()
    orders, vpn, proxy = await asyncio.gather(
        db_get("orders"), db_get("vpn_orders"), db_get("proxy_orders"),
    )
    orders = orders or {}
    vpn = vpn or {}
    proxy = proxy or {}

    # Calculate per-product revenue
    product_revenue = defaultdict(float)
    product_sold = defaultdict(int)
    for o in orders.values():
        pid = o.get("product_id", "")
        product_revenue[pid] += o.get("total_price", 0)
        product_sold[pid] += o.get("qty", 0)
    for o in vpn.values():
        if o.get("status") == "delivered":
            pid = o.get("product_id", "")
            product_revenue[pid] += o.get("price", 0)
            product_sold[pid] += 1
    for o in proxy.values():
        if o.get("status") == "delivered":
            pid = o.get("product_id", "")
            product_revenue[pid] += o.get("price", 0)
            product_sold[pid] += 1

    total_revenue = sum(product_revenue.values())
    total_cost = 0.0
    lines = [f"<b>Profit Calculator</b>\n{_SEP}\n"]
    lines.append("<b>Per-Product Breakdown:</b>\n")
    for pid, p in products.items():
        rev = product_revenue.get(pid, 0)
        cost_per = p.get("cost_price", 0)
        sold = product_sold.get(pid, 0)
        cost = cost_per * sold
        total_cost += cost
        profit = rev - cost
        margin = (profit / rev * 100) if rev > 0 else 0
        if rev > 0 or sold > 0:
            _pkg_emoji = p.get('emoji', '')
            lines.append(
                f"  {_pkg_emoji} <b>{p.get('name', pid)}</b>\n"
                f"Revenue: ${rev:.2f} | Cost: ${cost:.2f} | Profit: ${profit:.2f} ({margin:.0f}%)"
            )
    total_profit = total_revenue - total_cost
    overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    lines.append(f"\n{_SEP}")
    lines.append(f"<b>Total Revenue:</b> ${total_revenue:.2f}")
    lines.append(f"<b>Total Cost:</b> ${total_cost:.2f}")
    lines.append(f"<b>Net Profit:</b> ${total_profit:.2f}")
    lines.append(f"<b>Overall Margin:</b> {overall_margin:.1f}%")
    lines.append(f"\n<i>Set cost per item via:</i> <code>set_cost:PRODUCT_ID:amount</code>")
    await state.set_state(AdminFlow.profit_calc)
    await message.answer("\n".join(lines), reply_markup=_kb([BACK_BTN, HOME_BTN]))


@router_admin.message(AdminFlow.profit_calc)
async def admin_profit_set_cost(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("<b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    text = (message.text or "").strip()
    if not text.lower().startswith("set_cost:"):
        await message.answer("Use format: <code>set_cost:PRODUCT_ID:amount</code>")
        return
    parts = text.split(":", 2)
    if len(parts) < 3:
        await message.answer("Format: <code>set_cost:PRD-0001:0.10</code>")
        return
    pid = parts[1].strip()
    try:
        cost = float(parts[2].strip())
    except ValueError:
        await message.answer("Invalid cost amount.")
        return
    product = await get_product(pid)
    if not product:
        await message.answer(f"Product <code>{pid}</code> not found.")
        return
    await update_product(pid, {"cost_price": cost})
    await message.answer(
        f"Set cost for <b>{product.get('name', pid)}</b> to <b>${cost:.2f}</b> per item."
    )


# ══════════════════════════════════════════════════════════════════
# ADMIN — FEAT-002: Activity Logs
# ══════════════════════════════════════════════════════════════════

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_LOGS)
@router_admin.message(AdminFlow.reports_submenu, F.text == BTN_ADM_LOGS)
async def admin_activity_logs(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    logs = await get_activity_logs(limit=15, offset=0)
    if not logs:
        await message.answer(
            f"<b>Activity Logs</b>\n{_SEP}\n\n<i>No activity logs yet.</i>",
            reply_markup=admin_main_kb(),
        )
        return
    lines = [f"<b>Activity Logs</b>\n{_SEP}\n"]
    for log in logs:
        ts = _dt(log.get("timestamp", 0))
        admin_id = log.get("admin_id", "?")
        action = log.get("action", "?")
        details = log.get("details", "")
        detail_str = f" - {details}"if details else ""
        lines.append(f"<code>{ts}</code>\n  Admin: <code>{admin_id}</code> | <b>{action}</b>{detail_str}\n")
    buttons = []
    if len(logs) >= 15:
        buttons.append([InlineKeyboardButton(text="Next Page", callback_data="adm_logs:15")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await message.answer("\n".join(lines), reply_markup=kb or admin_main_kb())


@router_admin.callback_query(F.data.startswith("adm_logs:"))
async def admin_logs_page_cb(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Denied", show_alert=True)
        return
    offset = int(call.data.split(":", 1)[1])
    logs = await get_activity_logs(limit=15, offset=offset)
    if not logs:
        await call.answer("No more logs", show_alert=True)
        return
    lines = [f"<b>Activity Logs</b> (page {offset // 15 + 2})\n{_SEP}\n"]
    for log in logs:
        ts = _dt(log.get("timestamp", 0))
        admin_id = log.get("admin_id", "?")
        action = log.get("action", "?")
        details = log.get("details", "")
        detail_str = f" - {details}"if details else ""
        lines.append(f"<code>{ts}</code>\n  Admin: <code>{admin_id}</code> | <b>{action}</b>{detail_str}\n")
    buttons = []
    if len(logs) >= 15:
        buttons.append([InlineKeyboardButton(text="Next Page", callback_data=f"adm_logs:{offset + 15}")])
    if offset > 0:
        buttons.append([InlineKeyboardButton(text="⬅ Previous", callback_data=f"adm_logs:{max(0, offset - 15)}")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await call.message.answer("\n".join(lines), reply_markup=kb)
    await call.answer()


# ══════════════════════════════════════════════════════════════════
# DISPATCHER
# ══════════════════════════════════════════════════════════════════

def build_dp() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AntiSpamMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())   # FIX: apply to callbacks too

    dp.include_router(router_global)   # HOME first — highest priority
    dp.include_router(router_admin)    # Admin before user so AdminFlow states take priority
    dp.include_router(router_user_panel)  # User panel enhancements (before router_start for callbacks)
    dp.include_router(router_start)
    dp.include_router(router_mail)
    dp.include_router(router_vpn)
    dp.include_router(router_proxy)
    dp.include_router(router_deposit)
    dp.include_router(router_tempmail)
    return dp


# ══════════════════════════════════════════════════════════════════
# BACKGROUND TASK — Periodic Stock Export
# ══════════════════════════════════════════════════════════════════

async def stock_export_loop(bot: Bot) -> None:
    """Periodically export all stock as xlsx and send to the designated group."""
    while True:
        try:
            settings = await get_settings()
            interval = float(settings.get("stock_export_interval", 30))
            group_id = settings.get("stock_export_group_id") or os.getenv("STOCK_EXPORT_GROUP_ID") or STOCK_EXPORT_GROUP_ID
            if interval <= 0 or not group_id:
                # Export disabled; sleep and re-check later
                await asyncio.sleep(300)
                continue
            if interval < 1:
                interval = 1

            products = await get_all_products()
            if not products:
                await asyncio.sleep(interval * 60)
                continue

            all_stocks = {}
            for pid in products:
                all_stocks[pid] = await db_get(f"stocks/{pid}") or {}

            total_items = sum(len(v) for v in all_stocks.values())
            xlsx_bytes = make_products_xlsx(products, all_stocks)
            date_str = time.strftime("%Y%m%d_%H%M", time.gmtime())

            try:
                await bot.send_document(
                    chat_id=group_id,
                    document=BufferedInputFile(xlsx_bytes, filename=f"all_stock_{date_str}.xlsx"),
                    caption=(
                        f"<b>Auto Stock Export</b>\n"
                        f"Products: <b>{len(products)}</b>\n"
                        f"Total Items: <b>{total_items}</b>\n"
                        f"Interval: <b>{interval:.0f} min</b>\n\n"
                        f"<i>Exported at {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}</i>\n"
                        f"<i>This file is importable via Import Products.</i>"
                    ),
                )
            except Exception as send_err:
                logger.warning("Auto stock export failed to send to group %s: %s", group_id, send_err)
                await asyncio.sleep(300)
                continue

            await asyncio.sleep(interval * 60)
        except Exception as e:
            logger.error("stock_export_loop error: %s", e)
            await asyncio.sleep(60)


# ══════════════════════════════════════════════════════════════════
# BACKGROUND TASK — Periodic Database Backup
# ══════════════════════════════════════════════════════════════════

async def backup_loop(bot: Bot) -> None:
    """Periodically export the entire database as JSON and send to all admins."""
    while True:
        try:
            settings = await get_settings()
            interval = float(settings.get("backup_interval_hours", 24))
            if interval <= 0:
                await asyncio.sleep(300)
                continue

            # Whole database (every collection, counters, roles, logs ...)
            backup_data = await db_get("") or {}
            users = backup_data.get("users") or {}
            orders = backup_data.get("orders") or {}

            json_bytes = json.dumps(backup_data, indent=2, ensure_ascii=False).encode("utf-8")

            # Summary
            user_count = len(users)
            order_count = len(orders)
            total_revenue = sum(
                float(o.get("total_price", 0)) for o in orders.values() if isinstance(o, dict)
            )

            date_str = time.strftime("%Y%m%d_%H%M", time.gmtime())
            caption = (
                f"<b>Auto Database Backup</b>\n"
                f"Users: <b>{user_count}</b>\n"
                f"Orders: <b>{order_count}</b>\n"
                f"Total Revenue: <b>{total_revenue:.2f} BDT</b>\n"
                f"Interval: <b>{interval:.0f}h</b>\n\n"
                f"<i>Backup at {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}</i>"
            )

            for adm in ADMIN_IDS:
                try:
                    await bot.send_document(
                        chat_id=adm,
                        document=BufferedInputFile(json_bytes, filename=f"backup_{date_str}.json"),
                        caption=caption,
                    )
                except Exception:
                    logger.error("backup_loop: failed to send backup to admin %s", adm)

            await asyncio.sleep(interval * 3600)
        except Exception as e:
            logger.error("backup_loop error: %s", e)
            await asyncio.sleep(60)


# ══════════════════════════════════════════════════════════════════
# STARTUP / SHUTDOWN
# ══════════════════════════════════════════════════════════════════

async def on_startup(bot: Bot) -> None:
    global _stock_export_task, _backup_task
    if WEBHOOK_URL:
        full = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"
        await bot.set_webhook(full)
        logger.info("Webhook → %s", full)
    else:
        await bot.delete_webhook()
        logger.info("Polling mode active")
    me = await bot.get_me()
    logger.info("@%s (id=%s) is online ", me.username, me.id)
    _stock_export_task = asyncio.create_task(stock_export_loop(bot))
    _backup_task = asyncio.create_task(backup_loop(bot))


async def on_shutdown(bot: Bot) -> None:
    global _stock_export_task, _backup_task
    if _stock_export_task is not None:
        _stock_export_task.cancel()
        _stock_export_task = None
    if _backup_task is not None:
        _backup_task.cancel()
        _backup_task = None
    if WEBHOOK_URL:
        await bot.delete_webhook()
    _db.flush()
    logger.info("Bot shut down.")


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp  = build_dp()

    if WEBHOOK_URL:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        logger.info("Webhook server %s:%s%s", WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH)
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    else:
        asyncio.run(_poll(dp, bot))


async def _poll(dp: Dispatcher, bot: Bot) -> None:
    await on_startup(bot)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    main()
    
