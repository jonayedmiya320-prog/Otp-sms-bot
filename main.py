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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Number Bot HTTP URL ───────────────────────────────────────────────────────
# Number bot যে server এ run করছে সেই IP:PORT দাও।
# Railway তে deploy করলে: "https://your-app.railway.app/otp"
# Termux/VPS তে: "http://YOUR_SERVER_IP:8080/otp"
NUMBER_BOT_HTTP_URL = "http://localhost:8080/otp"
# ──────────────────────────────────────────────────────────────────────────────

AUTO_DELETE_SECONDS = 15 * 60  # ১৫ মিনিট

class OTPMonitorBot:
    def __init__(self, telegram_token, group_chat_id, session_cookie, target_url, target_host, csstr_param, timestamp_param):
        self.telegram_token = telegram_token
        self.group_chat_id = group_chat_id
        self.session_cookie = session_cookie
        self.target_url = target_url
        self.target_host = target_host
        self.sesskey_param = csstr_param  # Now using sesskey instead of csstr
        self.timestamp_param = timestamp_param
        self.processed_otps = set()
        self.processed_count = 0
        self.start_time = datetime.now()
        self.total_otps_sent = 0
        self.last_otp_time = None
        self.is_monitoring = True

        # OTP patterns
        self.otp_patterns = [
            r'#(\d{3}\s\d{3})',                # #209 658 (Instagram)
            r'(?<!\d)(\d{3})\s(\d{3})(?!\d)',  # 209 658
            r'(?<!\d)(\d{3})-(\d{3})(?!\d)',   # 209-658
            r'code[:\s]+(\d{4,8})',             # code: 123456
            r'কোড[:\s]+(\d{4,8})',              # code in Bengali
            r'(?<!\d)(\d{6})(?!\d)',            # 6 digits
            r'(?<!\d)(\d{5})(?!\d)',            # 5 digits
            r'(?<!\d)(\d{4})(?!\d)',            # 4 digits
            r'#\s*([A-Za-z0-9]{6,20})',         # # 78581H29QFsn4Sr (Facebook style)
            r'\b([A-Z0-9]{6,12})\b',            # pure alphanumeric caps code
        ]

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
        return text.replace('`', "'")

    async def send_telegram_message(self, message, chat_id=None, reply_markup=None):
        if chat_id is None:
            chat_id = self.group_chat_id

        try:
            from telegram.request import HTTPXRequest
            request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
            bot = Bot(token=self.telegram_token, request=request)
            sent_msg = await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            logger.info("✅ Telegram message sent successfully")
            return sent_msg.message_id
        except TelegramError as e:
            logger.info(f"❌ Telegram Error: {e}")
            print(f"❌ Telegram Error: {e}")
            return None
        except Exception as e:
            logger.info(f"❌ Send Message Error: {e}")
            print(f"❌ Send Message Error: {e}")
            return None

    async def delete_message_after_delay(self, message_id, delay_seconds):
        """নির্দিষ্ট সময় পর মেসেজ ডিলিট করে"""
        await asyncio.sleep(delay_seconds)
        try:
            from telegram.request import HTTPXRequest
            request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
            bot = Bot(token=self.telegram_token, request=request)
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
            "✅ *Status:* `Live & Monitoring`\n"
            "⚡ *Mode:* `First OTP Only`\n"
            f"📡 *Host:* `{self.target_host}`\n\n"
            f"⏰ *Start Time:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            "──────────────────\n"
            "🤖 *OTP Monitor Bot*"
        )

        keyboard = [
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/sadhin8miya")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/+QylG3hEY19c1Y2Y0")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            message_id = await self.send_telegram_message(startup_msg, reply_markup=reply_markup)
            if message_id:
                logger.info("✅ Startup message sent to group")
        except Exception as e:
            logger.info(f"⚠️ Startup message failed (monitoring will continue): {e}")

    def extract_otp(self, message):
        cleaned = re.sub(r'\d{4}-\d{2}-\d{2}', '', str(message))
        cleaned = re.sub(r'\d{2}:\d{2}:\d{2}', '', cleaned)

        for pattern in self.otp_patterns:
            matches = re.findall(pattern, cleaned)
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
        msg = self.escape_markdown(message_text)
        code = self.escape_markdown(otp_code) if otp_code else 'N/A'

        return (
            "🔥 *𝐅𝐈𝐑𝐒𝐓 𝐎𝐓𝐏 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃* 🔥\n"
            "➖➖➖➖➖➖➖➖➖➖➖\n\n"
            f"📱 *𝐍𝐮𝐦𝐛𝐞𝐫:* `{phone}`\n"
            f"🏢 *𝐎𝐩𝐞𝐫𝐚𝐭𝐨𝐫:* `{operator}`\n"
            f"📟 *𝐏𝐥𝐚𝐭𝐟𝐨𝐫𝐦:* `{service}`\n\n"
            f"🟢 *𝐎𝐓𝐏 𝐂𝐨𝐝𝐞:* `{code}`\n\n"
            f"📝 *𝐌𝐞𝐬𝐬𝐚𝐠𝐞:*\n`{msg}`\n\n"
            "➖➖➖➖➖➖➖➖➖➖➖\n"
            "🤖 *𝐎𝐓𝐏 𝐌𝐨𝐧𝐢𝐭𝐨𝐫 𝐁𝐨𝐭*"
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
        """
        Number bot কে HTTP POST দিয়ে সরাসরি notify করো।
        Telegram bot→bot message limitation bypass করার জন্য।
        """
        import urllib.request as _req
        import json as _json

        # Number পরিষ্কার করো (শুধু digits)
        clean_number = re.sub(r"\D", "", str(phone_number))
        # OTP থেকে space/dash সরাও: "684 928" → "684928"
        clean_otp = re.sub(r"[\s\-]", "", str(otp_code))
        # Service lowercase, প্রথম word নাও: "WhatsApp" → "whatsapp"
        clean_service = str(service).lower().split()[0] if service else "other"

        payload = {
            "number": clean_number,
            "otp":    clean_otp,
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
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://{self.target_host}/agent/SMSCDRReports',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,fr-DZ;q=0.8,fr;q=0.7,ru-RU;q=0.6,ru;q=0.5,kk-KZ;q=0.4,kk;q=0.3,ar-AE;q=0.2,ar;q=0.1,es-ES;q=0.1,es;q=0.1,uk-UA;q=0.1,uk;q=0.1,pt-PT;q=0.1,pt;q=0.1,fa-IR;q=0.1,fa;q=0.1,ms-MY;q=0.1,ms;q=0.1,bn-BD;q=0.1,bn;q=0.1',
            'Cookie': f'PHPSESSID={self.session_cookie}'
        }

        params = {
            'fdate1': f'{current_date} 00:00:00',
            'fdate2': f'{current_date} 23:59:59',
            'frange': '',
            'fclient': '',
            'fnum': '',
            'fcli': '',
            'fgdate': '',
            'fgmonth': '',
            'fgrange': '',
            'fgclient': '',
            'fgnumber': '',
            'fgcli': '',
            'fg': '0',
            'sesskey': self.sesskey_param,
            'sEcho': '1',
            'iColumns': '9',
            'sColumns': ',,,,,,,,',
            'iDisplayStart': '0',
            'iDisplayLength': '25',
            'mDataProp_0': '0',
            'sSearch_0': '',
            'bRegex_0': 'false',
            'bSearchable_0': 'true',
            'bSortable_0': 'true',
            'mDataProp_1': '1',
            'sSearch_1': '',
            'bRegex_1': 'false',
            'bSearchable_1': 'true',
            'bSortable_1': 'true',
            'mDataProp_2': '2',
            'sSearch_2': '',
            'bRegex_2': 'false',
            'bSearchable_2': 'true',
            'bSortable_2': 'true',
            'mDataProp_3': '3',
            'sSearch_3': '',
            'bRegex_3': 'false',
            'bSearchable_3': 'true',
            'bSortable_3': 'true',
            'mDataProp_4': '4',
            'sSearch_4': '',
            'bRegex_4': 'false',
            'bSearchable_4': 'true',
            'bSortable_4': 'true',
            'mDataProp_5': '5',
            'sSearch_5': '',
            'bRegex_5': 'false',
            'bSearchable_5': 'true',
            'bSortable_5': 'true',
            'mDataProp_6': '6',
            'sSearch_6': '',
            'bRegex_6': 'false',
            'bSearchable_6': 'true',
            'bSortable_6': 'true',
            'mDataProp_7': '7',
            'sSearch_7': '',
            'bRegex_7': 'false',
            'bSearchable_7': 'true',
            'bSortable_7': 'true',
            'mDataProp_8': '8',
            'sSearch_8': '',
            'bRegex_8': 'false',
            'bSearchable_8': 'true',
            'bSortable_8': 'false',
            'sSearch': '',
            'bRegex': 'false',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc',
            'iSortingCols': '1',
            '_': self.timestamp_param
        }

        try:
            response = requests.get(
                self.target_url,
                headers=headers,
                params=params,
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                if response.text.strip():
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        logger.error(f"JSON decode error: {response.text[:200]}")
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

        while self.is_monitoring:
            try:
                check_count += 1
                current_time = datetime.now().strftime("%H:%M:%S")

                logger.info(f"🔍 Check #{check_count} at {current_time}")

                data = self.fetch_sms_data()

                if data and 'aaData' in data:
                    sms_list = data['aaData']

                    valid_sms = [
                        sms for sms in sms_list
                        if len(sms) >= 6
                        and isinstance(sms[0], str)
                        and ':' in sms[0]
                    ]

                    if valid_sms:
                        first_sms = valid_sms[0]
                        timestamp = first_sms[0]
                        phone_number = str(first_sms[2])

                        message_text = ""
                        otp_code = None
                        for i, field in enumerate(first_sms):
                            if i <= 3:
                                continue
                            if isinstance(field, str) and len(field) > 3 and field.strip() not in ('$', '', '-'):
                                found = self.extract_otp(field)
                                if found:
                                    message_text = field
                                    otp_code = found
                                    logger.info(f"📍 OTP found at index {i}: {field[:80]}")
                                    break

                        if not message_text:
                            message_text = str(first_sms[5]) if len(first_sms) > 5 else ""

                        otp_id = self.create_otp_id(timestamp, phone_number)

                        if otp_id not in self.processed_otps:
                            logger.info(f"🚨 FIRST OTP DETECTED: {timestamp}")

                            if otp_code:
                                logger.info(f"🔐 OTP Code: {otp_code}")

                                formatted_msg = self.format_message(first_sms, message_text, otp_code)
                                reply_markup = self.create_response_buttons()

                                message_id = await self.send_telegram_message(
                                    formatted_msg,
                                    reply_markup=reply_markup
                                )

                                self.processed_otps.add(otp_id)
                                self.processed_count += 1

                                if self.processed_count >= 1000:
                                    self.processed_otps.clear()
                                    self.processed_count = 0
                                    logger.info("🧹 Processed OTPs cache cleared")

                                if message_id:
                                    self.total_otps_sent += 1
                                    self.last_otp_time = current_time
                                    logger.info(f"✅ OTP SENT: {timestamp} - Total: {self.total_otps_sent}")

                                    # ── Number Bot HTTP Notify ──────────────────
                                    service_name = first_sms[3] if len(first_sms) > 3 else "other"
                                    await self.notify_number_bot(phone_number, otp_code, service_name)
                                    # ───────────────────────────────────────────

                                    asyncio.create_task(
                                        self.delete_message_after_delay(message_id, AUTO_DELETE_SECONDS)
                                    )
                                else:
                                    logger.info(f"❌ Telegram send failed: {timestamp}")
                            else:
                                self.processed_otps.add(otp_id)
                                logger.info(f"⚠️ OTP not found. Full data: {first_sms}")
                        else:
                            logger.debug(f"⏩ Already Processed: {timestamp}")
                    else:
                        logger.info("ℹ️ No valid SMS records found")
                else:
                    logger.warning("⚠️ No data from API")

                if check_count % 20 == 0:
                    logger.info(f"📊 Status - Total OTPs Sent: {self.total_otps_sent}")

                await asyncio.sleep(0.50)

            except Exception as e:
                logger.error(f"❌ Monitor Loop Error: {e}")
                print(f"❌ Monitor Loop Error: {e}")
                await asyncio.sleep(1)

async def main():
    # === NEW CONFIGURATION ===
    TELEGRAM_BOT_TOKEN = "7955403590:AAFA_UsxTrbmiY9zSlFz3B9aZJ-XP0C2SYc"
    GROUP_CHAT_ID = "-1003774165897"
    SESSION_COOKIE = "l2nimubojmjmrgv4rveceub1eh"  # Updated PHPSESSID
    TARGET_HOST = "imssms.org"
    SESSKEY_PARAM = "Q05RR0FSUUlCTw=="  # This is the sesskey from the URL
    TIMESTAMP_PARAM = "1777375805554"
    TARGET_URL = f"https://{TARGET_HOST}/agent/res/data_smscdr.php"

    print("=" * 50)
    print("🤖 OTP MONITOR BOT - FIRST OTP ONLY")
    print("=" * 50)
    print(f"📡 Host: {TARGET_HOST}")
    print("📱 Group ID:", GROUP_CHAT_ID)
    print("🚀 Starting bot...")

    otp_bot = OTPMonitorBot(
        telegram_token=TELEGRAM_BOT_TOKEN,
        group_chat_id=GROUP_CHAT_ID,
        session_cookie=SESSION_COOKIE,
        target_url=TARGET_URL,
        target_host=TARGET_HOST,
        csstr_param=SESSKEY_PARAM,  # Now using sesskey
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

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    asyncio.run(main())