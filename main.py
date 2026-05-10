import time
import json
import re
import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ==========================================
#               CONFIGURATION
# ==========================================
BASE_URL   = "https://www.imssms.org"
LOGIN_PAGE = f"{BASE_URL}/login"
SIGNIN_URL = f"{BASE_URL}/signin"
STATS_PAGE = f"{BASE_URL}/agent/SMSCDRReports"
API_URL    = f"{BASE_URL}/agent/res/data_smscdr.php"

USERNAME   = "masud5798"
PASSWORD   = "aass1122"

# Telegram Details
BOT_TOKEN         = "8513071962:AAEuk7UOeKn1eV8rzCuB9B7giHbkAIudNGM"
PRIVATE_CHAT      = "-1003247504066" 
PUBLIC_CHAT       = "1003247504066" 
BOT_LINK          = "https://t.me/@EARNING_HUB_NUMBER_BOT"          
MAIN_CHANNEL_LINK = "https://t.me/earning_hub_official_channel" 

CHECK_INTERVAL = 60
SENT_IDS_FILE  = "sent_ids_final_v6.json" # ржирждрзБржи ржлрж╛ржЗрж▓ ржпрж╛рждрзЗ ржкрзБрж░рж╛ржирзЛ ржорзЗрж╕рзЗржЬржЧрзБрж▓рзЛржУ ржЖрж╕рзЗ

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

# Country Flag Map (Updated with Burkina Faso)
COUNTRY_FLAGS = {
    "BURKINA FASO": "ЁЯЗзЁЯЗл", "PAKISTAN": "ЁЯЗ╡ЁЯЗ░", "INDIA": "ЁЯЗоЁЯЗ│", "BANGLADESH": "ЁЯЗзЁЯЗй", 
    "USA": "ЁЯЗ║ЁЯЗ╕", "UK": "ЁЯЗмЁЯЗз", "NIGERIA": "ЁЯЗ│ЁЯЗм", "GHANA": "ЁЯЗмЁЯЗн", "KENYA": "ЁЯЗ░ЁЯЗк",
    "BRAZIL": "ЁЯЗзЁЯЗ╖", "INDONESIA": "ЁЯЗоЁЯЗй", "VIETNAM": "ЁЯЗ╗ЁЯЗ│", "SUDAN": "ЁЯЗ╕ЁЯЗй",
    "SENEGAL": "ЁЯЗ╕ЁЯЗ│", "EAST TIMOR": "ЁЯЗ╣ЁЯЗ▒"
}

# ==========================================
#             HELPER FUNCTIONS
# ==========================================

def get_country_and_flag(range_str):
    if not range_str or not isinstance(range_str, str): return "Unknown", "ЁЯМР"
    rs_upper = range_str.upper()
    
    for country, flag in COUNTRY_FLAGS.items():
        if country in rs_upper:
            return country.title(), flag
            
    return range_str.split(' ')[0].title(), "ЁЯМР"

def mask_number(number):
    n = str(number)
    return f"{n[:4]}XXXX{n[-3:]}" if len(n) > 7 else n

def extract_otp(message):
    msg_str = str(message)
    wa_match = re.search(r'(?<!\d)(\d{3})\s*[-тАФтАУ\.]\s*(\d{3})(?!\d)', msg_str)
    if wa_match: return wa_match.group(1) + wa_match.group(2)
    matches = re.findall(r'(?<!\d)(\d{4,8})(?!\d)', msg_str)
    return matches[-1] if matches else None

def load_sent():
    if os.path.exists(SENT_IDS_FILE):
        try:
            with open(SENT_IDS_FILE) as f: return set(json.load(f))
        except: return set()
    return set()

