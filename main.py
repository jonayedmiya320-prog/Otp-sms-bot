import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import json
import time
import logging
from datetime import datetime, timedelta
import requests

# Configuration
MASDAR_URL = "http://91.232.105.47"
USERNAME = "shadin"
PASSWORD = "shadin"

# Telegram Configuration
BOT_TOKEN = "8185988088:AAF2aW5exkeA2SDRWiAG8t8Gy4RHQ4GoDSI"
CHAT_ID = "-1003774165897"
OWNER_ID = "7095358778"

# Number Bot HTTP URL (localhost)
NUMBER_BOT_HTTP_URL = "http://localhost:8080/otp"

# Telegram Button URLs
NUMBER_BOT_URL     = "https://t.me/FAST_SMS_NUMBER_BOT"
MAIN_CHANNEL_URL   = "https://t.me/+QylG3hEY19c1Y2Y0"
NUMBER_CHANNEL_URL = "https://t.me/+eUvC-joJVa45NjZl"

# Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Infinix X6525B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.207 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9,bn-BD;q=0.8,bn;q=0.7',
    'X-Requested-With': 'XMLHttpRequest'
}

# Service patterns for OTP detection
SERVICE_PATTERNS = {
    # Social Media
    'WhatsApp':   r'whatsapp|واتساب|watsapp',
    'Telegram':   r'telegram',
    'Facebook':   r'facebook|fb\.com|meta',
    'Instagram':  r'instagram|ig\b',
    'Twitter':    r'twitter|x\.com',
    'TikTok':     r'tiktok|tik tok',
    'Snapchat':   r'snapchat',
    'LinkedIn':   r'linkedin',
    'Pinterest':  r'pinterest',
    'Reddit':     r'reddit',
    'Discord':    r'discord',
    'Viber':      r'viber',
    'Line':       r'\bline\b',
    'WeChat':     r'wechat|weixin',
    'KakaoTalk':  r'kakao',
    'Zalo':       r'zalo',
    'Skype':      r'skype',
    # Google
    'Google':     r'google|gmail|youtube',
    # Microsoft
    'Microsoft':  r'microsoft|outlook|hotmail|msn|xbox|live\.com',
    # Apple
    'Apple':      r'apple|icloud|itunes|app store',
    # Shopping
    'Amazon':     r'amazon',
    'SHEIN':      r'shein',
    'Alibaba':    r'alibaba|aliexpress|alipay',
    'eBay':       r'ebay',
    'Shopee':     r'shopee',
    'Lazada':     r'lazada',
    'Daraz':      r'daraz',
    'Jumia':      r'jumia',
    'Flipkart':   r'flipkart',
    'Noon':       r'\bnoon\b',
    # Payment
    'PayPal':     r'paypal',
    'Stripe':     r'stripe',
    'Wise':       r'\bwise\b|transferwise',
    'Binance':    r'binance',
    'Coinbase':   r'coinbase',
    'Crypto':     r'crypto\.com',
    'OKX':        r'\bokx\b',
    'Bybit':      r'bybit',
    'Banking':    r'bank|visa|mastercard|swift|iban',
    'Payoneer':   r'payoneer',
    'Skrill':     r'skrill',
    # Ride & Food
    'Uber':       r'\buber\b',
    'Lyft':       r'lyft',
    'Bolt':       r'\bbolt\b',
    'Careem':     r'careem',
    'Grab':       r'\bgrab\b',
    'Rapido':     r'rapido',
    'InDrive':    r'indrive',
    'Swiggy':     r'swiggy',
    'Zomato':     r'zomato',
    'Talabat':    r'talabat',
    # Streaming
    'Netflix':    r'netflix',
    'Spotify':    r'spotify',
    'YouTube':    r'youtube',
    'Disney':     r'disney',
    'HBO':        r'\bhbo\b',
    'Amazon Prime': r'prime video|primevideo',
    # Dating
    'Tinder':     r'tinder',
    'Bumble':     r'bumble',
    'Badoo':      r'badoo',
    'OkCupid':    r'okcupid',
    'Hinge':      r'hinge',
    # Travel
    'Airbnb':     r'airbnb',
    'Booking':    r'booking\.com',
    'Agoda':      r'agoda',
    'Expedia':    r'expedia',
    # Other Services
    'Zoom':       r'zoom',
    'Dropbox':    r'dropbox',
    'Adobe':      r'adobe',
    'Canva':      r'canva',
    'OpenAI':     r'openai|chatgpt',
    'Freelancer': r'freelancer',
    'Fiverr':     r'fiverr',
    'Upwork':     r'upwork',
    'Quora':      r'quora',
    'Truecaller': r'truecaller',
    'OLX':        r'\bolx\b',
    'Craigslist': r'craigslist',
    'Twilio':     r'twilio',
    'Textverify': r'textverify',
    # Fallback
    'OTP':        r'verification|verify|otp|code|كود|رمز|pin\b|passcode',
}

