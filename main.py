import requests
import json
import time
import re
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from datetime import datetime
import sys

# Fix for Python 3.13 compatibility
if sys.version_info >= (3, 13):
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ─── Number Bot HTTP URL ───────────────────────────────────────────────────────
NUMBER_BOT_HTTP_URL = "http://localhost:8080/otp"
# ──────────────────────────────────────────────────────────────────────────────

AUTO_DELETE_SECONDS = 15 * 60  # ১৫ মিনিট

class OTPMonitorBot:
    def __init__(self, telegram_token, group_chat_id, session_cookie, target_url, target_host, sesskey_param, timestamp_param):
        self.telegram_token = telegram_token
        self.group_chat_id = group_chat_id
        self.session_cookie = session_cookie
        self.target_url = target_url
        self.target_host = target_host
        self.sesskey_param = sesskey_param
        self.timestamp_param = timestamp_param
        self.processed_otps = set()
        self.processed_count = 0
        self.start_time = datetime.now()
        self.total_otps_sent = 0
        self.last_otp_time = None
        self.is_monitoring = True
        self.bot = None  # Initialize bot instance

        # OTP patterns
        self.otp_patterns = [
            r'#(\d{3}\s\d{3})',
            r'(?<!\d)(\d{3})\s(\d{3})(?!\d)',
            r'(?<!\d)(\d{3})-(\d{3})(?!\d)',
            r'code[:\s]+(\d{4,8})',
            r'কোড[:\s]+(\d{4,8})',
            r'(?<!\d)(\d{6})(?!\d)',
            r'(?<!\d)(\d{5})(?!\d)',
            r'(?<!\d)(\d{4})(?!\d)',
            r'#\s*([A-Za-z0-9]{6,20})',
            r'\b([A-Z0-9]{6,12})\b',
        ]

    async def get_bot(self):
        """Lazy initialization of bot instance"""
        if self.bot is None:
            from telegram.request import HTTPXRequest
            request = HTTPXRequest(
                connect_timeout=30, 
                read_timeout=30, 
                write_timeout=30,
                http_version="1.1"
            )
            self.bot = Bot(token=self.telegram_token, request=request)
        return self.bot

    def hide_phone_number(self, phone_number):
        phone_str = str(phone_number)
        if len(phone_str) >= 8:
            return phone_str[:5] + '***' + phone_str[-4:]
        return phone_str

    def extract_operator_name(self, operator):
        parts = str(operator).split()
        if parts:
            return parts[0]
        return str(operator)

    def escape_markdown(self, text):
        text = str(text)
        # Escape special characters for Markdown
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    async def send_telegram_message(self, message, chat_id=None, reply_markup=None):
        if chat_id is None:
            chat_id = self.group_chat_id

        try:
            bot = await self.get_bot()
            sent_msg = await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='MarkdownV2',  # Changed to MarkdownV2 for better escape handling
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            logger.info("✅ Telegram message sent successfully")
            return sent_msg.message_id
        except TelegramError as e:
            logger.error(f"❌ Telegram Error: {e}")
            # Try sending without markdown if markdown fails
            try:
                sent_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=None,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
                logger.info("✅ Telegram message sent successfully (without markdown)")
                return sent_msg.message_id
            except Exception as e2:
                logger.error(f"❌ Send failed even without markdown: {e2}")
                return None
        except Exception as e:
            logger.error(f"❌ Send Message Error: {e}")
            return None

    async def delete_message_after_delay(self, message_id, delay_seconds):
        await asyncio.sleep(delay_seconds)
        try:
            bot = await self.get_bot()
            await bot.delete_message(
                chat_id=self.group_chat_id,
                message_id=message_id
            )
            logger.info(f"🗑️ Message {message_id} auto-deleted after {delay_seconds // 60} minutes")
        except TelegramError as e:
            logger.warning(f"⚠️ Delete failed for message {message_id}: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Delete error for message {message_id}: {e}")

    async def send_startup_message(self):
        startup_msg = (
            "🚀 *OTP Monitor Bot Started* 🚀\n\n"
            "──────────────────\n\n"
            "✅ *Status:* Live & Monitoring\n"
            "⚡ *Mode:* First OTP Only\n"
            f"📡 *Host:* {self.target_host}\n\n"
            f"⏰ *Start Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "──────────────────\n"
            "🤖 OTP Monitor Bot"
        )

        keyboard = [
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Asif_store_bot")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/+QylG3hEY19c1Y2Y0")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            message_id = await self.send_telegram_message(startup_msg, reply_markup=reply_markup)
            if message_id:
                logger.info("✅ Startup message sent to group")
        except Exception as e:
            logger.error(f"⚠️ Startup message failed (monitoring will continue): {e}")

    def extract_otp(self, message):
        if not message:
            return None
        cleaned = re.sub(r'\d{4}-\d{2}-\d{2}', '', str(message))
        cleaned = re.sub(r'\d{2}:\d{2}:\d{2}', '', cleaned)

        for pattern in self.otp_patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            if matches:
                match = matches[0]
                if isinstance(match, tuple):
                    return ' '.join(m for m in match if m)
                return match
        return None

    def create_otp_id(self, timestamp, phone_number):
        return f"{timestamp}_{phone_number}"

    def format_message(self, sms_data, message_text, otp_code):
        operator = self.escape_markdown(self.extract_operator_name(sms_data[1]))
        phone = self.escape_markdown(self.hide_phone_number(sms_data[2]))
        service = self.escape_markdown(sms_data[3] if len(sms_data) > 3 else 'Unknown')
        msg = self.escape_markdown(message_text[:200])  # Limit message length
        code = self.escape_markdown(otp_code) if otp_code else 'N/A'

        return (
            "🔥 *FIRST OTP RECEIVED* 🔥\n"
            "➖➖➖➖➖➖➖➖➖➖➖\n\n"
            f"📱 *Number:* `{phone}`\n"
            f"🏢 *Operator:* `{operator}`\n"
            f"📟 *Platform:* `{service}`\n\n"
            f"🟢 *OTP Code:* `{code}`\n\n"
            f"📝 *Message:*\n`{msg}`\n\n"
            "➖➖➖➖➖➖➖➖➖➖➖\n"
            "🤖 *OTP Monitor Bot*"
        )

    def create_response_buttons(self):
        keyboard = [
            [InlineKeyboardButton("📱 Number Channel", url="https://t.me/+eUvC-joJVa45NjZl")],
            [
                InlineKeyboardButton("🤖 Number bot", url="https://t.me/FAST_SMS_NUMBER_BOT"),
                InlineKeyboardButton("📢 main Channel", url="https://t.me/+QylG3hEY19c1Y2Y0")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def notify_number_bot(self, phone_number: str, otp_code: str, service: str):
        import urllib.request as _req
        import json as _json

        clean_number = re.sub(r"\D", "", str(phone_number))
        clean_otp = re.sub(r"[\s\-]", "", str(otp_code))
        clean_service = str(service).lower().split()[0] if service else "other"

        payload = {
            "number": clean_number,
            "otp": clean_otp,
            "service": clean_service
        }

        def _post():
            data = _json.dumps(payload).encode("utf-8")
            request = _req.Request(
                NUMBER_BOT_HTTP_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with _req.urlopen(request, timeout=10) as resp:
                return _json.loads(resp.read().decode())

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(None, _post)
            logger.info(f"✅ Number bot notified → number={clean_number} otp={clean_otp} result={result}")
        except Exception as e:
            logger.warning(f"⚠️ Number bot HTTP notify failed (non-critical): {e}")

    def fetch_sms_data(self):
        current_date = time.strftime("%Y-%m-%d")

        headers = {
            'Host': self.target_host,
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; 23129RN51X Build/BP2A.250605.031.A3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.7727.55 Mobile Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'sec-ch-ua': '"Android WebView";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?1',
            'Referer': f'https://{self.target_host}/agent/SMSCDRReports',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cookie': f'PHPSESSID={self.session_cookie}'
        }

        params = {
            'fdate1': f'{current_date} 00:00:00',
            'fdate2': f'{current_date} 23:59:59',
            'frange': '', 'fclient': '', 'fnum': '', 'fcli': '',
            'fgdate': '', 'fgmonth': '', 'fgrange': '',
            'fgclient': '', 'fgnumber': '', 'fgcli': '', 'fg': '0',
            'sesskey': self.sesskey_param,
            'sEcho': '1', 
            'iColumns': '9',
            'sColumns': ',,,,,,,,',
            'iDisplayStart': '0', 
            'iDisplayLength': '25',
            'sSearch': '', 'bRegex': 'false',
            'iSortCol_0': '0', 'sSortDir_0': 'desc', 'iSortingCols': '1',
            '_': self.timestamp_param
        }

        # Add all mDataProp and search parameters dynamically
        for i in range(9):
            params[f'mDataProp_{i}'] = str(i)
            params[f'sSearch_{i}'] = ''
            params[f'bRegex_{i}'] = 'false'
            params[f'bSearchable_{i}'] = 'true'
            params[f'bSortable_{i}'] = 'true' if i != 8 else 'false'

        try:
            response = requests.get(
                self.target_url,
                headers=headers,
                params=params,
                timeout=15,
                verify=False
            )

            if response.status_code == 200:
                if response.text and response.text.strip():
                    try:
                        return response.json()
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        return None
                else:
                    return None
            else:
                logger.error(f"HTTP {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return None

    async def monitor_loop(self):
        logger.info("🚀 OTP Monitoring Started - FIRST OTP ONLY")
        await self.send_startup_message()

        check_count = 0
        error_count = 0

        while self.is_monitoring:
            try:
                check_count += 1
                current_time = datetime.now().strftime("%H:%M:%S")

                if check_count % 10 == 0:
                    logger.info(f"🔍 Check #{check_count} at {current_time}")

                data = self.fetch_sms_data()

                if data and 'aaData' in data:
                    sms_list = data['aaData']
                    error_count = 0  # Reset error count on success

                    if sms_list and len(sms_list) > 0:
                        first_sms = sms_list[0]
                        
                        if len(first_sms) >= 3:
                            timestamp = first_sms[0]
                            phone_number = str(first_sms[2])

                            message_text = ""
                            otp_code = None
                            
                            # Search through all fields for OTP
                            for i, field in enumerate(first_sms):
                                if i <= 3:
                                    continue
                                if field and isinstance(field, str) and len(field) > 3:
                                    found = self.extract_otp(field)
                                    if found:
                                        message_text = field
                                        otp_code = found
                                        logger.info(f"📍 OTP found in field {i}")
                                        break

                            if not message_text and len(first_sms) > 5:
                                message_text = str(first_sms[5]) if first_sms[5] else ""

                            otp_id = self.create_otp_id(timestamp, phone_number)

                            if otp_id not in self.processed_otps and otp_code:
                                logger.info(f"🚨 NEW OTP DETECTED: {timestamp} - Code: {otp_code}")

                                formatted_msg = self.format_message(first_sms, message_text, otp_code)
                                reply_markup = self.create_response_buttons()

                                message_id = await self.send_telegram_message(
                                    formatted_msg,
                                    reply_markup=reply_markup
                                )

                                if message_id:
                                    self.processed_otps.add(otp_id)
                                    self.processed_count += 1
                                    self.total_otps_sent += 1
                                    self.last_otp_time = current_time
                                    
                                    logger.info(f"✅ OTP SENT - Total: {self.total_otps_sent}")

                                    # Clean up old OTPs from cache
                                    if len(self.processed_otps) > 1000:
                                        old_otps = list(self.processed_otps)[:500]
                                        for old_otp in old_otps:
                                            self.processed_otps.discard(old_otp)
                                        logger.info("🧹 Old OTPs cleared from cache")

                                    # Notify number bot
                                    service_name = first_sms[3] if len(first_sms) > 3 else "other"
                                    asyncio.create_task(self.notify_number_bot(phone_number, otp_code, service_name))
                                    
                                    # Auto-delete message
                                    asyncio.create_task(self.delete_message_after_delay(message_id, AUTO_DELETE_SECONDS))
                            else:
                                if otp_id not in self.processed_otps and not otp_code:
                                    logger.debug(f"ℹ️ No OTP in message: {timestamp}")
                        else:
                            logger.warning("⚠️ Invalid SMS data format")
                    else:
                        if check_count % 20 == 0:
                            logger.info("ℹ️ No SMS records found")

                if check_count % 30 == 0:
                    logger.info(f"📊 Status - Total OTPs Sent: {self.total_otps_sent} | Cache: {len(self.processed_otps)}")

                await asyncio.sleep(0.5)

            except Exception as e:
                error_count += 1
                logger.error(f"❌ Monitor Loop Error ({error_count}): {e}")
                if error_count > 10:
                    logger.critical("Too many errors, waiting 30 seconds...")
                    await asyncio.sleep(30)
                    error_count = 0
                else:
                    await asyncio.sleep(2)

async def main():
    # Configuration from latest request
    TELEGRAM_BOT_TOKEN = "7955403590:AAFA_UsxTrbmiY9zSlFz3B9aZJ-XP0C2SYc"
    GROUP_CHAT_ID = "--1003774165897"  # Please update with your actual group ID
    SESSION_COOKIE = "l2nimubojmjmrgv4rveceub1eh"
    TARGET_HOST = "imssms.org"
    SESSKEY_PARAM = "Q05RR0FSUUlCTw=="
    TIMESTAMP_PARAM = str(int(time.time() * 1000))  # Dynamic timestamp
    TARGET_URL = f"https://{TARGET_HOST}/agent/res/data_smscdr.php"

    print("=" * 50)
    print("🤖 OTP MONITOR BOT - FIRST OTP ONLY")
    print("=" * 50)
    print(f"📡 Host: {TARGET_HOST}")
    print(f"📱 Group ID: {GROUP_CHAT_ID}")
    print("🚀 Starting bot...")

    otp_bot = OTPMonitorBot(
        telegram_token=TELEGRAM_BOT_TOKEN,
        group_chat_id=GROUP_CHAT_ID,
        session_cookie=SESSION_COOKIE,
        target_url=TARGET_URL,
        target_host=TARGET_HOST,
        sesskey_param=SESSKEY_PARAM,
        timestamp_param=TIMESTAMP_PARAM
    )

    print("✅ BOT STARTED SUCCESSFULLY!")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)

    try:
        await otp_bot.monitor_loop()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user!")
        otp_bot.is_monitoring = False
        print(f"📊 Total OTPs Sent: {otp_bot.total_otps_sent}")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        logger.critical(f"Fatal error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot shutdown complete")