def tg_send(chat_id, text, otp_val=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    kb =[]
    if otp_val:
        kb.append([{"text": f"Copy OTP: {otp_val}", "copy_text": {"text": str(otp_val)}}])
    kb.append([{"text": "Main Channel тЖЧ", "url": MAIN_CHANNEL_LINK}, {"text": "Number Bot тЖЧ", "url": BOT_LINK}])
    
    payload = {
        "chat_id": chat_id, 
        "text": text, 
        "parse_mode": "HTML", 
        "reply_markup": {"inline_keyboard": kb},
        "disable_web_page_preview": True
    }
    try: requests.post(url, json=payload, timeout=15)
    except: pass

# ==========================================
#             CORE PROCESS
# ==========================================

def do_login(session):
    print(f"[LOGIN] Solving captcha and logging in...")
    try:
        r = session.get(LOGIN_PAGE, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        
        etkk_input = soup.find("input", {"name": "etkk"})
        etkk_val = etkk_input.get("value", "") if etkk_input else ""
        
        math_match = re.search(r'(\d+)\s*([\+\-])\s*(\d+)', r.text)
        if not math_match:
            print("[!] Captcha not found!")
            return False, None
        
        a, op, b = int(math_match.group(1)), math_match.group(2), int(math_match.group(3))
        ans = str(a + b) if op == '+' else str(a - b)
        print(f"[CAPTCHA] {a} {op} {b} = {ans}")
        
        payload = {
            'etkk': etkk_val,
            'username': USERNAME,
            'password': PASSWORD,
            'capt': ans
        }
        
        login_headers = HEADERS.copy()
        login_headers.update({"Referer": LOGIN_PAGE, "Content-Type": "application/x-www-form-urlencoded"})
        
        time.sleep(2)
        session.post(SIGNIN_URL, data=payload, headers=login_headers, timeout=20)
        
        # рж╕рзЗрж╢ржи ржЯрзЛржХрзЗржи ржирзЗржУрзЯрж╛рж░ ржЬржирзНржп рж╕ржарж┐ржХ ржкрзЗржЬ (SMSCDRReports) ржнрж┐ржЬрж┐ржЯ ржХрж░рж╛
        time.sleep(2)
        cdr_page = session.get(STATS_PAGE, headers=HEADERS, timeout=20)
        
        skey_match = re.search(r'sesskey=([A-Za-z0-9%]+)', cdr_page.text)
        sesskey = skey_match.group(1) if skey_match else ""
        
        if USERNAME in cdr_page.text or "CDR" in cdr_page.text:
            print("[LOGIN] SUCCESS! Bot is online.")
            return True, sesskey
        
        print("[LOGIN] Failed. Credentials might be wrong.")
        return False, None
        
    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return False, None

def fetch_data(session, sesskey):
    today = datetime.now().strftime('%Y-%m-%d')
    # ржЖржкржирж╛рж░ ржлрзНрж░рзЗржирзНржбрзЗрж░ cURL ржерзЗржХрзЗ ржкрж╛ржУрзЯрж╛ рж╕ржорзНржкрзВрж░рзНржг DataTables ржкрзНржпрж╛рж░рж╛ржорж┐ржЯрж╛рж░
    params = {
        "fdate1": f"{today} 00:00:00",
        "fdate2": f"{today} 23:59:59",
        "frange": "", "fclient": "", "fnum": "", "fcli": "",
        "fgdate": "", "fgmonth": "", "fgrange": "", "fgclient": "",
        "fgnumber": "", "fgcli": "", "fg": "0", 
        "sEcho": "1", "iColumns": "9", "sColumns": ",,,,,,,,", 
        "iDisplayStart": "0", "iDisplayLength": "50",
        "mDataProp_0": "0", "bRegex_0": "false", "bSearchable_0": "true", "bSortable_0": "true",
        "mDataProp_1": "1", "bRegex_1": "false", "bSearchable_1": "true", "bSortable_1": "true",
        "mDataProp_2": "2", "bRegex_2": "false", "bSearchable_2": "true", "bSortable_2": "true",
        "mDataProp_3": "3", "bRegex_3": "false", "bSearchable_3": "true", "bSortable_3": "true",
        "mDataProp_4": "4", "bRegex_4": "false", "bSearchable_4": "true", "bSortable_4": "true",
        "mDataProp_5": "5", "bRegex_5": "false", "bSearchable_5": "true", "bSortable_5": "true",
        "mDataProp_6": "6", "bRegex_6": "false", "bSearchable_6": "true", "bSortable_6": "true",
        "mDataProp_7": "7", "bRegex_7": "false", "bSearchable_7": "true", "bSortable_7": "true",
        "mDataProp_8": "8", "bRegex_8": "false", "bSearchable_8": "true", "bSortable_8": "false",
        "sSearch": "", "bRegex": "false",
        "iSortCol_0": "0", "sSortDir_0": "desc", "iSortingCols": "1",
        "_": int(time.time() * 1000)
    }
    
    if sesskey: params["sesskey"] = sesskey

    try:
        r = session.get(API_URL, params=params, headers=HEADERS, timeout=25)
        if "login" in r.url or r.status_code != 200: return None
        return r.json().get("aaData",[])
    except: return None

def main():
    print("=" * 45)
    print(" IMS SMS PERFECT BOT RUNNING ")
    print("=" * 45)
    
    sent_ids = load_sent()
    session = requests.Session()
    logged_in = False
    sess_key = ""

    while True:
        try:
            if not logged_in:
                logged_in, sess_key = do_login(session)
                if not logged_in:
                    print("[!] Login failed. Waiting 30s...")
                    time.sleep(30); continue
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking Data...")
            rows = fetch_data(session, sess_key)
            
            if rows is None:
                print("[!] Session Expired. Re-logging...")
                logged_in = False; continue
                
            print(f"[*] Received {len(rows)} records from server. Filtering new ones...")
            
            count = 0
            if isinstance(rows, list):
                for item in reversed(rows):
                    if not isinstance(item, list) or len(item) < 6: continue
                    
                    uid = f"{item[0]}_{item[2]}_{str(item[5])[:15]}"
                    if uid in sent_ids: continue
                    
                    otp = extract_otp(item[5])
                    if not otp:
                        sent_ids.add(uid); continue
                    
                    country, flag = get_country_and_flag(item[1])
                    num, cli, sms = str(item[2]), str(item[3]), str(item[5])

                    # рзз. ржкрж╛ржмрж▓рж┐ржХ ржЪрзНржпрж╛ржирзЗрж▓ (ржмржбрж┐ ржпрж╛ржмрзЗ ржирж╛)
                    pub_format = f"#{country} #{cli}  [{mask_number(num)}] {flag}"
                    tg_send(PUBLIC_CHAT, pub_format, otp)

                    # рзи. ржкрзНрж░рж╛ржЗржнрзЗржЯ ржЧрзНрж░рзБржк (ржлрзБрж▓ ржбрж┐ржЯрзЗржЗрж▓рж╕)
                    priv_format = f"#{country} #{cli}  <code>{num}</code> {flag}\n\n{sms}"
                    tg_send(PRIVATE_CHAT, priv_format, otp)

                    sent_ids.add(uid)
                    count += 1
            
            if count > 0:
                with open(SENT_IDS_FILE, "w") as f: json.dump(list(sent_ids), f)
                print(f"[*] Successfully sent {count} new messages to Telegram.")
            else:
                print("[*] No new data to send (already sent or no OTP).")
            
            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(20)

if __name__ == "__main__":
    main()()