# Extended Country flags emojis - 250+ countries
COUNTRY_FLAGS = {
    'USA': '🇺🇸', 'UK': '🇬🇧', 'India': '🇮🇳', 'Bangladesh': '🇧🇩', 'Canada': '🇨🇦',
    'Australia': '🇦🇺', 'Germany': '🇩🇪', 'France': '🇫🇷', 'Italy': '🇮🇹', 'Spain': '🇪🇸',
    'Brazil': '🇧🇷', 'Russia': '🇷🇺', 'China': '🇨🇳', 'Japan': '🇯🇵', 'South Korea': '🇰🇷',
    'Singapore': '🇸🇬', 'Malaysia': '🇲🇾', 'UAE': '🇦🇪', 'Saudi Arabia': '🇸🇦', 'Pakistan': '🇵🇰',
    'Iran': '🇮🇷', 'Myanmar': '🇲🇲', 'Ghana': '🇬🇭', 'Egypt': '🇪🇬', 'Turkey': '🇹🇷',
    'Indonesia': '🇮🇩', 'Philippines': '🇵🇭', 'Vietnam': '🇻🇳', 'Thailand': '🇹🇭', 'Mexico': '🇲🇽',
    'Argentina': '🇦🇷', 'Chile': '🇨🇱', 'Peru': '🇵🇪', 'Colombia': '🇨🇴', 'Venezuela': '🇻🇪',
    'Ukraine': '🇺🇦', 'Poland': '🇵🇱', 'Netherlands': '🇳🇱', 'Belgium': '🇧🇪', 'Sweden': '🇸🇪',
    'Norway': '🇳🇴', 'Denmark': '🇩🇰', 'Finland': '🇫🇮', 'Switzerland': '🇨🇭', 'Austria': '🇦🇹',
    'Portugal': '🇵🇹', 'Greece': '🇬🇷', 'Israel': '🇮🇱', 'South Africa': '🇿🇦', 'Nigeria': '🇳🇬',
    'Kenya': '🇰🇪', 'Morocco': '🇲🇦', 'Algeria': '🇩🇿', 'Iraq': '🇮🇶', 'Lebanon': '🇱🇧',
    'Jordan': '🇯🇴', 'Kuwait': '🇰🇼', 'Qatar': '🇶🇦', 'Oman': '🇴🇲', 'Bahrain': '🇧🇭',
    'Afghanistan': '🇦🇫', 'Bahamas': '🇧🇸', 'Barbados': '🇧🇧', 'Anguilla': '🇦🇮', 'Antigua': '🇦🇬',
    'British Virgin Islands': '🇻🇬', 'US Virgin Islands': '🇻🇮', 'Bermuda': '🇧🇲', 'Grenada': '🇬🇩',
    'Turks and Caicos': '🇹🇨', 'Montserrat': '🇲🇸', 'Northern Mariana': '🇲🇵', 'Guam': '🇬🇺',
    'American Samoa': '🇦🇸', 'Saint Lucia': '🇱🇨', 'Dominica': '🇩🇲', 'Saint Vincent': '🇻🇨',
    'Puerto Rico': '🇵🇷', 'Dominican Republic': '🇩🇴', 'Trinidad': '🇹🇹', 'Saint Kitts': '🇰🇳',
    'Jamaica': '🇯🇲', 'South Sudan': '🇸🇸', 'Libya': '🇱🇾', 'Gambia': '🇬🇲', 'Senegal': '🇸🇳',
    'Mauritania': '🇲🇷', 'Mali': '🇲🇱', 'Guinea': '🇬🇳', 'Ivory Coast': '🇨🇮', 'Burkina Faso': '🇧🇫',
    'Niger': '🇳🇪', 'Togo': '🇹🇬', 'Benin': '🇧🇯', 'Mauritius': '🇲🇺', 'Liberia': '🇱🇷',
    'Sierra Leone': '🇸🇱', 'Chad': '🇹🇩', 'Central Africa': '🇨🇫', 'Cameroon': '🇨🇲',
    'Cape Verde': '🇨🇻', 'Sao Tome': '🇸🇹', 'Equatorial Guinea': '🇬🇶', 'Gabon': '🇬🇦',
    'Congo': '🇨🇬', 'DR Congo': '🇨🇩', 'Angola': '🇦🇴', 'Guinea-Bissau': '🇬🇼', 'British Indian Ocean': '🇮🇴',
    'Seychelles': '🇸🇨', 'Rwanda': '🇷🇼', 'Ethiopia': '🇪🇹', 'Somalia': '🇸🇴', 'Djibouti': '🇩🇯',
    'Tanzania': '🇹🇿', 'Uganda': '🇺🇬', 'Burundi': '🇧🇮', 'Mozambique': '🇲🇿', 'Zambia': '🇿🇲',
    'Madagascar': '🇲🇬', 'Reunion': '🇷🇪', 'Zimbabwe': '🇿🇼', 'Namibia': '🇳🇦', 'Malawi': '🇲🇼',
    'Lesotho': '🇱🇸', 'Botswana': '🇧🇼', 'Eswatini': '🇸🇿', 'Comoros': '🇰🇲', 'Saint Helena': '🇸🇭',
    'Eritrea': '🇪🇷', 'Aruba': '🇦🇼', 'Faroe Islands': '🇫🇴', 'Greenland': '🇬🇱', 'Gibraltar': '🇬🇮',
    'Luxembourg': '🇱🇺', 'Ireland': '🇮🇪', 'Iceland': '🇮🇸', 'Albania': '🇦🇱', 'Malta': '🇲🇹',
    'Bulgaria': '🇧🇬', 'Hungary': '🇭🇺', 'Lithuania': '🇱🇹', 'Latvia': '🇱🇻', 'Estonia': '🇪🇪',
    'Moldova': '🇲🇩', 'Armenia': '🇦🇲', 'Belarus': '🇧🇾', 'Andorra': '🇦🇩', 'Monaco': '🇲🇨',
    'San Marino': '🇸🇲', 'Vatican': '🇻🇦', 'Serbia': '🇷🇸', 'Montenegro': '🇲🇪', 'Kosovo': '🇽🇰',
    'Croatia': '🇭🇷', 'Slovenia': '🇸🇮', 'Bosnia': '🇧🇦', 'North Macedonia': '🇲🇰', 'Romania': '🇷🇴',
    'Czech Republic': '🇨🇿', 'Slovakia': '🇸🇰', 'Liechtenstein': '🇱🇮', 'Falkland Islands': '🇫🇰',
    'Belize': '🇧🇿', 'Guatemala': '🇬🇹', 'El Salvador': '🇸🇻', 'Honduras': '🇭🇳', 'Nicaragua': '🇳🇮',
    'Costa Rica': '🇨🇷', 'Panama': '🇵🇦', 'Saint Pierre': '🇵🇲', 'Haiti': '🇭🇹', 'Cuba': '🇨🇺',
    'Bolivia': '🇧🇴', 'Guyana': '🇬🇾', 'Ecuador': '🇪🇨', 'French Guiana': '🇬🇫', 'Paraguay': '🇵🇾',
    'Martinique': '🇲🇶', 'Suriname': '🇸🇷', 'Uruguay': '🇺🇾', 'Timor-Leste': '🇹🇱', 'Norfolk Island': '🇳🇫',
    'Brunei': '🇧🇳', 'Nauru': '🇳🇷', 'Papua New Guinea': '🇵🇬', 'Tonga': '🇹🇴', 'Solomon Islands': '🇸🇧',
    'Vanuatu': '🇻🇺', 'Fiji': '🇫🇯', 'Palau': '🇵🇼', 'Wallis and Futuna': '🇼🇫', 'Cook Islands': '🇨🇰',
    'Niue': '🇳🇺', 'Samoa': '🇼🇸', 'Kiribati': '🇰🇮', 'New Caledonia': '🇳🇨', 'Tuvalu': '🇹🇻',
    'French Polynesia': '🇵🇫', 'Tokelau': '🇹🇰', 'Micronesia': '🇫🇲', 'Marshall Islands': '🇲🇭',
    'Maldives': '🇲🇻', 'Syria': '🇸🇾', 'Yemen': '🇾🇪', 'Bhutan': '🇧🇹', 'Mongolia': '🇲🇳',
    'Tajikistan': '🇹🇯', 'Turkmenistan': '🇹🇲', 'Azerbaijan': '🇦🇿', 'Georgia': '🇬🇪', 'Kyrgyzstan': '🇰🇬',
    'Uzbekistan': '🇺🇿', 'Unknown': '🌍'
}

