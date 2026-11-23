<?php
require_once 'security.php';

// =========================================================================
// LOCAL API ROUTER FOR AGENT SPECIFIC ACTIONS
// =========================================================================
$action = isset($_GET['action']) ? $_GET['action'] : '';
if (!empty($action)) {
    if ($action === 'subuser-status') {
        $user = get_current_user_optimized();
        if (!$user || $user['role'] !== 'agent') {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized Access. Agent session required.']);
            exit();
        }
        $target_uid = isset($_GET['uid']) ? trim($_GET['uid']) : '';
        $pdo = get_db_connection();
        
        // Verify this sub-user belongs to the logged-in agent
        $stmtCheck = $pdo->prepare("SELECT * FROM users WHERE uid = ? AND agent_uid = ?");
        $stmtCheck->execute([$target_uid, $user['uid']]);
        $u = $stmtCheck->fetch();
        if (!$u) {
            echo json_encode(['status' => 'error', 'message' => 'Sub-user not found or unauthorized']);
            exit();
        }
        
        $now = new DateTime('now', new DateTimeZone('UTC'));
        $created = new DateTime($u['createdAt']);
        $diff = $created->diff($now);
        
        $account_age_str = "";
        if ($diff->y > 0) $account_age_str .= $diff->y . " years ";
        if ($diff->m > 0) $account_age_str .= $diff->m . " months ";
        if ($diff->d > 0) $account_age_str .= $diff->d . " days ";
        if (empty($account_age_str)) $account_age_str = $diff->h . " hours " . $diff->i . " minutes";
        $account_age = trim($account_age_str);

        $today_str = $now->format('Y-m-d');
        $yesterday_str = (clone $now)->modify('-1 day')->format('Y-m-d');

        $stmtT = $pdo->prepare("SELECT COUNT(*) FROM otp_logs WHERE userId = ? AND DATE(createdAt) = ?");
        $stmtT->execute([$target_uid, $today_str]);
        $today_otps = $stmtT->fetchColumn();

        $stmtY = $pdo->prepare("SELECT COUNT(*) FROM otp_logs WHERE userId = ? AND DATE(createdAt) = ?");
        $stmtY->execute([$target_uid, $yesterday_str]);
        $yesterday_otps = $stmtY->fetchColumn();

        echo json_encode([
            'status' => 'success',
            'data' => [
                'uid' => $u['uid'],
                'id_code' => $u['id_code'],
                'name' => $u['name'],
                'email' => $u['email'],
                'join_date' => $u['createdAt'],
                'account_age' => $account_age,
                'today_otp' => $today_otps,
                'yesterday_otp' => $yesterday_otps,
                'balance' => (float)$u['balance'],
                'account_status' => $u['status']
            ]
        ]);
        exit();
    }
}

