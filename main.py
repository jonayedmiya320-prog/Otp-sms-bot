import requests
import json
import time
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

AUTO_DELETE_SECONDS = 15 * 60  # 15 minutes

class CreditNotesMonitorBot:
    def __init__(self, telegram_token, group_chat_id, session_cookie, target_url, target_host):
        self.telegram_token = telegram_token
        self.group_chat_id = group_chat_id
        self.session_cookie = session_cookie
        self.target_url = target_url
        self.target_host = target_host
        self.processed_notes = set()
        self.processed_count = 0
        self.start_time = datetime.now()
        self.total_notes_sent = 0
        self.last_note_time = None
        self.is_monitoring = True

    def hide_phone_number(self, phone_number):
        phone_str = str(phone_number)
        if len(phone_str) >= 8:
            return phone_str[:5] + '***' + phone_str[-4:]
        return phone_str

    def escape_markdown(self, text):
        text = str(text)
        return text.replace('`', "'").replace('*', '\\*').replace('_', '\\_')

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
            return None
        except Exception as e:
            logger.info(f"❌ Send Message Error: {e}")
            return None

    async def delete_message_after_delay(self, message_id, delay_seconds):
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

    async def send_startup_message(self):
        startup_msg = (
            "🚀 *Credit Notes Monitor Bot Started* 🚀\n\n"
            "──────────────────\n\n"
            "✅ *Status:* `Live & Monitoring`\n"
            "⚡ *Mode:* `Real-time Credit Notes`\n"
            f"📡 *Host:* `{self.target_host}`\n\n"
            f"⏰ *Start Time:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            "──────────────────\n"
            "🤖 *Credit Monitor Bot*"
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
            logger.info(f"⚠️ Startup message failed: {e}")

    def create_note_id(self, timestamp, identifier):
        return f"{timestamp}_{identifier}"

    def format_credit_note_message(self, note_data):
        """Format credit note data for Telegram message"""
        # Adjust indices based on your actual data structure
        # Typical structure might be: [timestamp, client_name, amount, status, etc.]
        
        timestamp = self.escape_markdown(note_data[0]) if len(note_data) > 0 else 'N/A'
        client = self.escape_markdown(note_data[1]) if len(note_data) > 1 else 'N/A'
        amount = self.escape_markdown(note_data[2]) if len(note_data) > 2 else 'N/A'
        status = self.escape_markdown(note_data[3]) if len(note_data) > 3 else 'N/A'
        description = self.escape_markdown(note_data[4]) if len(note_data) > 4 else 'N/A'
        
        return (
            "💰 *NEW CREDIT NOTE DETECTED* 💰\n"
            "➖➖➖➖➖➖➖➖➖➖➖\n\n"
            f"📅 *Date:* `{timestamp}`\n"
            f"👤 *Client:* `{client}`\n"
            f"💵 *Amount:* `{amount}`\n"
            f"📊 *Status:* `{status}`\n"
            f"📝 *Description:* `{description}`\n\n"
            "➖➖➖➖➖➖➖➖➖➖➖\n"
            "🤖 *Credit Monitor Bot*"
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

    def fetch_credit_notes(self):
        current_date = time.strftime("%Y-%m-%d")
        # Fetch last 30 days instead of just today
        from_date = (datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        
        headers = {
            'Host': self.target_host,
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; 23129RN51X Build/BP2A.250605.031.A3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.7727.55 Mobile Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'http://{self.target_host}/ints/agent/CreditNotes',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr-DZ;q=0.8,fr;q=0.7,ru-RU;q=0.6,ru;q=0.5,kk-KZ;q=0.4,kk;q=0.3,ar-AE;q=0.2,ar;q=0.1,es-ES;q=0.1,es;q=0.1,uk-UA;q=0.1,uk;q=0.1,pt-PT;q=0.1,pt;q=0.1,fa-IR;q=0.1,fa;q=0.1,ms-MY;q=0.1,ms;q=0.1,bn-BD;q=0.1,bn;q=0.1',
            'Cookie': f'PHPSESSID={self.session_cookie}'
        }

        params = {
            'fdate1': f'{from_date} 00:00:00',
            'fdate2': f'{current_date} 23:59:59',
            'sEcho': '1',
            'iColumns': '7',
            'sColumns': ',,,,,,',
            'iDisplayStart': '0',
            'iDisplayLength': '25',
            'mDataProp_0': '0', 'sSearch_0': '', 'bRegex_0': 'false', 'bSearchable_0': 'true', 'bSortable_0': 'true',
            'mDataProp_1': '1', 'sSearch_1': '', 'bRegex_1': 'false', 'bSearchable_1': 'true', 'bSortable_1': 'true',
            'mDataProp_2': '2', 'sSearch_2': '', 'bRegex_2': 'false', 'bSearchable_2': 'true', 'bSortable_2': 'true',
            'mDataProp_3': '3', 'sSearch_3': '', 'bRegex_3': 'false', 'bSearchable_3': 'true', 'bSortable_3': 'true',
            'mDataProp_4': '4', 'sSearch_4': '', 'bRegex_4': 'false', 'bSearchable_4': 'true', 'bSortable_4': 'true',
            'mDataProp_5': '5', 'sSearch_5': '', 'bRegex_5': 'false', 'bSearchable_5': 'true', 'bSortable_5': 'true',
            'mDataProp_6': '6', 'sSearch_6': '', 'bRegex_6': 'false', 'bSearchable_6': 'true', 'bSortable_6': 'true',
            'sSearch': '', 'bRegex': 'false',
            'iSortCol_0': '0', 'sSortDir_0': 'desc', 'iSortingCols': '1',
            '_': str(int(time.time() * 1000))
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

        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return None

    async def monitor_loop(self):
        logger.info("🚀 Credit Notes Monitoring Started")
        await self.send_startup_message()

        check_count = 0

        while self.is_monitoring:
            try:
                check_count += 1
                current_time = datetime.now().strftime("%H:%M:%S")

                if check_count % 10 == 0:
                    logger.info(f"🔍 Check #{check_count} at {current_time}")

                data = self.fetch_credit_notes()

                if data and 'aaData' in data:
                    notes_list = data['aaData']

                    valid_notes = [
                        note for note in notes_list
                        if len(note) >= 3 and note[0] and note[0] != ''
                    ]

                    if valid_notes:
                        # Get the latest note
                        latest_note = valid_notes[0]
                        
                        # Create unique ID (using timestamp and client name as identifier)
                        note_id = self.create_note_id(latest_note[0], latest_note[1] if len(latest_note) > 1 else str(check_count))

                        if note_id not in self.processed_notes:
                            logger.info(f"💰 NEW CREDIT NOTE DETECTED: {latest_note[0]}")

                            formatted_msg = self.format_credit_note_message(latest_note)
                            reply_markup = self.create_response_buttons()

                            message_id = await self.send_telegram_message(
                                formatted_msg,
                                reply_markup=reply_markup
                            )

                            self.processed_notes.add(note_id)
                            self.processed_count += 1

                            if self.processed_count >= 1000:
                                self.processed_notes.clear()
                                self.processed_count = 0
                                logger.info("🧹 Processed notes cache cleared")

                            if message_id:
                                self.total_notes_sent += 1
                                self.last_note_time = current_time
                                logger.info(f"✅ Credit Note SENT - Total: {self.total_notes_sent}")

                                asyncio.create_task(
                                    self.delete_message_after_delay(message_id, AUTO_DELETE_SECONDS)
                                )
                            else:
                                logger.info(f"❌ Telegram send failed")
                        else:
                            logger.debug(f"⏩ Already Processed: {latest_note[0]}")
                    else:
                        if check_count % 20 == 0:
                            logger.info("ℹ️ No valid credit notes found")
                else:
                    if check_count % 20 == 0:
                        logger.warning("⚠️ No data from API")

                if check_count % 50 == 0:
                    logger.info(f"📊 Status - Total Notes Sent: {self.total_notes_sent}")

                await asyncio.sleep(2)  # Check every 2 seconds

            except Exception as e:
                logger.error(f"❌ Monitor Loop Error: {e}")
                await asyncio.sleep(5)

async def main():
    # === CREDIT NOTES MONITOR CONFIGURATION ===
    TELEGRAM_BOT_TOKEN = "8185988088:AAF2aW5exkeA2SDRWiAG8t8Gy4RHQ4GoDSI"
    GROUP_CHAT_ID = "-1003774165897"  # Replace with your actual group chat ID
    SESSION_COOKIE = "nqv0r4h7mne6r4hee6t1gsvefi"
    TARGET_HOST = "45.82.67.20"
    TARGET_URL = f"http://{TARGET_HOST}/ints/agent/res/data_creditnotes.php"

    print("=" * 50)
    print("💰 CREDIT NOTES MONITOR BOT")
    print("=" * 50)
    print(f"📡 Host: {TARGET_HOST}")
    print(f"📱 Group ID: {GROUP_CHAT_ID}")
    print("🚀 Starting bot...")

    monitor_bot = CreditNotesMonitorBot(
        telegram_token=TELEGRAM_BOT_TOKEN,
        group_chat_id=GROUP_CHAT_ID,
        session_cookie=SESSION_COOKIE,
        target_url=TARGET_URL,
        target_host=TARGET_HOST
    )

    print("✅ BOT STARTED SUCCESSFULLY!")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)

    try:
        await monitor_bot.monitor_loop()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user!")
        monitor_bot.is_monitoring = False
        print(f"📊 Total Credit Notes Sent: {monitor_bot.total_notes_sent}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    asyncio.run(main())