# File paths
OTP_HISTORY_FILE = "otp_history.json"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

class MasdarAlkonOTPBot:
    def __init__(self):
        self.base_url = MASDAR_URL
        self.session = None
        self.csrf_token = None
        self.last_login_time = 0
        
    async def start_session(self):
        """সেশন শুরু করুন"""
        self.session = aiohttp.ClientSession(
            headers=HEADERS,
            cookie_jar=aiohttp.CookieJar(unsafe=True)
        )
        
    async def close_session(self):
        """সেশন বন্ধ করুন"""
        if self.session:
            await self.session.close()
    
    async def auto_login(self):
        """অটো লগইন করুন"""
        try:
            LOGGER.info("🔐 Auto লগইন শুরু...")
            
            await self.close_session()
            await self.start_session()
            
            # লগইন পেজ নিন
            async with self.session.get(f'{self.base_url}/ints/login', ssl=False) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # ক্যাপচা সলভ করুন
                captcha_input = soup.find('input', {'name': 'capt'})
                captcha_answer = "5"
                if captcha_input:
                    parent_div = captcha_input.find_parent('div')
                    if parent_div:
                        captcha_text = parent_div.get_text(strip=True)
                        numbers = re.findall(r'\d+', captcha_text)
                        if len(numbers) >= 2:
                            captcha_answer = str(int(numbers[0]) + int(numbers[1]))
                            LOGGER.info(f"🧮 ক্যাপচা: {captcha_text} = {captcha_answer}")
                
                # লগইন করুন
                login_data = {
                    'username': USERNAME,
                    'password': PASSWORD,
                    'capt': captcha_answer
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': f'{self.base_url}/ints/login',
                    'Origin': self.base_url
                }
                
                async with self.session.post(
                    f'{self.base_url}/ints/signin',
                    data=login_data,
                    headers=headers,
                    allow_redirects=True,
                    ssl=False
                ) as response:
                    
                    final_url = str(response.url)
                    if "login" not in final_url.lower():
                        LOGGER.info("🎉 লগইন সফল!")
                        self.last_login_time = time.time()
                        return True
                    else:
                        LOGGER.error("❌ লগইন ব্যর্থ")
                        return False
                        
        except Exception as e:
            LOGGER.error(f"❌ লগইন error: {e}")
            return False
    
    async def get_sms_data_api(self):
        """API থেকে SMS data fetch করুন - AUTO SERVER TIME DETECTION"""
        try:
            timestamp = int(time.time() * 1000)
            
            # AUTO SERVER TIME DETECTION
            # প্রথমে আজকের date দিয়ে try করবে
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # প্রথমে TODAY এর date দিয়ে try করুন
            dates_to_try = [today, yesterday]
            
            for server_date in dates_to_try:
                start_date = f"{server_date}%2000:00:00"
                end_date = f"{server_date}%2023:59:59"
                
                # API URL with current date
                api_url = (
                    f"{self.base_url}/ints/client/res/data_smscdr.php?"
                    f"fdate1={start_date}&fdate2={end_date}&"
                    f"frange=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgnumber=&fgcli=&fg=0&"
                    f"sEcho=1&iColumns=7&sColumns=%2C%2C%2C%2C%2C%2C&"
                    f"iDisplayStart=0&iDisplayLength=100&"
                    f"mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&"
                    f"mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&"
                    f"mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&"
                    f"mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&"
                    f"mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&"
                    f"mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&"
                    f"mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&"
                    f"sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1&_={timestamp}"
                )
                
                LOGGER.info(f"📡 API থেকে DATE ({server_date}) এর SMS data fetch করার চেষ্টা করছি...")
                
                # API headers
                api_headers = {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Infinix X6525B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.207 Mobile Safari/537.36',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9,bn-BD;q=0.8,bn;q=0.7',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f'{self.base_url}/ints/client/SMSCDRStats'
                }
                
                async with self.session.get(api_url, headers=api_headers, ssl=False) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # JSON response check করুন
                        try:
                            data = json.loads(response_text)
                            total_records = int(data.get('iTotalRecords', 0))
                            
                            # যদি data পাওয়া যায় (0 এর বেশি records)
                            if total_records > 0:
                                LOGGER.info(f"✅ Server time detected: {server_date} (Records: {total_records})")
                                
                                if "aaData" in data:
                                    sms_list = []
                                    for item in data["aaData"]:
                                        if isinstance(item, list) and len(item) >= 5 and isinstance(item[0], str):
                                            if item[0].startswith('0,0,0,0'):
                                                continue
                                                
                                            sms_entry = {
                                                'timestamp': item[0],
                                                'range': item[1],
                                                'number': item[2],
                                                'service': item[3],
                                                'message': item[4],
                                                'otp': self.extract_otp(item[4]),
                                                'country': self.extract_country_from_number(item[2]),
                                                'country_emoji': self.get_country_emoji(self.extract_country_from_number(item[2]))
                                            }
                                            if sms_entry['otp']:
                                                sms_list.append(sms_entry)
                                                LOGGER.info(f"✅ OTP পাওয়া গেছে: {sms_entry['number']} - {sms_entry['otp']} - {sms_entry['timestamp']}")
                                
                                LOGGER.info(f"📨 API থেকে {len(sms_list)} টি OTP মেসেজ পাওয়া গেছে")
                                return sms_list
                            else:
                                LOGGER.info(f"⚠️ No records found for date: {server_date}, trying next date...")
                                continue
                                
                        except json.JSONDecodeError:
                            LOGGER.error(f"❌ JSON parse error for date: {server_date}")
                            continue
                        
                    else:
                        LOGGER.error(f"❌ API error {response.status} for date: {server_date}")
                        continue
            
            # যদি কোনো date এ data না পাওয়া যায়
            LOGGER.error("❌ No data found for any date (today/yesterday)")
            return []
                        
        except Exception as e:
            LOGGER.error(f"❌ API fetch error: {e}")
            return []
    
    def extract_otp(self, message):
        """মেসেজ থেকে OTP extract করুন"""
        if not message:
            return None
            
        # Facebook patterns
        facebook_patterns = [
            r'Facebook.*?[#]?\s*(\d{4,6})',
            r'[#]?\s*(\d{4,6})\s+.*Facebook',
            r'FB.*?[#]?\s*(\d{4,6})',
            r'[#]?\s*(\d{4,6})\s+.*FB',
            r'FB-(\d{5}).*Facebook'
        ]
        
        for pattern in facebook_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Bolt patterns
        bolt_patterns = [
            r'Bolt.*?code\s+(\d{4})',
            r'code\s+(\d{4}).*?Bolt',
            r'use code\s+(\d{4})'
        ]
        
        for pattern in bolt_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # WhatsApp Arabic patterns
        whatsapp_patterns = [
            r'واتساب.*?(\d{3}[- ]?\d{3})',
            r'(\d{3}[- ]?\d{3}).*?واتساب',
            r'كود.*?(\d{3}[- ]?\d{3})',
            r'(\d{3}[- ]?\d{3}).*?كود'
        ]
        
        for pattern in whatsapp_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Afrikaans/Dutch patterns (Jou WhatsApp-kode)
        afrikaans_patterns = [
            r'WhatsApp.*?(\d{3}[- ]?\d{3})',
            r'(\d{3}[- ]?\d{3}).*?WhatsApp',
            r'kode.*?(\d{3}[- ]?\d{3})',
            r'(\d{3}[- ]?\d{3}).*?kode'
        ]
        
        for pattern in afrikaans_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Universal patterns
        universal_patterns = [
            r'\b(\d{4,6})\b',
            r'\b(\d{3}[- ]?\d{3})\b',
            r'[#]?\s*(\d{4,6})\s',
            r'\s(\d{4,6})\s'
        ]
        
        for pattern in universal_patterns:
            match = re.search(pattern, message)
            if match:
                otp = match.group(1)
                if otp and re.match(r'^\d+$', otp.replace(' ', '').replace('-', '')):
                    return otp
        
        return None
    
    def extract_country_from_number(self, phone_number):
        """ফোন নাম্বার থেকে country detect করুন - INTELLIGENT AUTO DETECTION"""
        if not phone_number:
            return "Unknown"
        
        try:
            # Remove any non-digit characters
            clean_number = re.sub(r'\D', '', str(phone_number))
            
            # Remove leading zeros if any
            clean_number = clean_number.lstrip('0')
            
            if not clean_number:
                return "Unknown"
            
            LOGGER.info(f"🔍 Checking country for number: {clean_number}")
            
            # EXTENDED Country code mapping - 250+ countries
            EXTENDED_COUNTRY_CODES = {
                # North America
                '1': 'US', '1242': 'BS', '1246': 'BB', '1264': 'AI', '1268': 'AG', '1284': 'VG',
                '1340': 'VI', '1441': 'BM', '1473': 'GD', '1649': 'TC', '1664': 'MS', '1670': 'MP',
                '1671': 'GU', '1684': 'AS', '1758': 'LC', '1767': 'DM', '1784': 'VC', '1787': 'PR',
                '1809': 'DO', '1868': 'TT', '1869': 'KN', '1876': 'JM', 
                
                # Africa
                '20': 'EG', '211': 'SS', '212': 'MA', '213': 'DZ', '216': 'TN', '218': 'LY',
                '220': 'GM', '221': 'SN', '222': 'MR', '223': 'ML', '224': 'GN', '225': 'CI',
                '226': 'BF', '227': 'NE', '228': 'TG', '229': 'BJ', '230': 'MU', '231': 'LR',
                '232': 'SL', '233': 'GH', '234': 'NG', '235': 'TD', '236': 'CF', '237': 'CM',
                '238': 'CV', '239': 'ST', '240': 'GQ', '241': 'GA', '242': 'CG', '243': 'CD',
                '244': 'AO', '245': 'GW', '246': 'IO', '248': 'SC', '249': 'SD', '250': 'RW',
                '251': 'ET', '252': 'SO', '253': 'DJ', '254': 'KE', '255': 'TZ', '256': 'UG',
                '257': 'BI', '258': 'MZ', '260': 'ZM', '261': 'MG', '262': 'RE', '263': 'ZW',
                '264': 'NA', '265': 'MW', '266': 'LS', '267': 'BW', '268': 'SZ', '269': 'KM',
                '27': 'ZA', '290': 'SH', '291': 'ER', '297': 'AW', '298': 'FO', '299': 'GL',
                
                # Europe
                '30': 'GR', '31': 'NL', '32': 'BE', '33': 'FR', '34': 'ES', '350': 'GI',
                '351': 'PT', '352': 'LU', '353': 'IE', '354': 'IS', '355': 'AL', '356': 'MT',
                '357': 'CY', '358': 'FI', '359': 'BG', '36': 'HU', '370': 'LT', '371': 'LV',
                '372': 'EE', '373': 'MD', '374': 'AM', '375': 'BY', '376': 'AD', '377': 'MC',
                '378': 'SM', '379': 'VA', '380': 'UA', '381': 'RS', '382': 'ME', '383': 'XK',
                '385': 'HR', '386': 'SI', '387': 'BA', '389': 'MK', '39': 'IT', '40': 'RO',
                '41': 'CH', '420': 'CZ', '421': 'SK', '423': 'LI', '43': 'AT', '44': 'GB',
                '45': 'DK', '46': 'SE', '47': 'NO', '48': 'PL', '49': 'DE',
                
                # Latin America
                '500': 'FK', '501': 'BZ', '502': 'GT', '503': 'SV', '504': 'HN', '505': 'NI',
                '506': 'CR', '507': 'PA', '508': 'PM', '509': 'HT', '51': 'PE', '52': 'MX',
                '53': 'CU', '54': 'AR', '55': 'BR', '56': 'CL', '57': 'CO', '58': 'VE',
                '590': 'GP', '591': 'BO', '592': 'GY', '593': 'EC', '594': 'GF', '595': 'PY',
                '596': 'MQ', '597': 'SR', '598': 'UY', '599': 'CW',
                
                # Asia
                '60': 'MY', '61': 'AU', '62': 'ID', '63': 'PH', '64': 'NZ', '65': 'SG',
                '66': 'TH', '670': 'TL', '672': 'NF', '673': 'BN', '674': 'NR', '675': 'PG',
                '676': 'TO', '677': 'SB', '678': 'VU', '679': 'FJ', '680': 'PW', '681': 'WF',
                '682': 'CK', '683': 'NU', '685': 'WS', '686': 'KI', '687': 'NC', '688': 'TV',
                '689': 'PF', '690': 'TK', '691': 'FM', '692': 'MH', '7': 'RU', '81': 'JP',
                '82': 'KR', '84': 'VN', '86': 'CN', '90': 'TR', '91': 'IN', '92': 'PK',
                '93': 'AF', '94': 'LK', '95': 'MM', '98': 'IR', '960': 'MV', '961': 'LB',
                '962': 'JO', '963': 'SY', '964': 'IQ', '965': 'KW', '966': 'SA', '967': 'YE',
                '968': 'OM', '970': 'PS', '971': 'AE', '972': 'IL', '973': 'BH', '974': 'QA',
                '975': 'BT', '976': 'MN', '977': 'NP', '992': 'TJ', '993': 'TM', '994': 'AZ',
                '995': 'GE', '996': 'KG', '998': 'UZ'
            }
            
            # EXTENDED Country name mapping
            COUNTRY_NAME_MAP = {
                'US': 'USA', 'GB': 'UK', 'IN': 'India', 'BD': 'Bangladesh', 'CA': 'Canada',
                'AU': 'Australia', 'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'ES': 'Spain',
                'BR': 'Brazil', 'RU': 'Russia', 'CN': 'China', 'JP': 'Japan', 'KR': 'South Korea',
                'SG': 'Singapore', 'MY': 'Malaysia', 'AE': 'UAE', 'SA': 'Saudi Arabia', 'PK': 'Pakistan',
                'IR': 'Iran', 'MM': 'Myanmar', 'GH': 'Ghana', 'EG': 'Egypt', 'TR': 'Turkey',
                'ID': 'Indonesia', 'PH': 'Philippines', 'VN': 'Vietnam', 'TH': 'Thailand', 'MX': 'Mexico',
                'AR': 'Argentina', 'CL': 'Chile', 'PE': 'Peru', 'CO': 'Colombia', 'VE': 'Venezuela',
                'UA': 'Ukraine', 'PL': 'Poland', 'NL': 'Netherlands', 'BE': 'Belgium', 'SE': 'Sweden',
                'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland', 'CH': 'Switzerland', 'AT': 'Austria',
                'PT': 'Portugal', 'GR': 'Greece', 'IL': 'Israel', 'ZA': 'South Africa', 'NG': 'Nigeria',
                'KE': 'Kenya', 'MA': 'Morocco', 'DZ': 'Algeria', 'IQ': 'Iraq', 'LB': 'Lebanon',
                'JO': 'Jordan', 'KW': 'Kuwait', 'QA': 'Qatar', 'OM': 'Oman', 'BH': 'Bahrain',
                'AF': 'Afghanistan', 'BS': 'Bahamas', 'BB': 'Barbados', 'AI': 'Anguilla', 'AG': 'Antigua',
                'VG': 'British Virgin Islands', 'VI': 'US Virgin Islands', 'BM': 'Bermuda', 'GD': 'Grenada',
                'TC': 'Turks and Caicos', 'MS': 'Montserrat', 'MP': 'Northern Mariana', 'GU': 'Guam',
                'AS': 'American Samoa', 'LC': 'Saint Lucia', 'DM': 'Dominica', 'VC': 'Saint Vincent',
                'PR': 'Puerto Rico', 'DO': 'Dominican Republic', 'TT': 'Trinidad', 'KN': 'Saint Kitts',
                'JM': 'Jamaica', 'SS': 'South Sudan', 'LY': 'Libya', 'GM': 'Gambia', 'SN': 'Senegal',
                'MR': 'Mauritania', 'ML': 'Mali', 'GN': 'Guinea', 'CI': 'Ivory Coast', 'BF': 'Burkina Faso',
                'NE': 'Niger', 'TG': 'Togo', 'BJ': 'Benin', 'MU': 'Mauritius', 'LR': 'Liberia',
                'SL': 'Sierra Leone', 'TD': 'Chad', 'CF': 'Central Africa', 'CM': 'Cameroon',
                'CV': 'Cape Verde', 'ST': 'Sao Tome', 'GQ': 'Equatorial Guinea', 'GA': 'Gabon',
                'CG': 'Congo', 'CD': 'DR Congo', 'AO': 'Angola', 'GW': 'Guinea-Bissau', 'IO': 'British Indian Ocean',
                'SC': 'Seychelles', 'RW': 'Rwanda', 'ET': 'Ethiopia', 'SO': 'Somalia', 'DJ': 'Djibouti',
                'TZ': 'Tanzania', 'UG': 'Uganda', 'BI': 'Burundi', 'MZ': 'Mozambique', 'ZM': 'Zambia',
                'MG': 'Madagascar', 'RE': 'Reunion', 'ZW': 'Zimbabwe', 'NA': 'Namibia', 'MW': 'Malawi',
                'LS': 'Lesotho', 'BW': 'Botswana', 'SZ': 'Eswatini', 'KM': 'Comoros', 'SH': 'Saint Helena',
                'ER': 'Eritrea', 'AW': 'Aruba', 'FO': 'Faroe Islands', 'GL': 'Greenland', 'GI': 'Gibraltar',
                'LU': 'Luxembourg', 'IE': 'Ireland', 'IS': 'Iceland', 'AL': 'Albania', 'MT': 'Malta',
                'BG': 'Bulgaria', 'HU': 'Hungary', 'LT': 'Lithuania', 'LV': 'Latvia', 'EE': 'Estonia',
                'MD': 'Moldova', 'AM': 'Armenia', 'BY': 'Belarus', 'AD': 'Andorra', 'MC': 'Monaco',
                'SM': 'San Marino', 'VA': 'Vatican', 'RS': 'Serbia', 'ME': 'Montenegro', 'XK': 'Kosovo',
                'HR': 'Croatia', 'SI': 'Slovenia', 'BA': 'Bosnia', 'MK': 'North Macedonia', 'RO': 'Romania',
                'CZ': 'Czech Republic', 'SK': 'Slovakia', 'LI': 'Liechtenstein', 'FK': 'Falkland Islands',
                'BZ': 'Belize', 'GT': 'Guatemala', 'SV': 'El Salvador', 'HN': 'Honduras', 'NI': 'Nicaragua',
                'CR': 'Costa Rica', 'PA': 'Panama', 'PM': 'Saint Pierre', 'HT': 'Haiti', 'CU': 'Cuba',
                'BO': 'Bolivia', 'GY': 'Guyana', 'EC': 'Ecuador', 'GF': 'French Guiana', 'PY': 'Paraguay',
                'MQ': 'Martinique', 'SR': 'Suriname', 'UY': 'Uruguay', 'TL': 'Timor-Leste', 'NF': 'Norfolk Island',
                'BN': 'Brunei', 'NR': 'Nauru', 'PG': 'Papua New Guinea', 'TO': 'Tonga', 'SB': 'Solomon Islands',
                'VU': 'Vanuatu', 'FJ': 'Fiji', 'PW': 'Palau', 'WF': 'Wallis and Futuna', 'CK': 'Cook Islands',
                'NU': 'Niue', 'WS': 'Samoa', 'KI': 'Kiribati', 'NC': 'New Caledonia', 'TV': 'Tuvalu',
                'PF': 'French Polynesia', 'TK': 'Tokelau', 'FM': 'Micronesia', 'MH': 'Marshall Islands',
                'MV': 'Maldives', 'SY': 'Syria', 'YE': 'Yemen', 'BT': 'Bhutan', 'MN': 'Mongolia',
                'TJ': 'Tajikistan', 'TM': 'Turkmenistan', 'AZ': 'Azerbaijan', 'GE': 'Georgia', 'KG': 'Kyrgyzstan',
                'UZ': 'Uzbekistan'
            }
            
            # Check country codes from longest to shortest (4 digits to 1 digit)
            for code_length in range(4, 0, -1):
                if len(clean_number) >= code_length:
                    country_code = clean_number[:code_length]
                    if country_code in EXTENDED_COUNTRY_CODES:
                        country_iso = EXTENDED_COUNTRY_CODES[country_code]
                        country_name = COUNTRY_NAME_MAP.get(country_iso, "Unknown")
                        
                        LOGGER.info(f"✅ Country detected: {country_name} ({country_iso}) for code: {country_code}")
                        return country_name
            
            # If no country code found in extended list
            LOGGER.warning(f"⚠️ Unknown country code for number: {clean_number}")
            return "Unknown"
            
        except Exception as e:
            LOGGER.error(f"❌ Error extracting country from number {phone_number}: {e}")
            return "Unknown"
    
    def get_country_emoji(self, country_name):
        """Country name থেকে flag emoji দিন"""
        return COUNTRY_FLAGS.get(country_name, "🌍")
    
    def extract_service(self, message, range_name):
        """Service type detect করুন"""
        # First check message content
        for service, pattern in SERVICE_PATTERNS.items():
            if re.search(pattern, message, re.IGNORECASE):
                return service
                
        # Then check range name
        if 'facebook' in range_name.lower() or 'fb' in range_name.lower():
            return 'Facebook'
        elif 'whatsapp' in range_name.lower() or 'واتساب' in message.lower() or 'WhatsApp' in message:
            return 'WhatsApp'
        elif 'telegram' in range_name.lower():
            return 'Telegram'
        elif 'bolt' in message.lower():
            return 'Bolt'
        elif 'google' in message.lower():
            return 'Google'
        elif 'instagram' in message.lower():
            return 'Instagram'
        elif 'twitter' in message.lower():
            return 'Twitter'
        elif 'amazon' in message.lower():
            return 'Amazon'
        elif 'microsoft' in message.lower() or 'outlook' in message.lower() or 'hotmail' in message.lower():
            return 'Microsoft'
        elif 'apple' in message.lower() or 'icloud' in message.lower():
            return 'Apple'
        elif 'paypal' in message.lower():
            return 'PayPal'
        elif 'bank' in message.lower() or 'visa' in message.lower() or 'mastercard' in message.lower():
            return 'Banking'
            
        return "Other"