if (is_maintenance()) {
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>OFFICIAL MAINTENANCE ACTIVE - MINO SMS</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-screen p-4 select-none font-sans overflow-hidden">
      <div class="max-w-md w-full bg-white text-slate-800 border border-slate-200 p-8 rounded-3xl shadow-2xl text-center space-y-6 relative">
        <div class="absolute inset-x-0 -top-12 flex justify-center">
          <div class="bg-rose-50 border border-rose-200 text-rose-600 h-24 w-24 rounded-full flex items-center justify-center text-4xl shadow-lg">
            <i class="fa-solid fa-triangle-exclamation animate-pulse"></i>
          </div>
        </div>
        
        <div class="pt-8 space-y-2">
          <span class="px-3 py-1 bg-rose-600 text-white font-black text-xs rounded-full uppercase tracking-widest shadow-sm">SYSTEM LOCKED</span>
          <h1 class="text-2xl font-black tracking-tight text-slate-900 uppercase mt-3">OFFICIAL MAINTENANCE</h1>
          <p class="text-xs text-slate-505 font-semibold leading-relaxed">
            Mino SMS is undergoing planned system maintenance for security and network upgrades.
          </p>
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
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MINO SMS - AGENT PORTAL</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vue/3.3.4/vue.global.prod.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    [v-cloak] { display: none; }
    body { background-color: #F8FAFC; }
    .page-enter-active {
      animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body class="text-slate-707 font-sans select-none pb-4 md:pb-0">
  
  <div id="app" v-cloak>

    <!-- Global Loading Screen Overlay -->
    <div v-if="!userLoaded" class="fixed inset-0 bg-slate-50 flex flex-col items-center justify-center space-y-4 z-[99999] p-4 text-center">
      <div class="h-12 w-12 border-4 border-[#0088CC] border-t-transparent rounded-full animate-spin"></div>
      <p class="text-xs font-black text-[#0088CC] uppercase tracking-widest">MINO AGENT PORTAL LOADING...</p>
    </div>

    <!-- Interface Main Mount Wrapper -->
    <div v-else>

      <!-- Action Confirmation Toast -->
      <div v-if="showToast" class="fixed top-5 left-1/2 -translate-x-1/2 bg-emerald-600 text-white font-black text-xs px-5 py-3 rounded-2xl shadow-xl z-[9999] transition-all duration-300 transform scale-100 animate-bounce flex items-center gap-2 select-none">
        <i class="fa-solid fa-circle-check"></i> {{ toastMessage }}
      </div>

      <!-- Main Portal Interface Layout -->
      <div class="min-h-screen flex flex-col md:flex-row bg-[#F8FAFC]">
        
        <!-- Desktop Sidebar Navigation -->
        <aside class="hidden md:flex w-64 bg-white border-r border-slate-200 flex-col shrink-0 select-none">
          <div class="p-6 border-b border-slate-100 flex items-center gap-3">
            <span class="px-2 py-1 bg-gradient-to-r from-[#0088CC] to-[#0077b5] rounded flex items-center justify-center text-white font-black text-sm">MINO</span>
            <span class="text-lg font-black text-slate-955 font-bold">MINO SMS</span>
          </div>

          <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
            <div class="space-y-1">
              <span class="px-4 text-[9px] uppercase font-black text-indigo-600 tracking-wider block mb-2">Agent Controls</span>
              <button @click="currentTab = 'dashboard'" :class="currentTab === 'dashboard' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-house"></i> Agent Dashboard
              </button>
              <button @click="currentTab = 'summary'" :class="currentTab === 'summary' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-square-poll-vertical"></i> Summary
              </button>
              <button @click="currentTab = 'auto-active'" :class="currentTab === 'auto-active' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-bolt"></i> Auto Active Account
              </button>
              <button @click="currentTab = 'my-network-users'" :class="currentTab === 'my-network-users' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-users"></i> My Network Users
              </button>
              <button @click="currentTab = 'user-payments'" :class="currentTab === 'user-payments' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-receipt"></i> User Payments
              </button>

              <span class="px-4 text-[9px] uppercase font-black text-indigo-600 tracking-wider block pt-4 mb-2">Agent Analytics</span>
              <button @click="currentTab = 'top-number-user'" :class="currentTab === 'top-number-user' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-phone-volume"></i> Top Number User
              </button>
              <button @click="currentTab = 'top-otp-user'" :class="currentTab === 'top-otp-user' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-envelope-circle-check"></i> Top OTP User
              </button>
              <button @click="currentTab = 'inactive-user'" :class="currentTab === 'inactive-user' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-user-slash"></i> Inactive User
              </button>
              <button @click="currentTab = 'leaderboard'" :class="currentTab === 'leaderboard' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
                <i class="fa-solid fa-trophy"></i> Leaderboard
              </button>
            </div>

            <span class="px-4 text-[9px] uppercase font-black text-slate-505 tracking-wider block pt-4 mb-2">Account Controls</span>
            <button @click="currentTab = 'withdraw'" :class="currentTab === 'withdraw' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
              <i class="fa-solid fa-wallet"></i> Withdraw Commissions
            </button>
            <button @click="currentTab = 'profile'" :class="currentTab === 'profile' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-left">
              <i class="fa-solid fa-user"></i> Profile Details
            </button>
          </nav>

          <div class="p-4 border-t border-slate-100 flex items-center gap-3 select-none">
            <div class="h-9 w-9 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0">
              AG
            </div>
            <div class="flex-1 overflow-hidden">
              <p class="text-xs font-black text-slate-888 truncate">Official Agent</p>
              <p class="text-[10px] text-slate-404 truncate">{{ user?.email }}</p>
            </div>
            <button @click="signOut" class="text-slate-444 hover:text-rose-650"><i class="fa-solid fa-right-from-bracket"></i></button>
          </div>
        </aside>

        <!-- Slide-out Mobile Sidebar with Working Close (Cross) Button -->
        <transition enter-active-class="transition ease-out duration-300" enter-from-class="-translate-x-full" enter-to-class="translate-x-0" leave-active-class="transition ease-in duration-200" leave-from-class="translate-x-0" leave-to-class="-translate-x-full">
          <aside v-if="mobileMenuOpen" class="fixed inset-y-0 left-0 w-64 bg-white text-slate-707 flex flex-col z-50 md:hidden shadow-2xl border-r border-slate-200 select-none">
            <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div class="flex items-center gap-3">
                <span class="px-2 py-1 bg-indigo-600 rounded flex items-center justify-center text-white font-black text-xs font-bold">MINO</span>
                <span class="text-md font-black text-slate-900 font-bold">MINO AGENT</span>
              </div>
              <button @click="mobileMenuOpen = false" class="text-slate-444 hover:text-slate-850 focus:outline-none"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>

            <nav class="flex-1 p-4 space-y-1 bg-white overflow-y-auto">
              <div class="space-y-1">
                <span class="px-4 text-[9px] uppercase font-black text-indigo-600 tracking-wider block mb-2">Agent Controls</span>
                <button @click="navigateMobile('dashboard')" :class="currentTab === 'dashboard' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                  <i class="fa-solid fa-house"></i> Agent Dashboard
                </button>
                <button @click="navigateMobile('summary')" :class="currentTab === 'summary' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                  <i class="fa-solid fa-square-poll-vertical"></i> Summary
                </button>
                <button @click="navigateMobile('auto-active')" :class="currentTab === 'auto-active' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left font-bold">
                  <i class="fa-solid fa-bolt"></i> Auto Active Account
                </button>
                <button @click="navigateMobile('my-network-users')" :class="currentTab === 'my-network-users' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left font-bold">
                  <i class="fa-solid fa-users"></i> My Network Users
                </button>
                <button @click="navigateMobile('user-payments')" :class="currentTab === 'user-payments' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left font-bold">
                  <i class="fa-solid fa-receipt"></i> User Payments
                </button>

                <span class="px-4 text-[9px] uppercase font-black text-indigo-600 tracking-wider block pt-4 mb-2">Agent Analytics</span>
                <button @click="navigateMobile('top-number-user')" :class="currentTab === 'top-number-user' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                  <i class="fa-solid fa-phone-volume"></i> Top Number User
                </button>
                <button @click="navigateMobile('top-otp-user')" :class="currentTab === 'top-otp-user' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                  <i class="fa-solid fa-envelope-circle-check"></i> Top OTP User
                </button>
                <button @click="navigateMobile('inactive-user')" :class="currentTab === 'inactive-user' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                  <i class="fa-solid fa-user-slash"></i> Inactive User
                </button>
                <button @click="navigateMobile('leaderboard')" :class="currentTab === 'leaderboard' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                  <i class="fa-solid fa-trophy"></i> Leaderboard
                </button>
              </div>

              <span class="px-4 text-[9px] uppercase font-black text-slate-505 tracking-wider block pt-4 mb-2">Account Controls</span>
              <button @click="navigateMobile('withdraw')" :class="currentTab === 'withdraw' ? 'bg-indigo-50 text-indigo-600 border-l-2 border-indigo-600' : 'text-slate-600 hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-wallet"></i> Withdraw Commissions
              </button>
              <button @click="navigateMobile('profile')" :class="currentTab === 'profile' ? 'bg-indigo-50 text-indigo-600' : 'hover:bg-slate-50'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition text-left">
                <i class="fa-solid fa-user"></i> Profile Details
              </button>
            </nav>

            <div class="p-4 border-t border-slate-200 bg-slate-50 text-xs font-bold flex flex-col gap-3">
              <span class="text-slate-808 font-bold">Official Agent Portal</span>
              <button @click="signOut" class="text-rose-500 font-bold text-left">LOGOUT</button>
            </div>
          </aside>
        </transition>

        <div v-if="mobileMenuOpen" @click="mobileMenuOpen = false" class="fixed inset-0 bg-black/40 backdrop-blur-xs z-40 md:hidden"></div>

        <!-- Main Content Area -->
        <main class="flex-1 p-4 md:p-8 space-y-6 overflow-y-auto">
          
          <header class="flex justify-between items-center border-b border-slate-200 pb-4 select-none">
            <div class="flex items-center gap-3">
              <button @click="mobileMenuOpen = true" class="md:hidden text-slate-707 bg-white shadow-xs border p-2.5 rounded-xl focus:outline-none transition active:scale-95">
                <i class="fa-solid fa-bars text-lg"></i>
              </button>
              <span class="h-2.5 w-2.5 bg-indigo-600 rounded-full hidden md:inline-block"></span>
              <h2 class="text-md md:text-lg font-black text-slate-900 capitalize font-bold">
                {{ currentTab.replace('-', ' ') }} Workspace
              </h2>
            </div>
            <div class="flex items-center gap-2">
              <span class="bg-indigo-600 text-white text-[10px] md:text-xs font-bold px-3 py-1.5 rounded-full shadow-sm font-semibold">
                OFFICIAL AGENT
              </span>
              <button @click="signOut" class="hidden md:block text-slate-444 hover:text-rose-600 p-2 transition-all"><i class="fa-solid fa-right-from-bracket text-lg"></i></button>
            </div>
          </header>

          <!-- ==================== Tab: Dashboard ==================== -->
          <div v-if="currentTab === 'dashboard'" class="page-enter-active space-y-6">
            
            <div class="space-y-4 select-none">
              <h3 class="text-xs font-extrabold text-slate-444 uppercase tracking-widest font-bold">My Earnings (Agent Commission)</h3>
              
              <!-- Refactored premium 5-card layout containing Withdrawable Wallet Balance -->
              <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div class="bg-gradient-to-r from-emerald-600 to-emerald-800 text-white p-5 rounded-2xl shadow-md flex flex-col justify-between hover-card transition-all duration-300">
                  <p class="text-[10px] text-emerald-100 font-bold uppercase tracking-wide">Wallet Balance (৳)</p>
                  <h3 class="text-2xl font-black mt-2 font-mono">৳ {{ parseFloat(profile ? profile.balance : 0).toFixed(2) }}</h3>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                  <p class="text-[10px] text-slate-404 font-bold uppercase tracking-wide">Today</p>
                  <h3 class="text-2xl font-black text-slate-900 mt-2 font-mono">৳ {{ parseFloat(agentStats.today_revenue || 0).toFixed(2) }}</h3>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                  <p class="text-[10px] text-slate-404 font-bold uppercase tracking-wide">Yesterday</p>
                  <h3 class="text-2xl font-black text-slate-900 mt-2 font-mono">৳ {{ parseFloat(agentStats.yesterday_revenue || 0).toFixed(2) }}</h3>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                  <p class="text-[10px] text-slate-404 font-bold uppercase tracking-wide">Last 7 Days</p>
                  <h3 class="text-2xl font-black text-slate-900 mt-2 font-mono">৳ {{ parseFloat(agentStats.days7_revenue || 0).toFixed(2) }}</h3>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                  <p class="text-[10px] text-slate-404 font-bold uppercase tracking-wide">Lifetime</p>
                  <h3 class="text-2xl font-black text-[#0088CC] mt-2 font-mono">৳ {{ parseFloat(agentStats.lifetime_revenue || 0).toFixed(2) }}</h3>
                </div>
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4 select-none">
              
              <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 hover-card transition-all duration-300">
                <h4 class="font-extrabold text-xs text-slate-444 uppercase tracking-widest border-b pb-2 font-bold">Network Top Services</h4>
                <div class="space-y-3">
                  <div class="text-xs text-slate-404 font-bold py-6 text-center" v-if="agentStats.top_services.length === 0">No service data tracked yet.</div>
                  <div v-else v-for="svc in agentStats.top_services" class="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-100">
                    <div class="flex items-center gap-2.5 text-xs font-bold text-slate-808 uppercase font-semibold">
                      {{ svc.name }}
                    </div>
                    <span class="text-xs font-black text-slate-600 font-mono font-bold">{{ svc.count }} OTP</span>
                  </div>
                </div>
              </div>

              <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 hover-card transition-all duration-300">
                <h4 class="font-extrabold text-xs text-slate-444 uppercase tracking-widest border-b pb-2 font-bold">Top Performing Users</h4>
                <div class="space-y-3">
                  <div class="text-xs text-slate-404 font-bold py-6 text-center" v-if="agentStats.top_users.length === 0">No successful OTP users today.</div>
                  <div v-else v-for="(u, index) in agentStats.top_users" class="flex justify-between items-center text-xs font-sans">
                    <div class="flex items-center gap-2">
                      <span class="font-bold text-slate-400">#{{ index + 1 }}</span>
                      <div>
                        <p class="font-black text-slate-800 font-bold">{{ u.name }}</p>
                        <p class="text-[9px] text-slate-404 font-mono">{{ u.id_code }}</p>
                      </div>
                    </div>
                    <span class="bg-indigo-50 text-indigo-600 text-[10px] font-bold px-2 py-0.5 rounded-full font-mono font-bold">
                      {{ u.count }} Hits
                    </span>
                  </div>
                </div>
              </div>

            </div>

            <!-- Unseen / Pending registrations waiting agent approval -->
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 select-none hover-card transition-all duration-300">
              <h4 class="font-extrabold text-xs text-slate-444 uppercase tracking-widest border-b pb-2 font-bold">Unseen / Pending Registration Users</h4>
              <div class="space-y-2">
                <div class="text-xs text-slate-404 font-bold py-6 text-center" v-if="agentStats.unseen_users.length === 0">All user registrations are approved and active!</div>
                <div v-else v-for="u in agentStats.unseen_users" class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 bg-slate-50 border border-slate-100 rounded-2xl gap-3 text-xs font-sans hover:border-indigo-500/30 transition-all duration-200">
                  <div>
                    <p class="font-black text-slate-808 font-bold">{{ u.name }}</p>
                    <p class="text-slate-505 font-semibold">{{ u.email }}</p>
                  </div>
                  <div class="flex gap-1.5 w-full sm:w-auto font-bold">
                    <button @click="agentUpdateUserStatusDirect(u.uid, 'approved')" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 px-4 rounded-xl transition flex-1 sm:flex-none shadow-sm font-bold">
                      Approve
                    </button>
                    <button @click="agentUpdateUserStatusDirect(u.uid, 'banned')" class="bg-rose-600 hover:bg-rose-700 text-white font-bold py-2 px-4 rounded-xl transition flex-1 sm:flex-none shadow-sm font-bold">
                      Ban
                    </button>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- ==================== Tab: Summary Payout Metrics ==================== -->
          <div v-if="currentTab === 'summary'" class="page-enter-active space-y-6">
            
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4 select-none hover-card transition-all duration-300">
              <h3 class="font-black text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2 border-b pb-2 font-bold">
                <i class="fa-solid fa-square-poll-vertical text-indigo-600"></i> Agency OTP Summary Report
              </h3>
              
              <div class="grid grid-cols-2 md:grid-cols-5 gap-4 pt-2 font-semibold">
                <div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 flex flex-col justify-between">
                  <span class="text-[9px] text-slate-404 block uppercase font-bold">Today</span>
                  <span class="text-md text-slate-808 block mt-1 font-mono font-bold">{{ agentStats.today_success_otp }} OTPs</span>
                  <span class="text-xs text-emerald-605 block mt-1 font-bold">৳ {{ parseFloat(agentStats.today_revenue).toFixed(2) }}</span>
                </div>
                <div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 flex flex-col justify-between">
                  <span class="text-[9px] text-slate-404 block uppercase font-bold">Yesterday</span>
                  <span class="text-md text-slate-808 block mt-1 font-mono font-bold">{{ agentStats.yesterday_success }} OTPs</span>
                  <span class="text-xs text-emerald-605 block mt-1 font-bold">৳ {{ parseFloat(agentStats.yesterday_revenue).toFixed(2) }}</span>
                </div>
                <div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 flex flex-col justify-between">
                  <span class="text-[9px] text-slate-404 block uppercase font-bold">Last 7 Days</span>
                  <span class="text-md text-slate-808 block mt-1 font-mono font-bold">{{ agentStats.days7_success }} OTPs</span>
                  <span class="text-xs text-emerald-605 block mt-1 font-bold">৳ {{ parseFloat(agentStats.days7_revenue).toFixed(2) }}</span>
                </div>
                <div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 flex flex-col justify-between">
                  <span class="text-[9px] text-slate-404 block uppercase font-bold">Last 30 Days</span>
                  <span class="text-md text-slate-808 block mt-1 font-mono font-bold">{{ agentStats.days30_success }} OTPs</span>
                  <span class="text-xs text-emerald-605 block mt-1 font-bold">৳ {{ parseFloat(agentStats.days30_revenue).toFixed(2) }}</span>
                </div>
                <div class="bg-emerald-50/50 p-4 rounded-2xl border border-emerald-100 flex flex-col justify-between">
                  <span class="text-[9px] text-emerald-600 block uppercase font-bold">Lifetime Total</span>
                  <span class="text-md text-slate-808 block mt-1 font-mono font-bold">{{ agentStats.lifetime_success }} OTPs</span>
                  <span class="text-xs text-emerald-605 block mt-1 font-bold">৳ {{ parseFloat(agentStats.lifetime_revenue).toFixed(2) }}</span>
                </div>
              </div>
            </div>

          </div>

          <!-- ==================== Tab: Auto Active Settings ==================== -->
          <div v-if="currentTab === 'auto-active'" class="page-enter-active space-y-6">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-6 select-none max-w-2xl hover-card transition-all duration-300">
              <div class="flex items-center gap-3">
                <div class="h-10 w-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center">
                  <i class="fa-solid fa-bolt text-lg"></i>
                </div>
                <div>
                  <h3 class="text-md font-black text-slate-900 font-bold">Auto Account Active Setting</h3>
                  <p class="text-xs text-slate-404 font-medium">এনেবল করা থাকলে নতুন রেজিস্টার করা ইউজারদের একাউন্ট অটোমেটিক একটিভ হবে।</p>
                </div>
              </div>

              <div class="space-y-4 font-bold">
                <div>
                  <label class="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">Auto Account Approval Option</label>
                  <button @click="agentAutoApprove = !agentAutoApprove" :class="agentAutoApprove ? 'bg-emerald-600 text-white border-emerald-700' : 'bg-slate-200 text-slate-600 border-slate-350'" class="px-5 py-2.5 rounded-xl text-xs font-black transition-all border active:scale-95">
                    {{ agentAutoApprove ? 'AUTO ACTIVE – ON' : 'AUTO ACTIVE – OFF' }}
                  </button>
                </div>

                <div>
                  <label class="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">Auto Activate Rate (Per OTP) – Max: ৳{{ parseFloat(user?.otp_rate || 0.60).toFixed(2) }}</label>
                  <div class="relative max-w-xs">
                    <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500 font-bold font-mono">৳</span>
                    <input type="number" step="0.01" v-model.number="agentAutoRate" class="w-full pl-8 pr-4 py-3 bg-slate-50 border rounded-xl text-sm font-bold font-mono outline-none" />
                  </div>
                </div>

                <button @click="saveAgentSettings" class="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-6 py-3 rounded-xl text-xs transition-all shadow-sm">
                  Save Agent Settings
                </button>
              </div>
            </div>
          </div>

          <!-- ==================== Tab: My Network Users ==================== -->
          <div v-if="currentTab === 'my-network-users'" class="page-enter-active space-y-4 select-none">
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div>
                <h3 class="font-black text-sm text-slate-808 font-bold">Manage Your Agency Network</h3>
                <p class="text-[10px] text-slate-404 font-medium">Update sub-user payout rates, passwords, credentials and check profile age summaries.</p>
              </div>
              <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                <input type="text" v-model="searchQuery" placeholder="Search sub-users by name or ID..." class="p-2.5 bg-slate-50 border rounded-xl text-xs font-bold outline-none focus:border-indigo-500 w-full sm:w-64" />
                <span class="bg-indigo-50 text-indigo-600 border border-indigo-100 text-[10px] font-bold px-3 py-2 rounded-xl font-mono shrink-0">
                  Total Sub-Users: {{ agentUsers.length }} / {{ user?.agent_limit || 120 }} (Quota Used)
                </span>
              </div>
            </div>

            <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden hover-card transition-all duration-300">
              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 text-slate-404 font-bold uppercase tracking-wider">
                      <th class="p-4">User Details</th>
                      <th class="p-4">Email (Click to Copy)</th>
                      <th class="p-4">My Agent Rate</th>
                      <th class="p-4">User Rate</th>
                      <th class="p-4">User Balance</th>
                      <th class="p-4">API Status</th>
                      <th class="p-4">Status</th>
                      <th class="p-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-semibold text-slate-707">
                    <tr class="hover:bg-slate-50/50" v-if="filteredAgentUsers.length === 0">
                      <td colspan="8" class="p-8 text-center text-slate-404 font-bold">No registered network users found under your agency.</td>
                    </tr>
                    <!-- API status check corrected with (subU.api_key_approved == 1 || subU.api_key_approved === true) and copyToClipboard applied on email click -->
                    <tr v-else v-for="subU in filteredAgentUsers" :key="subU.uid" class="hover:bg-slate-50/50 transition-all duration-200">
                      <td class="p-4">
                        <p class="font-black text-slate-800 text-sm font-bold">{{ subU.name }}</p>
                        <p class="text-[10px] text-indigo-600 font-mono font-bold">{{ subU.id_code }}</p>
                      </td>
                      <td class="p-4 cursor-pointer hover:text-indigo-600" @click="copyToClipboard(subU.email, 'email_copy_' + subU.uid)">
                        <p class="font-bold text-slate-555 select-all">{{ subU.email }}</p>
                        <span v-if="copiedStates['email_copy_' + subU.uid]" class="text-[8px] text-emerald-500 font-extrabold block">Email Copied!</span>
                      </td>
                      <td class="p-4 font-mono font-bold text-slate-505">৳ {{ parseFloat(user?.otp_rate || 0).toFixed(2) }}</td>
                      <td class="p-4 font-mono font-bold text-indigo-600 font-bold">৳ {{ parseFloat(subU.otp_rate || 0).toFixed(2) }}</td>
                      <td class="p-4 font-black font-mono text-slate-808 font-bold">৳ {{ parseFloat(subU.balance || 0).toFixed(2) }}</td>
                      <td class="p-4">
                        <span :class="(subU.api_key_approved == 1 || subU.api_key_approved === true) ? 'bg-emerald-100 text-emerald-808' : 'bg-rose-100 text-rose-808'" class="text-[9px] font-black px-2 py-0.5 rounded uppercase font-bold">
                          {{ (subU.api_key_approved == 1 || subU.api_key_approved === true) ? 'ON' : 'OFF' }}
                        </span>
                      </td>
                      <td class="p-4">
                        <span v-if="subU.status === 'approved'" class="bg-emerald-100 text-emerald-808 text-[9px] font-bold px-2 py-0.5 rounded-full uppercase">Active</span>
                        <span v-else-if="subU.status === 'pending'" class="bg-amber-100 text-amber-808 text-[9px] font-bold px-2 py-0.5 rounded-full uppercase">Pending</span>
                        <span v-else class="bg-rose-100 text-rose-808 text-[9px] font-bold px-2 py-0.5 rounded-full uppercase">Banned</span>
                      </td>
                      <td class="p-4 text-right flex items-center justify-end gap-1 pt-5">
                        <button @click="viewSubUserStatus(subU.uid)" class="bg-teal-50 hover:bg-teal-100 text-teal-700 text-[10px] font-bold px-3 py-1.5 rounded-xl transition font-bold">
                          View Status
                        </button>
                        <button @click="openAgentManageUserModal(subU)" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-600 font-bold text-[10px] px-3.5 py-1.5 rounded-xl transition font-bold">
                          Manage
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab: User Payments ==================== -->
          <div v-if="currentTab === 'user-payments'" class="page-enter-active space-y-4 select-none">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                <span class="text-[10px] text-slate-404 font-bold uppercase tracking-wider">Total Distributed</span>
                <h4 class="text-lg md:text-xl font-black text-slate-900 mt-2 font-mono">৳ {{ parseFloat(subUsersWithdrawalSum).toFixed(2) }}</h4>
              </div>
              <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                <span class="text-[10px] text-slate-404 font-bold uppercase tracking-wider">Total Approved</span>
                <h4 class="text-lg md:text-xl font-black text-indigo-600 mt-2 font-mono">{{ subUsersApprovedWithdrawals.length }} Successful</h4>
              </div>
              <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                <span class="text-[10px] text-slate-404 font-bold uppercase tracking-wider">Pending Requests</span>
                <h4 class="text-lg md:text-xl font-black text-amber-500 mt-2 font-mono">{{ subUsersPendingWithdrawals.length }} Waiting</h4>
              </div>
              <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover-card transition-all duration-300">
                <span class="text-[10px] text-slate-404 font-bold uppercase tracking-wider">Total Rejected</span>
                <h4 class="text-lg md:text-xl font-black text-rose-505 mt-2 font-mono">{{ subUsersRejectedWithdrawals.length }} Denied</h4>
              </div>
            </div>

            <!-- Subuser Withdrawals List Configured from agent withdrawals database query -->
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 hover-card transition-all duration-300">
              <h4 class="font-extrabold text-xs text-slate-404 uppercase tracking-widest border-b pb-2">Network Payout Transaction History</h4>
              
              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 text-slate-404 font-bold uppercase font-sans">
                      <th class="p-3">Reference ID & User</th>
                      <th class="p-3">Amount</th>
                      <th class="p-3">Method & Details</th>
                      <th class="p-3">Status</th>
                      <th class="p-3">Date</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-semibold text-slate-707">
                    <tr v-if="subUsersWithdrawals.length === 0">
                      <td colspan="5" class="p-8 text-center text-slate-404 font-bold font-sans">No payout history logged for your sub-users.</td>
                    </tr>
                    <tr v-else v-for="wd in subUsersWithdrawals" :key="wd.id" class="hover:bg-slate-50/50 font-sans">
                      <td class="p-3">
                        <p class="font-mono font-black text-slate-808 font-bold">{{ wd.id }}</p>
                        <p class="text-[10px] text-slate-404">{{ wd.userName }} <span class="font-bold">({{ getUserIdCode(wd.userId) }})</span></p>
                      </td>
                      <td class="p-3 font-mono font-black text-slate-808 font-bold">৳ {{ parseFloat(wd.amount).toFixed(2) }}</td>
                      <td class="p-3 font-mono">
                        <span class="text-indigo-600 uppercase font-bold">{{ wd.method }}</span>
                        <p class="text-[9px] text-slate-404 max-w-xs truncate select-all" :title="wd.address">{{ wd.address }}</p>
                      </td>
                      <td class="p-3">
                        <span v-if="wd.status === 'approved'" class="bg-emerald-100 text-emerald-808 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Paid</span>
                        <span v-else-if="wd.status === 'pending'" class="bg-amber-100 text-amber-808 px-2 py-0.5 rounded-full text-[9px] font-black uppercase animate-pulse">Pending</span>
                        <span v-else class="bg-rose-100 text-rose-808 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Rejected</span>
                      </td>
                      <td class="p-3 text-[10px] font-mono text-slate-404">{{ formatTimestamp(wd.createdAt) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab: Leaderboard ==================== -->
          <div v-if="currentTab === 'leaderboard'" class="page-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 select-none font-bold hover-card transition-all duration-300">
              <span class="text-xs uppercase font-extrabold block text-indigo-600">Sub-User Leaderboard rankings</span>
              
              <div class="space-y-2">
                <div v-for="(worker, idx) in leaderboardData[leaderboardTab]" :key="idx" class="flex justify-between items-center bg-slate-50/50 p-4 rounded-2xl border border-slate-200/60 text-xs hover:border-indigo-600/30 transition-all duration-200">
                  <div class="flex items-center gap-3">
                    <span class="font-black text-xs h-7 w-7 rounded-full flex items-center justify-center border bg-indigo-50 font-mono text-indigo-707">
                      #{{ idx + 1 }}
                    </span>
                    <div>
                      <span class="font-extrabold text-slate-808 text-sm block font-bold">{{ worker.name }}</span>
                      <span class="text-[10px] text-slate-405 block font-semibold font-mono font-bold">{{ worker.id_code }}</span>
                    </div>
                  </div>
                  <span class="font-black text-indigo-600 text-xs bg-white border px-3.5 py-1.5 rounded-full font-mono font-bold">
                    {{ worker.count }} Successful OTPs
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- ==================== Tab: Inactive User ==================== -->
          <div v-if="currentTab === 'inactive-user'" class="page-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 hover-card transition-all duration-300">
              <h2 class="text-md font-black text-slate-900 font-bold">Agent Inactive User</h2>
              
              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 font-bold text-slate-404 uppercase">
                      <th class="p-4">NAME</th>
                      <th class="p-4">EMAIL</th>
                      <th class="p-4">ID CODE</th>
                      <th class="p-4">REGISTRATION DATE</th>
                      <th class="p-4">STATUS</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="inactiveUsersList.length === 0">
                      <td colspan="5" class="p-8 text-center text-slate-404 font-bold font-sans">No inactive sub-users found.</td>
                    </tr>
                    <tr v-else v-for="user in inactiveUsersList" :key="user.uid" class="hover:bg-slate-50">
                      <td class="p-4 font-black text-slate-900">{{ user.name }}</td>
                      <td class="p-4 font-mono select-all">{{ user.email }}</td>
                      <td class="p-4 text-indigo-600 font-bold">{{ user.id_code }}</td>
                      <td class="p-4 text-slate-404 font-mono">{{ formatTimestamp(user.createdAt) }}</td>
                      <td class="p-4 font-black text-emerald-600 uppercase">{{ user.status }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab: Top Number User ==================== -->
          <div v-if="currentTab === 'top-number-user'" class="page-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 hover-card transition-all duration-300">
              <h2 class="text-md font-black text-slate-900 font-bold">Agent Top Number User</h2>
              
              <div class="overflow-x-auto font-bold">
                <table class="w-full text-left text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 font-bold text-slate-404 uppercase">
                      <th class="p-4">RANK</th>
                      <th class="p-4">NAME</th>
                      <th class="p-4">ID CODE</th>
                      <th class="p-4">NUMBERS TAKEN</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="topNumberUsers.length === 0">
                      <td colspan="4" class="p-8 text-center text-slate-404 font-bold">No number booking records found.</td>
                    </tr>
                    <tr v-else-if="topNumberUsers" v-for="(worker, idx) in topNumberUsers" :key="idx" class="hover:bg-slate-50">
                      <td class="p-4 font-black">#{{ idx + 1 }}</td>
                      <td class="p-4 font-black text-slate-900">{{ worker.name }}</td>
                      <td class="p-4 text-indigo-600 font-bold">{{ worker.id_code }}</td>
                      <td class="p-4 text-xs font-black">{{ worker.count }} numbers</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab: Top OTP User ==================== -->
          <div v-if="currentTab === 'top-otp-user'" class="page-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 hover-card transition-all duration-300">
              <h2 class="text-md font-black text-slate-900 font-bold">Agent Top OTP User</h2>
              
              <div class="overflow-x-auto font-bold">
                <table class="w-full text-left text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 font-bold text-slate-404 uppercase">
                      <th class="p-4">RANK</th>
                      <th class="p-4">NAME</th>
                      <th class="p-4">ID CODE</th>
                      <th class="p-4">SUCCESSFUL OTPs</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="topOtpUsers.length === 0">
                      <td colspan="4" class="p-8 text-center text-slate-404 font-bold">No successful OTP records found.</td>
                    </tr>
                    <tr v-else v-for="(worker, idx) in topOtpUsers" :key="idx" class="hover:bg-slate-50">
                      <td class="p-4 font-black">#{{ idx + 1 }}</td>
                      <td class="p-4 font-black text-slate-900">{{ worker.name }}</td>
                      <td class="p-4 text-indigo-600 font-bold">{{ worker.id_code }}</td>
                      <td class="p-4 text-xs font-black text-emerald-600">{{ worker.count }} OTPs</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab: Agent Commission Withdraw Workspace ==================== -->
          <div v-if="currentTab === 'withdraw'" class="page-enter-active space-y-6">
            
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-2xs space-y-4 hover-card select-none font-bold transition-all duration-300">
              <h3 class="font-black text-xs text-slate-808 flex items-center gap-2 font-bold"><i class="fa-solid fa-wallet text-indigo-600"></i> Configure My Payout Address (Binance / TRC20 / Bkash)</h3>
              
              <div class="bg-indigo-50/50 border border-indigo-100 p-4 rounded-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                  <p class="text-[10px] text-slate-404 font-bold uppercase font-bold">Payout Destination address</p>
                  <p class="font-mono font-black text-indigo-705 mt-1 select-all break-all flex items-center gap-1.5 font-bold">
                    {{ user?.wallet_address || 'No payout address configured' }}
                    <i class="fa-regular text-[10px] cursor-pointer" v-if="user?.wallet_address" @click="copyToClipboard(user?.wallet_address, 'wallet_addr')" :class="copiedStates['wallet_addr'] ? 'fa-circle-check text-emerald-505 scale-125' : 'fa-copy text-indigo-500'"></i>
                    <span v-if="copiedStates['wallet_addr']" class="text-[8px] text-emerald-500 font-extrabold animate-pulse">Copied!</span>
                  </p>
                </div>
                <span class="bg-indigo-600 text-white text-[10px] font-bold px-2.5 py-1 rounded-full shadow-sm"><i class="fa-solid fa-money-bill-transfer"></i> Payout</span>
              </div>

              <div class="flex flex-col sm:flex-row gap-2 pt-2 select-none">
                <input type="text" v-model="walletAddressInput" placeholder="Enter Binance Pay ID, Bkash No, or TRC20 address" class="flex-1 p-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-semibold outline-none focus:border-indigo-600 transition" />
                <button @click="handleUpdateWallet" :disabled="walletLoading" class="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-5 py-3.5 rounded-2xl text-xs tracking-wider transition-all duration-200 active:scale-95 disabled:bg-slate-300 shrink-0 font-bold">
                  {{ walletLoading ? 'Saving...' : 'Save Payout Details' }}
                </button>
              </div>
            </div>

            <!-- Submit Withdraw Form -->
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-2xs space-y-4 hover-card select-none font-bold transition-all duration-300">
              <h3 class="font-black text-xs text-slate-808 flex items-center gap-2 font-bold">
                <i class="fa-solid fa-hand-holding-dollar text-emerald-600"></i> Withdraw My Agent Earnings (মিনিমাম ৫০ টাকা)
              </h3>
              <!-- Explicit dynamic payout balances indicators -->
              <p class="text-sm font-black text-slate-808 flex items-center gap-2 font-sans bg-emerald-50 border border-emerald-150 p-4 rounded-2xl text-emerald-800">
                <i class="fa-solid fa-vault text-lg"></i>
                <span>Your Current Withdrawable Wallet Balance: <strong>৳ {{ parseFloat(profile ? profile.balance : 0).toFixed(2) }}</strong></span>
              </p>
              
              <div class="grid sm:grid-cols-2 gap-3 text-xs font-bold font-sans">
                <div>
                  <label class="text-slate-404 font-bold">Withdraw Amount (৳)</label>
                  <input type="number" step="1" v-model="withdrawAmount" placeholder="e.g., 50" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl font-mono focus:border-indigo-600 transition font-bold" />
                </div>
                <div>
                  <label class="text-slate-404 font-bold">Payment Method</label>
                  <select v-model="withdrawMethod" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl focus:border-indigo-600 transition font-bold font-bold">
                    <option value="">Select Configured Method</option>
                    <option v-for="m in withdrawalMethods" :key="m.id" :value="m.method_name">{{ m.method_name }}</option>
                  </select>
                </div>
                <div v-if="profile?.withdraw_pin">
                  <label class="text-slate-404 font-bold">Secure Withdraw PIN (4 Digits)</label>
                  <input type="password" maxlength="4" v-model="withdrawPinInput" placeholder="e.g. 1234" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl font-mono focus:border-indigo-600 transition font-bold" />
                </div>
              </div>

              <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-2 border-t pt-3 select-none">
                <div class="text-[11px] font-bold text-slate-555 flex items-center gap-1">
                  Destination Address: 
                  <span class="text-indigo-600 font-mono select-all font-bold font-mono">{{ user?.wallet_address || 'Please set a wallet address first.' }}</span>
                </div>
                <button @click="submitWithdrawal" :disabled="!user?.wallet_address || withdrawAmount < 50 || !withdrawMethod" class="bg-emerald-600 hover:bg-emerald-700 text-white font-black px-6 py-3 rounded-xl text-xs transition flex items-center gap-1.5 disabled:bg-slate-200 shadow-sm active:scale-95 font-bold font-bold">
                  <i class="fa-solid fa-paper-plane"></i> Submit Withdraw Request
                </button>
              </div>
            </div>

            <!-- Withdraw History -->
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-2xs space-y-4 select-none font-bold hover-card transition-all duration-300">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b pb-3 font-sans">
                <h3 class="font-black text-xs text-slate-808 flex items-center gap-2 font-bold">
                  <i class="fa-solid fa-history text-indigo-600"></i> Withdrawal History
                </h3>
                
                <div class="flex gap-1 bg-slate-100 p-1 rounded-xl text-[9px] font-bold select-none font-bold">
                  <button v-for="mode in ['today', 'yesterday', '7days', 'lifetime']" :key="mode" @click="withdrawHistoryFilter = mode" :class="withdrawHistoryFilter === mode ? 'bg-indigo-600 text-white shadow-2xs' : 'text-slate-505 hover:bg-slate-200'" class="px-2.5 py-1.5 rounded-lg uppercase tracking-wider transition-all duration-200">
                    {{ mode === '7days' ? '7 Days' : mode }}
                  </button>
                </div>
              </div>

              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs font-semibold">
                  <thead>
                    <tr class="text-slate-404 font-bold uppercase tracking-wider border-b">
                      <th class="py-2.5 font-bold">Date</th>
                      <th class="py-2.5 font-bold">Amount</th>
                      <th class="py-2.5 font-bold">Method</th>
                      <th class="py-2.5 font-bold">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="filteredWithdrawals.length === 0">
                      <td colspan="4" class="py-8 text-center text-slate-404 font-bold">No matching withdrawals found.</td>
                    </tr>
                    <tr v-else v-for="wd in filteredWithdrawals" :key="wd.id" class="border-b border-slate-100 hover:bg-slate-50/50 transition-all duration-200">
                      <td class="py-3 font-mono text-slate-555 text-[10px]">{{ formatTimestamp(wd.createdAt) }}</td>
                      <td class="py-3 font-black text-slate-808 font-bold font-mono">৳ {{ parseFloat(wd.amount || 0).toFixed(2) }}</td>
                      <td class="py-3 uppercase text-indigo-600 font-bold font-bold">{{ wd.method }}</td>
                      <td class="py-3">
                        <span v-if="wd.status === 'approved'" class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Approved</span>
                        <span v-else-if="wd.status === 'pending'" class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Pending</span>
                        <span v-else class="bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full text-[9px] font-black uppercase">Rejected</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
          </div>

          <!-- Shared Tab: Profile details -->
          <div v-if="currentTab === 'profile'" class="page-enter-active space-y-6">
            <div class="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm space-y-4 hover-card transition-all duration-300">
              <h3 class="font-bold text-slate-808 border-b pb-2 font-sans">My Agency Profile</h3>
              
              <div class="space-y-4 font-sans text-xs">
                <div>
                  <label class="text-slate-404 uppercase text-[10px] tracking-wider font-bold">Agent UID (Read-Only)</label>
                  <input type="text" readonly :value="profile?.uid" class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-slate-404 font-mono" />
                </div>
                <div>
                  <label class="text-slate-404 uppercase text-[10px] tracking-wider font-bold">Email Address (Read-Only)</label>
                  <input type="text" readonly :value="profile?.email" class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-slate-404 font-mono" />
                </div>
                <div>
                  <label class="text-slate-404 uppercase text-[10px] tracking-wider font-bold">Agent Base OTP Rate</label>
                  <input type="text" readonly :value="'৳ ' + parseFloat(profile?.otp_rate || 0.63).toFixed(2)" class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-slate-808 font-bold font-mono" />
                </div>
                <div>
                  <label class="text-slate-404 uppercase text-[10px] tracking-wider font-bold">Telegram Username</label>
                  <input type="text" v-model="profileTelegramUsername" placeholder="e.g. @MinoXSupport0" class="w-full mt-1.5 p-3.5 bg-white border rounded-xl text-slate-808 font-bold focus:border-indigo-600 transition-all outline-none" />
                </div>

                <button @click="saveProfileChanges" :disabled="profileTelegramLoading" class="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-6 py-3 rounded-2xl text-xs tracking-wider transition-all duration-200 active:scale-95 disabled:bg-slate-300 font-bold">
                  {{ profileTelegramLoading ? 'Saving...' : 'Save Profile Changes' }}
                </button>
              </div>
            </div>
          </div>

        </main>
      </div>

      <!-- Agent Modal: Manage Sub-User Configuration -->
      <div v-if="activeAgentManageUser" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-[99999] select-none font-sans">
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-2xl max-w-sm w-full space-y-4 animate-bounce-in max-h-[90vh] overflow-y-auto relative">
          <div class="flex justify-between items-center border-b border-slate-200 pb-2">
            <h3 class="font-black text-slate-808 text-sm font-bold text-slate-900">Manage Sub-User Settings</h3>
            <button @click="activeAgentManageUser = null" class="text-slate-444 hover:text-rose-500 transition-all"><i class="fa-solid fa-xmark text-lg"></i></button>
          </div>

          <div class="space-y-4 text-xs text-slate-655 font-sans">
            <div>
              <p class="text-slate-404 font-bold">Username (Read-Only)</p>
              <p class="text-sm font-black text-slate-808 mt-1 font-mono font-bold">{{ activeAgentManageUser.name }}</p>
            </div>

            <div class="bg-indigo-50/30 border border-slate-100 p-3 rounded-2xl flex justify-between items-center">
              <div>
                <p class="font-black text-slate-800 font-bold">DEVELOPER API ACCESS</p>
                <p class="text-[9px] text-slate-404 font-medium font-semibold">Allow user to generate numbers via API</p>
              </div>
              <button @click="activeAgentManageUser.api_key_approved = !activeAgentManageUser.api_key_approved" :class="activeAgentManageUser.api_key_approved ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-600'" class="px-3 py-1.5 rounded-lg font-black transition-all">
                {{ activeAgentManageUser.api_key_approved ? 'ACTIVE' : 'INACTIVE' }}
              </button>
            </div>

            <div class="flex justify-between items-center bg-slate-50 p-2.5 rounded-xl border">
              <span class="text-[10px] text-slate-404 font-bold">Compromised Key?</span>
              <button @click="agentGenerateApiKey = true" class="bg-purple-100 hover:bg-purple-200 text-purple-700 text-[10px] font-bold px-3 py-1.5 rounded-lg transition-all uppercase font-bold">
                Generate Key
              </button>
            </div>

            <div>
              <label class="text-slate-404 font-bold">Account Status</label>
              <select v-model="activeAgentManageUser.status" class="w-full mt-1.5 p-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 outline-none focus:border-indigo-600 transition font-semibold">
                <option value="approved">Active (Can Work)</option>
                <option value="pending">Pending Approval</option>
                <option value="banned">Banned (Suspended)</option>
              </select>
            </div>

            <div>
              <label class="text-slate-404 font-bold">Set User Pay Rate (Max: ৳{{ parseFloat(user?.otp_rate || 0).toFixed(2) }})</label>
              <input type="number" step="0.01" v-model.number="activeAgentManageUser.otp_rate" class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-slate-800 font-mono outline-none focus:border-indigo-600 transition font-bold" />
            </div>

            <div>
              <label class="text-slate-404 font-bold">Transfer Balance from My Wallet (৳)</label>
              <input type="number" step="1" v-model.number="agentTransferAmount" placeholder="e.g. 100" class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-slate-808 font-mono outline-none focus:border-indigo-600 transition font-bold" />
            </div>

            <div>
              <label class="text-slate-404 font-bold">Set Withdraw Secure PIN (4 Digits)</label>
              <input type="password" maxlength="4" v-model="agentWithdrawPin" placeholder="e.g. 1234" class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-slate-808 font-mono outline-none focus:border-indigo-600 transition font-bold" />
            </div>

            <div>
              <label class="text-slate-404 font-bold">Reset Password (Keep empty to unchanged)</label>
              <input type="text" v-model="agentNewUserPassword" placeholder="New Password..." class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-slate-808 outline-none focus:border-indigo-600 transition font-bold" />
            </div>
          </div>

          <div class="flex gap-2 pt-2 font-bold select-none">
            <button @click="activeAgentManageUser = null" class="bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold py-3.5 rounded-xl text-xs transition flex-1">
              Cancel
            </button>
            <button @click="submitAgentManageUserChanges" class="bg-indigo-600 hover:bg-indigo-700 text-white font-black py-3.5 rounded-xl text-xs transition flex-1">
              Update User Details
            </button>
          </div>
        </div>
      </div>

      <!-- Agent Modal: Live Sub-User Status View -->
      <div v-if="activeSubUserStatus" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-[99999] select-none font-sans text-xs">
        <div class="bg-white p-6 rounded-3xl border shadow-2xl max-w-sm w-full space-y-4 animate-bounce-in">
          <div class="flex justify-between items-center border-b pb-2">
            <h3 class="font-black text-slate-808 text-sm">Sub-User Account Summary</h3>
            <button @click="activeSubUserStatus = null" class="text-slate-444 hover:text-rose-500 transition-all"><i class="fa-solid fa-xmark text-lg"></i></button>
          </div>

          <div class="space-y-3 font-semibold text-slate-707">
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">User Name</span>
              <span class="font-bold text-slate-808">{{ activeSubUserStatus.name }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">User ID Code</span>
              <span class="font-mono text-indigo-600 font-bold">{{ activeSubUserStatus.id_code }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Email Address</span>
              <span class="select-all text-slate-808">{{ activeSubUserStatus.email }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Joined Date</span>
              <span class="font-mono">{{ activeSubUserStatus.join_date }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Account Age (id er boyos)</span>
              <span class="font-bold text-slate-808">{{ activeSubUserStatus.account_age }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Today's OTP Hits</span>
              <span class="bg-indigo-100 text-indigo-707 px-2.5 py-0.5 rounded-full font-mono">{{ activeSubUserStatus.today_otp }} OTPs</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Yesterday's OTP Hits</span>
              <span class="bg-slate-100 text-slate-707 px-2.5 py-0.5 rounded-full font-mono">{{ activeSubUserStatus.yesterday_otp }} OTPs</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Wallet Balance</span>
              <span class="text-emerald-600 font-bold text-sm font-mono">৳ {{ activeSubUserStatus.balance }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-404">System Status</span>
              <span class="uppercase font-black text-indigo-600">{{ activeSubUserStatus.account_status }}</span>
            </div>
          </div>

          <button @click="activeSubUserStatus = null" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl">Close Summary</button>
        </div>
      </div>

    </div>

  </div>

  <script>
    const { createApp, ref, onMounted, computed } = Vue;

    try {
      createApp({
        setup() {
          const userLoaded = ref(false); 
          const user = ref(null);
          const profile = ref(null);
          const authName = ref('');
          const authEmail = ref('');
          const authPassword = ref('');
          const authAgentEmail = ref(''); 
          const isRegistering = ref(false);
          const authLoading = ref(false);

          const currentTab = ref('dashboard');
          const announcement = ref('');
          const mobileMenuOpen = ref(false);
          
          const allocations = ref([]);
          const liveLogs = ref([]);
          const successOtps = ref([]);
          
          const walletAddressInput = ref('');
          const walletLoading = ref(false);
          const apiGenLoading = ref(false);

          const searchQuery = ref('');

          const showToast = ref(false);
          const toastMessage = ref('');
          
          let generalTimer = null;
          let consoleTimer = null;

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

          const serviceRates = ref({
            facebook: { rate: 0.40, status: 'ON' },
            instagram: { rate: 0.40, status: 'ON' },
            whatsapp: { rate: 0.00, status: 'OFF' },
            telegram: { rate: 0.00, status: 'OFF' },
            google: { rate: 0.40, status: 'ON' },
            generic: { rate: 0.40, status: 'ON' }
          });

          // Live Access
          const liveAccessSearchQuery = ref('');
          const openAccordions = ref({});

          // Agent Configurations
          const agentUsers = ref([]);
          const activeAgentManageUser = ref(null);
          const activeSubUserStatus = ref(null);
          const agentNewUserPassword = ref('');
          const agentTransferAmount = ref('');
          const agentWithdrawPin = ref('');
          const agentGenerateApiKey = ref(false);
          const agentAutoApprove = ref(true);
          const agentAutoRate = ref(0.40);
          const subUsersWithdrawals = ref([]);
          const agentStats = ref({
            today_success_otp: 0,
            today_revenue: 0.00,
            yesterday_success: 0,
            yesterday_revenue: 0.00,
            days7_success: 0,
            days7_revenue: 0.00,
            days30_success: 0,
            days30_revenue: 0.00,
            lifetime_success: 0,
            lifetime_revenue: 0.00,
            top_services: [],
            top_users: [],
            unseen_users: []
          });

          // Telegram edit
          const profileTelegramUsername = ref('');
          const profileTelegramLoading = ref(false);

          const copiedStates = ref({});

          const countryPrefixes = {
            "880": { name: "Bangladesh", flag: "🇧🇩" },
            "91": { name: "India", flag: "🇮🇳" },
            "1": { name: "USA/Canada", flag: "🇺🇸" }
          };

          const triggerToast = (msg) => {
            toastMessage.value = msg;
            showToast.value = true;
            setTimeout(() => { showToast.value = false; }, 2000);
          };

          const copyToClipboard = (text, key = null) => {
            if (!text) return;
            navigator.clipboard.writeText(text);
            triggerToast("Copied successfully! ✅");
            if (key) {
              copiedStates.value[key] = true;
              setTimeout(() => { copiedStates.value[key] = false; }, 2000);
            }
          };

          const navigateMobile = (tabName) => {
            currentTab.value = tabName;
            mobileMenuOpen.value = false;
          };

          const filterByDate = (items, filterType, dateKey = 'createdAt') => {
            const now = new Date();
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
            const yesterdayStart = todayStart - 24 * 60 * 60 * 1000;
            const sevenDaysAgo = todayStart - 7 * 24 * 60 * 60 * 1000;
            const fifteenDaysAgo = todayStart - 15 * 24 * 60 * 60 * 1000;
            const thirtyDaysAgo = todayStart - 30 * 24 * 60 * 60 * 1000;

            return items.filter(item => {
              if (!item[dateKey]) return false;
              const itemTime = new Date(item[dateKey]).getTime();
              if (filterType === 'today') {
                return itemTime >= todayStart;
              } else if (filterType === 'yesterday') {
                return itemTime >= yesterdayStart && itemTime < todayStart;
              } else if (filterType === '7days') {
                return itemTime >= sevenDaysAgo;
              } else if (filterType === '15days') {
                return itemTime >= fifteenDaysAgo;
              } else if (filterType === '30days') {
                return itemTime >= thirtyDaysAgo;
              } else {
                return true;
              }
            });
          };

          const startPolling = () => {
            stopPolling();
            fetchGeneralData();
            // Polling speed adjusted to 5s to ensure complete real-time accuracy across workspaces
            generalTimer = setInterval(fetchGeneralData, 5000);
          };

          const stopPolling = () => {
            if (generalTimer) clearInterval(generalTimer);
          };

          const fetchGeneralData = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) {
              userLoaded.value = true;
              return;
            }

            try {
              const profileRes = await fetch('user_api.php?action=me', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              
              if (profileRes.status === 401 || profileRes.status === 402) {
                signOut();
                userLoaded.value = true;
                return;
              }

              const profileData = await profileRes.json();
              if (profileData.status === 'success') {
                if (profileData.user.role !== 'agent') {
                  // Direct Redirect normal users to normal user portal index page
                  window.location.href = 'index.php';
                  return;
                }
                user.value = profileData.user;
                profile.value = profileData.user;
                announcement.value = profileData.announcement;
                
                if (profileData.user.wallet_address && !walletAddressInput.value) {
                  walletAddressInput.value = profileData.user.wallet_address;
                }
                
                if (profileData.user.telegram_username && !profileTelegramUsername.value) {
                  profileTelegramUsername.value = profileData.user.telegram_username;
                }

                agentAutoApprove.value = !!profileData.user.agent_auto_approve;
                agentAutoRate.value = parseFloat(profileData.user.agent_auto_rate || 0.40);
                fetchAgentSpecificData();
              }
            } catch (e) {}

            userLoaded.value = true; 

            try {
              const boardRes = await fetch('user_api.php?action=leaderboard', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const boardData = await boardRes.json();
              if (boardData.status === 'success') {
                leaderboardData.value.today = boardData.today || [];
                leaderboardData.value.weekly = boardData.weekly || [];
                leaderboardData.value.lifetime = boardData.lifetime || [];
                personalRank.value = boardData.user_rank || 0;
                personalOtpCount.value = boardData.user_count || 0;
              }
            } catch (e) {}
          };

          const fetchAgentSpecificData = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;

            try {
              const res = await fetch('user_api.php?action=agent-users', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data.status === 'success') {
                agentUsers.value = data.users || [];
              }
            } catch(e) {}

            try {
              const res = await fetch('user_api.php?action=agent-stats', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data.status === 'success') {
                agentStats.value = {
                  today_success_otp: data.today_success_otp || 0,
                  today_revenue: data.today_revenue || 0.00,
                  yesterday_success: data.yesterday_success || 0,
                  yesterday_revenue: data.yesterday_revenue || 0.00,
                  days7_success: data.days7_success || 0,
                  days7_revenue: data.days7_revenue || 0.00,
                  days30_success: data.days30_success || 0,
                  days30_revenue: data.days30_revenue || 0.00,
                  lifetime_success: data.lifetime_success || 0,
                  lifetime_revenue: data.lifetime_revenue || 0.00,
                  top_services: data.top_services || [],
                  top_users: data.top_users || [],
                  unseen_users: data.unseen_users || []
                };
              }
            } catch(e) {}

            try {
              const res = await fetch('user_api.php?action=agent-withdrawals', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data.status === 'success') {
                subUsersWithdrawals.value = data.withdrawals || [];
              }
            } catch(e) {}

            try {
              const mRes = await fetch('user_api.php?action=withdrawal-methods', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const mData = await mRes.json();
              if (mData.status === 'success') {
                withdrawalMethods.value = mData.methods || [];
              }
            } catch(e) {}

            try {
              const res = await fetch('user_api.php?action=user-withdrawals', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const data = await res.json();
              if (data.status === 'success') {
                withdrawalsHistory.value = data.withdrawals || [];
              }
            } catch (e) {}
          };

          const subUsersApprovedWithdrawals = computed(() => {
            return subUsersWithdrawals.value.filter(w => w.status === 'approved');
          });
          const subUsersPendingWithdrawals = computed(() => {
            return subUsersWithdrawals.value.filter(w => w.status === 'pending');
          });
          const subUsersRejectedWithdrawals = computed(() => {
            return subUsersWithdrawals.value.filter(w => w.status === 'rejected');
          });
          const subUsersWithdrawalSum = computed(() => {
            return subUsersApprovedWithdrawals.value.reduce((sum, w) => sum + parseFloat(w.amount || 0), 0);
          });

          const filteredWithdrawals = computed(() => {
            return filterByDate(withdrawalsHistory.value, withdrawHistoryFilter.value, 'createdAt');
          });

          const filteredAgentUsers = computed(() => {
            const list = agentUsers.value || [];
            const q = searchQuery.value ? searchQuery.value.toLowerCase().trim() : '';
            if (!q) return list;
            return list.filter(u => 
              u && (
                (u.name && u.name.toLowerCase().includes(q)) || 
                (u.email && u.email.toLowerCase().includes(q)) ||
                (u.id_code && u.id_code.toLowerCase().includes(q))
              )
            );
          });

          const topNumberUsers = computed(() => {
            if (!agentUsers.value) return [];
            return leaderboardData.value.lifetime.filter(x => agentUsers.value.some(su => su.uid === x.uid));
          });

          const topOtpUsers = computed(() => {
            if (!agentUsers.value) return [];
            return leaderboardData.value.lifetime.filter(x => agentUsers.value.some(su => su.uid === x.uid));
          });

          const inactiveUsersList = computed(() => {
            if (!agentUsers.value) return [];
            const activeUserIds = new Set(allocations.value.map(a => a.userId));
            return agentUsers.value.filter(u => u.role === 'user' && !activeUserIds.has(u.uid));
          });

          const agentUpdateUserStatusDirect = async (uid, statusValue) => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            try {
              const res = await fetch('user_api.php?action=agent-update-user', {
                method: 'POST',
                headers: { 
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ uid: uid, status: statusValue })
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast("Sub-user status updated successfully! ✅");
                fetchAgentSpecificData();
              } else {
                alert(data.message);
              }
            } catch(e) {}
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
                triggerToast("Payout address successfully configured! ✅");
                fetchGeneralData();
              } else {
                alert(data.message);
              }
            } catch (e) {
              alert("Failed to update payout address.");
            }
            walletLoading.value = false;
          };

          const openAgentManageUserModal = (subUser) => {
            activeAgentManageUser.value = { ...subUser };
            agentNewUserPassword.value = '';
            agentTransferAmount.value = '';
            agentWithdrawPin.value = '';
            agentGenerateApiKey.value = false;
          };

          // Fetch sub-user live statistics & metrics
          const viewSubUserStatus = async (uid) => {
            try {
              const res = await fetch('agent_manager.php?action=subuser-status&uid=' + uid, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('mino_session_token')}` }
              });
              const data = await res.json();
              if (data.status === 'success') {
                activeSubUserStatus.value = data.data;
              } else {
                alert(data.message);
              }
            } catch(e) {}
          };

          const submitAgentManageUserChanges = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token || !activeAgentManageUser.value) return;

            try {
              const res = await fetch('user_api.php?action=agent-update-user', {
                method: 'POST',
                headers: { 
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                  uid: activeAgentManageUser.value.uid,
                  otp_rate: activeAgentManageUser.value.otp_rate,
                  status: activeAgentManageUser.value.status,
                  password: agentNewUserPassword.value,
                  transfer_amount: agentTransferAmount.value,
                  withdraw_pin: agentWithdrawPin.value,
                  generate_api_key: agentGenerateApiKey.value,
                  api_key_approved: activeAgentManageUser.value.api_key_approved
                })
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast(data.message);
                activeAgentManageUser.value = null;
                fetchAgentSpecificData();
                fetchGeneralData();
              } else {
                alert(data.message);
              }
            } catch(e) {
              alert("Process failed.");
            }
          };

          const submitWithdrawal = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            if (withdrawAmount.value < 50) {
              alert("মিনিমাম উইথড্র ৫০ টাকা হতে হবে।");
              return;
            }
            if (!withdrawMethod.value) {
              alert("পেমেন্ট মেথড সিলেক্ট করুন।");
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
                  method: withdrawMethod.value,
                  address: profile.value.wallet_address,
                  withdraw_pin: withdrawPinInput.value
                })
              });
              const data = await res.json();
              if (data.status === 'success') {
                alert("Your withdrawal request has been submitted.");
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

          const saveAgentSettings = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            try {
              const res = await fetch('user_api.php?action=agent-save-settings', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                  agent_auto_approve: agentAutoApprove.value ? 1 : 0,
                  agent_auto_rate: agentAutoRate.value
                })
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast(data.message);
                fetchGeneralData();
              } else {
                alert(data.message);
              }
            } catch (e) {
              alert("Error saving agent configurations.");
            }
          };

          const saveProfileChanges = async () => {
            const token = localStorage.getItem('mino_session_token');
            if (!token) return;
            profileTelegramLoading.value = true;
            try {
              const res = await fetch('user_api.php?action=update-profile', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                  telegram_username: profileTelegramUsername.value
                })
              });
              const data = await res.json();
              if (data.status === 'success') {
                triggerToast(data.message);
                fetchGeneralData();
              } else {
                alert(data.message);
              }
            } catch (e) {
              alert("Could not update profile fields.");
            }
            profileTelegramLoading.value = false;
          };

          const getUserIdCode = (userId) => {
            if (!userId) return 'N/A';
            const found = agentUsers.value.find(u => u.uid === userId || u.id === userId);
            return found ? found.id_code : 'N/A';
          };

          const signOut = () => {
            localStorage.removeItem('mino_session_token');
            user.value = null;
            profile.value = null;
            stopPolling();
            window.location.href = 'index.php';
          };

          const formatTimestamp = (timestamp) => {
            if (!timestamp) return 'N/A';
            const d = new Date(timestamp);
            return d.toLocaleString();
          };

          onMounted(() => {
            const token = localStorage.getItem('mino_session_token');
            if (token) {
              startPolling();
            } else {
              window.location.href = 'index.php';
            }
          });

          return {
            userLoaded, user, profile, authName, authEmail, authPassword, authAgentEmail, isRegistering, authLoading,
            currentTab, announcement, mobileMenuOpen, navigateMobile, liveLogs, successOtps,
            searchQuery, showToast, toastMessage, copyToClipboard,
            signOut, formatTimestamp, copiedStates, agentTransferAmount, agentWithdrawPin, agentGenerateApiKey,
            agentUsers, activeAgentManageUser, activeSubUserStatus, agentNewUserPassword, subUsersWithdrawals, agentStats,
            subUsersApprovedWithdrawals, subUsersPendingWithdrawals, subUsersRejectedWithdrawals, subUsersWithdrawalSum,
            agentUpdateUserStatusDirect, openAgentManageUserModal, submitAgentManageUserChanges, getUserIdCode,
            agentAutoApprove, agentAutoRate, saveAgentSettings, profileTelegramUsername, profileTelegramLoading, saveProfileChanges,
            topNumberUsers, topOtpUsers, inactiveUsersList, leaderboardTab, leaderboardData, personalRank, personalOtpCount,
            viewSubUserStatus, handleUpdateWallet, walletAddressInput, walletLoading, withdrawAmount, withdrawMethod,
            withdrawalMethods, submitWithdrawal, withdrawalsHistory, withdrawHistoryFilter, filteredWithdrawals, withdrawPinInput,
            filteredAgentUsers
          };
        }
      }).mount('#app');
    } catch (e) {
      console.error("Vue Mount Error:", e);
    }
  </script>
</body>
</html>