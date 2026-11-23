<?php
require_once 'security.php';

// Safe & Self-Contained Maintenance Check
if (is_maintenance()) {
    header("HTTP/1.1 503 Service Unavailable");
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
      <title>MINO SMS - FAST OTP PROVIDER</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-slate-950 text-slate-100 flex items-center justify-center min-h-screen p-4 select-none font-sans overflow-hidden">
      <div class="max-w-md w-full bg-slate-900/90 border border-slate-800 p-8 rounded-3xl shadow-2xl text-center space-y-6 relative backdrop-blur-xl">
        <div class="absolute inset-x-0 -top-12 flex justify-center">
          <div class="bg-rose-500/10 border border-rose-500/30 text-rose-500 h-24 w-24 rounded-full flex items-center justify-center text-4xl shadow-lg backdrop-blur-md">
            <i class="fa-solid fa-triangle-exclamation animate-pulse"></i>
          </div>
        </div>
        
        <div class="pt-8 space-y-2">
          <span class="px-3 py-1 bg-rose-600 text-white font-black text-xs rounded-full uppercase tracking-widest shadow-sm">SYSTEM LOCKED</span>
          <h1 class="text-2xl font-black tracking-tight text-white uppercase mt-3">OFFICIAL MAINTENANCE</h1>
          <p class="text-xs text-slate-400 font-semibold leading-relaxed">
            Mino SMS is undergoing planned system maintenance for security and network upgrades.
          </p>
        </div>

        <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-2xl text-left space-y-2.5">
          <div class="flex items-center gap-2.5 text-xs font-bold text-slate-300">
            <i class="fa-solid fa-circle-check text-rose-500"></i> No Balance Loss
          </div>
          <div class="flex items-center gap-2.5 text-xs font-bold text-slate-300">
            <i class="fa-solid fa-circle-check text-rose-500"></i> Real-time Database Backup Secure
          </div>
        </div>

        <div class="space-y-3">
          <a href="https://t.me/MINOSMSOFFICIALS" target="_blank" class="w-full bg-[#0088CC] hover:bg-[#0077B5] text-white font-black py-4 rounded-2xl shadow-md transition-all duration-300 flex items-center justify-center gap-2.5 text-sm">
            <i class="fa-brands fa-telegram text-lg"></i> JOIN TELEGRAM CHANNEL
          </a>
        </div>
      </div>
    </body>
    </html>
    <?php
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>MINO SMS - FAST OTP PROVIDER</title>

  <!-- PWA & Mobile Web App Settings -->
  <meta name="theme-color" content="#080b14">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="MINO SMS">
  <meta name="application-name" content="MINO SMS">

  <!-- SVG Favicon and Apple Touch Icon -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='25' fill='%230f172a'/><path d='M15 52 L85 15 L55 85 L42 56 Z' fill='%233b82f6'/><path d='M42 56 L85 15 L55 85 Z' fill='%231d4ed8'/><path d='M25 42 L42 22 M30 52 L48 32' stroke='%23f97316' stroke-width='4' stroke-linecap='round'/></svg>">
  <link rel="apple-touch-icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='25' fill='%230f172a'/><path d='M15 52 L85 15 L55 85 L42 56 Z' fill='%233b82f6'/><path d='M42 56 L85 15 L55 85 Z' fill='%231d4ed8'/><path d='M25 42 L42 22 M30 52 L48 32' stroke='%23f97316' stroke-width='4' stroke-linecap='round'/></svg>">
  <link rel="shortcut icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='25' fill='%230f172a'/><path d='M15 52 L85 15 L55 85 L42 56 Z' fill='%233b82f6'/><path d='M42 56 L85 15 L55 85 Z' fill='%231d4ed8'/><path d='M25 42 L42 22 M30 52 L48 32' stroke='%23f97316' stroke-width='4' stroke-linecap='round'/></svg>">

  <script src="https://cdnjs.cloudflare.com/ajax/libs/vue/3.3.4/vue.global.prod.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://cdn.tailwindcss.com"></script>

  <script>
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.addEventListener('keydown', e => {
      const target = e.target.tagName.toLowerCase();
      const isInput = target === 'input' || target === 'textarea';
      if (e.keyCode === 123) e.preventDefault();
      if (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 67 || e.keyCode === 74)) e.preventDefault();
      if (e.ctrlKey && e.keyCode === 85) e.preventDefault();
      if (e.ctrlKey && e.keyCode === 67 && !isInput) e.preventDefault();
      if (e.ctrlKey && e.keyCode === 65 && !isInput) e.preventDefault();
    });
  </script>
  
  <style>
    [v-cloak] { display: none !important; }
    html, body {
      -webkit-tap-highlight-color: transparent;
      -webkit-touch-callout: none;
    }
    body { 
      background-color: #080b14; 
      background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.18) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.12) 0px, transparent 50%),
        radial-gradient(at 50% 50%, rgba(249, 115, 22, 0.05) 0px, transparent 60%);
      background-attachment: fixed;
    }
    
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(14px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes popIn {
      0% { opacity: 0; transform: scale(0.95); }
      100% { opacity: 1; transform: scale(1); }
    }
    @keyframes pulseGlow {
      0%, 100% { box-shadow: 0 0 15px rgba(16, 185, 129, 0.45); border-color: #10b981; }
      50% { box-shadow: 0 0 25px rgba(16, 185, 129, 0.85); border-color: #059669; }
    }
    @keyframes beaconPulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.3; transform: scale(1.35); }
    }
    @keyframes toastProgress {
      from { width: 100%; }
      to { width: 0%; }
    }
    @keyframes radarPulse {
      0% { opacity: 1; transform: scale(0.8); }
      50% { opacity: 0.5; transform: scale(1.25); }
      100% { opacity: 1; transform: scale(0.8); }
    }

    .page-enter-active { animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .pop-in { animation: popIn 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .otp-hit-glow { animation: pulseGlow 1.2s infinite ease-in-out; }
    .beacon-dot { animation: beaconPulse 1.5s infinite ease-in-out; }
    .radar-pulse { animation: radarPulse 1.8s infinite ease-in-out; }
    .toast-progress-bar { animation: toastProgress 2.8s linear forwards; }
    
    .hover-card {
      transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hover-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 14px 32px -4px rgba(99, 102, 241, 0.28);
    }

    .ios-scroll {
      -webkit-overflow-scrolling: touch;
    }

    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #080b14;
    }
    ::-webkit-scrollbar-thumb {
      background: #1e293b;
      border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #334155;
    }
  </style>
</head>
<body class="text-slate-200 font-sans select-none pb-6 md:pb-0 min-h-screen ios-scroll">

  <div id="app" v-cloak>

    <!-- 🔔 ENHANCED AI NOTIFICATION TOAST -->
    <transition name="toast">
      <div v-if="showToast" class="fixed top-4 right-3 sm:right-6 z-[999999] max-w-sm w-full select-none">
        <div class="relative bg-slate-900/95 backdrop-blur-2xl rounded-2xl p-4 shadow-2xl border border-indigo-500/40 flex items-center justify-between gap-3 overflow-hidden">
          
          <div class="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500 toast-progress-bar"></div>
          <div class="absolute left-0 top-0 bottom-0 w-1.5 bg-emerald-500 rounded-l-xl"></div>

          <div class="flex items-center gap-3.5 pl-1 flex-1 min-w-0">
            <div class="h-9 w-9 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shrink-0">
              <i class="fa-solid fa-circle-check text-emerald-400 text-base font-black"></i>
            </div>
            
            <div class="flex flex-col min-w-0">
              <span class="font-black text-white text-xs sm:text-sm leading-tight truncate">
                {{ toastTitle }}
              </span>
              <span class="text-xs font-bold text-slate-400 mt-0.5 truncate leading-tight">
                {{ toastMessage }}
              </span>
            </div>
          </div>

          <button @click="showToast = false" class="h-7 w-7 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition shrink-0">
            <i class="fa-solid fa-xmark text-xs"></i>
          </button>
        </div>
      </div>
    </transition>

    <!-- POST-LOGIN MANDATORY TELEGRAM USERNAME PROMPT MODAL -->
    <div v-if="showTelegramModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 z-[999999] select-none">
      <div class="bg-slate-900 border border-indigo-500/40 p-6 rounded-3xl shadow-2xl max-w-sm w-full space-y-4 pop-in">
        <div class="text-center space-y-2">
          <div class="h-12 w-12 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mx-auto text-xl">
            <i class="fa-brands fa-telegram"></i>
          </div>
          <h3 class="text-base font-black text-white">Telegram Account Required</h3>
          <p class="text-xs text-slate-400 font-medium leading-relaxed">
            কাজ শুরু করতে আপনার টেলিগ্রাম ইউজারনেম দিন (e.g. @your_username)।
          </p>
        </div>

        <div class="space-y-3">
          <input type="text" v-model="promptTelegramUsername" placeholder="@your_username" class="w-full p-3.5 bg-slate-950 border border-slate-800 rounded-2xl text-xs font-bold font-mono text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
          <button @click="saveTelegramFromModal" :disabled="!promptTelegramUsername.trim()" class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-black py-3.5 rounded-2xl text-xs transition shadow-lg active:scale-95">
            Save & Continue
          </button>
        </div>
      </div>
    </div>

    <!-- 📖 INTERACTIVE "HOW TO USE NUMBER PANEL" GUIDE MODAL -->
    <div v-if="showGuideModal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 z-[999999] select-none">
      <div class="bg-slate-900 border border-slate-800 p-6 rounded-3xl shadow-2xl max-w-2xl w-full space-y-5 max-h-[85vh] overflow-y-auto pop-in ios-scroll">
        
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2.5">
            <div class="h-10 w-10 bg-indigo-600/20 border border-indigo-500/30 rounded-2xl flex items-center justify-center text-indigo-400">
              <i class="fa-solid fa-book-open-reader text-base"></i>
            </div>
            <div>
              <h3 class="text-base font-black text-white">How to Use Number Panel</h3>
              <p class="text-xs text-slate-400 font-medium">নম্বর প্যানেল ব্যবহারের সম্পূর্ণ নির্দেশিকা (v1.2)</p>
            </div>
          </div>

          <!-- Language Switcher -->
          <div class="flex items-center gap-1.5 bg-slate-950 p-1.5 rounded-2xl border border-slate-800">
            <button @click="guideLang = 'bn'" :class="guideLang === 'bn' ? 'bg-indigo-600 text-white font-black' : 'text-slate-400 hover:text-white'" class="px-3.5 py-1.5 rounded-xl text-xs transition">বাংলা</button>
            <button @click="guideLang = 'en'" :class="guideLang === 'en' ? 'bg-indigo-600 text-white font-black' : 'text-slate-400 hover:text-white'" class="px-3.5 py-1.5 rounded-xl text-xs transition">English</button>
            <button @click="showGuideModal = false" class="text-slate-400 hover:text-white p-1.5 ml-2"><i class="fa-solid fa-xmark text-base"></i></button>
          </div>
        </div>

        <!-- Guide Content in Bangla -->
        <div v-if="guideLang === 'bn'" class="space-y-4 text-xs leading-relaxed text-slate-300 font-sans">
          
          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-1 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> ১. রেঞ্জ আইডি (Range ID) নির্বাচন করা
            </h4>
            <p>
              প্রথমে <strong>Live Access</strong> বা <strong>Radar</strong> সেকশন থেকে চলমান সার্ভিসসমূহের একটি সক্রিয় রেঞ্জ কোড (যেমন: <code class="bg-slate-900 px-2 py-0.5 rounded font-mono text-emerald-400">2250789XXX</code>) কপি করুন।
            </p>
          </div>

          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-2 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> ২. নম্বর ইনপুট ও বুকিং (Get Number)
            </h4>
            <p>
              <strong>Get Number</strong> পেজে এসে কপি করা রেঞ্জ আইডিটি পেস্ট করুন এবং <span class="text-white font-bold">"Get Number"</span> বাটনে চাপ দিন। সাথে সাথে ভার্চুয়াল নম্বর বরাদ্দ হয়ে যাবে এবং স্ক্রিনে শো করবে।
            </p>
          </div>

          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-3 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> ৩. ওটিপি (OTP) লাইভ রিসিভ ও কপি
            </h4>
            <p>
              নম্বরটি আপনার অ্যাপে বসানোর পর ওটিপি আসা মাত্রই প্যানেলে সাউন্ড এবং গ্রিন গ্লো সহকারে ওটিপি কোড চলে আসবে। ওটিপির ওপর ক্লিক করলেই তা কপি হয়ে যাবে।
            </p>
          </div>

          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-4 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> ৪. ব্যালেন্স ইনকাম ও উইথড্র
            </h4>
            <p>
              প্রতিটি সফল ওটিপির জন্য আপনার ওয়ালেটে ব্যালেন্স জমা হবে। <strong>Withdraw</strong> অপশন থেকে আপনার বিকাশ, নগদ বা বাইন্যান্স অ্যাকাউন্ট সেভ করে সর্বনিম্ন ১৫০ টাকা (৳150) হলে সহজেই উইথড্র করতে পারবেন।
            </p>
          </div>

        </div>

        <!-- Guide Content in English -->
        <div v-else class="space-y-4 text-xs leading-relaxed text-slate-300 font-sans">
          
          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-1 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> 1. Select Range ID
            </h4>
            <p>
              Copy an active Range ID (e.g. <code class="bg-slate-900 px-2 py-0.5 rounded font-mono text-emerald-400">2250789XXX</code>) from the <strong>Live Access</strong> or <strong>Radar</strong> stream tab.
            </p>
          </div>

          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-2 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> 2. Book Virtual Number
            </h4>
            <p>
              Navigate to <strong>Get Number</strong> tab, paste your Range ID, and click <span class="text-white font-bold">"Get Number"</span> to allocate your virtual phone number.
            </p>
          </div>

          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-3 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> 3. Intercept & Copy OTP
            </h4>
            <p>
              Use the number on your desired target app. As soon as the SMS arrives, the OTP code will display with an audio beep. Click the OTP code to copy it instantly.
            </p>
          </div>

          <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-1.5">
            <h4 class="font-extrabold text-indigo-400 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-4 text-xs bg-indigo-500/20 p-1.5 rounded-lg"></i> 4. Track Earnings & Withdraw
            </h4>
            <p>
              Revenue credits automatically upon every successful OTP. Manage your payout accounts in <strong>Withdraw</strong> tab (Min withdrawal ৳150) to request payouts.
            </p>
          </div>

        </div>

        <button @click="showGuideModal = false" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-black py-4 rounded-2xl text-xs transition active:scale-98">
          Got It! Start Working
        </button>
      </div>
    </div>

    <!-- Auth Screen -->
    <div v-if="!user" class="min-h-screen flex items-center justify-center p-4">
      <div class="bg-slate-900/90 border border-slate-800/80 backdrop-blur-2xl p-6 sm:p-8 rounded-3xl shadow-2xl max-w-md w-full space-y-6 pop-in">
        
        <!-- BRANDING LOGO -->
        <div class="text-center space-y-3">
          <div class="flex items-center justify-center">
            <img src="logo.png" alt="Mino SMS" class="h-14 w-auto object-contain" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
            <div class="hidden items-center justify-center">
              <svg class="h-14 w-auto" viewBox="0 0 280 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 48 L78 12 L50 82 L38 52 Z" fill="#3b82f6"/>
                <path d="M38 52 L78 12 L50 82 Z" fill="#1d4ed8"/>
                <path d="M22 38 L38 20 M26 48 L44 30" stroke="#f97316" stroke-width="4" stroke-linecap="round"/>
                <text x="90" y="58" font-family="Arial, sans-serif" font-weight="900" font-size="38" fill="#ffffff">Mino</text>
                <text x="180" y="58" font-family="Arial, sans-serif" font-weight="900" font-size="38" fill="#f97316">SMS</text>
              </svg>
            </div>
          </div>
          <p class="text-[10px] font-black text-indigo-400 uppercase tracking-widest">{{ isRegistering ? 'Register Account' : 'Sign in to network' }}</p>
        </div>

        <div class="flex bg-slate-950/80 p-1.5 rounded-2xl font-bold border border-slate-800/80">
          <button type="button" @click="isRegistering = false" :class="!isRegistering ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white'" class="flex-1 font-bold py-3 rounded-xl text-xs transition">
            LOG IN
          </button>
          <button type="button" @click="isRegistering = true" :class="isRegistering ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white'" class="flex-1 font-bold py-3 rounded-xl text-xs transition">
            CREATE ACCOUNT
          </button>
        </div>

        <form @submit.prevent="handleAuth" class="space-y-4">
          <div v-if="isRegistering">
            <label class="text-xs font-bold text-slate-400">Your Name</label>
            <input type="text" required v-model="authName" placeholder="Name" class="w-full mt-1.5 p-4 bg-slate-950/80 border border-slate-800 rounded-2xl text-sm font-semibold text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
          </div>
          <div>
            <label class="text-xs font-bold text-slate-400">Email Address</label>
            <input type="email" required v-model="authEmail" placeholder="user@network.com" class="w-full mt-1.5 p-4 bg-slate-950/80 border border-slate-800 rounded-2xl text-sm font-semibold text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
          </div>
          <div>
            <label class="text-xs font-bold text-slate-400">Password</label>
            <input type="password" required v-model="authPassword" placeholder="••••••••" class="w-full mt-1.5 p-4 bg-slate-950/80 border border-slate-800 rounded-2xl text-sm font-semibold text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
          </div>
          
          <!-- TELEGRAM USERNAME FIELD ON REGISTRATION -->
          <div v-if="isRegistering">
            <label class="text-xs font-bold text-slate-400">Telegram Username <span class="text-indigo-400">*</span></label>
            <input type="text" required v-model="authTelegramUsername" placeholder="@your_username" class="w-full mt-1.5 p-4 bg-slate-950/80 border border-slate-800 rounded-2xl text-sm font-semibold text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
          </div>

          <div v-if="isRegistering">
            <label class="text-xs font-bold text-slate-400">Agent Email <span class="text-rose-500">*</span></label>
            <input type="email" required v-model="authAgentEmail" placeholder="Enter Valid Agent Email Address" class="w-full mt-1.5 p-4 bg-slate-950/80 border border-slate-800 rounded-2xl text-sm font-semibold text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
          </div>

          <div class="bg-slate-950/80 border border-slate-800 p-4 rounded-2xl space-y-2 select-none">
            <div class="flex justify-between items-center">
              <label class="text-xs font-bold text-slate-300">
                What is <span class="text-indigo-400 font-mono font-extrabold text-sm">{{ captchaNum1 }}</span> + <span class="text-indigo-400 font-mono font-extrabold text-sm">{{ captchaNum2 }}</span> = ?
              </label>
              <button type="button" @click="generateCaptcha" class="text-slate-500 hover:text-indigo-400 text-xs font-bold transition" title="New Math Problem">
                <i class="fa-solid fa-arrows-rotate"></i>
              </button>
            </div>
            <input type="number" required v-model="captchaAnswerInput" placeholder="Enter correct answer..." class="w-full p-3.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold font-mono text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
          </div>

          <button type="submit" :disabled="authLoading" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 rounded-2xl text-sm shadow-lg transition active:scale-98 disabled:bg-slate-800 cursor-pointer">
            {{ authLoading ? 'Please wait...' : (isRegistering ? 'REGISTER ACCOUNT' : 'LOG IN NOW') }}
          </button>
        </form>

        <div class="text-center">
          <button type="button" @click="isRegistering = !isRegistering" class="text-xs font-semibold text-indigo-400 hover:underline cursor-pointer">
            {{ isRegistering ? 'Already have an account? Log In' : "Don't have an account? Create One" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Portal Interface Layout -->
    <div v-else class="min-h-screen flex flex-col md:flex-row bg-[#080b14]">
      
      <!-- Sidebar Navigation (FIXED ALIGNMENT & LARGER BUTTONS) -->
      <aside class="hidden md:flex w-64 bg-slate-900/90 border-r border-slate-800/80 flex-col shrink-0 select-none backdrop-blur-md">
        <div class="p-5 border-b border-slate-800/80 flex items-center justify-between">
          
          <!-- BRANDING LOGO IN SIDEBAR (ENLARGED) -->
          <div class="flex items-center gap-2">
            <img src="logo.png" alt="Mino SMS" class="h-11 w-auto object-contain" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
            <div class="hidden items-center gap-2">
              <svg class="h-10 w-auto" viewBox="0 0 280 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 48 L78 12 L50 82 L38 52 Z" fill="#3b82f6"/>
                <path d="M38 52 L78 12 L50 82 Z" fill="#1d4ed8"/>
                <path d="M22 38 L38 20 M26 48 L44 30" stroke="#f97316" stroke-width="4" stroke-linecap="round"/>
                <text x="90" y="58" font-family="Arial, sans-serif" font-weight="900" font-size="38" fill="#ffffff">Mino</text>
                <text x="180" y="58" font-family="Arial, sans-serif" font-weight="900" font-size="38" fill="#f97316">SMS</text>
              </svg>
            </div>
          </div>

          <span class="flex h-2.5 w-2.5 relative" title="Live Sync Active">
            <span class="beacon-dot absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
        </div>

        <nav class="flex-1 p-4 space-y-1.5 overflow-y-auto">
          <div class="space-y-1">
            <span class="px-4 text-[9px] uppercase font-black text-indigo-400 tracking-wider block mb-2">User Workspace</span>
            
            <button @click="currentTab = 'dashboard'" :class="currentTab === 'dashboard' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <i class="fa-solid fa-gauge-high text-base w-5 text-center shrink-0"></i> <span>Dashboard</span>
            </button>
            
            <button @click="currentTab = 'get-number'" :class="currentTab === 'get-number' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center justify-between px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <span class="flex items-center gap-3.5"><i class="fa-solid fa-sim-card text-base w-5 text-center shrink-0"></i> Get Number</span>
              <span v-if="activeAllocationsCount > 0" class="px-2 py-0.5 bg-emerald-500 text-slate-950 rounded-full text-[9px] font-black animate-pulse">
                {{ activeAllocationsCount }}
              </span>
            </button>
            
            <!-- RADAR (FIXED ICON ALIGNMENT) -->
            <button @click="currentTab = 'console'" :class="currentTab === 'console' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <i class="fa-solid fa-radar text-base w-5 text-center shrink-0"></i> <span>Radar</span>
            </button>

            <button @click="currentTab = 'live-access'" :class="currentTab === 'live-access' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <i class="fa-solid fa-tower-cell text-emerald-400 text-base w-5 text-center shrink-0"></i> <span>Live Access</span>
            </button>

            <button @click="currentTab = 'summary'" :class="currentTab === 'summary' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <i class="fa-solid fa-chart-pie text-base w-5 text-center shrink-0"></i> <span>Summary</span>
            </button>

            <button @click="currentTab = 'leaderboard'" :class="currentTab === 'leaderboard' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <i class="fa-solid fa-award text-base w-5 text-center shrink-0"></i> <span>Leaderboard</span>
            </button>
          </div>

          <span class="px-4 text-[9px] uppercase font-black text-slate-500 tracking-wider block pt-4 mb-2">Account & Tools</span>
          <button @click="currentTab = 'payment'" :class="currentTab === 'payment' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
            <i class="fa-solid fa-money-check-dollar text-base w-5 text-center shrink-0"></i> <span>Withdraw</span>
          </button>
          <button @click="currentTab = 'profile'" :class="currentTab === 'profile' ? 'bg-indigo-600/20 text-indigo-300 border-l-2 border-indigo-500 font-bold' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
            <i class="fa-solid fa-user-gear text-base w-5 text-center shrink-0"></i> <span>Profile</span>
          </button>

          <!-- HOW TO USE PANEL BUTTON -->
          <div class="pt-2 px-1">
            <button @click="showGuideModal = true" class="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-bold py-3.5 px-4 rounded-2xl text-xs flex items-center justify-between shadow-lg transition active:scale-95">
              <span class="flex items-center gap-2">
                <i class="fa-solid fa-book-open-reader text-sm"></i> How to Use Panel
              </span>
              <i class="fa-solid fa-chevron-right text-[10px]"></i>
            </button>
          </div>

          <!-- DEV CARD -->
          <div class="pt-2 px-1 select-none">
            <div @click="currentTab = 'api-docs'" class="bg-gradient-to-br from-slate-900 to-slate-950 border border-emerald-500/20 rounded-3xl p-4 space-y-3 hover:border-emerald-500/50 transition-all duration-300 shadow-xl cursor-pointer group hover-card">
              <div class="flex justify-between items-center">
                <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-black px-2.5 py-0.5 rounded-full uppercase tracking-wider">DEV</span>
                <div class="h-9 w-9 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-mono font-bold text-xs">
                  &lt;&gt;
                </div>
              </div>
              <div>
                <h4 class="text-sm font-black text-white leading-tight">Are you a developer?</h4>
                <p class="text-[11px] text-slate-400 font-medium mt-0.5">See the API documentation</p>
              </div>
              <div class="flex justify-end pt-1">
                <button class="bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-black px-4 py-1.5 rounded-xl text-xs transition-all duration-200 shadow-md shadow-emerald-500/20 active:scale-95">
                  View
                </button>
              </div>
            </div>
          </div>
        </nav>

        <!-- USER PROFILE FOOTER WITH AVATAR IMAGE -->
        <div class="p-4 border-t border-slate-800/80 flex items-center gap-3 select-none">
          <div class="h-10 w-10 rounded-full bg-indigo-600 border border-indigo-500/40 flex items-center justify-center text-white font-bold text-xs shrink-0 overflow-hidden shadow-inner">
            <img v-if="userAvatarUrl" :src="userAvatarUrl" alt="Profile Avatar" class="h-full w-full object-cover" />
            <span v-else>{{ user?.name ? user.name.slice(0, 2).toUpperCase() : 'US' }}</span>
          </div>
          <div class="flex-1 overflow-hidden">
            <p class="text-xs font-black text-white truncate">{{ user?.name || 'User' }}</p>
            <p class="text-[10px] text-slate-400 truncate cursor-pointer hover:text-indigo-400 transition" @click="copyToClipboard(user?.email, 'Email Address Copied', 'user_email_sidebar')">{{ user?.email }}</p>
          </div>
          <button @click="signOut" class="text-slate-400 hover:text-rose-400 transition"><i class="fa-solid fa-right-from-bracket"></i></button>
        </div>
      </aside>

      <!-- Mobile Drawer -->
      <transition enter-active-class="transition ease-out duration-300" enter-from-class="-translate-x-full" enter-to-class="translate-x-0" leave-active-class="transition ease-in duration-200" leave-from-class="translate-x-0" leave-to-class="-translate-x-full">
        <aside v-if="mobileMenuOpen" class="fixed inset-y-0 left-0 w-72 bg-[#0f172a] text-slate-200 flex flex-col z-50 md:hidden shadow-2xl border-r border-slate-800 select-none">
          <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
            <div class="flex items-center gap-2">
              <img src="logo.png" alt="Mino SMS" class="h-8 w-auto object-contain" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
              <div class="hidden items-center gap-2">
                <svg class="h-7 w-auto" viewBox="0 0 280 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 48 L78 12 L50 82 L38 52 Z" fill="#3b82f6"/>
                  <path d="M38 52 L78 12 L50 82 Z" fill="#1d4ed8"/>
                  <path d="M22 38 L38 20 M26 48 L44 30" stroke="#f97316" stroke-width="4" stroke-linecap="round"/>
                  <text x="90" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#ffffff">Mino</text>
                  <text x="175" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#f97316">SMS</text>
                </svg>
              </div>
            </div>
            <button @click="mobileMenuOpen = false" class="text-slate-400 hover:text-white p-1.5"><i class="fa-solid fa-xmark text-xl"></i></button>
          </div>

          <nav class="flex-1 p-4 space-y-1.5 bg-[#0f172a] overflow-y-auto ios-scroll">
            <div class="space-y-1">
              <span class="px-3 text-[9px] uppercase font-black text-indigo-400 tracking-wider block mb-2">User Workspace</span>
              <button @click="navigateMobile('dashboard')" :class="currentTab === 'dashboard' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-gauge-high text-base w-5 text-center shrink-0"></i> <span>Dashboard</span>
              </button>
              <button @click="navigateMobile('get-number')" :class="currentTab === 'get-number' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-sim-card text-base w-5 text-center shrink-0"></i> <span>Get Number</span>
              </button>
              <button @click="navigateMobile('console')" :class="currentTab === 'console' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-radar text-base w-5 text-center shrink-0"></i> <span>Radar</span>
              </button>
              <button @click="navigateMobile('live-access')" :class="currentTab === 'live-access' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-tower-cell text-emerald-400 text-base w-5 text-center shrink-0"></i> <span>Live Access</span>
              </button>
              <button @click="navigateMobile('summary')" :class="currentTab === 'summary' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-chart-pie text-base w-5 text-center shrink-0"></i> <span>Summary</span>
              </button>
              <button @click="navigateMobile('leaderboard')" :class="currentTab === 'leaderboard' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-award text-base w-5 text-center shrink-0"></i> <span>Leaderboard</span>
              </button>
            </div>

            <span class="px-3 text-[9px] uppercase font-black text-slate-500 tracking-wider block pt-4 mb-2">Account & Tools</span>
            <button @click="navigateMobile('payment')" :class="currentTab === 'payment' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <i class="fa-solid fa-money-check-dollar text-base w-5 text-center shrink-0"></i> <span>Withdraw</span>
            </button>
            <button @click="navigateMobile('profile')" :class="currentTab === 'profile' ? 'bg-indigo-600/20 text-indigo-300 font-bold' : 'hover:bg-slate-800/50'" class="w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-sm font-semibold transition text-left">
              <i class="fa-solid fa-user-gear text-base w-5 text-center shrink-0"></i> <span>Profile</span>
            </button>

            <!-- MOBILE HOW TO USE BUTTON -->
            <div class="pt-3 px-1">
              <button @click="showGuideModal = true; mobileMenuOpen = false" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 px-4 rounded-2xl text-xs flex items-center justify-between shadow-lg transition">
                <span class="flex items-center gap-2">
                  <i class="fa-solid fa-book-open-reader text-sm"></i> How to Use Panel
                </span>
                <i class="fa-solid fa-chevron-right text-[10px]"></i>
              </button>
            </div>

            <!-- DEV CARD IN MOBILE DRAWER -->
            <div class="pt-3 px-1 select-none">
              <div @click="navigateMobile('api-docs')" class="bg-gradient-to-br from-slate-900 to-slate-950 border border-emerald-500/20 rounded-3xl p-4 space-y-3 hover:border-emerald-500/50 transition-all duration-300 shadow-xl cursor-pointer">
                <div class="flex justify-between items-center">
                  <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-black px-2.5 py-0.5 rounded-full uppercase tracking-wider">DEV</span>
                  <div class="h-8 w-8 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-mono font-bold text-xs">
                    &lt;&gt;
                  </div>
                </div>
                <div>
                  <h4 class="text-xs font-black text-white leading-tight">Are you a developer?</h4>
                  <p class="text-[10px] text-slate-400 font-medium mt-0.5">See the API documentation</p>
                </div>
                <div class="flex justify-end pt-1">
                  <button class="bg-emerald-400 text-slate-950 font-black px-4 py-1.5 rounded-xl text-xs shadow-md shadow-emerald-500/20">
                    View
                  </button>
                </div>
              </div>
            </div>
          </nav>

          <div class="p-4 border-t border-slate-800 bg-slate-950 text-xs font-bold flex flex-col gap-3">
            <a href="https://t.me/MinoXSupport0" target="_blank" class="flex items-center gap-2 text-indigo-400 hover:underline">
              <i class="fa-brands fa-telegram text-base"></i> Telegram Support
            </a>
            <div class="flex items-center justify-between border-t border-slate-800/80 pt-3">
              <span class="text-white font-bold">{{ user?.name || 'User' }}</span>
              <button @click="signOut" class="text-rose-400 hover:text-rose-300 transition font-bold">LOGOUT</button>
            </div>
          </div>
        </aside>
      </transition>
      
      <div v-if="mobileMenuOpen" @click="mobileMenuOpen = false" class="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 md:hidden"></div>

      <!-- Main Content Area -->
      <main class="flex-1 p-4 md:p-8 space-y-6 overflow-y-auto">
        
        <!-- HEADER (REPLACEMENT OF GREEN CIRCLED BADGES WITH USER BALANCE) -->
        <header class="flex justify-between items-center border-b border-slate-800/80 pb-4 select-none">
          <div class="flex items-center gap-3">
            <button @click="mobileMenuOpen = true" class="md:hidden text-slate-300 bg-slate-900 border border-slate-800 p-2.5 rounded-xl focus:outline-none transition active:scale-95">
              <i class="fa-solid fa-bars text-lg"></i>
            </button>
            <span class="h-2.5 w-2.5 bg-indigo-500 rounded-full hidden md:inline-block"></span>
            <h2 class="text-md md:text-lg font-black text-white capitalize font-bold">
              {{ currentTab === 'console' ? 'Radar' : currentTab.replace('-', ' ') }}
            </h2>
          </div>
          
          <div class="flex items-center gap-3">
            <!-- REPLACED HEADER BADGE: SHOW LIVE USER BALANCE -->
            <div class="flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 px-3.5 py-1.5 rounded-2xl text-xs font-mono font-black text-emerald-400 shadow-sm">
              <i class="fa-solid fa-wallet text-indigo-400"></i>
              <span>{{ formatBalance(profile?.balance) }}</span>
            </div>

            <button @click="showGuideModal = true" class="hidden sm:flex items-center gap-1.5 bg-indigo-950/80 hover:bg-indigo-900/80 border border-indigo-800/50 text-indigo-300 text-xs font-bold px-3 py-1.5 rounded-xl transition active:scale-95">
              <i class="fa-solid fa-book-open-reader text-xs"></i>
              <span>How to Use</span>
            </button>

            <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] md:text-xs font-bold px-3 py-1.5 rounded-full shadow-xs flex items-center gap-2">
              <span class="h-2 w-2 rounded-full bg-emerald-500 beacon-dot"></span>
              <span class="hidden sm:inline">LIVE SYNC ON</span>
            </span>
            
            <span class="bg-indigo-600 text-white text-[10px] md:text-xs font-bold px-3 py-1.5 rounded-full shadow-md font-semibold">
              v1.2 · {{ user?.name }}
            </span>
            <button @click="signOut" class="hidden md:block text-slate-400 hover:text-rose-400 p-2 transition"><i class="fa-solid fa-right-from-bracket text-lg"></i></button>
          </div>
        </header>

        <div v-if="announcement" class="bg-indigo-950/60 border border-indigo-800/60 text-indigo-300 px-5 py-3 rounded-2xl text-xs font-bold flex items-center gap-2 select-none font-semibold shadow-md">
          <i class="fa-solid fa-bullhorn text-[#0088CC] text-sm animate-bounce"></i>
          <span>{{ announcement }}</span>
        </div>

        <div>

          <!-- User Tab 1: Dashboard -->
          <div v-if="currentTab === 'dashboard'" class="page-enter-active space-y-6 select-none">
            
            <!-- WELCOME HEADER WITH REAL-TIME BANGLADESH CLOCK -->
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-slate-900/40 p-6 rounded-3xl border border-slate-800/80 backdrop-blur-md">
              <div class="space-y-1">
                <h1 class="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  Welcome back, <span class="text-indigo-400">{{ user?.name || 'minhaz' }}</span>!
                </h1>
                <p class="text-xs text-slate-400 font-medium">Here's what's happening with your account today.</p>
              </div>

              <!-- REAL-TIME BANGLADESH TIME CLOCK BADGE -->
              <div class="flex items-center gap-2 bg-slate-950/80 border border-slate-800 px-4 py-2 rounded-2xl text-xs font-mono font-bold text-slate-300">
                <i class="fa-regular fa-clock text-indigo-400"></i>
                <span>{{ liveBangladeshTime }}</span>
              </div>
            </div>

            <!-- 4 METRIC CARDS GRID (100% REAL TIME DATA) -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 font-semibold">
              
              <div class="bg-slate-900/90 border border-slate-800/80 p-5 rounded-3xl shadow-lg hover-card space-y-2">
                <p class="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">TODAY'S EARNINGS</p>
                <h4 class="text-xl sm:text-2xl font-black text-emerald-400 font-mono">{{ formatBalance(todayEarnings) }}</h4>
              </div>

              <div class="bg-slate-900/90 border border-slate-800/80 p-5 rounded-3xl shadow-lg hover-card space-y-2">
                <p class="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">TODAY'S SUCCESS OTP</p>
                <h4 class="text-xl sm:text-2xl font-black text-emerald-400 font-mono">{{ todayOtpsCount }} <span class="text-xs text-slate-500 font-sans">Hits</span></h4>
              </div>

              <div class="bg-slate-900/90 border border-slate-800/80 p-5 rounded-3xl shadow-lg hover-card space-y-2">
                <p class="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">YESTERDAY'S EARNINGS</p>
                <h4 class="text-xl sm:text-2xl font-black text-emerald-400 font-mono">{{ formatBalance(yesterdayEarnings) }}</h4>
              </div>

              <div class="bg-slate-900/90 border border-slate-800/80 p-5 rounded-3xl shadow-lg hover-card space-y-2">
                <p class="text-[10px] text-slate-400 font-extrabold uppercase tracking-wider">YESTERDAY'S SUCCESS</p>
                <h4 class="text-xl sm:text-2xl font-black text-emerald-400 font-mono">{{ yesterdayOtpsCount }} <span class="text-xs text-slate-500 font-sans">Hits</span></h4>
              </div>

            </div>

            <!-- HOURLY TRAFFIC CURVE GRAPH CARD -->
            <div class="bg-slate-900/90 border border-slate-800/80 p-6 rounded-3xl shadow-xl space-y-4 hover-card">
              <div class="flex justify-between items-center border-b border-slate-800/80 pb-3">
                <h3 class="font-extrabold text-base text-white tracking-wide">Hourly Traffic</h3>
                <span class="bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider">LIVE DATA</span>
              </div>

              <div class="relative h-44 w-full pt-2">
                <svg class="w-full h-full" viewBox="0 0 500 120" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.45" />
                      <stop offset="100%" stop-color="#6366f1" stop-opacity="0.0" />
                    </linearGradient>
                  </defs>
                  <path d="M 0 80 Q 80 15, 160 65 T 320 75 T 500 85 L 500 120 L 0 120 Z" fill="url(#chartGradient)" />
                  <path d="M 0 80 Q 80 15, 160 65 T 320 75 T 500 85" fill="none" stroke="#6366f1" stroke-width="3.5" stroke-linecap="round" />
                </svg>
              </div>

              <div class="flex justify-between text-[10px] font-mono text-slate-500 font-bold px-2 pt-1 border-t border-slate-800/60">
                <span>00:00</span>
                <span>04:00</span>
                <span>08:00</span>
                <span>12:00</span>
                <span>16:00</span>
                <span>20:00</span>
              </div>
            </div>

            <!-- YOUR TOP PERFORMERS CARD (NO FAKE DATA) -->
            <div class="bg-slate-900/90 border border-slate-800/80 p-6 rounded-3xl shadow-xl space-y-4 hover-card">
              <h3 class="font-extrabold text-base text-white tracking-wide border-b border-slate-800/80 pb-3">Your Top Performers</h3>

              <div v-if="topPerformersList.length === 0" class="text-center text-slate-500 text-xs py-8 font-medium">
                No active traffic performance records recorded yet.
              </div>

              <div v-else class="space-y-3">
                <div v-for="perf in topPerformersList" :key="perf.name" class="bg-slate-950/80 border border-slate-800 p-4 rounded-2xl flex items-center justify-between gap-4 hover:border-indigo-500/40 transition">
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="h-10 w-10 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center overflow-hidden shrink-0 p-2 shadow-inner">
                      <img :src="getServiceLogoUrl(perf.name)" 
                           :alt="perf.name" 
                           class="h-full w-full object-contain" 
                           @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                      <div class="hidden h-full w-full rounded-2xl items-center justify-center font-bold text-xs uppercase" :class="getServiceIconBg(perf.name)">
                        <i :class="getServiceIcon(perf.name)"></i>
                      </div>
                    </div>
                    <div class="min-w-0">
                      <h4 class="font-black text-white text-sm uppercase tracking-wide truncate">{{ perf.name }}</h4>
                      <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">SERVICE NAME</p>
                    </div>
                  </div>

                  <div class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-xl text-xs font-black font-mono shadow-xs shrink-0">
                    {{ perf.count }} Hits
                  </div>
                </div>
              </div>
            </div>

            <!-- Latest OTP Reports -->
            <div class="bg-slate-900/90 rounded-3xl border border-slate-800/80 shadow-lg overflow-hidden">
              <div class="p-4 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center">
                <h4 class="font-bold text-xs text-slate-400 uppercase tracking-widest font-sans flex items-center gap-2">
                  <i class="fa-solid fa-clock-rotate-left text-indigo-400"></i> Latest OTP Reports
                </h4>
                <span class="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
                  Auto-Refreshed
                </span>
              </div>

              <div class="block divide-y divide-slate-800/80">
                <div class="p-8 text-center text-slate-500 font-semibold text-xs font-sans" v-if="!successOtps || successOtps.length === 0">
                  No OTP data currently available.
                </div>
                
                <div v-else class="divide-y divide-slate-800/80">
                  <div v-for="log in successOtps" :key="log.created_at || log.number" class="p-4 space-y-2 text-xs hover:bg-slate-800/30 transition font-semibold text-slate-300 font-sans">
                    <div class="flex justify-between items-center font-sans">
                      <span @click="copyToClipboard(log.number, 'Number Copied', 'dash_num_' + log.number)" class="font-bold text-white text-sm font-mono select-all cursor-pointer hover:text-indigo-400 flex items-center gap-1.5 font-bold">
                        {{ log.number }}
                        <i class="fa-regular text-[10px]" :class="copiedStates['dash_num_' + log.number] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy text-slate-500'"></i>
                      </span>
                      <span class="px-2.5 py-1 text-white text-[9px] font-bold uppercase rounded-md flex items-center gap-1.5 shadow-xs" :class="getServiceIconBg(log.service)">
                        <i :class="getServiceIcon(log.service)"></i>
                        {{ log.service }}
                      </span>
                    </div>
                    <div class="flex justify-between items-center bg-emerald-500/10 p-2.5 rounded-xl border border-dashed border-emerald-500/30 font-sans">
                      <span class="text-slate-400 font-bold">OTP Code:</span>
                      <span @click="copyToClipboard(log.otp_code, 'OTP Code Copied', 'dash_otp_' + log.number)" class="font-bold text-emerald-400 text-sm font-mono tracking-wider select-all cursor-pointer hover:underline flex items-center gap-1.5 font-bold">
                        {{ log.otp_code }}
                        <i class="fa-regular text-[11px]" :class="copiedStates['dash_otp_' + log.number] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy text-emerald-500'"></i>
                      </span>
                    </div>
                    <p @click.stop="copyToClipboard(decodeHtml(log.message), 'Full Message Copied', 'dashboard_msg_' + log.number)" class="text-[11px] text-slate-300 leading-relaxed font-semibold bg-slate-950/60 hover:bg-slate-950 p-2 rounded-xl border border-slate-800/80 cursor-pointer transition flex items-center justify-between gap-1" title="Click to copy full message">
                      <span><strong class="text-white font-bold font-sans">SMS Content:</strong> {{ decodeHtml(log.message) }}</span>
                      <i class="fa-regular text-[10px]" :class="copiedStates['dashboard_msg_' + log.number] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy text-slate-500'"></i>
                    </p>
                  </div>
                </div>
              </div>

            </div>

          </div>

          <!-- User Tab 2: Get Number -->
          <div v-if="currentTab === 'get-number'" class="page-enter-active space-y-6">
            
            <div class="bg-slate-900/90 p-5 md:p-6 rounded-3xl border border-slate-800/80 shadow-lg space-y-5 select-none relative">
              <div class="flex justify-between items-center">
                <span class="text-xs font-bold text-indigo-400 uppercase tracking-widest font-sans">RANGE (MANUAL)</span>
                
                <button @click="showGuideModal = true" class="text-xs text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1 bg-indigo-950/60 border border-indigo-800/50 px-3 py-1.5 rounded-xl">
                  <i class="fa-solid fa-book-open-reader text-xs"></i> How to Use Guide
                </button>
              </div>
              
              <div class="relative flex items-center">
                <input type="text" v-model="rid" placeholder="Range ID (e.g., 22465XXX)" class="w-full p-4 pr-24 bg-slate-950/80 border border-slate-800 rounded-2xl text-lg font-black outline-none tracking-wide text-white text-center font-mono focus:border-indigo-500 transition" />
                <button type="button" @click="pasteFromClipboard" class="absolute right-2 bg-indigo-950/80 border border-indigo-800/50 hover:bg-indigo-900/80 text-indigo-300 font-bold px-3 py-2 rounded-xl text-xs transition flex items-center gap-1.5 active:scale-95 shadow-xs" title="Paste from Clipboard">
                  <i class="fa-regular fa-paste text-sm"></i>
                  <span>Paste</span>
                </button>
              </div>
              
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div class="flex items-center gap-4 text-xs font-bold text-slate-400 font-sans">
                  <label class="flex items-center gap-2 cursor-pointer select-none">
                    <input type="checkbox" v-model="nationalFormat" class="rounded text-indigo-500 bg-slate-950 border-slate-800 h-4 w-4" /> National Format
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer select-none">
                    <input type="checkbox" v-model="removePlus" class="rounded text-indigo-500 bg-slate-950 border-slate-800 h-4 w-4" /> Remove (+)
                  </label>
                </div>

                <button @click="handleGetNumber" :disabled="loadingNumber" class="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 px-6 rounded-2xl shadow-lg transition flex items-center justify-center gap-2 disabled:bg-slate-800 font-sans cursor-pointer active:scale-95">
                  <i v-if="loadingNumber" class="fa-solid fa-spinner animate-spin"></i>
                  <i v-else class="fa-solid fa-phone-volume text-sm"></i>
                  <span class="tracking-wide font-bold">{{ loadingNumber ? 'Allocating...' : 'Get Number' }}</span>
                </button>
              </div>
            </div>

            <!-- Allocations List -->
            <div class="space-y-4">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-2 select-none font-sans">
                <input type="text" v-model="searchQuery" placeholder="Search by number..." class="w-full sm:w-64 p-3 bg-slate-900/90 border border-slate-800 rounded-2xl text-xs font-semibold outline-none focus:border-indigo-500 text-white placeholder-slate-500" />
                
                <div class="flex gap-2 text-[10px] font-bold text-slate-400 items-center justify-between w-full sm:w-auto">
                  <div class="flex items-center gap-2">
                    <button @click="prevPage" :disabled="currentPage === 1" class="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 disabled:opacity-50 shadow-xs transition">Prev</button>
                    <span>Page {{ currentPage }} of {{ totalPages }}</span>
                    <button @click="nextPage" :disabled="currentPage === totalPages" class="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 disabled:opacity-50 shadow-xs transition">Next</button>
                  </div>

                  <button @click="refreshAllocations" :disabled="isRefreshingAllocations" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-xs active:scale-95 disabled:bg-slate-800">
                    <i class="fa-solid fa-rotate text-[10px]" :class="isRefreshingAllocations ? 'animate-spin' : ''"></i>
                    <span>{{ isRefreshingAllocations ? 'Syncing...' : 'Refresh' }}</span>
                  </button>
                </div>
              </div>

              <div class="bg-slate-900/90 rounded-t-2xl border border-b-0 border-slate-800/80 px-4 py-3 hidden sm:grid grid-cols-12 text-[10px] font-black uppercase text-slate-400 select-none tracking-wider font-sans">
                <div class="col-span-5">Number & Status</div>
                <div class="col-span-4">Country & Operator</div>
                <div class="col-span-3 text-right">Activity & Timer</div>
              </div>

              <div class="bg-slate-900/90 p-12 text-center text-slate-500 border border-slate-800/80 rounded-3xl font-semibold text-xs font-sans" v-if="paginatedAllocations.length === 0">
                No allocated numbers found.
              </div>

              <div v-else class="space-y-2">
                <div v-for="alloc in paginatedAllocations" :key="alloc.id || alloc.createdAt" 
                     :class="[
                       'bg-slate-900/90 rounded-2xl border transition overflow-hidden shadow-md hover:shadow-xl pop-in',
                       alloc.justHit ? 'border-emerald-500 otp-hit-glow' : 'border-slate-800/80 hover:border-indigo-500/50'
                     ]">
                  <div class="grid grid-cols-12 items-center min-h-[55px] divide-x divide-slate-800/80">
                    
                    <div class="col-span-12 sm:col-span-5 p-3.5 flex flex-col justify-center min-w-0">
                      <span class="text-[8px] text-slate-500 font-extrabold uppercase tracking-wider block sm:hidden font-sans">Number</span>
                      <div class="flex items-center flex-wrap gap-2 mt-0.5">
                        <div @click="copyToClipboard(alloc.number, 'Number Copied', 'alloc_num_' + alloc.id)" class="flex items-center gap-1.5 cursor-pointer hover:opacity-80 active:scale-95 transition">
                          <span class="font-mono font-black text-white text-sm tracking-tight break-all select-all font-bold">{{ alloc.number }}</span>
                          <i class="fa-regular text-[11px] transition" :class="copiedStates['alloc_num_' + alloc.id] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy text-indigo-400'"></i>
                        </div>

                        <span v-if="alloc.status === 'completed'" class="bg-emerald-500 text-slate-950 text-[8px] font-black px-2.5 py-0.5 rounded-md uppercase tracking-wider font-sans shadow-xs flex items-center gap-1">
                          <i class="fa-solid fa-check"></i> SUCCESS
                        </span>
                        <span v-else-if="alloc.status === 'active'" class="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[8px] font-black px-2 py-0.5 rounded-md uppercase tracking-wider radar-pulse font-sans flex items-center gap-1">
                          <span class="h-1.5 w-1.5 rounded-full bg-amber-400 animate-ping"></span> WAITING
                        </span>
                        <span v-else class="bg-slate-800 text-slate-400 text-[8px] font-black px-2 py-0.5 rounded-md uppercase tracking-wider font-bold font-sans">EXPIRED</span>
                      </div>

                      <div class="mt-1 min-w-0">
                        <div class="text-[9px] text-amber-400 font-extrabold italic flex items-center gap-1 font-sans" v-if="alloc.status === 'active'">
                          <i class="fa-solid fa-spinner animate-spin text-[8px]"></i> Listening live for OTP...
                        </div>
                        
                        <div v-else-if="alloc.status === 'completed'" class="flex flex-col gap-1 min-w-0 pop-in">
                          <div class="flex flex-wrap gap-1.5">
                            <div v-for="(singleOtp, otpIdx) in getOtpsList(alloc)" :key="otpIdx" @click.stop="copyToClipboard(singleOtp, 'OTP Code Copied', 'alloc_otp_' + alloc.id + '_' + otpIdx)" class="bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 px-2.5 py-0.5 rounded-lg text-emerald-300 cursor-pointer active:scale-95 transition flex items-center gap-1.5 font-bold text-xs font-mono shadow-xs">
                              <span>{{ singleOtp }}</span>
                              <i class="fa-regular" :class="copiedStates['alloc_otp_' + alloc.id + '_' + otpIdx] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy text-emerald-400'"></i>
                            </div>
                          </div>

                          <p v-if="alloc.message" 
                             @click.stop="copyToClipboard(decodeHtml(alloc.message), 'Full Message Copied', 'sms_msg_' + alloc.id)" 
                             class="text-[10px] text-slate-300 font-semibold max-w-full truncate font-sans bg-slate-950/60 hover:bg-slate-950 p-1.5 rounded border border-slate-800/80 cursor-pointer active:scale-98 transition flex items-center justify-between gap-1 mt-0.5" 
                             :title="decodeHtml(alloc.message)">
                            <span class="truncate">{{ decodeHtml(alloc.message) }}</span>
                            <i class="fa-regular text-[9px] shrink-0" :class="copiedStates['sms_msg_' + alloc.id] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy text-slate-500'"></i>
                          </p>
                        </div>

                        <div class="text-[8px] text-rose-400 font-extrabold flex items-center gap-0.5 font-sans" v-else>
                          <i class="fa-solid fa-circle-exclamation shrink-0 font-bold"></i> Expired. No OTP received.
                        </div>
                      </div>
                    </div>

                    <!-- COUNTRY FLAG & NAME -->
                    <div class="col-span-7 sm:col-span-4 p-3.5 flex flex-col justify-center min-w-0">
                      <span class="text-[8px] text-slate-500 font-extrabold uppercase tracking-wider block sm:hidden font-sans">Country / Operator</span>
                      <div class="flex items-center gap-1.5 font-sans">
                        <span class="text-lg select-none">{{ getCountryFlag(alloc.number) }}</span>
                        <span class="font-extrabold text-white text-[11px] uppercase truncate font-bold">{{ getCountryName(alloc.number) !== 'International' ? getCountryName(alloc.number) : (alloc.country || 'International') }}</span>
                      </div>
                      <span class="text-[9px] text-slate-400 font-black uppercase mt-0.5 font-bold font-sans">{{ alloc.operator }}</span>
                    </div>

                    <div class="col-span-5 sm:col-span-3 p-3.5 flex flex-col justify-center items-end font-semibold text-slate-300">
                      <span class="text-[8px] text-slate-500 font-extrabold uppercase tracking-wider block sm:hidden font-sans">Activity</span>
                      <div class="text-[11px] font-mono font-black text-white tracking-tight mt-0.5 font-bold flex items-center gap-1">
                        <i v-if="alloc.status === 'active'" class="fa-regular fa-clock text-amber-400 animate-spin"></i>
                        {{ alloc.status === 'active' && alloc.timeLeft > 0 ? formatTime(alloc.timeLeft) : 'Completed' }}
                      </div>
                      <span class="text-[8px] text-slate-500 font-bold font-sans mt-0.5">{{ formatTimestamp(alloc.createdAt) }}</span>
                    </div>

                  </div>
                </div>
              </div>

            </div>

          </div>

          <!-- User Tab 3: Radar (Console Stream) -->
          <div v-if="currentTab === 'console'" class="page-enter-active space-y-6">
            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-6 hover-card select-none" v-if="topApps.list && topApps.list.length > 0">
              <div class="flex items-center gap-2 border-b border-slate-800 pb-2">
                <i class="fa-solid fa-chart-simple text-indigo-400 text-md"></i>
                <h3 class="font-extrabold text-xs text-slate-400 uppercase tracking-widest font-bold">Top Apps</h3>
              </div>

              <div class="relative h-56 border border-slate-800/80 bg-slate-950/40 rounded-2xl flex items-end justify-around pb-4 pt-8 px-6 gap-6">
                <div class="absolute inset-x-0 top-0 h-full flex flex-col justify-between pointer-events-none select-none opacity-20 p-4">
                  <div class="border-t border-dashed border-slate-700 w-full h-0"></div>
                  <div class="border-t border-dashed border-slate-700 w-full h-0"></div>
                  <div class="border-t border-dashed border-slate-700 w-full h-0"></div>
                  <div class="border-t border-dashed border-slate-700 w-full h-0"></div>
                </div>

                <div v-for="(appItem, idx) in topApps.list" :key="appItem.name" class="relative flex flex-col items-center group w-16 z-10 h-full justify-end transition font-sans">
                  <span class="bg-slate-800 text-white text-[10px] px-2 py-0.5 rounded font-black mb-2 shadow-2xs font-mono">
                    {{ appItem.count }}
                  </span>
                  <div :style="{ height: Math.max(10, appItem.percentage) + '%' }" :class="barColors[idx % 4]" class="w-8 rounded-t-xl transition-all duration-300 shadow-sm relative flex items-end justify-center">
                  </div>
                  <span class="text-[10px] font-black text-slate-400 mt-2 truncate max-w-full block uppercase tracking-wider">{{ appItem.name }}</span>
                </div>
              </div>

              <div class="space-y-2.5 font-semibold text-slate-300 font-sans">
                <div v-for="(appItem, idx) in topApps.list" :key="appItem.name" class="flex justify-between items-center text-xs font-semibold font-sans">
                  <div class="flex items-center gap-2">
                    <span :class="dotColors[idx % 4]" class="h-3 w-3 rounded-full shrink-0"></span>
                    <span class="text-white font-bold">{{ appItem.name }}</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <span class="text-white font-black font-mono font-bold">{{ appItem.count }}</span>
                    <span class="text-slate-400 font-bold w-10 text-right font-mono font-bold">{{ appItem.percentage }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg flex justify-between items-center hover-card select-none">
              <div>
                <div class="flex items-center gap-2">
                  <i class="fa-solid fa-radar text-indigo-400 text-lg animate-pulse"></i>
                  <h2 class="text-md font-black text-white font-bold">Signal Radar Stream</h2>
                </div>
                <p class="text-[10px] text-slate-400 font-medium mt-1">Real-time signal interception from global gateways.</p>
              </div>
              <span class="bg-slate-950 text-slate-300 text-[10px] font-bold px-3 py-1.5 rounded-full select-none border border-slate-800 font-mono">
                {{ liveLogs.length }} / 150 Active Logs
              </span>
            </div>

            <div class="space-y-3">
              <div class="p-12 text-slate-500 text-center font-semibold bg-slate-900/90 border border-slate-800/80 rounded-3xl text-xs font-sans" v-if="liveLogs.length === 0">Initializing global radar tracker...</div>
              
              <div v-else class="space-y-2.5 select-none">
                <div v-for="log in liveLogs" :key="log.range + '_' + log.time" @click="copyToClipboard(log.range, 'Range ID Copied', 'log_' + log.range + '_' + log.time)" class="bg-slate-900/90 p-4 rounded-2xl border border-slate-800/80 shadow-md cursor-pointer hover:border-indigo-500/50 transition active:scale-[0.99] space-y-2">
                  <div class="flex justify-between items-start border-b border-slate-800/80 pb-1.5 font-sans">
                    <div>
                      <span class="text-xs font-black text-indigo-400 uppercase tracking-wide block flex items-center gap-1.5 select-none font-bold">
                        <i :class="getServiceIcon(log.service)"></i>
                        {{ log.service }}
                        <span v-if="copiedStates['log_' + log.range + '_' + log.time]" class="text-[8px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.25 rounded font-black animate-pulse">Copied!</span>
                      </span>
                      <span class="text-[10px] font-bold text-slate-400 block mt-0.5 font-mono select-all flex items-center gap-1.5 font-bold">
                        {{ log.range }}
                        <i class="fa-regular text-[10px]" :class="copiedStates['log_' + log.range + '_' + log.time] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy text-indigo-400'"></i>
                      </span>
                    </div>
                    <span class="bg-slate-950 text-slate-300 text-[9px] font-bold px-2 py-0.5 rounded uppercase select-none font-sans border border-slate-800 font-bold flex items-center gap-1">
                      <span>{{ getCountryFlag(log.range) }}</span>
                      <span>{{ log.country }}</span>
                    </span>
                  </div>
                  <div class="space-y-1">
                    <p class="font-mono font-bold text-slate-200 text-[11px] leading-tight break-words mt-1 font-semibold">
                      {{ decodeHtml(log.message) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- User Tab 4: Live Access -->
          <div v-if="currentTab === 'live-access'" class="page-enter-active space-y-6">
            
            <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-lg space-y-4 hover-card text-center select-none font-sans">
              <h4 class="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center justify-center gap-2">
                <i class="fa-solid fa-chart-pie text-indigo-400"></i> Today's Service Demand
              </h4>
              <div class="relative h-48 w-48 rounded-full flex items-center justify-center mx-auto transition-all duration-300" :style="serviceDemandChartStyle">
                <div class="h-36 w-36 bg-[#070a12] rounded-full flex flex-col items-center justify-center text-center shadow-inner">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Active Ranges</span>
                  <span class="text-2xl font-black text-white mt-0.5 font-mono">{{ activeRangesCount }}</span>
                </div>
              </div>
            </div>

            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-4 hover-card select-none">
              <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                <div class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest font-sans">
                  <i class="fa-solid fa-magnifying-glass text-indigo-400"></i> Find Active Service Ranges
                </div>
                <button @click="fetchLiveAccessData" class="text-xs text-indigo-400 font-bold hover:underline flex items-center gap-1">
                  <i class="fa-solid fa-rotate text-[10px]" :class="liveAccessLoading ? 'animate-spin' : ''"></i> Refresh Ranges
                </button>
              </div>
              <input type="text" v-model="liveAccessSearchQuery" placeholder="Type to search services... (e.g. WhatsApp, TikTok, Binance)" class="w-full p-4 bg-slate-950/80 border border-slate-800 rounded-2xl text-md font-bold outline-none text-white focus:border-indigo-500 transition placeholder-slate-600" />
            </div>

            <div class="space-y-3">
              <div class="p-12 text-slate-500 text-center font-semibold bg-slate-900/90 border border-slate-800/80 rounded-3xl text-xs font-bold font-sans" v-if="filteredLiveAccessServices.length === 0">
                <i class="fa-solid fa-spinner animate-spin text-lg text-indigo-400 block mb-2" v-if="liveAccessLoading"></i>
                <span>{{ liveAccessLoading ? 'Loading live active ranges...' : 'No active services or ranges found.' }}</span>
              </div>
              
              <div v-else class="space-y-2">
                <div v-for="service in filteredLiveAccessServices" :key="service.name" class="bg-slate-900/90 rounded-2xl border border-slate-800/80 overflow-hidden shadow-md hover:border-indigo-500/50 transition">
                  <div @click="toggleServiceAccordion(service.name)" class="flex justify-between items-center p-4 bg-slate-950/40 hover:bg-slate-950/80 cursor-pointer select-none transition">
                    <div class="flex items-center gap-3">
                      <div class="h-9 w-9 rounded-full flex items-center justify-center bg-slate-950 border border-slate-800 shadow-xs shrink-0 overflow-hidden p-1.5">
                        <img :src="getServiceLogoUrl(service.name)" 
                             :alt="service.name" 
                             class="h-full w-full object-contain" 
                             @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                        <div class="hidden h-full w-full rounded-full items-center justify-center font-bold text-xs uppercase" :class="getServiceIconBg(service.name)">
                          <i :class="getServiceIcon(service.name)"></i>
                        </div>
                      </div>
                      <span class="text-sm font-black text-white uppercase tracking-wide font-bold">
                        {{ service.name }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2 font-sans">
                      <span class="bg-emerald-500/10 text-emerald-400 text-[10px] font-extrabold px-2.5 py-1 rounded-full border border-emerald-500/20 font-mono">
                        {{ service.ranges.length }} Ranges
                      </span>
                      <i class="fa-solid" :class="isAccordionOpen(service.name) ? 'fa-chevron-up text-slate-400' : 'fa-chevron-down text-slate-400'"></i>
                    </div>
                  </div>

                  <div class="border-t border-slate-800/80 p-4 space-y-2.5" v-if="isAccordionOpen(service.name)">
                    <div v-for="(range, idx) in service.ranges" :key="range.code" class="flex justify-between items-center p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl hover:border-indigo-500/40 transition">
                      <div class="flex items-center gap-2.5 min-w-0 font-sans">
                        <span class="text-xs flex items-center gap-0.5 select-none animate-pulse" v-if="idx === 0">
                          🔥 🏳️
                        </span>
                        <span class="text-[11px] font-black text-slate-500 w-6 font-mono" v-else>
                          #{{ idx + 1 }}
                        </span>
                        
                        <span class="text-lg select-none">
                          {{ getCountryFlag(range.code) }}
                        </span>
                        
                        <span class="text-[11px] sm:text-xs font-bold text-slate-300 flex flex-wrap items-center gap-1.5 min-w-0">
                          <span class="font-extrabold text-white font-bold">{{ range.country }}</span> 
                          <span class="text-slate-600">|</span> 
                          <span class="font-mono font-black text-indigo-300 select-all font-bold">{{ range.code }}</span>
                        </span>
                      </div>
                      
                      <button @click="copyToClipboard(range.code, 'Range ID Copied', 'la_' + range.code)" class="text-indigo-400 hover:text-indigo-300 p-1.5 hover:bg-slate-900 rounded-lg transition flex items-center gap-1.5 shrink-0 font-bold font-sans">
                        <i class="fa-regular text-[10px]" :class="copiedStates['la_' + range.code] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy'"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- User Tab 5: Summary -->
          <div v-if="currentTab === 'summary'" class="page-enter-active space-y-6 select-none font-sans">
            <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-lg space-y-6 hover-card">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h3 class="font-extrabold text-md text-white flex items-center gap-2 font-bold">
                    <i class="fa-solid fa-chart-pie text-indigo-400 font-bold"></i> WORK STATS SUMMARY
                  </h3>
                  <p class="text-xs text-slate-404 font-medium">ইউজারের পারফরম্যান্স ও ওটিপি কনভার্সন সামারি রিপোর্ট</p>
                </div>
                
                <div class="flex flex-wrap gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
                  <button v-for="t in ['today', 'yesterday', '7days', '15days', '30days', 'lifetime']" :key="t" @click="summaryFilter = t" :class="summaryFilter === t ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-400 hover:bg-slate-900'" class="px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition font-bold">
                    {{ t === '7days' ? '7 Days' : t === '15days' ? '15 Days' : t === '30days' ? '30 Days' : t }}
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 flex flex-col justify-between">
                  <span class="text-[10px] text-slate-400 font-black uppercase tracking-wider">Total Booking</span>
                  <h4 class="text-2xl font-black text-white mt-2 font-mono font-bold">{{ summaryStats.total }}</h4>
                </div>
                <div class="bg-emerald-500/10 p-4 rounded-2xl border border-emerald-500/20 flex flex-col justify-between">
                  <span class="text-[10px] text-emerald-400 font-black uppercase tracking-wider">OTP Hits</span>
                  <h4 class="text-2xl font-black text-emerald-400 mt-2 font-mono font-bold">{{ summaryStats.success }}</h4>
                </div>
                <div class="bg-indigo-500/10 p-4 rounded-2xl border border-indigo-500/20 flex flex-col justify-between">
                  <span class="text-[10px] text-indigo-400 font-black uppercase tracking-wider">Success Rate</span>
                  <h4 class="text-2xl font-black text-indigo-400 mt-2 font-mono font-bold">{{ summaryStats.successRate }}%</h4>
                </div>
                <div class="bg-rose-500/10 p-4 rounded-2xl border border-rose-500/20 flex flex-col justify-between">
                  <span class="text-[10px] text-rose-400 font-black uppercase tracking-wider">Failed / Expired</span>
                  <h4 class="text-2xl font-black text-rose-400 mt-2 font-mono font-bold">{{ summaryStats.failed }}</h4>
                </div>
                <div class="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 flex flex-col justify-between">
                  <span class="text-[10px] text-slate-400 font-black uppercase tracking-wider">Fail Rate</span>
                  <h4 class="text-2xl font-black text-slate-300 mt-2 font-mono font-bold">{{ summaryStats.failRate }}%</h4>
                </div>
              </div>

              <div class="space-y-2">
                <div class="flex justify-between text-xs font-bold text-slate-400 font-sans">
                  <span>Succeed vs Failed Numbers Ratio</span>
                  <span>{{ summaryStats.successRate }}% Success</span>
                </div>
                <div class="w-full h-3 bg-rose-950/80 rounded-full overflow-hidden flex shadow-inner border border-slate-800">
                  <div :style="{ width: summaryStats.successRate + '%' }" class="h-full bg-emerald-500 transition-all duration-300"></div>
                  <div :style="{ width: summaryStats.failRate + '%' }" class="h-full bg-rose-600 transition-all duration-300"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- User Tab 6: Leaderboard (NAME MASKING & AVATAR INTEGRATION) -->
          <div v-if="currentTab === 'leaderboard'" class="page-enter-active space-y-6 select-none font-semibold text-slate-200 font-sans font-bold">
            
            <div class="bg-gradient-to-r from-indigo-600 to-indigo-800 text-white p-5 rounded-3xl shadow-lg flex items-center justify-between hover-card font-sans border border-indigo-500/30">
              <div class="space-y-1">
                <span class="text-[9px] font-black bg-white/20 px-2.5 py-1 rounded-full uppercase tracking-wider font-sans">My Ranking Status</span>
                <h3 class="text-base font-black font-bold font-sans">Your current network position is #{{ personalRank }}</h3>
                <p class="text-[11px] text-white/80 font-sans">You have completed a total of <strong class="text-white font-bold font-mono">{{ personalOtpCount }}</strong> successful OTP checks!</p>
              </div>
              <div class="text-3xl font-black opacity-40 select-none font-mono">#{{ personalRank }}</div>
            </div>

            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg font-sans">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                  <div class="flex items-center gap-2">
                    <i class="fa-solid fa-award text-amber-400 text-lg"></i>
                    <h2 class="text-md font-black text-white font-bold">TOP WORKERS LEADERBOARD</h2>
                  </div>
                  <p class="text-[10px] text-slate-400 font-medium mt-1 font-sans">Real-time work ranks based on completed OTP codes verified securely.</p>
                </div>
                <span class="text-[10px] text-slate-400 font-bold uppercase tracking-tight italic bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-full shrink-0 flex items-center gap-1.5 font-mono">
                  <i class="fa-regular fa-clock animate-spin"></i> Restarts every 25 Hours
                </span>
              </div>

              <div class="flex gap-2 text-xs font-black mt-5">
                <button @click="leaderboardTab = 'today'" :class="leaderboardTab === 'today' ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-950 text-slate-400 hover:bg-slate-800'" class="px-4 py-2 rounded-xl transition border border-slate-800">Today (25H)</button>
                <button @click="leaderboardTab = 'weekly'" :class="leaderboardTab === 'weekly' ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-950 text-slate-400 hover:bg-slate-800'" class="px-4 py-2 rounded-xl transition border border-slate-800">Weekly</button>
                <button @click="leaderboardTab = 'lifetime'" :class="leaderboardTab === 'lifetime' ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-950 text-slate-400 hover:bg-slate-800'" class="px-4 py-2 rounded-xl transition border border-slate-800">Lifetime</button>
              </div>

              <!-- LEADERBOARD MASKED NAME LIST -->
              <div class="space-y-3 mt-4 max-h-[500px] overflow-y-auto pr-1">
                <div v-for="(worker, idx) in leaderboardData[leaderboardTab]" :key="idx" class="flex justify-between items-center bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800/80 text-xs hover:border-indigo-500/40 transition">
                  <div class="flex items-center gap-3">
                    <span class="font-black text-xs h-8 w-8 rounded-full flex items-center justify-center shrink-0 border shadow-xs font-mono font-bold" :class="idx === 0 ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : idx === 1 ? 'bg-slate-700/30 text-slate-200 border-slate-600' : 'bg-orange-500/20 text-orange-300 border-orange-500/40'">
                      #{{ idx + 1 }}
                    </span>

                    <!-- AVATAR THUMBNAIL -->
                    <div class="h-8 w-8 rounded-full bg-indigo-600 border border-indigo-400/40 flex items-center justify-center text-white font-bold text-xs shrink-0 overflow-hidden shadow-inner">
                      <span>{{ worker.name ? worker.name.slice(0, 1).toUpperCase() : 'U' }}</span>
                    </div>

                    <div>
                      <!-- MASKED NAME -->
                      <span class="font-extrabold text-white text-sm block font-bold font-mono">{{ maskName(worker.name) }}</span>
                      <span class="text-[10px] text-slate-500 block font-semibold font-mono">{{ worker.id_code }}</span>
                    </div>
                  </div>
                  <span class="font-black text-indigo-400 text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full shadow-xs font-mono font-bold">
                    {{ worker.count }} Successful OTPs
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- User Tab 7: API Docs & Playground -->
          <div v-if="currentTab === 'api-docs'" class="page-enter-active space-y-6 select-none font-sans font-bold">
            <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-lg space-y-4">
              <h3 class="text-md font-black text-white flex items-center gap-2 font-bold">
                <i class="fa-solid fa-laptop-code text-indigo-400"></i> Developer API Docs
              </h3>
              <p class="text-xs text-slate-400 font-medium leading-relaxed font-semibold">
                Integrate MINO SMS services directly into your custom Telegram bots or backend applications.
              </p>
            </div>

            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-2 select-none">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <i class="fa-solid fa-server text-indigo-400"></i> API Base Endpoint URL
                </span>
                <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase">Active</span>
              </div>
              <div class="flex items-center justify-between bg-slate-950 text-emerald-400 p-3.5 rounded-2xl font-mono text-xs sm:text-sm border border-slate-800">
                <span class="truncate font-black select-all">https://mino-sms-panel.xyz</span>
                <button @click="copyToClipboard('https://mino-sms-panel.xyz', 'API Base URL Copied', 'api_base_copy')" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-xl text-xs font-sans font-bold flex items-center gap-1 shrink-0 ml-2 transition">
                  <i class="fa-regular" :class="copiedStates['api_base_copy'] ? 'fa-circle-check' : 'fa-copy'"></i>
                  <span>{{ copiedStates['api_base_copy'] ? 'Copied' : 'Copy' }}</span>
                </button>
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-6">
              <div class="space-y-4 select-none">
                <h4 class="text-sm font-black text-white px-1 font-bold border-b border-slate-800 pb-2">API Documentation</h4>
                
                <div class="space-y-4 text-xs font-semibold">
                  <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-3">
                    <div class="flex items-center justify-between">
                      <span class="bg-indigo-600 text-white text-[9px] font-black px-2 py-0.5 rounded uppercase font-bold">POST / GET</span>
                      <span class="text-[10px] text-slate-400 font-mono">getnumber</span>
                    </div>
                    <p class="font-mono font-black text-indigo-400 mt-1 font-bold">/getnumber</p>
                    <p class="text-[11px] text-slate-400 font-medium font-semibold">Allocate a temporary virtual number instantly using target range.</p>
                    <div class="text-[10px] bg-slate-950 text-emerald-400 p-3 rounded-xl font-mono select-all border border-slate-800 leading-relaxed">
                      Header: { "mauthapi": "YOUR_API_KEY" }<br>
                      Payload: { "rid": "2250789XXX" }
                    </div>
                  </div>

                  <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-3">
                    <div class="flex items-center justify-between">
                      <span class="bg-emerald-600 text-white text-[9px] font-black px-2 py-0.5 rounded uppercase font-bold">GET</span>
                      <span class="text-[10px] text-slate-400 font-mono">check</span>
                    </div>
                    <p class="font-mono font-black text-emerald-400 mt-1 font-bold">/check</p>
                    <p class="text-[11px] text-slate-400 font-medium font-semibold">Check active booking status and intercept incoming OTP SMS.</p>
                    <div class="text-[10px] bg-slate-950 text-emerald-400 p-3 rounded-xl font-mono select-all border border-slate-800 leading-relaxed">
                      Query: ?api_key=YOUR_KEY&number=NUMBER
                    </div>
                  </div>

                  <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-3">
                    <div class="flex items-center justify-between">
                      <span class="bg-blue-600 text-white text-[9px] font-black px-2 py-0.5 rounded uppercase font-bold">GET</span>
                      <span class="text-[10px] text-slate-404 font-mono">liveaccess</span>
                    </div>
                    <p class="font-mono font-black text-blue-400 mt-1 font-bold">/liveaccess</p>
                    <p class="text-[11px] text-slate-400 font-medium font-semibold">Get a list of currently active services and active ranges.</p>
                    <div class="text-[10px] bg-slate-950 text-emerald-400 p-3 rounded-xl font-mono select-all border border-slate-800 leading-relaxed">
                      Query: ?api_key=YOUR_KEY
                    </div>
                  </div>

                  <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-3">
                    <div class="flex items-center justify-between">
                      <span class="bg-purple-600 text-white text-[9px] font-black px-2 py-0.5 rounded uppercase font-bold">GET</span>
                      <span class="text-[10px] text-slate-404 font-mono">console</span>
                    </div>
                    <p class="font-mono font-black text-purple-400 mt-1 font-bold">/console</p>
                    <p class="text-[11px] text-slate-400 font-medium font-semibold">Fetch the latest 150 live OTP messages flowing through the master console.</p>
                    <div class="text-[10px] bg-slate-950 text-emerald-400 p-3 rounded-xl font-mono select-all border border-slate-800 leading-relaxed">
                      Query: ?api_key=YOUR_KEY
                    </div>
                  </div>
                </div>
              </div>

              <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-lg space-y-4 select-none h-max">
                <h4 class="text-sm font-black text-white border-b border-slate-800 pb-2 font-bold">API Playground / Tester</h4>
                
                <div class="space-y-4 text-xs font-bold text-slate-300 font-sans">
                  <div>
                    <label class="text-slate-400">Select Endpoint</label>
                    <select v-model="selectedTestApi" class="w-full mt-1.5 p-3.5 bg-slate-950 border border-slate-800 rounded-xl outline-none focus:border-indigo-500 transition font-bold text-white">
                      <option value="getnum">POST /getnumber</option>
                      <option value="check">GET /check</option>
                      <option value="liveaccess">GET /liveaccess</option>
                      <option value="success-otp">GET /success_otp</option>
                      <option value="console">GET /console</option>
                    </select>
                  </div>

                  <div v-if="selectedTestApi === 'getnum' || selectedTestApi === 'check'">
                    <label class="text-slate-400">{{ selectedTestApi === 'getnum' ? 'Range ID (rid)' : 'Phone Number (number)' }}</label>
                    <input type="text" v-model="testRange" class="w-full mt-1.5 p-3.5 bg-slate-950 border border-slate-800 rounded-xl font-mono text-white outline-none focus:border-indigo-500 transition font-semibold" />
                  </div>

                  <button @click="runLiveApiTest" :disabled="testApiLoading" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl transition shadow-md flex items-center justify-center gap-2 active:scale-95 disabled:bg-slate-800">
                    <i v-if="testApiLoading" class="fa-solid fa-spinner animate-spin"></i>
                    <i v-else class="fa-solid fa-paper-plane"></i>
                    Send Request
                  </button>

                  <div v-if="testApiResponse" class="space-y-2 pt-2">
                    <span class="text-[10px] uppercase font-black text-slate-400 block">Live Response:</span>
                    <pre class="bg-slate-950 text-emerald-400 p-4 rounded-2xl font-mono text-[11px] select-all max-h-60 overflow-y-auto leading-relaxed border border-slate-800 font-semibold font-sans">{{ testApiResponse }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Shared Tab: Payment/Withdraw -->
          <div v-if="currentTab === 'payment'" class="page-enter-active space-y-6 select-none font-semibold text-slate-200 font-bold">
            
            <!-- CARD 1: MANAGE MY ACCOUNTS -->
            <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-xl space-y-5 hover-card select-none">
              <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div class="flex items-center gap-2.5">
                  <i class="fa-solid fa-building-columns text-indigo-400 text-base"></i>
                  <h3 class="font-extrabold text-sm text-white">Manage My Accounts</h3>
                </div>
                <!-- EXCHANGE RATE BADGE -->
                <span class="bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-[10px] font-black px-3 py-1 rounded-full font-mono">
                  $1.00 USD = ৳100.00 BDT
                </span>
              </div>

              <div class="space-y-4 text-xs font-sans">
                <div>
                  <label class="text-slate-400 font-bold uppercase text-[10px] tracking-wider block mb-1.5">Select Method</label>
                  <select v-model="newAccMethod" class="w-full p-3.5 bg-slate-950 border border-slate-800 rounded-2xl text-white outline-none focus:border-indigo-500 transition font-bold">
                    <option value="">Select Allowed Method</option>
                    <option v-for="m in withdrawalMethods" :key="m.id" :value="m.method_name">{{ m.method_name }}</option>
                  </select>
                </div>

                <div>
                  <label class="text-slate-400 font-bold uppercase text-[10px] tracking-wider block mb-1.5">Account Label / Name</label>
                  <input type="text" v-model="newAccName" placeholder="e.g. My Personal Bkash / Main Binance" class="w-full p-3.5 bg-slate-950 border border-slate-800 rounded-2xl text-xs font-semibold text-white outline-none focus:border-indigo-500 transition placeholder-slate-600" />
                </div>

                <div>
                  <label class="text-slate-400 font-bold uppercase text-[10px] tracking-wider block mb-1.5">Account Details (Number / ID)</label>
                  <input type="text" v-model="newAccDetails" placeholder="e.g. 018XXXXXXXX or Binance Pay ID" class="w-full p-3.5 bg-slate-950 border border-slate-800 rounded-2xl text-xs font-semibold text-white outline-none focus:border-indigo-500 transition placeholder-slate-600 font-mono" />
                </div>

                <button @click="addOrUpdateAccount" :disabled="!newAccMethod || !newAccName || !newAccDetails" class="w-full bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 text-white font-black py-4 rounded-2xl text-xs transition-all duration-200 shadow-lg active:scale-95 flex items-center justify-center gap-2">
                  <i class="fa-solid fa-plus text-xs"></i>
                  <span>{{ editingAccountIndex !== null ? 'Save Account Changes' : '+ Add Account' }}</span>
                </button>

                <!-- ADDED ACCOUNTS LIST -->
                <div class="pt-2 space-y-2">
                  <label class="text-slate-400 font-bold uppercase text-[10px] tracking-wider block">Added Accounts:</label>
                  
                  <div v-if="userSavedAccounts.length === 0" class="text-slate-500 text-xs italic text-center p-4 bg-slate-950/60 rounded-2xl border border-slate-800/80">
                    No withdrawal accounts added yet.
                  </div>

                  <div v-else class="space-y-2">
                    <div v-for="(acc, accIdx) in userSavedAccounts" :key="accIdx" class="bg-slate-950/80 border border-slate-800 p-3.5 rounded-2xl flex items-center justify-between gap-3 hover:border-slate-700 transition">
                      <div class="min-w-0 flex-1">
                        <div class="flex items-center gap-2">
                          <span class="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[9px] font-extrabold px-2 py-0.5 rounded-md uppercase font-mono">
                            {{ acc.method }}
                          </span>
                          <span class="text-white font-black text-xs truncate">{{ acc.name }}</span>
                        </div>
                        <p class="text-[11px] font-mono text-slate-400 mt-1 select-all truncate">{{ acc.details }}</p>
                      </div>

                      <div class="flex items-center gap-2 shrink-0">
                        <button @click="editAccount(accIdx)" class="h-8 w-8 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl flex items-center justify-center transition active:scale-95" title="Edit Account">
                          <i class="fa-solid fa-pen text-xs"></i>
                        </button>
                        <button @click="deleteAccount(accIdx)" class="h-8 w-8 bg-rose-600 hover:bg-rose-500 text-white rounded-xl flex items-center justify-center transition active:scale-95" title="Delete Account">
                          <i class="fa-solid fa-trash text-xs"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- CARD 2: WITHDRAW FUNDS (MIN 150 TK) -->
            <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-xl space-y-5 hover-card select-none">
              <div class="flex items-center gap-2.5 border-b border-slate-800/80 pb-3">
                <i class="fa-solid fa-money-bill-transfer text-amber-400 text-base"></i>
                <h3 class="font-extrabold text-sm text-white">Withdraw Funds</h3>
              </div>
              
              <div class="space-y-4 text-xs font-sans">
                <div>
                  <label class="text-slate-400 font-bold uppercase text-[10px] tracking-wider block mb-1.5">Select Your Account</label>
                  <select v-model="selectedSavedAccountIndex" class="w-full p-3.5 bg-slate-950 border border-slate-800 text-white rounded-2xl outline-none focus:border-indigo-500 transition font-bold">
                    <option value="">Select Saved Account</option>
                    <option v-for="(acc, idx) in userSavedAccounts" :key="idx" :value="idx">
                      {{ acc.method }} - {{ acc.details }} ({{ acc.name }})
                    </option>
                  </select>
                </div>

                <div>
                  <label class="text-slate-400 font-bold uppercase text-[10px] tracking-wider block mb-1.5">Amount (৳)</label>
                  <input type="number" step="1" v-model="withdrawAmount" placeholder="Min: ৳150, Max: ৳10000" class="w-full p-3.5 bg-slate-950 border border-slate-800 text-white rounded-2xl font-mono focus:border-indigo-500 transition font-bold placeholder-slate-600" />
                </div>

                <div v-if="profile?.withdraw_pin">
                  <label class="text-slate-400 font-bold uppercase text-[10px] tracking-wider block mb-1.5">Secure Withdraw PIN (4 Digits)</label>
                  <input type="password" maxlength="4" v-model="withdrawPinInput" placeholder="e.g. 1234" class="w-full p-3.5 bg-slate-950 border border-slate-800 text-white rounded-2xl font-mono focus:border-indigo-500 transition font-bold placeholder-slate-600" />
                </div>

                <button @click="submitWithdrawFromSavedAccount" :disabled="selectedSavedAccountIndex === '' || !withdrawAmount || withdrawAmount < 150" class="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 disabled:opacity-50 text-slate-950 font-black py-4 rounded-2xl text-xs transition-all duration-200 shadow-xl active:scale-95 flex items-center justify-center gap-2">
                  <i class="fa-solid fa-hand-holding-dollar text-sm"></i>
                  <span>Withdraw Funds</span>
                </button>
              </div>
            </div>

            <!-- Withdraw History -->
            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-4 select-none">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-800 pb-3 font-sans">
                <h3 class="font-black text-xs text-white flex items-center gap-2">
                  <i class="fa-solid fa-history text-indigo-400"></i> Withdrawal History
                </h3>
                
                <div class="flex gap-1 bg-slate-950 p-1 rounded-xl text-[9px] font-bold select-none border border-slate-800">
                  <button v-for="mode in ['today', 'yesterday', '7days', 'lifetime']" :key="mode" @click="withdrawHistoryFilter = mode" :class="withdrawHistoryFilter === mode ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-400 hover:bg-slate-900'" class="px-2.5 py-1.5 rounded-lg uppercase tracking-wider transition">
                    {{ mode === '7days' ? '7 Days' : mode }}
                  </button>
                </div>
              </div>

              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs font-semibold">
                  <thead>
                    <tr class="text-slate-400 font-bold uppercase tracking-wider border-b border-slate-800">
                      <th class="py-2.5 font-bold">Date</th>
                      <th class="py-2.5 font-bold">Amount</th>
                      <th class="py-2.5 font-bold">Method</th>
                      <th class="py-2.5 font-bold">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="filteredWithdrawals.length === 0">
                      <td colspan="4" class="py-8 text-center text-slate-500 font-bold">No matching withdrawals found.</td>
                    </tr>
                    <tr v-else v-for="wd in filteredWithdrawals" :key="wd.id" class="border-b border-slate-800/80 hover:bg-slate-950/40 transition">
                      <td class="py-3 font-mono text-slate-400 text-[10px]">{{ formatTimestamp(wd.createdAt) }}</td>
                      <td class="py-3 font-black text-white font-bold font-mono">{{ formatBalance(wd.amount) }}</td>
                      <td class="py-3 uppercase text-indigo-400 font-bold">{{ wd.method }}</td>
                      <td class="py-3">
                        <span v-if="wd.status === 'approved'" class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Approved</span>
                        <span v-else-if="wd.status === 'pending'" class="bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Pending</span>
                        <span v-else class="bg-rose-500/20 text-rose-300 border border-rose-500/30 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Rejected</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
          </div>

          <!-- Shared Tab: Profile details (SCREENSHOT 3 FIXED + LARGER AVATAR & LOGOUT AT BOTTOM) -->
          <div v-if="currentTab === 'profile'" class="page-enter-active space-y-6 select-none font-semibold text-slate-300 font-sans">
            
            <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-lg flex flex-col sm:flex-row items-center gap-5 hover-card select-none">
              <!-- LARGER PROFILE PICTURE WITH UPLOAD TRIGGER -->
              <div class="relative group cursor-pointer" @click="triggerProfilePicUpload">
                <div class="h-24 w-24 rounded-full bg-indigo-600 border-2 border-indigo-400 flex items-center justify-center text-white font-black text-2xl shrink-0 overflow-hidden shadow-2xl">
                  <img v-if="userAvatarUrl" :src="userAvatarUrl" alt="Profile Avatar" class="h-full w-full object-cover" />
                  <span v-else>{{ user?.name ? user.name.slice(0, 2).toUpperCase() : 'US' }}</span>
                </div>
                <div class="absolute inset-0 bg-black/60 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <i class="fa-solid fa-camera text-white text-lg"></i>
                </div>
                <input type="file" ref="profilePicInput" @change="onProfilePicChange" accept="image/*" class="hidden" />
              </div>

              <div class="flex-1 text-center sm:text-left overflow-hidden select-none font-bold space-y-1.5">
                <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                  <p class="text-lg font-black text-white">{{ user?.name || 'User' }}</p>
                  <span class="bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-[9px] font-bold px-2.5 py-0.5 rounded-full uppercase">
                    MEMBER PORTAL
                  </span>
                </div>
                <p class="text-xs text-slate-400 truncate cursor-pointer hover:text-indigo-400 transition" @click="copyToClipboard(user?.email, 'Email Address Copied', 'profile_email')">{{ user?.email }}</p>
                <button @click="triggerProfilePicUpload" class="text-xs text-indigo-400 hover:text-indigo-300 font-bold flex items-center justify-center sm:justify-start gap-1 pt-1">
                  <i class="fa-solid fa-upload text-xs"></i> Upload Profile Picture
                </button>
              </div>
            </div>

            <div class="bg-slate-900/90 p-6 rounded-3xl border border-slate-800/80 shadow-lg space-y-4 text-xs hover-card select-none">
              <h3 class="font-bold text-white border-b border-slate-800 pb-2 font-sans">My Profile Settings</h3>
              
              <div class="space-y-4 font-sans text-xs">
                <!-- DISPLAY CURRENCY SELECTOR -->
                <div>
                  <label class="text-slate-400 uppercase text-[10px] tracking-wider font-bold block mb-1.5">Display Currency Mode</label>
                  <select v-model="currencyMode" class="w-full p-3.5 bg-slate-950 border border-slate-800 text-white rounded-xl outline-none focus:border-indigo-500 transition font-bold">
                    <option value="BDT">BDT (৳) - Bangladeshi Taka</option>
                    <option value="USD">USD ($) - US Dollar ($1 = ৳100)</option>
                  </select>
                </div>

                <div>
                  <label class="text-slate-400 uppercase text-[10px] tracking-wider font-bold">User UID (Read-Only)</label>
                  <input type="text" readonly :value="profile?.uid" class="w-full mt-1.5 p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 font-mono" />
                </div>
                <div>
                  <label class="text-slate-400 uppercase text-[10px] tracking-wider font-bold">Email Address (Read-Only)</label>
                  <input type="text" readonly :value="profile?.email" class="w-full mt-1.5 p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 font-mono" />
                </div>
                
                <!-- ACCOUNT WALLET BALANCE BOX -->
                <div>
                  <label class="text-slate-400 uppercase text-[10px] tracking-wider font-bold">Account Wallet Balance</label>
                  <div class="w-full mt-1.5 p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-emerald-400 font-mono font-bold text-sm flex items-center justify-between">
                    <span>{{ formatBalance(profile?.balance) }}</span>
                    <span class="text-[10px] text-slate-500 font-sans uppercase">Withdrawable</span>
                  </div>
                </div>

                <div>
                  <label class="text-slate-400 uppercase text-[10px] tracking-wider font-bold">Telegram Username</label>
                  <input type="text" v-model="profileTelegramUsername" placeholder="e.g. @MinoXSupport0" class="w-full mt-1.5 p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-bold focus:border-indigo-500 transition outline-none" />
                </div>

                <button @click="saveProfileChanges" :disabled="profileTelegramLoading" class="bg-indigo-600 hover:bg-indigo-500 text-white font-black px-6 py-3.5 rounded-2xl text-xs tracking-wider transition active:scale-95 disabled:bg-slate-800 font-bold">
                  {{ profileTelegramLoading ? 'Saving...' : 'Save Profile Changes' }}
                </button>
              </div>
            </div>

            <!-- API ACCESS KEY MANAGEMENT CARD (INSTANT REGENERATE NO RE-APPROVAL NEEDED) -->
            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-4 text-xs hover-card select-none">
              <h3 class="font-bold text-white border-b border-slate-800 pb-2 font-sans">API Key Lifecycle & Security</h3>
              
              <div class="space-y-4 font-semibold text-slate-300">
                <p class="text-slate-400">ID Code / Unique Identifier: <span class="text-white font-bold ml-1 font-mono select-all font-mono cursor-pointer hover:text-indigo-400" @click="copyToClipboard(profile?.id_code, 'ID Code Copied', 'id_prof')">{{ profile ? profile.id_code : 'N/A' }}</span></p>
                
                <div class="space-y-3">
                  <div v-if="profile && profile.api_key" class="space-y-3">
                    <p class="text-slate-400 font-sans">Active API Key:</p>
                    
                    <div class="flex flex-col gap-2 font-sans">
                      <span class="text-emerald-400 font-mono text-[10px] bg-slate-950 px-3.5 py-2.5 rounded-xl border border-slate-800 break-all select-all font-semibold flex items-center justify-between gap-1.5 font-mono">
                        <span>{{ profile.api_key }}</span>
                        <button @click="copyToClipboard(profile.api_key, 'API Key Copied', 'profile_key')" class="text-indigo-400 hover:text-indigo-300 text-xs flex items-center gap-1 font-bold shrink-0">
                          <i class="fa-regular" :class="copiedStates['profile_key'] ? 'fa-circle-check text-emerald-400 scale-125' : 'fa-copy'"></i>
                        </button>
                      </span>
                      
                      <div class="flex items-center gap-2">
                        <span v-if="profile.api_key_approved" class="text-emerald-400 text-[10px]">
                          <i class="fa-solid fa-circle-check"></i> Key Active & Approved
                        </span>
                        <span v-else class="text-amber-400 text-[10px]">
                          <i class="fa-solid fa-clock"></i> Pending Admin Approval
                        </span>
                      </div>
                    </div>

                    <!-- API KEY CONTROLS -->
                    <div class="flex flex-wrap gap-2 pt-1">
                      <button @click="handleRegenerateApiKey" :disabled="apiGenLoading" class="bg-indigo-600 hover:bg-indigo-500 text-white font-black px-4 py-2.5 rounded-xl text-[11px] transition active:scale-95 disabled:bg-slate-800 flex items-center gap-1.5">
                        <i class="fa-solid fa-arrows-rotate"></i> Regenerate Key
                      </button>
                      
                      <button @click="handleRevokeApiKey" :disabled="apiGenLoading" class="bg-rose-600 hover:bg-rose-500 text-white font-black px-4 py-2.5 rounded-xl text-[11px] transition active:scale-95 disabled:bg-slate-800 flex items-center gap-1.5">
                        <i class="fa-solid fa-ban"></i> Revoke Key
                      </button>
                    </div>
                  </div>
                  
                  <div v-else class="space-y-2 select-none font-sans">
                    <p class="text-amber-400 text-[10px] font-bold"><i class="fa-solid fa-triangle-exclamation"></i> No active API key found. Generate your API key below.</p>
                    <button @click="handleGenerateApiKey" :disabled="apiGenLoading" class="bg-emerald-600 hover:bg-emerald-500 text-white font-black px-4 py-2.5 rounded-2xl text-[11px] tracking-wider transition active:scale-95 disabled:bg-slate-800">
                      {{ apiGenLoading ? 'Generating...' : 'GENERATE API KEY' }}
                    </button>
                  </div>
                </div>

              </div>
            </div>

            <!-- Assigned Agent Info Card -->
            <div class="bg-slate-900/90 p-5 rounded-3xl border border-slate-800/80 shadow-lg space-y-4 hover-card select-none font-sans">
              <h3 class="font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <i class="fa-solid fa-user-tie text-indigo-400"></i> Your Assigned Agent
              </h3>
              <div class="space-y-3 font-semibold text-slate-300">
                <div class="flex justify-between items-center text-xs">
                  <span class="text-slate-404">Agent Name</span>
                  <span class="text-white font-bold font-sans">Official Agent</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-slate-404">Agent Email</span>
                  <span class="text-indigo-400 font-mono select-all font-bold cursor-pointer hover:underline" @click="copyToClipboard('official@minosms.xyz', 'Agent Email Copied', 'agent_email')">official@minosms.xyz</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-slate-404">Agent Telegram</span>
                  <div class="flex items-center gap-1.5">
                    <span class="text-white font-bold font-mono">@MinoXSupport0</span>
                    <button @click="copyToClipboard('@MinoXSupport0', 'Telegram Handle Copied', 'agent_tele')" class="bg-indigo-950/80 border border-indigo-800/50 hover:bg-indigo-900/80 text-indigo-300 font-black px-2.5 py-1 rounded-lg text-[9px] uppercase tracking-wide flex items-center gap-1">
                      <i class="fa-regular fa-copy"></i> Copy
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- LOGOUT BUTTON AT BOTTOM OF PROFILE PAGE -->
            <div class="pt-2">
              <button @click="signOut" class="w-full bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 text-rose-400 font-black py-4 rounded-2xl text-xs transition active:scale-95 flex items-center justify-center gap-2 shadow-lg">
                <i class="fa-solid fa-right-from-bracket"></i>
                <span>LOGOUT ACCOUNT</span>
              </button>
            </div>

          </div>

        </div>

      </main>
    </div>

  </div>

  <script>
    const { createApp, ref, onMounted, computed, watch } = Vue;

    try {
      createApp({
        setup() {
          const userLoaded = ref(true); 
          const user = ref(null);
          const profile = ref(null);
          const authName = ref('');
          const authEmail = ref('');
          const authPassword = ref('');
          const authAgentEmail = ref(''); 
          const authTelegramUsername = ref(''); 
          const isRegistering = ref(false);
          const authLoading = ref(false);

          // Currency Mode State ('BDT' or 'USD')
          const currencyMode = ref(localStorage.getItem('mino_currency_mode') || 'BDT');

          watch(currencyMode, (newMode) => {
            localStorage.setItem('mino_currency_mode', newMode);
          });

          // Currency Formatter ($1 = ৳100)
          const formatBalance = (amount) => {
            const val = parseFloat(amount || 0);
            if (currencyMode.value === 'USD') {
              return '$' + (val / 100).toFixed(2);
            }
            return '৳' + val.toFixed(2);
          };

          // Name Masking Helper for Leaderboard (e.g. "Minhaz" -> "Mi***az")
          const maskName = (name) => {
            if (!name) return 'An***ym';
            const str = String(name).trim();
            if (str.length <= 4) {
              return str.substring(0, 1) + '***' + str.substring(str.length - 1);
            }
            return str.substring(0, 2) + '***' + str.substring(str.length - 2);
          };

          // Live Bangladesh Time Clock
          const liveBangladeshTime = ref('');
          const updateBangladeshTime = () => {
            const now = new Date();
            const options = {
              timeZone: 'Asia/Dhaka',
              weekday: 'short',
              day: '2-digit',
              month: 'short',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: true
            };
            liveBangladeshTime.value = new Intl.DateTimeFormat('en-US', options).format(now);
          };

          // Avatar Image State
          const userAvatarUrl = ref(localStorage.getItem('mino_user_avatar') || '');
          const profilePicInput = ref(null);

          // Telegram Modal & How to Use Guide States
          const showTelegramModal = ref(false);
          const promptTelegramUsername = ref('');
          const showGuideModal = ref(false);
          const guideLang = ref('bn');

          // Saved Accounts & Manage Accounts System States
          const userSavedAccounts = ref([]);
          const newAccMethod = ref('');
          const newAccName = ref('');
          const newAccDetails = ref('');
          const selectedSavedAccountIndex = ref('');
          const editingAccountIndex = ref(null);

          const captchaNum1 = ref(0);
          const captchaNum2 = ref(0);
          const captchaAnswerInput = ref('');
          const failedCaptchaCount = ref(parseInt(localStorage.getItem('mino_captcha_fails') || '0'));
          const captchaLockoutUntil = ref(parseInt(localStorage.getItem('mino_captcha_lockout') || '0'));

          const generateCaptcha = () => {
            captchaNum1.value = Math.floor(Math.random() * 8) + 1;
            captchaNum2.value = Math.floor(Math.random() * 8) + 1;
            captchaAnswerInput.value = '';
          };

          const currentTab = ref('dashboard');
          const announcement = ref('');
          const mobileMenuOpen = ref(false);

          const urlParams = new URLSearchParams(window.location.search);
          const urlRid = urlParams.get('rid');
          const savedRid = localStorage.getItem('mino_last_rid');
          const rid = ref(urlRid || savedRid || '880X01');

          watch(rid, (newVal) => {
            if (newVal) {
              localStorage.setItem('mino_last_rid', newVal.trim());
            }
          });

          const nationalFormat = ref(true); 
          const removePlus = ref(true);     
          
          const activeNumber = ref(null);
          const activeCountry = ref('');
          const activeOperator = ref('');
          const otpResult = ref(null);
          const loadingNumber = ref(false);
          const isRefreshingAllocations = ref(false);
          const liveLogs = ref([]);
          const successOtps = ref([]);
          
          const walletAddressInput = ref('');
          const walletLoading = ref(false);
          const apiGenLoading = ref(false);

          const searchQuery = ref('');

          const getInitialAllocations = () => {
            try {
              const cached = localStorage.getItem('mino_cached_allocations');
              if (cached) {
                const parsed = JSON.parse(cached);
                if (Array.isArray(parsed)) return parsed;
              }
            } catch (e) {}
            return [];
          };

          const allocations = ref(getInitialAllocations());
          const currentPage = ref(1);
          const itemsPerPage = 200;

          const showToast = ref(false);
          const toastTitle = ref('Notification');
          const toastMessage = ref('');
          
          let generalTimer = null;
          let consoleTimer = null;
          let liveAccessTimer = null;
          let pollingActive = true;

          const knownCompletedIds = new Set();
          let isInitialCompletedLoad = true;

          const apiBaseUrl = ref(window.location.origin);
          const selectedTestApi = ref('getnum');
          const testRange = ref('880X01');
          const testApiLoading = ref(false);
          const testApiResponse = ref(null);

          const barColors = ['bg-indigo-500', 'bg-[#1877F2]', 'bg-[#25D366]', 'bg-[#24A1DE]'];
          const dotColors = ['bg-indigo-500', 'bg-[#1877F2]', 'bg-[#25D366]', 'bg-[#24A1DE]'];

          const leaderboardTab = ref('today');
          const leaderboardData = ref({ today: [], weekly: [], lifetime: [] });
          const personalRank = ref(0);
          const personalOtpCount = ref(0);

          const withdrawAmount = ref('');
          const withdrawMethod = ref('');
          const withdrawPinInput = ref('');
          const withdrawalsHistory = ref([]);
          const withdrawHistoryFilter = ref('lifetime');
          const withdrawalMethods = ref([]);

          const summaryFilter = ref('lifetime');

          const serviceRates = ref({
            facebook: { rate: 0.40, status: 'ON' },
            instagram: { rate: 0.40, status: 'ON' },
            whatsapp: { rate: 0.00, status: 'OFF' },
            telegram: { rate: 0.00, status: 'OFF' },
            google: { rate: 0.40, status: 'ON' },
            generic: { rate: 0.40, status: 'ON' }
          });

          const liveAccessSearchQuery = ref('');
          const openAccordions = ref({});
          const serverLiveAccessServices = ref([]);
          const liveAccessLoading = ref(false);

          const profileTelegramUsername = ref('');
          const profileTelegramLoading = ref(false);

          const copiedStates = ref({});

          const countryPrefixes = {
            "1": { name: "USA/Canada", flag: "🇺🇸" },
            "7": { name: "Russia/Kazakhstan", flag: "🇷🇺" },
            "20": { name: "Egypt", flag: "🇪🇬" },
            "212": { name: "Morocco", flag: "🇲🇦" },
            "213": { name: "Algeria", flag: "🇩🇿" },
            "216": { name: "Tunisia", flag: "🇹🇳" },
            "218": { name: "Libya", flag: "🇱🇾" },
            "220": { name: "Gambia", flag: "🇬🇲" },
            "221": { name: "Senegal", flag: "🇸🇳" },
            "222": { name: "Mauritania", flag: "🇲🇷" },
            "223": { name: "Mali", flag: "🇲🇱" },
            "224": { name: "Guinea", flag: "🇬🇳" },
            "225": { name: "Ivory Coast", flag: "🇨🇮" },
            "226": { name: "Burkina Faso", flag: "🇧🇫" },
            "227": { name: "Niger", flag: "🇳🇪" },
            "228": { name: "Togo", flag: "🇹🇬" },
            "229": { name: "Benin", flag: "🇧🇯" },
            "230": { name: "Mauritius", flag: "🇲🇺" },
            "231": { name: "Liberia", flag: "🇱🇷" },
            "232": { name: "Sierra Leone", flag: "🇸🇱" },
            "233": { name: "Ghana", flag: "🇬🇭" },
            "234": { name: "Nigeria", flag: "🇳🇬" },
            "235": { name: "Chad", flag: "🇹🇩" },
            "237": { name: "Cameroon", flag: "🇨🇲" },
            "241": { name: "Gabon", flag: "🇬🇦" },
            "242": { name: "Congo", flag: "🇨🇬" },
            "243": { name: "DR Congo", flag: "🇨🇩" },
            "244": { name: "Angola", flag: "🇦🇴" },
            "245": { name: "Guinea-Bissau", flag: "🇬🇼" },
            "249": { name: "Sudan", flag: "🇸🇩" },
            "250": { name: "Rwanda", flag: "🇷🇼" },
            "251": { name: "Ethiopia", flag: "🇪🇹" },
            "252": { name: "Somalia", flag: "🇸🇴" },
            "254": { name: "Kenya", flag: "🇰🇪" },
            "255": { name: "Tanzania", flag: "🇹🇿" },
            "256": { name: "Uganda", flag: "🇺🇬" },
            "257": { name: "Burundi", flag: "🇧🇮" },
            "258": { name: "Mozambique", flag: "🇲🇿" },
            "260": { name: "Zambia", flag: "🇿🇲" },
            "261": { name: "Madagascar", flag: "🇲🇬" },
            "263": { name: "Zimbabwe", flag: "🇿🇼" },
            "30": { name: "Greece", flag: "🇬🇷" },
            "31": { name: "Netherlands", flag: "🇳🇱" },
            "32": { name: "Belgium", flag: "🇧🇪" },
            "33": { name: "France", flag: "🇫🇷" },
            "34": { name: "Spain", flag: "🇪🇸" },
            "351": { name: "Portugal", flag: "🇵🇹" },
            "358": { name: "Finland", flag: "🇫🇮" },
            "370": { name: "Lithuania", flag: "🇱🇹" },
            "371": { name: "Latvia", flag: "🇱🇻" },
            "372": { name: "Estonia", flag: "🇪🇪" },
            "374": { name: "Armenia", flag: "🇦🇲" },
            "375": { name: "Belarus", flag: "🇧🇾" },
            "380": { name: "Ukraine", flag: "🇺🇦" },
            "40": { name: "Romania", flag: "🇷🇴" },
            "41": { name: "Switzerland", flag: "🇨🇭" },
            "43": { name: "Austria", flag: "🇦🇹" },
            "44": { name: "United Kingdom", flag: "🇬🇧" },
            "45": { name: "Denmark", flag: "🇩🇰" },
            "46": { name: "Sweden", flag: "🇸🇪" },
            "47": { name: "Norway", flag: "🇳🇴" },
            "48": { name: "Poland", flag: "🇵🇱" },
            "49": { name: "Germany", flag: "🇩🇪" },
            "51": { name: "Peru", flag: "🇵🇪" },
            "52": { name: "Mexico", flag: "🇲🇽" },
            "54": { name: "Argentina", flag: "🇦🇷" },
            "55": { name: "Brazil", flag: "🇧🇷" },
            "56": { name: "Chile", flag: "🇨🇱" },
            "57": { name: "Colombia", flag: "🇨🇴" },
            "60": { name: "Malaysia", flag: "🇲🇾" },
            "61": { name: "Australia", flag: "🇦🇺" },
            "62": { name: "Indonesia", flag: "🇮🇩" },
            "63": { name: "Philippines", flag: "🇵🇭" },
            "65": { name: "Singapore", flag: "🇸🇬" },
            "66": { name: "Thailand", flag: "🇹🇭" },
            "81": { name: "Japan", flag: "🇯🇵" },
            "82": { name: "South Korea", flag: "🇰🇷" },
            "84": { name: "Vietnam", flag: "🇻🇳" },
            "880": { name: "Bangladesh", flag: "🇧🇩" },
            "90": { name: "Turkey", flag: "🇹🇷" },
            "91": { name: "India", flag: "🇮🇳" },
            "92": { name: "Pakistan", flag: "🇵🇰" },
            "93": { name: "Afghanistan", flag: "🇦🇫" },
            "94": { name: "Sri Lanka", flag: "🇱🇰" },
            "95": { name: "Myanmar", flag: "🇲🇲" },
            "961": { name: "Lebanon", flag: "🇱🇧" },
            "962": { name: "Jordan", flag: "🇯🇴" },
            "963": { name: "Syria", flag: "🇸🇾" },
            "964": { name: "Iraq", flag: "🇮🇶" },
            "965": { name: "Kuwait", flag: "🇰🇼" },
            "966": { name: "Saudi Arabia", flag: "🇸🇦" },
            "971": { name: "UAE", flag: "🇦🇪" },
            "972": { name: "Israel", flag: "🇮🇱" },
            "974": { name: "Qatar", flag: "🇶🇦" },
            "977": { name: "Nepal", flag: "🇳🇵" },
            "992": { name: "Tajikistan", flag: "🇹🇯" },
            "993": { name: "Turkmenistan", flag: "🇹🇲" },
            "994": { name: "Azerbaijan", flag: "🇦🇿" },
            "995": { name: "Georgia", flag: "🇬🇪" },
            "996": { name: "Kyrgyzstan", flag: "🇰🇬" },
            "998": { name: "Uzbekistan", flag: "🇺🇿" }
          };

          // Profile Picture Upload Handler
          const triggerProfilePicUpload = () => {
            if (profilePicInput.value) {
              profilePicInput.value.click();
            }
          };

          const onProfilePicChange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            if (file.size > 3 * 1024 * 1024) {
              alert("Image size should be less than 3MB.");
              return;
            }
            const reader = new FileReader();
            reader.onload = (event) => {
              userAvatarUrl.value = event.target.result;
              localStorage.setItem('mino_user_avatar', event.target.result);
              triggerToast("Profile picture updated!", "Avatar Updated");
            };
            reader.readAsDataURL(file);
          };

          const decodeHtml = (html) => {
            if (!html) return '';
            const txt = document.createElement("textarea");
            txt.innerHTML = html;
            return txt.value;
          };

          let audioCtx = null;
          const playBeep = () => {
            try {
              if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
              }
              if (audioCtx.state === 'suspended') {
                audioCtx.resume();
              }
              const osc = audioCtx.createOscillator();
              const gain = audioCtx.createGain();
              osc.connect(gain);
              gain.connect(audioCtx.destination);
              osc.type = "sine";
              osc.frequency.setValueAtTime(880, audioCtx.currentTime); 
              gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
              osc.start();
              osc.stop(audioCtx.currentTime + 0.18); 
            } catch (e) {}
          };

          const toggleServiceAccordion = (svcName) => {
            openAccordions.value[svcName] = !openAccordions.value[svcName];
          };

          const isAccordionOpen = (svcName) => {
            return !!openAccordions.value[svcName];
          };

          // HIGH RESOLUTION DYNAMIC LOGO ENGINE (FB, INSTAGRAM, WHATSAPP FIX)
          const getServiceLogoUrl = (name) => {
            if (!name) return 'https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg';
            let n = String(name).toLowerCase().trim();
            if (n.includes('facebook') || n === 'fb') return 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/facebook/facebook-original.svg';
            if (n.includes('instagram') || n === 'ig') return 'https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg';
            if (n.includes('whatsapp') || n === 'wa') return 'https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg';
            if (n.includes('telegram') || n === 'tg') return 'https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg';
            if (n.includes('google') || n.includes('gmail')) return 'https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg';
            if (n.includes('tiktok')) return 'https://upload.wikimedia.org/wikipedia/en/a/a9/TikTok_logo.svg';
            if (n.includes('binance')) return 'https://upload.wikimedia.org/wikipedia/commons/1/12/Binance_logo.svg';
            if (n.includes('netflix')) return 'https://assets.nflxext.com/us/ffe/siteui/common/icons/nficon2016.ico';
            if (n.includes('twitter') || n === 'x') return 'https://upload.wikimedia.org/wikipedia/commons/c/ce/X_logo_2023.svg';
            
            const domain = getServiceDomain(name);
            return `https://www.google.com/s2/favicons?domain=${domain}&sz=128`;
          };

          const getServiceDomain = (name) => {
            if (!name) return 'google.com';
            let n = String(name).toLowerCase().trim();
            if (n.includes('telegram') || n === 'tg') return 'telegram.org';
            if (n.includes('whatsapp') || n === 'wa') return 'whatsapp.com';
            if (n.includes('facebook') || n === 'fb') return 'facebook.com';
            if (n.includes('instagram') || n === 'ig') return 'instagram.com';
            if (n.includes('google') || n.includes('gmail')) return 'google.com';
            if (n.includes('tiktok')) return 'tiktok.com';
            if (n.includes('binance')) return 'binance.com';
            if (n.includes('imo')) return 'imo.im';
            if (n.includes('netflix')) return 'netflix.com';
            if (n.includes('uber')) return 'uber.com';
            if (n.includes('snapchat')) return 'snapchat.com';
            if (n.includes('discord')) return 'discord.com';
            if (n.includes('steam')) return 'steampowered.com';
            if (n.includes('twitter') || n === 'x') return 'x.com';
            if (n.includes('tinder')) return 'tinder.com';
            if (n.includes('viber')) return 'viber.com';
            if (n.includes('line')) return 'line.me';
            return 'google.com';
          };

          const getServiceIcon = (name) => {
            if (!name) return 'fa-solid fa-comment-sms';
            const n = String(name).toLowerCase();
            if (n.includes('facebook') || n.includes('fb')) return 'fa-brands fa-facebook-f';
            if (n.includes('instagram') || n.includes('ig')) return 'fa-brands fa-instagram';
            if (n.includes('whatsapp') || n.includes('wa')) return 'fa-brands fa-whatsapp';
            if (n.includes('telegram') || n.includes('tg')) return 'fa-brands fa-telegram';
            if (n.includes('google') || n.includes('g-')) return 'fa-brands fa-google';
            return 'fa-solid fa-comment-sms';
          };

          const getServiceIconBg = (name) => {
            if (!name) return 'bg-indigo-600 text-white';
            const n = String(name).toLowerCase();
            if (n.includes('facebook') || n.includes('fb')) return 'bg-[#1877F2] text-white';
            if (n.includes('instagram') || n.includes('ig')) return 'bg-gradient-to-tr from-[#f09433] via-[#dc2743] to-[#bc1888] text-white';
            if (n.includes('whatsapp') || n.includes('wa')) return 'bg-[#25D366] text-white';
            if (n.includes('telegram') || n.includes('tg')) return 'bg-[#24A1DE] text-white';
            if (n.includes('google') || n.includes('g-')) return 'bg-[#4285F4] text-white';
            return 'bg-indigo-600 text-white';
          };

          // REAL COUNTRY NAME & FLAG LOOKUP ENGINE
          const getCountryName = (range) => {
            if (!range) return 'International';
            const clean = String(range).replace(/[^0-9]/g, '');
            for (let len = 4; len >= 1; len--) {
              const prefix = clean.substring(0, len);
              if (countryPrefixes[prefix]) {
                return countryPrefixes[prefix].name;
              }
            }
            return 'International';
          };

          const getCountryFlag = (range) => {
            if (!range) return '🌐';
            const clean = String(range).replace(/[^0-9]/g, '');
            for (let len = 4; len >= 1; len--) {
              const prefix = clean.substring(0, len);
              if (countryPrefixes[prefix]) {
                return countryPrefixes[prefix].flag;
              }
            }
            return '🌐';
          };

          const fetchLiveAccessData = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            liveAccessLoading.value = true;
            try {
              const res = await fetch('user_api.php?action=live-access', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data && data.data && Array.isArray(data.data.services)) {
                serverLiveAccessServices.value = data.data.services.map(svc => ({
                  name: svc.sid || 'Generic',
                  ranges: (svc.ranges || []).map(rCode => ({
                    code: rCode,
                    country: getCountryName(rCode)
                  })),
                  totalHits: (svc.ranges || []).length
                }));
              }
            } catch (e) {}
            liveAccessLoading.value = false;
          };

          const liveAccessData = computed(() => {
            if (Array.isArray(serverLiveAccessServices.value) && serverLiveAccessServices.value.length > 0) {
              return serverLiveAccessServices.value;
            }
            return [];
          });

          const activeRangesCount = computed(() => {
            let total = 0;
            if (Array.isArray(liveAccessData.value)) {
              liveAccessData.value.forEach(s => {
                if (s && Array.isArray(s.ranges)) total += s.ranges.length;
              });
            }
            return total;
          });

          const filteredLiveAccessServices = computed(() => {
            const list = Array.isArray(liveAccessData.value) ? liveAccessData.value : [];
            const q = liveAccessSearchQuery.value ? liveAccessSearchQuery.value.toLowerCase().trim() : '';
            if (!q) return list;
            return list.filter(svc => 
              svc && svc.name && svc.name.toLowerCase().includes(q)
            );
          });

          const serviceDemandChartStyle = computed(() => {
            return { background: 'conic-gradient(#6366f1 0% 100%)' };
          });

          const getOtpsList = (alloc) => {
            if (!alloc || !alloc.otp) return [];
            return String(alloc.otp).split(/[\s,;/]+/).filter(x => x.trim().length > 0);
          };

          const triggerToast = (msg, title = "Notification") => {
            toastTitle.value = title;
            toastMessage.value = msg;
            showToast.value = true;
            setTimeout(() => {
              showToast.value = false;
            }, 2800);
          };

          const pasteFromClipboard = async () => {
            try {
              if (navigator.clipboard && navigator.clipboard.readText) {
                const text = await navigator.clipboard.readText();
                if (text && text.trim()) {
                  rid.value = text.trim();
                  triggerToast(text.trim(), "Pasted Range ID");
                }
              }
            } catch (err) {}
          };

          // KEYBOARD GLITCH FREE COPY FUNCTION
          const copyToClipboard = (text, titleDesc = "Copied to Clipboard", key = null) => {
            if (!text) return;

            const doSuccess = () => {
              triggerToast(text, titleDesc);
              if (key) {
                copiedStates.value[key] = true;
                setTimeout(() => { copiedStates.value[key] = false; }, 2000);
              }
            };

            if (navigator.clipboard && window.isSecureContext) {
              navigator.clipboard.writeText(text).then(() => {
                doSuccess();
              }).catch(() => {
                fallbackCopyText(text, doSuccess);
              });
            } else {
              fallbackCopyText(text, doSuccess);
            }
          };

          const fallbackCopyText = (text, onSuccess) => {
            try {
              const textArea = document.createElement("textarea");
              textArea.value = text;
              textArea.setAttribute("readonly", "");
              textArea.style.position = "fixed";
              textArea.style.left = "-999999px";
              textArea.style.top = "-999999px";
              document.body.appendChild(textArea);
              
              const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
              if (!isMobile) {
                textArea.focus();
              }
              
              textArea.select();
              textArea.setSelectionRange(0, 999999);
              const successful = document.execCommand('copy');
              document.body.removeChild(textArea);
              if (successful) onSuccess();
            } catch (err) {
              onSuccess();
            }
          };

          const navigateMobile = (tabName) => {
            currentTab.value = tabName;
            mobileMenuOpen.value = false;
          };

          const filterByDate = (items, filterType, dateKey = 'createdAt') => {
            if (!Array.isArray(items)) return [];
            return items;
          };

          const filteredAllocations = computed(() => {
            if (!Array.isArray(allocations.value)) return [];
            const q = (searchQuery.value || '').toLowerCase().trim();
            if (!q) return allocations.value;
            return allocations.value.filter(alloc => 
              alloc && alloc.number && String(alloc.number).includes(q)
            );
          });

          const activeAllocationsCount = computed(() => {
            if (!Array.isArray(allocations.value)) return 0;
            return allocations.value.filter(a => a && a.status === 'active').length;
          });

          const paginatedAllocations = computed(() => {
            if (!Array.isArray(filteredAllocations.value)) return [];
            const start = (currentPage.value - 1) * itemsPerPage;
            return filteredAllocations.value.slice(start, start + itemsPerPage);
          });

          const totalPages = computed(() => {
            if (!Array.isArray(filteredAllocations.value)) return 1;
            return Math.ceil(filteredAllocations.value.length / itemsPerPage) || 1;
          });

          const prevPage = () => {
            if (currentPage.value > 1) currentPage.value--;
          };

          const nextPage = () => {
            if (currentPage.value < totalPages.value) currentPage.value++;
          };

          const fetchUserAllocationsOnly = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token || !profile.value) return;

            try {
              const allocRes = await fetch('user_api.php?action=user-allocations', {
                headers: { 
                  'Authorization': `Bearer ${token}`,
                  'X-MINO-API-KEY': profile.value.api_key || ''
                }
              });
              const allocData = await allocRes.json();
              if (allocData && allocData.status === 'success') {
                const fetchedAllocations = Array.isArray(allocData.allocations) ? allocData.allocations : [];
                
                let hasNewLiveOtp = false;
                let latestOtpMessage = '';

                fetchedAllocations.forEach(newAlloc => {
                  if (newAlloc && newAlloc.status === 'completed') {
                    const allocId = newAlloc.id || newAlloc.number;
                    if (!knownCompletedIds.has(allocId)) {
                      knownCompletedIds.add(allocId);
                      if (!isInitialCompletedLoad) {
                        hasNewLiveOtp = true;
                        latestOtpMessage = newAlloc.number + " · " + (newAlloc.otp || 'OTP Received');
                        newAlloc.justHit = true;
                        setTimeout(() => { newAlloc.justHit = false; }, 3000);
                      }
                    }
                  }
                });

                if (isInitialCompletedLoad) {
                  isInitialCompletedLoad = false;
                } else if (hasNewLiveOtp) {
                  playBeep();
                  triggerToast(latestOtpMessage, "🎉 New OTP Received");
                }

                allocations.value = fetchedAllocations;
                localStorage.setItem('mino_cached_allocations', JSON.stringify(fetchedAllocations));
                updateTimers();
              }
            } catch (e) {}
          };

          const refreshAllocations = async () => {
            if (isRefreshingAllocations.value) return;
            isRefreshingAllocations.value = true;
            await fetchUserAllocationsOnly();
            triggerToast("Allocations List Synced", "Refreshed");
            isRefreshingAllocations.value = false;
          };

          const updateTimers = () => {
            if (!Array.isArray(allocations.value)) return;
            allocations.value.forEach(alloc => {
              if (alloc && alloc.status === 'active') {
                const createdAt = alloc.createdAt ? new Date(alloc.createdAt) : null;
                if (createdAt && !isNaN(createdAt.getTime())) {
                  const elapsedSeconds = Math.floor((new Date() - createdAt) / 1000);
                  const remaining = Math.max(0, 1190 - elapsedSeconds);
                  alloc.timeLeft = remaining;
                  if (remaining === 0) alloc.status = 'expired';
                }
              }
            });
          };

          let isFetchingGeneral = false;
          let isFetchingConsole = false;
          let isFetchingLiveAccess = false;

          const pollGeneralData = async () => {
            if (!pollingActive || isFetchingGeneral) return;
            isFetchingGeneral = true;
            try {
              await fetchGeneralData();
            } catch (e) {
            } finally {
              isFetchingGeneral = false;
              if (pollingActive) generalTimer = setTimeout(pollGeneralData, 1000);
            }
          };

          const pollConsoleData = async () => {
            if (!pollingActive || isFetchingConsole) return;
            isFetchingConsole = true;
            try {
              await fetchConsoleData();
            } catch (e) {
            } finally {
              isFetchingConsole = false;
              if (pollingActive) consoleTimer = setTimeout(pollConsoleData, 2000);
            }
          };

          const pollLiveAccessData = async () => {
            if (!pollingActive || isFetchingLiveAccess) return;
            isFetchingLiveAccess = true;
            try {
              await fetchLiveAccessData();
            } catch (e) {
            } finally {
              isFetchingLiveAccess = false;
              if (pollingActive) liveAccessTimer = setTimeout(pollLiveAccessData, 6000);
            }
          };

          const startPolling = () => {
            stopPolling();
            pollingActive = true;
            pollGeneralData();
            pollConsoleData();
            pollLiveAccessData();
            fetchUserWithdrawals();
          };

          const stopPolling = () => {
            pollingActive = false;
            if (generalTimer) clearTimeout(generalTimer);
            if (consoleTimer) clearTimeout(consoleTimer);
            if (liveAccessTimer) clearTimeout(liveAccessTimer);
          };

          const mergeLogs = (newLogs) => {
            if (!Array.isArray(newLogs)) return;
            newLogs.forEach(newLog => {
              if (!newLog || !newLog.range) return;
              const key = `${newLog.range}_${newLog.service}_${newLog.time}`;
              const exists = liveLogs.value.some(existingLog => 
                existingLog && `${existingLog.range}_${existingLog.service}_${existingLog.time}` === key
              );
              if (!exists) liveLogs.value.unshift(newLog);
            });
            if (liveLogs.value.length > 150) liveLogs.value = liveLogs.value.slice(0, 150);
          };

          const topApps = computed(() => {
            const counts = {};
            let total = 0;
            const logs = Array.isArray(liveLogs.value) ? liveLogs.value : [];
            logs.forEach(log => {
              if (log) {
                const serviceName = log.service || 'SMS Service';
                counts[serviceName] = (counts[serviceName] || 0) + 1;
                total++;
              }
            });
            const list = Object.keys(counts).map(key => ({
              name: key,
              count: counts[key],
              percentage: total > 0 ? Math.round((counts[key] / total) * 100) : 0
            }));
            list.sort((a, b) => b.count - a.count);
            return { list: list.slice(0, 4), total };
          });

          const fetchConsoleData = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            try {
              const consoleRes = await fetch('main_api.php?action=live-console', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const consoleData = await consoleRes.json();
              if (consoleData && consoleData.status === 'success') {
                mergeLogs(consoleData.data);
              }
            } catch (e) {}
          };

          const fetchUserWithdrawals = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            try {
              const res = await fetch('user_api.php?action=user-withdrawals', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data && data.status === 'success') {
                withdrawalsHistory.value = data.withdrawals || [];
              }
            } catch (e) {}
          };

          const filteredWithdrawals = computed(() => withdrawalsHistory.value);
          const summaryStats = computed(() => ({ total: allocations.value.length, success: 0, failed: 0, successRate: '0.0', failRate: '0.0' }));

          // DASHBOARD REAL-TIME METRICS & TOP PERFORMERS
          const currentDateBadge = computed(() => {
            const now = new Date();
            const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const dayName = days[now.getDay()];
            const dateNum = String(now.getDate()).padStart(2, '0');
            const monthName = months[now.getMonth()];
            return `${dayName} - ${dateNum} ${monthName}`;
          });

          const todayOtps = computed(() => {
            const now = new Date();
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
            return (successOtps.value || []).filter(log => {
              if (!log.created_at) return true;
              return new Date(log.created_at).getTime() >= todayStart;
            });
          });

          const todayOtpsCount = computed(() => todayOtps.value.length);

          const todayEarnings = computed(() => {
            const rate = profile.value?.otp_rate || 0.40;
            return todayOtps.value.reduce((sum, log) => sum + (parseFloat(log.revenue_earned) || rate), 0);
          });

          const yesterdayOtps = computed(() => {
            const now = new Date();
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
            const yesterdayStart = todayStart - (24 * 60 * 60 * 1000);
            return (successOtps.value || []).filter(log => {
              if (!log.created_at) return false;
              const t = new Date(log.created_at).getTime();
              return t >= yesterdayStart && t < todayStart;
            });
          });

          const yesterdayOtpsCount = computed(() => yesterdayOtps.value.length);

          const yesterdayEarnings = computed(() => {
            const rate = profile.value?.otp_rate || 0.40;
            return yesterdayOtps.value.reduce((sum, log) => sum + (parseFloat(log.revenue_earned) || rate), 0);
          });

          const topPerformersList = computed(() => {
            const counts = {};
            (successOtps.value || []).forEach(log => {
              if (log && log.service) {
                const svc = log.service;
                counts[svc] = (counts[svc] || 0) + 1;
              }
            });
            const list = Object.keys(counts).map(svc => ({
              name: svc,
              count: counts[svc]
            }));
            list.sort((a, b) => b.count - a.count);
            return list;
          });

          // SAVED ACCOUNTS LOGIC
          const loadUserSavedAccounts = () => {
            if (!user.value || !user.value.uid) return;
            try {
              const saved = localStorage.getItem('mino_saved_accs_' + user.value.uid);
              if (saved) {
                userSavedAccounts.value = JSON.parse(saved);
              } else {
                userSavedAccounts.value = [];
              }
            } catch (e) {
              userSavedAccounts.value = [];
            }
          };

          const saveUserSavedAccountsToStorage = () => {
            if (!user.value || !user.value.uid) return;
            localStorage.setItem('mino_saved_accs_' + user.value.uid, JSON.stringify(userSavedAccounts.value));
          };

          const addOrUpdateAccount = () => {
            if (!newAccMethod.value || !newAccName.value.trim() || !newAccDetails.value.trim()) return;

            const accItem = {
              method: newAccMethod.value,
              name: newAccName.value.trim(),
              details: newAccDetails.value.trim()
            };

            if (editingAccountIndex.value !== null) {
              userSavedAccounts.value[editingAccountIndex.value] = accItem;
              triggerToast("Account Updated Successfully", "Manage Accounts");
              editingAccountIndex.value = null;
            } else {
              userSavedAccounts.value.push(accItem);
              triggerToast("New Account Added", "Manage Accounts");
            }

            saveUserSavedAccountsToStorage();
            newAccMethod.value = '';
            newAccName.value = '';
            newAccDetails.value = '';
          };

          const editAccount = (index) => {
            const acc = userSavedAccounts.value[index];
            if (!acc) return;
            newAccMethod.value = acc.method;
            newAccName.value = acc.name;
            newAccDetails.value = acc.details;
            editingAccountIndex.value = index;
          };

          const deleteAccount = (index) => {
            if (!confirm("Are you sure you want to delete this account?")) return;
            userSavedAccounts.value.splice(index, 1);
            saveUserSavedAccountsToStorage();
            if (selectedSavedAccountIndex.value === index) {
              selectedSavedAccountIndex.value = '';
            }
            triggerToast("Account Removed", "Manage Accounts");
          };

          const submitWithdrawFromSavedAccount = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;

            if (selectedSavedAccountIndex.value === '' || selectedSavedAccountIndex.value === null) {
              alert("Please select your withdrawal account.");
              return;
            }

            const acc = userSavedAccounts.value[selectedSavedAccountIndex.value];
            if (!acc) {
              alert("Selected account not found.");
              return;
            }

            if (!withdrawAmount.value || withdrawAmount.value < 150) {
              alert("মিনিমাম উইথড্র ১৫০ টাকা হতে হবে।");
              return;
            }

            try {
              const res = await fetch('user_api.php?action=withdraw', {
                method: 'POST',
                headers: { 
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                  amount: withdrawAmount.value,
                  method: acc.method,
                  address: `${acc.details} (${acc.name})`,
                  withdraw_pin: withdrawPinInput.value
                })
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast("৳" + withdrawAmount.value + " · " + acc.method, "Withdrawal Requested");
                withdrawAmount.value = '';
                withdrawPinInput.value = '';
                fetchGeneralData();
              } else {
                alert(data.message);
              }
            } catch (e) {
              alert("An error occurred while submitting withdrawal request.");
            }
          };

          const fetchGeneralData = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;

            try {
              const profileRes = await fetch('user_api.php?action=me', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              if (profileRes.ok) {
                const profileData = await profileRes.json();
                if (profileData && profileData.status === 'success') {
                  user.value = profileData.user;
                  profile.value = profileData.user;
                  announcement.value = profileData.announcement;
                  if (profileData.user.wallet_address && !walletAddressInput.value) {
                    walletAddressInput.value = profileData.user.wallet_address;
                  }

                  if (!profileData.user.telegram_username || profileData.user.telegram_username.trim() === '') {
                    showTelegramModal.value = true;
                  } else {
                    showTelegramModal.value = false;
                  }

                  loadUserSavedAccounts();
                }
              }
            } catch (e) {}

            fetchUserAllocationsOnly();
          };

          const saveTelegramFromModal = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token || !promptTelegramUsername.value.trim()) return;

            try {
              const res = await fetch('user_api.php?action=update-profile', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                  telegram_username: promptTelegramUsername.value.trim()
                })
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast("Telegram Username Saved!", "Profile Saved");
                showTelegramModal.value = false;
                fetchGeneralData();
              } else {
                alert(data.message);
              }
            } catch (e) {
              alert("Failed to save Telegram username.");
            }
          };

          const handleUpdateWallet = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token || !walletAddressInput.value.trim()) return;
            
            walletLoading.value = true;
            try {
              const res = await fetch('user_api.php?action=update-wallet', {
                method: 'POST',
                headers: { 
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ wallet_address: walletAddressInput.value })
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast("Wallet Address Updated", "Saved");
                fetchGeneralData();
              }
            } catch (e) {}
            walletLoading.value = false;
          };

          // API KEY LIFECYCLE HANDLERS (INSTANT REGENERATE NO RE-APPROVAL)
          const handleGenerateApiKey = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            apiGenLoading.value = true;
            try {
              const res = await fetch('user_api.php?action=generate-key', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast(data.message || "API Key Generated", "API Key Update");
                fetchGeneralData();
              } else {
                alert(data.message);
              }
            } catch (e) {
              alert("Failed to generate API Key.");
            }
            apiGenLoading.value = false;
          };

          const handleRegenerateApiKey = async () => {
            if (!confirm("Regenerating will instantly issue a new API key. Proceed?")) return;
            handleGenerateApiKey();
          };

          const handleRevokeApiKey = async () => {
            if (!confirm("Are you sure you want to revoke and disable your current API key?")) return;
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            apiGenLoading.value = true;
            try {
              const res = await fetch('user_api.php?action=generate-key', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast("API Key Revoked", "Security Alert");
                fetchGeneralData();
              }
            } catch (e) {}
            apiGenLoading.value = false;
          };

          const runLiveApiTest = async () => {};

          const handleAuth = async () => {
            authLoading.value = true;
            const url = isRegistering.value ? 'user_api.php?action=register' : 'user_api.php?action=login';
            const payload = isRegistering.value ? {
              name: authName.value,
              email: authEmail.value,
              password: authPassword.value,
              agent_email: authAgentEmail.value,
              telegram_username: authTelegramUsername.value
            } : {
              email: authEmail.value,
              password: authPassword.value
            };

            try {
              const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
              });
              const data = await res.json();
              if (data.status === 'success') {
                localStorage.setItem('mino_session_token', data.token);
                user.value = data.user;
                profile.value = data.user;
                triggerToast("Connected Successfully", isRegistering.value ? "Account Created" : "Logged In");
                await fetchGeneralData();
                startPolling();
              } else {
                alert(data.message || "Auth error");
              }
            } catch (e) {}
            authLoading.value = false;
          };

          const signOut = () => {
            stopPolling();
            localStorage.removeItem('mino_session_token');
            user.value = null;
            profile.value = null;
          };

          const handleGetNumber = async () => {
            loadingNumber.value = true;
            const token = localStorage.getItem('mino_session_token');
            
            if (document.activeElement) {
              document.activeElement.blur();
            }

            try {
              const res = await fetch('getnumber.php', {
                method: 'POST',
                headers: { 
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                  api_key: profile.value?.api_key || '',
                  rid: rid.value
                })
              });
              const data = await res.json();
              if (data.status === 'success' || data.success === true) {
                const num = data.number || data.data?.full_number;
                const newAlloc = {
                  id: data.id || ('alloc_' + Date.now()),
                  number: num,
                  rid: rid.value,
                  status: 'active',
                  country: data.country || 'Guinea',
                  operator: data.operator || 'Mobile',
                  createdAt: new Date().toISOString(),
                  timeLeft: 1190,
                  otp: '',
                  message: '',
                  justHit: false
                };
                allocations.value.unshift(newAlloc);
                copyToClipboard(num, "Number Copied: " + num, 'new_num_' + newAlloc.id);
                fetchGeneralData();
              } else {
                alert(data.message || "No numbers available");
              }
            } catch (e) {}
            loadingNumber.value = false;
          };

          const saveProfileChanges = async () => {};
          const formatTime = (s) => Math.floor(s/60) + ':' + (s%60 < 10 ? '0' : '') + (s%60);
          const formatTimestamp = (ts) => ts ? new Date(ts).toLocaleString() : 'N/A';

          onMounted(() => {
            userLoaded.value = true;
            generateCaptcha();
            updateBangladeshTime();
            setInterval(updateBangladeshTime, 1000);
            
            const token = localStorage.getItem('mino_session_token');
            if (token) startPolling();
            setInterval(updateTimers, 1000);
          });

          return {
            userLoaded, user, profile, authName, authEmail, authPassword, authAgentEmail, authTelegramUsername, isRegistering, authLoading,
            userAvatarUrl, profilePicInput, triggerProfilePicUpload, onProfilePicChange,
            showTelegramModal, promptTelegramUsername, saveTelegramFromModal,
            showGuideModal, guideLang,
            userSavedAccounts, newAccMethod, newAccName, newAccDetails, selectedSavedAccountIndex, editingAccountIndex,
            addOrUpdateAccount, editAccount, deleteAccount, submitWithdrawFromSavedAccount,
            currentDateBadge, liveBangladeshTime, todayEarnings, todayOtpsCount, yesterdayEarnings, yesterdayOtpsCount, topPerformersList,
            currencyMode, formatBalance, maskName,
            captchaNum1, captchaNum2, captchaAnswerInput, generateCaptcha, pasteFromClipboard,
            currentTab, announcement, mobileMenuOpen, navigateMobile, rid, nationalFormat, removePlus, activeNumber, activeCountry, activeOperator, otpResult, loadingNumber, isRefreshingAllocations, refreshAllocations, liveLogs, successOtps,
            allocations, currentPage, itemsPerPage, paginatedAllocations, totalPages, prevPage, nextPage, searchQuery, activeAllocationsCount,
            showToast, toastTitle, toastMessage, copyToClipboard, decodeHtml, walletAddressInput, walletLoading, handleUpdateWallet,
            handleAuth, signOut, handleGetNumber, formatTime, formatTimestamp,
            apiGenLoading, handleGenerateApiKey, handleRegenerateApiKey, handleRevokeApiKey, selectedTestApi, runLiveApiTest, testRange, testApiLoading, testApiResponse, apiBaseUrl,
            barColors, dotColors, topApps, leaderboardTab, leaderboardData, personalRank, personalOtpCount,
            withdrawAmount, withdrawMethod, withdrawalsHistory, withdrawHistoryFilter, filteredWithdrawals,
            summaryFilter, summaryStats, serviceRates,
            liveAccessSearchQuery, openAccordions, toggleServiceAccordion, isAccordionOpen,
serverLiveAccessServices, liveAccessLoading, fetchLiveAccessData, activeRangesCount,
            copiedStates,
            getServiceIcon, getServiceIconBg, getCountryName, getCountryFlag, filteredLiveAccessServices, serviceDemandChartStyle,
            countryPrefixes, getOtpsList, withdrawalMethods,
            profileTelegramUsername, profileTelegramLoading, saveProfileChanges, withdrawPinInput,
            getServiceLogoUrl
          };
        }
      }).mount('#app');
    } catch (e) {
      console.error("Vue Mount Error:", e);
    }
  </script>
</body>
</html>