async def load_otp_history():
    """OTP history load করুন"""
    try:
        with open(OTP_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

async def save_otp_history(history):
    """OTP history save করুন"""
    try:
        with open(OTP_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        LOGGER.error(f"❌ History save error: {e}")

async def check_and_save_otp(sms_data):
    """নতুন OTP check করুন এবং save করুন"""
    history = await load_otp_history()
    current_time = datetime.now().isoformat()
    
    otp_id = f"{sms_data['number']}_{sms_data['otp']}_{sms_data['timestamp']}"
    
    if otp_id not in history:
        history[otp_id] = {
            "otp": sms_data['otp'],
            "number": sms_data['number'],
            "service": sms_data['service'],
            "range": sms_data['range'],
            "country": sms_data['country'],
            "message": sms_data['message'],
            "timestamp": sms_data['timestamp'],
            "bot_received_time": current_time
        }
        
        await save_otp_history(history)
        return True
    
    return False

def send_telegram_message(message, reply_markup=None):
    """Telegram এ message send করুন (optional inline buttons সহ)"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }

        if reply_markup:
            payload['reply_markup'] = reply_markup

        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            LOGGER.info("✅ Telegram message sent successfully")
            result = response.json()
            return result.get('result', {}).get('message_id')
        else:
            LOGGER.error(f"❌ Telegram API error: {response.status_code} — {response.text[:200]}")
            return None
        
    except Exception as e:
        LOGGER.error(f"❌ Telegram send error: {e}")
        return None


def delete_telegram_message(message_id):
    """Telegram থেকে message delete করুন"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
        payload = {'chat_id': CHAT_ID, 'message_id': message_id}
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            LOGGER.info(f"🗑️ Message {message_id} deleted")
        else:
            LOGGER.warning(f"⚠️ Delete failed: {response.status_code}")
    except Exception as e:
        LOGGER.error(f"❌ Delete error: {e}")


async def auto_delete_after_delay(message_id, delay_seconds=900):
    """১৫ মিনিট পর message delete করুন"""
    await asyncio.sleep(delay_seconds)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, delete_telegram_message, message_id)


def make_otp_buttons():
    """OTP মেসেজের নিচে ৩টা inline button — OTP বটের মতো সাজানো"""
    return {
        "inline_keyboard": [
            [
                {"text": "📱 Number Channel", "url": NUMBER_CHANNEL_URL}
            ],
            [
                {"text": "🤖 Number bot",    "url": NUMBER_BOT_URL},
                {"text": "📢 main Channel",  "url": MAIN_CHANNEL_URL}
            ]
        ]
    }


async def notify_number_bot(phone_number: str, otp_code: str, service: str):
    """Number Bot কে HTTP POST দিয়ে OTP notify করুন"""
    import urllib.request as _req

    clean_number  = re.sub(r"\D", "", str(phone_number))
    clean_otp     = re.sub(r"[\s\-]", "", str(otp_code))
    clean_service = str(service).lower().split()[0] if service else "other"

    payload = {
        "number":  clean_number,
        "otp":     clean_otp,
        "service": clean_service
    }

    def _post():
        data = json.dumps(payload).encode("utf-8")
        req  = _req.Request(
            NUMBER_BOT_HTTP_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with _req.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, _post)
        LOGGER.info(f"✅ Number Bot notified → number={clean_number} otp={clean_otp} result={result}")
    except Exception as e:
        LOGGER.warning(f"⚠️ Number Bot HTTP notify failed (non-critical): {e}")

# ═══════════════════════════════════════════════════════════════
# ✅ CHANGED: mask_phone — স্ক্রিনশটের মতো 5 digit + *** + 4 digit
# ═══════════════════════════════════════════════════════════════
def mask_phone(number: str) -> str:
    """
    স্ক্রিনশটের মতো মাস্কিং: প্রথম ৫ সংখ্যা + *** + শেষ ৪ সংখ্যা।
    যেমন: 96478***9825
    """
    try:
        if not number:
            return ""
        s = str(number)
        digits = re.findall(r'\d', s)
        total = len(digits)
        if total == 0:
            return s

        masked_digits = []
        for i in range(total):
            if i < 5 or i >= total - 4:
                masked_digits.append(digits[i])
            else:
                masked_digits.append('*')

        result_chars = []
        digit_idx = 0
        for ch in s:
            if ch.isdigit():
                result_chars.append(masked_digits[digit_idx])
                digit_idx += 1
            else:
                result_chars.append(ch)
        return ''.join(result_chars)
    except Exception as e:
        LOGGER.error(f"❌ Error in mask_phone: {e}")
        return re.sub(r'\d', '*', str(number))


# ═══════════════════════════════════════════════════════════════
# ✅ CHANGED: format_otp_message — স্ক্রিনশটের মতো ফরম্যাট
# ═══════════════════════════════════════════════════════════════
def format_otp_message(sms_data):
    """OTP message formatting করুন"""
    country       = sms_data['country']
    country_emoji = sms_data.get('country_emoji', '🌍')
    service       = sms_data['service']
    otp_code      = sms_data['otp']
    number        = sms_data['number']
    full_message  = sms_data['message']

    masked_number = mask_phone(number)

    # Service Unknown হলে message থেকে প্রথম শব্দ দেখাও
    if not service or service == 'Other' or service == 'OTP':
        # message এর প্রথম [] bracket এর ভেতর থেকে service নাও
        bracket = re.search(r'\[([^\]]+)\]', full_message)
        if bracket:
            service = bracket.group(1)
        else:
            service = 'Unknown'

    message = (
        "🔥 <b>FIRST OTP RECEIVED</b> 🔥\n\n"
        f"📱 <b>Number:</b> <code>{masked_number}</code>\n"
        f"🏢 <b>Operator:</b> <code>{country_emoji} {country}</code>\n"
        f"📟 <b>Platform:</b> <code>{service}</code>\n\n"
        f"🟢 <b>OTP Code:</b> <code>{otp_code}</code>\n\n"
        f"📝 <b>Message:</b>\n<code>{full_message}</code>"
    )

    return message


def send_start_alert():
    """Bot start alert send করুন"""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")
        date = datetime.now().strftime("%d-%m-%Y")
        
        message = (
            "<b>🤖 OTP Bot Started Successfully ✅</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>⏰ Time:</b> <code>{timestamp}</code>\n"
            f"<b>📅 Date:</b> <code>{date}</code>\n"
            f"<b>🤵 Owner:</b> <code>{OWNER_ID}</code>\n"
            f"<b>💰 Traffic:</b> Running.....📡\n"
            f"<b>📩 OTP Scrapper:</b> Running...🔍\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Don't Spam Here Just Wait For OTP ❌</b>"
        )
        
        success = send_telegram_message(message)
        if success:
            LOGGER.info("✅ Start alert sent successfully")
        else:
            LOGGER.error("❌ Failed to send start alert")
                
    except Exception as e:
        LOGGER.error(f"❌ Error sending start alert: {e}")

async def monitor_otp_loop():
    """Main OTP monitoring loop"""
    bot = MasdarAlkonOTPBot()
    
    # Start alert send করুন
    send_start_alert()
    
    try:
        # প্রথমে লগইন করুন
        LOGGER.info("🚀 Bot starting...")
        success = await bot.auto_login()
        
        if not success:
            LOGGER.error("❌ Initial login failed")
            return
        
        LOGGER.info("✅ Login successful, starting OTP monitoring...")

        # ── পুরনো history load করো — restart এ পুরনো OTP আবার না পাঠাতে ──
        history = await load_otp_history()
        previous_otps = set(history.keys())
        LOGGER.info(f"📂 History loaded: {len(previous_otps)} OTPs already tracked")

        while True:
            try:
                # Session check করুন
                current_time = time.time()
                if current_time - bot.last_login_time > 600:
                    LOGGER.info("🔄 Session refresh needed...")
                    if not await bot.auto_login():
                        LOGGER.error("❌ Re-login failed")
                        await asyncio.sleep(30)
                        continue
                
                # API থেকে SMS data fetch করুন
                sms_result = await bot.get_sms_data_api()
                
                # নতুন OTP process করুন
                for sms in sms_result:
                    otp_id = f"{sms['number']}_{sms['otp']}_{sms['timestamp']}"
                    
                    if otp_id not in previous_otps:
                        LOGGER.info(f"🎯 নতুন OTP পাওয়া গেছে: {sms['number']} - {sms['otp']} - {sms['timestamp']}")
                        
                        # Service detect করুন
                        sms['service'] = bot.extract_service(sms['message'], sms['range'])
                        
                        # History তে save করুন
                        is_new = await check_and_save_otp(sms)
                        
                        if is_new:
                            # Telegram এ send করুন (৩টা বাটন সহ)
                            formatted_message = format_otp_message(sms)
                            message_id = send_telegram_message(
                                formatted_message,
                                reply_markup=make_otp_buttons()
                            )
                            
                            if message_id:
                                LOGGER.info(f"✅ OTP sent to Telegram: {sms['number']} - {sms['otp']}")
                                # ── ১৫ মিনিট পর auto delete ──
                                asyncio.create_task(auto_delete_after_delay(message_id, 900))
                                # ── Number Bot কে localhost HTTP দিয়ে notify করুন ──
                                await notify_number_bot(
                                    sms['number'],
                                    sms['otp'],
                                    sms['service']
                                )
                            else:
                                LOGGER.error(f"❌ Failed to send OTP for {sms['number']}")
                        
                        previous_otps.add(otp_id)
                
                # Clean up old OTPs
                current_time_str = datetime.now().isoformat()
                twenty_four_hours_ago = (datetime.now() - timedelta(hours=24)).isoformat()
                
                previous_otps = {otp_id for otp_id in previous_otps 
                               if otp_id.split('_')[-1] > twenty_four_hours_ago}
                
                LOGGER.info(f"⏳ 10 সেকেন্ড অপেক্ষা... (Tracked: {len(previous_otps)} OTPs)")
                await asyncio.sleep(5)
                
            except Exception as e:
                LOGGER.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(30)
                
    except KeyboardInterrupt:
        LOGGER.info("⏹️ Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Main loop error: {e}")
    finally:
        await bot.close_session()
        LOGGER.info("🔚 Bot stopped")

async def main():
    """Main function"""
    print("🤖Telegram OTP Bot - ALL LANGUAGES SUPPORT\n")
    print("="*50)
    print("🔐 Auto Login & OTP Forwarding to Telegram")
    print("="*50)
    
    await monitor_otp_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
