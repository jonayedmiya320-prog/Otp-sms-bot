async def main():
    TELEGRAM_BOT_TOKEN = "8672122739:AAGXzye3H-78dPMswDLCzMLkkoimcDCqihY"
    GROUP_CHAT_ID = "-1003247504066"
    SESSION_COOKIE = "kfe450mhnclli7rfmu4327i6k2"
    TARGET_HOST = "91.232.105.47"
    CSSTR_PARAM = "3acc348a709215e69664db0772be8876"
    TIMESTAMP_PARAM = "1777215360230"
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