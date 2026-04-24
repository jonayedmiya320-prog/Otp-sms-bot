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

class OTPMonitorBot:
    def __init__(self, telegram_token, group_chat_id, session_cookie, target_url, target_host, csstr_param, timestamp_param):
        self.telegram_token = telegram_token
        self.group_chat_id = group_chat_id
        self.session_cookie = session_cookie
        self.target_url = target_url
        self.target_host = target_host
        self.csstr_param = csstr_param
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
        """Global Network style: 96778AW536 (first5 + AW + last3)"""
        phone_str = str(phone_number)
        if len(phone_str) >= 8:
            return phone_str[:5] + 'AW' + phone_str[-3:]
        return phone_str

    def extract_operator_name(self, operator):
        parts = str(operator).split()
        if parts:
            return parts[0]
        return str(operator)

    def escape_markdown(self, text):
        text = str(text)
        return text.replace('`', "'")

    def detect_language_from_text(self, message_text):
        """
        SMS message text এর script/character দেখে language detect করে।
        sms_data[3] এর উপর নির্ভর না করে, actual message থেকে বের করে।
        """
        text = str(message_text)

        # প্রতিটা character count করো
        scores = {
            'Arabic':     0,
            'Persian':    0,
            'Hebrew':     0,
            'Russian':    0,
            'Hindi':      0,
            'Bengali':    0,
            'Thai':       0,
            'Chinese':    0,
            'Japanese':   0,
            'Korean':     0,
            'Greek':      0,
            'Turkish':    0,
        }

        for ch in text:
            cp = ord(ch)
            # Arabic / Urdu
            if 0x0600 <= cp <= 0x06FF or 0x0750 <= cp <= 0x077F:
                scores['Arabic'] += 1
            # Hebrew
            elif 0x0590 <= cp <= 0x05FF:
                scores['Hebrew'] += 1
            # Cyrillic (Russian, Ukrainian, Bulgarian...)
            elif 0x0400 <= cp <= 0x04FF:
                scores['Russian'] += 1
            # Devanagari (Hindi, Marathi, Nepali)
            elif 0x0900 <= cp <= 0x097F:
                scores['Hindi'] += 1
            # Bengali
            elif 0x0980 <= cp <= 0x09FF:
                scores['Bengali'] += 1
            # Thai
            elif 0x0E00 <= cp <= 0x0E7F:
                scores['Thai'] += 1
            # CJK (Chinese, Japanese Kanji)
            elif 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF:
                scores['Chinese'] += 1
            # Hiragana / Katakana (Japanese)
            elif 0x3040 <= cp <= 0x30FF:
                scores['Japanese'] += 1
            # Korean Hangul
            elif 0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF:
                scores['Korean'] += 1
            # Greek
            elif 0x0370 <= cp <= 0x03FF:
                scores['Greek'] += 1

        # সর্বোচ্চ score যেটা, সেটা return করো
        best_lang = max(scores, key=scores.get)
        best_score = scores[best_lang]

        # Japanese: Chinese + Japanese char দুটোই থাকতে পারে
        if scores['Japanese'] > 0:
            return 'Japanese'

        # কোনো non-Latin script না থাকলে → Latin ভাষা detect করো
        if best_score == 0:
            text_lower = text.lower()
            # common Spanish markers
            if any(w in text_lower for w in ['código', 'contraseña', 'verificación', 'su código', 'tu código']):
                return 'Spanish'
            # French markers  
            if any(w in text_lower for w in ['votre', 'code est', 'vérification', 'ne pas partager', 'bonjour']):
                return 'French'
            # Portuguese markers
            if any(w in text_lower for w in ['seu código', 'código de', 'não compartilhe', 'verificação']):
                return 'Portuguese'
            # German markers
            if any(w in text_lower for w in ['ihr code', 'dein code', 'verifizierung', 'nicht weitergeben']):
                return 'German'
            # Turkish markers
            if any(w in text_lower for w in ['doğrulama', 'kodunuz', 'paylaşmayın']):
                return 'Turkish'
            # Indonesian/Malay markers
            if any(w in text_lower for w in ['kode', 'verifikasi', 'jangan bagikan']):
                return 'Indonesian'
            # Default Latin → English
            return 'English'

        return best_lang

    def get_country_flag(self, phone_number):
        """Phone prefix থেকে flag + code বের করে"""
        phone = str(phone_number).strip().lstrip('+')
        country_map = {
            '880': ('BD', '🇧🇩'), '91': ('IN', '🇮🇳'), '92': ('PK', '🇵🇰'),
            '94': ('LK', '🇱🇰'), '98': ('IR', '🇮🇷'), '93': ('AF', '🇦🇫'),
            '95': ('MM', '🇲🇲'), '66': ('TH', '🇹🇭'), '62': ('ID', '🇮🇩'),
            '60': ('MY', '🇲🇾'), '63': ('PH', '🇵🇭'), '65': ('SG', '🇸🇬'),
            '84': ('VN', '🇻🇳'), '86': ('CN', '🇨🇳'), '81': ('JP', '🇯🇵'),
            '82': ('KR', '🇰🇷'), '886': ('TW', '🇹🇼'),
            '964': ('IQ', '🇮🇶'), '966': ('SA', '🇸🇦'), '971': ('AE', '🇦🇪'),
            '963': ('SY', '🇸🇾'), '962': ('JO', '🇯🇴'), '961': ('LB', '🇱🇧'),
            '967': ('YE', '🇾🇪'), '968': ('OM', '🇴🇲'), '965': ('KW', '🇰🇼'),
            '974': ('QA', '🇶🇦'), '973': ('BH', '🇧🇭'), '972': ('IL', '🇮🇱'),
            '90': ('TR', '🇹🇷'), '20': ('EG', '🇪🇬'), '212': ('MA', '🇲🇦'),
            '213': ('DZ', '🇩🇿'), '216': ('TN', '🇹🇳'), '234': ('NG', '🇳🇬'),
            '255': ('TZ', '🇹🇿'), '254': ('KE', '🇰🇪'), '256': ('UG', '🇺🇬'),
            '7': ('RU', '🇷🇺'), '44': ('GB', '🇬🇧'), '33': ('FR', '🇫🇷'),
            '49': ('DE', '🇩🇪'), '39': ('IT', '🇮🇹'), '34': ('ES', '🇪🇸'),
            '31': ('NL', '🇳🇱'), '46': ('SE', '🇸🇪'), '47': ('NO', '🇳🇴'),
            '48': ('PL', '🇵🇱'), '32': ('BE', '🇧🇪'), '41': ('CH', '🇨🇭'),
            '1': ('US', '🇺🇸'), '55': ('BR', '🇧🇷'), '52': ('MX', '🇲🇽'),
            '54': ('AR', '🇦🇷'), '57': ('CO', '🇨🇴'), '58': ('VE', '🇻🇪'),
            '51': ('PE', '🇵🇪'), '56': ('CL', '🇨🇱'), '61': ('AU', '🇦🇺'),
            '64': ('NZ', '🇳🇿'), '27': ('ZA', '🇿🇦'),
        }
        for length in (3, 2, 1):
            prefix = phone[:length]
            if prefix in country_map:
                code, flag = country_map[prefix]
                return flag, code
        return '🌐', 'XX'

    def get_platform_icon(self, message_text, service_field=''):
        """SMS text থেকে platform icon + label বের করে"""
        combined = (str(message_text) + ' ' + str(service_field)).lower()
        platforms = [
            ('facebook',  '📘', 'Facebook'),
            ('fb.com',    '📘', 'Facebook'),
            ('whatsapp',  '💬', 'WhatsApp'),
            ('instagram', '📸', 'Instagram'),
            ('telegram',  '✈️',  'Telegram'),
            ('twitter',   '🐦', 'Twitter'),
            ('x.com',     '🐦', 'Twitter'),
            ('tiktok',    '🎵', 'TikTok'),
            ('snapchat',  '👻', 'Snapchat'),
            ('discord',   '🎮', 'Discord'),
            ('google',    '🔍', 'Google'),
            ('gmail',     '📧', 'Gmail'),
            ('youtube',   '▶️',  'YouTube'),
            ('apple',     '🍎', 'Apple'),
            ('microsoft', '🪟', 'Microsoft'),
            ('amazon',    '📦', 'Amazon'),
            ('paypal',    '💳', 'PayPal'),
            ('binance',   '🟡', 'Binance'),
            ('bybit',     '🔵', 'ByBit'),
            ('okx',       '⚫', 'OKX'),
            ('coinbase',  '🔵', 'Coinbase'),
            ('uber',      '🚗', 'Uber'),
            ('grab',      '🟢', 'Grab'),
            ('netflix',   '🎬', 'Netflix'),
            ('spotify',   '🎵', 'Spotify'),
            ('linkedin',  '💼', 'LinkedIn'),
            ('viber',     '💜', 'Viber'),
            ('wechat',    '💬', 'WeChat'),
            ('bkash',     '🩷', 'bKash'),
            ('nagad',     '🟠', 'Nagad'),
            ('reddit',    '🟠', 'Reddit'),
        ]
        for keyword, icon, label in platforms:
            if keyword in combined:
                return icon, label
        return '📩', 'SMS'

    def detect_language(self, message_text, service_field=''):
        """SMS language detect করে Arabic/English/Spanish etc"""
        combined = (str(message_text) + ' ' + str(service_field)).lower()
        # Arabic script check
        if any('؀' <= c <= 'ۿ' for c in str(message_text)):
            return 'Arabic'
        lang_map = {
            'arabic': 'Arabic', 'english': 'English', 'spanish': 'Spanish',
            'french': 'French', 'german': 'German', 'turkish': 'Turkish',
            'russian': 'Russian', 'portuguese': 'Portuguese',
            'hindi': 'Hindi', 'bengali': 'Bengali', 'urdu': 'Urdu',
            'chinese': 'Chinese', 'japanese': 'Japanese', 'korean': 'Korean',
            'indonesian': 'Indonesian', 'malay': 'Malay', 'thai': 'Thai',
            'vietnamese': 'Vietnamese', 'persian': 'Persian',
        }
        for key, lang in lang_map.items():
            if key in combined:
                return lang
        return 'English' 

    async def send_telegram_message(self, message, chat_id=None, reply_markup=None):
        if chat_id is None:
            chat_id = self.group_chat_id

        try:
            from telegram.request import HTTPXRequest
            request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
            bot = Bot(token=self.telegram_token, request=request)
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            logger.info("✅ Telegram message sent successfully")
            return True
        except TelegramError as e:
            logger.info(f"❌ Telegram Error: {e}")
            print(f"❌ Telegram Error: {e}")
            return False
        except Exception as e:
            logger.info(f"❌ Send Message Error: {e}")
            print(f"❌ Send Message Error: {e}")
            return False

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
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/FBDEALZONEOWNER")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/FBDEALZONEofficial")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            success = await self.send_telegram_message(startup_msg, reply_markup=reply_markup)
            if success:
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

    def format_main_message(self, sms_data, message_text, otp_code):
        """Global Network style — main info message"""
        raw_phone = str(sms_data[2])
        phone     = self.hide_phone_number(raw_phone)

        # message text এর actual script দেখে language detect করো
        language = self.detect_language_from_text(message_text)

        flag, country_code    = self.get_country_flag(raw_phone)
        plat_icon, plat_label = self.get_platform_icon(message_text, str(sms_data[3] if len(sms_data) > 3 else ''))

        # 🇾🇪 #YE 💬 96778AW536
        # #Arabic
        line1 = f"{flag} #{country_code} {plat_icon} {phone}"
        line2 = f"#{language}"

        return line1 + "\n" + line2

    def format_otp_message(self, otp_code):
        """OTP শুধু আলাদা message হিসেবে — copy করা সহজ হয়"""
        code = otp_code if otp_code else 'N/A'
        return code

    # backward compat alias
    def format_message(self, sms_data, message_text, otp_code):
        return self.format_main_message(sms_data, message_text, otp_code)

    def create_response_buttons(self):
        """Global Network style: Main Channel | Bot Panel"""
        keyboard = [
            [
                InlineKeyboardButton("Main Channel", url="https://t.me/earning_hub_official_channel"),
                InlineKeyboardButton("Bot Panel", url="https://t.me/EARNING_HUB_NUMBER_BOT"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def fetch_sms_data(self):
        current_date = time.strftime("%Y-%m-%d")

        headers = {
            'Host': self.target_host,
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; 23129RN51X Build/BP2A.250605.031.A3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.7680.177 Mobile Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'http://{self.target_host}/ints/client/SMSCDRStats',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr-DZ;q=0.8,fr;q=0.7,ru-RU;q=0.6,ru;q=0.5,kk-KZ;q=0.4,kk;q=0.3,ar-AE;q=0.2,ar;q=0.1,es-ES;q=0.1,es;q=0.1,uk-UA;q=0.1,uk;q=0.1,pt-PT;q=0.1,pt;q=0.1,fa-IR;q=0.1,fa;q=0.1,ms-MY;q=0.1,ms;q=0.1,bn-BD;q=0.1,bn;q=0.1',
            'Cookie': f'PHPSESSID={self.session_cookie}'
        }

        params = {
            'fdate1': f'{current_date} 00:00:00',
            'fdate2': f'{current_date} 23:59:59',
            'frange': '', 'fnum': '', 'fcli': '',
            'fgdate': '', 'fgmonth': '', 'fgrange': '',
            'fgnumber': '', 'fgcli': '', 'fg': '0',
            'csstr': self.csstr_param,
            'sEcho': '1', 'iColumns': '7', 'sColumns': ',,,,,,',
            'iDisplayStart': '0', 'iDisplayLength': '25',
            'mDataProp_0': '0', 'sSearch_0': '', 'bRegex_0': 'false',
            'bSearchable_0': 'true', 'bSortable_0': 'true',
            'mDataProp_1': '1', 'sSearch_1': '', 'bRegex_1': 'false',
            'bSearchable_1': 'true', 'bSortable_1': 'true',
            'mDataProp_2': '2', 'sSearch_2': '', 'bRegex_2': 'false',
            'bSearchable_2': 'true', 'bSortable_2': 'true',
            'mDataProp_3': '3', 'sSearch_3': '', 'bRegex_3': 'false',
            'bSearchable_3': 'true', 'bSortable_3': 'true',
            'mDataProp_4': '4', 'sSearch_4': '', 'bRegex_4': 'false',
            'bSearchable_4': 'true', 'bSortable_4': 'true',
            'mDataProp_5': '5', 'sSearch_5': '', 'bRegex_5': 'false',
            'bSearchable_5': 'true', 'bSortable_5': 'true',
            'mDataProp_6': '6', 'sSearch_6': '', 'bRegex_6': 'false',
            'bSearchable_6': 'true', 'bSortable_6': 'true',
            'sSearch': '', 'bRegex': 'false',
            'iSortCol_0': '0', 'sSortDir_0': 'desc', 'iSortingCols': '1',
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

                            # ── Message 1: info (flag + platform + masked number + language) ──
                            main_msg     = self.format_main_message(first_sms, message_text, otp_code)
                            reply_markup = self.create_response_buttons()
                            success1 = await self.send_telegram_message(main_msg, reply_markup=reply_markup)

                            # ── Message 2: শুধু OTP code (copy করা সহজ) ──
                            otp_msg  = self.format_otp_message(otp_code)
                            success2 = await self.send_telegram_message(otp_msg)

                            success = success1 or success2

                            self.processed_otps.add(otp_id)
                            self.processed_count += 1

                            if self.processed_count >= 1000:
                                self.processed_otps.clear()
                                self.processed_count = 0
                                logger.info("🧹 Cache cleared")

                            if success:
                                self.total_otps_sent += 1
                                self.last_otp_time = current_time
                                logger.info(f"✅ SENT: {timestamp} OTP={otp_code} Total={self.total_otps_sent}")
                            else:
                                logger.warning(f"❌ Send failed: {timestamp}")
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
    TELEGRAM_BOT_TOKEN = "7955403590:AAFA_UsxTrbmiY9zSlFz3B9aZJ-XP0C2SYc"
    GROUP_CHAT_ID = "-1003247504066"
    SESSION_COOKIE = "8da33674c0afe01df340e2fdab40cd95"
    TARGET_HOST = "168.119.13.175"
    CSSTR_PARAM = "702e1a61e513a43c6e46dcdd9f1f7cce"
    TIMESTAMP_PARAM = "1777019662550"
    TARGET_URL = f"http://{TARGET_HOST}/ints/client/res/data_smscdr.php"

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
        csstr_param=CSSTR_PARAM,
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