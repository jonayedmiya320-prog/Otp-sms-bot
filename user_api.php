<?php
require_once 'security.php';
handle_pre_requests(false);

$action = isset($_GET['action']) ? $_GET['action'] : '';

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

switch ($action) {
    case 'register':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $data = json_decode(file_get_contents('php://input'), true) ?: [];
        $email = isset($data['email']) ? trim($data['email']) : '';
        $password = isset($data['password']) ? trim($data['password']) : '';
        $name = isset($data['name']) ? trim($data['name']) : '';
        $agent_email = isset($data['agent_email']) ? trim($data['agent_email']) : '';

        if (empty($email) || empty($password)) {
            echo json_encode(['status' => 'error', 'message' => 'Email and password are required.']);
            exit();
        }

        // 🚨 MANDATORY AGENT EMAIL CHECK
        if (empty($agent_email)) {
            echo json_encode(['status' => 'error', 'message' => 'Agent Email is required. You cannot create an account without a valid Agent.']);
            exit();
        }

        $pdo = get_db_connection();

        // Check if agent exists in database
        $stmtAgent = $pdo->prepare("SELECT * FROM users WHERE email = ? AND role = 'agent'");
        $stmtAgent->execute([$agent_email]);
        $agent = $stmtAgent->fetch();

        if (!$agent) {
            echo json_encode(['status' => 'error', 'message' => 'Invalid Agent Email. No active agent found with this email address.']);
            exit();
        }

        // Check quota limit of agent
        $stmtCount = $pdo->prepare("SELECT COUNT(*) FROM users WHERE agent_uid = ? AND role = 'user'");
        $stmtCount->execute([$agent['uid']]);
        $used_quota = (int)$stmtCount->fetchColumn();
        $agent_limit = isset($agent['agent_limit']) ? (int)$agent['agent_limit'] : 120;

        if ($used_quota >= $agent_limit) {
            echo json_encode(['status' => 'error', 'message' => 'This Agent has reached their maximum user account quota limit.']);
            exit();
        }

        $agent_uid = $agent['uid'];

        if (empty($name)) {
            $parts = explode('@', $email);
            $name = $parts[0];
        }

        $stmtEmail = $pdo->prepare("SELECT COUNT(*) FROM users WHERE email = ?");
        $stmtEmail->execute([$email]);
        if ($stmtEmail->fetchColumn() > 0) {
            echo json_encode(['status' => 'error', 'message' => 'This email address is already registered. Please Log In.']);
            exit();
        }

        $status = 'approved';
        $user_otp_rate = isset($agent['agent_auto_rate']) ? (float)$agent['agent_auto_rate'] : 0.40;

        $uid = "usr_" . bin2hex(random_bytes(8));
        $user_data = [
            'uid' => $uid,
            'name' => $name,
            'email' => $email,
            'password' => hash_user_password($password),
            'api_key' => '',
            'api_key_approved' => false,
            'balance' => 0.00,
            'otp_rate' => $user_otp_rate,
            'wallet_address' => '', 
            'id_code' => "MINO-" . rand(1000, 9999),
            'status' => $status, 
            'role' => 'user',
            'agent_uid' => $agent_uid,
            'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
        ];
        
        db_request('/users/' . $uid, 'PUT', $user_data);
        echo json_encode([
            'status' => 'success', 
            'message' => 'Account created and approved successfully!', 
            'token' => $uid, 
            'user' => public_user_data($user_data)
        ]);
        exit();

    case 'login':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $data = json_decode(file_get_contents('php://input'), true) ?: [];
        $email = isset($data['email']) ? trim($data['email']) : '';
        $password = isset($data['password']) ? trim($data['password']) : '';

        if (empty($email) || empty($password)) {
            echo json_encode(['status' => 'error', 'message' => 'Email and password are required']);
            exit();
        }

        $pdo = get_db_connection();
        $stmtLogin = $pdo->prepare("SELECT * FROM users WHERE email = ? LIMIT 1");
        $stmtLogin->execute([$email]);
        $u = $stmtLogin->fetch();
        if ($u && verify_user_password($password, (string)($u['password'] ?? ''))) {
            // Rehash automatically when PHP's recommended password algorithm
            // changes, without ever returning the stored hash to the client.
            if (password_needs_rehash((string)$u['password'], PASSWORD_DEFAULT)) {
                $stmtRehash = $pdo->prepare("UPDATE users SET password = ? WHERE uid = ?");
                $stmtRehash->execute([hash_user_password($password), $u['uid']]);
            }

            $u = handle_row_types('users', $u);
            $status = isset($u['status']) ? $u['status'] : 'approved';
            
            if ($status === 'banned') {
                http_response_code(403);
                echo json_encode(['status' => 'error', 'message' => 'Your account has been suspended.']);
                exit();
            }

            if ($status === 'pending') {
                $stmtApprove = $pdo->prepare("UPDATE users SET status = 'approved' WHERE uid = ?");
                $stmtApprove->execute([$u['uid']]);
                $u['status'] = 'approved';
            }

            echo json_encode(['status' => 'success', 'token' => $u['uid'], 'user' => public_user_data($u)]);
            exit();
        }
        http_response_code(401);
        echo json_encode(['status' => 'error', 'message' => 'Incorrect email or password.']);
        exit();

    case 'me':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }
        $announcement = db_request_cached('/settings/announcement', 'GET', null, 5) ?: '';
        echo json_encode(['status' => 'success', 'user' => $user, 'announcement' => $announcement]);
        exit();

    case 'live-access':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }
        $parsed = parse_live_access_response();
        header("Content-Type: application/json");
        echo json_encode($parsed);
        exit();

    case 'generate-key':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }
        
        $user_id = $user['uid'];
        $api_key_approved = isset($user['api_key_approved']) ? $user['api_key_approved'] : false;
        $existing_key = isset($user['api_key']) ? $user['api_key'] : '';
        
        if (!empty($existing_key) && !$api_key_approved) {
            echo json_encode(['status' => 'success', 'message' => 'API Key request is pending approval', 'api_key' => $existing_key, 'api_key_approved' => false]);
            exit();
        } elseif (!empty($existing_key) && $api_key_approved) {
            echo json_encode(['status' => 'success', 'message' => 'API Key is already active and approved', 'api_key' => $existing_key, 'api_key_approved' => true]);
            exit();
        }
        
        $unique_key = 'mino_live_' . bin2hex(random_bytes(16));
        $updates = [
            'api_key' => $unique_key,
            'api_key_approved' => false
        ];
        db_request('/users/' . $user_id, 'PATCH', $updates);
        echo json_encode(['status' => 'success', 'message' => 'API Key generated. Awaiting approval.', 'api_key' => $unique_key, 'api_key_approved' => false]);
        exit();

    case 'update-wallet':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }
        
        $data = json_decode(file_get_contents('php://input'), true) ?: [];
        $wallet_address = isset($data['wallet_address']) ? trim($data['wallet_address']) : '';
        
        $user_id = $user['uid'];
        db_request('/users/' . $user_id . '/wallet_address', 'PUT', $wallet_address);
        echo json_encode(['status' => 'success', 'message' => 'Wallet updated successfully', 'wallet_address' => $wallet_address]);
        exit();

    case 'update-profile':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }
        $data = json_decode(file_get_contents('php://input'), true) ?: [];
        $telegram = isset($data['telegram_username']) ? trim($data['telegram_username']) : '';

        $pdo = get_db_connection();
        $stmt = $pdo->prepare("UPDATE users SET telegram_username = ? WHERE uid = ?");
        $stmt->execute([$telegram, $user['uid']]);

        echo json_encode(['status' => 'success', 'message' => 'Profile details saved successfully']);
        exit();

    case 'withdrawal-methods':
        $pdo = get_db_connection();
        $stmt = $pdo->query("SELECT * FROM withdrawal_methods");
        $methods = $stmt->fetchAll();
        echo json_encode(['status' => 'success', 'methods' => $methods]);
        exit();

    case 'withdraw':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }
        
        $data = json_decode(file_get_contents('php://input'), true) ?: [];
        $amount = isset($data['amount']) ? (float)$data['amount'] : 0.0;
        $method = isset($data['method']) ? trim($data['method']) : '';
        $address = isset($data['address']) ? trim($data['address']) : '';
        $withdraw_pin = isset($data['withdraw_pin']) ? trim($data['withdraw_pin']) : '';
        
        if ($amount < 50.0) {
            echo json_encode(['status' => 'error', 'message' => 'মিনিমাম উইথড্র ৫০ টাকা হতে হবে।']);
            exit();
        }
        $current_balance = isset($user['balance']) ? (float)$user['balance'] : 0.0;
        if ($amount > $current_balance) {
            echo json_encode(['status' => 'error', 'message' => 'Insufficient wallet balance.']);
            exit();
        }
        if (empty($address)) {
            echo json_encode(['status' => 'error', 'message' => 'A withdrawal destination address is required.']);
            exit();
        }

        if (!empty($user['withdraw_pin']) && $user['withdraw_pin'] !== $withdraw_pin) {
            echo json_encode(['status' => 'error', 'message' => 'Incorrect 4-digit Withdraw PIN entered.']);
            exit();
        }

        $pdo = get_db_connection();
        $stmtM = $pdo->prepare("SELECT COUNT(*) FROM withdrawal_methods WHERE method_name = ?");
        $stmtM->execute([$method]);
        if ($stmtM->fetchColumn() == 0) {
            echo json_encode(['status' => 'error', 'message' => 'Selected Withdrawal Method is not active.']);
            exit();
        }
        
        $user_id = $user['uid'];
        $new_balance = $current_balance - $amount;
        db_request('/users/' . $user_id . '/balance', 'PUT', $new_balance);
        
        $with_id = "wd_" . bin2hex(random_bytes(8));
        $withdrawal_data = [
            'id' => $with_id,
            'userId' => $user_id,
            'userEmail' => $user['email'],
            'userName' => $user['name'],
            'amount' => $amount,
            'method' => $method,
            'address' => $address,
            'status' => 'pending',
            'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
        ];
        db_request('/withdrawals/' . $with_id, 'PUT', $withdrawal_data);
        echo json_encode(['status' => 'success', 'message' => 'Withdrawal request submitted successfully.', 'new_balance' => $new_balance]);
        exit();

    case 'user-withdrawals':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }
        $pdo = get_db_connection();
        $stmt = $pdo->prepare("SELECT * FROM withdrawals WHERE userId = ? ORDER BY createdAt DESC");
        $stmt->execute([$user['uid']]);
        $user_wd = $stmt->fetchAll();
        echo json_encode(['status' => 'success', 'withdrawals' => $user_wd]);
        exit();

    case 'service-rates':
        try {
            $raw_rates = db_request_cached('/settings/service_rates', 'GET', null, 5) ?: [];
            $default_services = ['facebook', 'instagram', 'whatsapp', 'telegram', 'google', 'generic'];
            $rates = [];
            foreach ($default_services as $svc) {
                $item = isset($raw_rates[$svc]) ? $raw_rates[$svc] : null;
                if (is_array($item)) {
                    $rates[$svc] = [
                        'rate' => (float)(isset($item['rate']) ? $item['rate'] : 0.40),
                        'status' => strtoupper(isset($item['status']) ? $item['status'] : 'ON')
                    ];
                } else {
                    $legacy_val = 0.40;
                    if ($item !== null) {
                        $legacy_val = (float)$item;
                    }
                    $rates[$svc] = [
                        'rate' => $legacy_val,
                        'status' => 'ON'
                    ];
                }
            }
            echo json_encode(['status' => 'success', 'rates' => $rates]);
        } catch (Exception $e) {
            echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);
        }
        exit();

    case 'user-allocations':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }

        $user_id = $user['uid'];
        $otp_rate = isset($user['otp_rate']) ? (float)$user['otp_rate'] : 0.40;

        $all_allocs_dict = db_query('/allocated_numbers', 'userId', $user_id) ?: [];
        $active_allocs_list = rows_to_list($all_allocs_dict);

        $has_active_allocations = false;
        foreach ($active_allocs_list as $alloc) {
            if (isset($alloc['status']) && $alloc['status'] === 'active') {
                $has_active_allocations = true;
                break;
            }
        }

        if ($has_active_allocations) {
            $service_rates_raw = db_request_cached('/settings/service_rates', 'GET', null, 5) ?: [];
            $service_rates = [];
            foreach ($service_rates_raw as $k => $v) {
                $service_rates[strtolower($k)] = $v;
            }

            try {
                $json_data = get_voltx_success_otp_cached();
                $meta = isset($json_data['meta']) ? $json_data['meta'] : [];
                if ((isset($meta['status']) && $meta['status'] === 'ok') || (isset($meta['code']) && $meta['code'] == 200)) {
                    $otps = isset($json_data['data']['otps']) ? $json_data['data']['otps'] : [];
                    foreach ($otps as $otp_item) {
                        $otp_num = str_replace(['+', ' '], '', isset($otp_item['number']) ? $otp_item['number'] : '');
                        
                        foreach ($active_allocs_list as &$alloc) {
                            $alloc_num = str_replace(['+', ' '], '', isset($alloc['number']) ? $alloc['number'] : '');
                            if (isset($alloc['status']) && $alloc['status'] === 'active' && 
                                (!empty($otp_num) && !empty($alloc_num)) &&
                                (strpos($alloc_num, $otp_num) !== false || strpos($otp_num, $alloc_num) !== false)) {
                                
                                $message = isset($otp_item['message']) ? trim($otp_item['message']) : '';
                                $otp_code = extract_otp_code($message);

                                if (empty($message) || empty($otp_code) || $otp_code === 'N/A') {
                                    continue;
                                }

                                $service = 'generic';
                                $msg_lower = strtolower($message);
                                if (strpos($msg_lower, 'facebook') !== false || strpos($msg_lower, 'fb') !== false) {
                                    $service = 'facebook';
                                } elseif (strpos($msg_lower, 'instagram') !== false || strpos($msg_lower, 'ig') !== false) {
                                    $service = 'instagram';
                                } elseif (strpos($msg_lower, 'whatsapp') !== false || strpos($msg_lower, 'wa') !== false) {
                                    $service = 'whatsapp';
                                } elseif (strpos($msg_lower, 'telegram') !== false || strpos($msg_lower, 'tg') !== false) {
                                    $service = 'telegram';
                                } elseif (strpos($msg_lower, 'google') !== false || strpos($msg_lower, 'g-') !== false) {
                                    $service = 'google';
                                }

                                $earned_revenue = get_scaled_service_rate($service, $otp_rate, $service_rates);

                                $pdo = get_db_connection();
                                $stmt_up = $pdo->prepare("UPDATE allocated_numbers SET status = 'completed', otp = ?, message = ? WHERE id = ? AND status = 'active'");
                                $stmt_up->execute([$otp_code, $message, $alloc['id']]);

                                if ($stmt_up->rowCount() > 0) {
                                    $alloc['status'] = 'completed'; 

                                    $stmt_bal = $pdo->prepare("UPDATE users SET balance = balance + ? WHERE uid = ?");
                                    $stmt_bal->execute([$earned_revenue, $user_id]);

                                    credit_agent_commission($pdo, $user_id, $earned_revenue);
                                    
                                    $otp_id = "otp_" . bin2hex(random_bytes(8));
                                    db_request('/otp_logs/' . $otp_id, 'PUT', [
                                        'userId' => $user_id,
                                        'number' => $alloc['number'],
                                        'service' => $service,
                                        'otpCode' => $otp_code,
                                        'message' => $message,
                                        'revenue' => $earned_revenue,
                                        'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
                                    ]);
                                }
                            }
                        }
                    }
                }
            } catch (Exception $e) {}
        }

        $now = new DateTime('now', new DateTimeZone('UTC'));
        foreach ($active_allocs_list as $alloc) {
            if (isset($alloc['status']) && $alloc['status'] === 'active') {
                $created_at_str = isset($alloc['createdAt']) ? $alloc['createdAt'] : '';
                if (!empty($created_at_str)) {
                    $created_at = parse_iso_datetime($created_at_str);
                    $elapsed_seconds = $now->getTimestamp() - $created_at->getTimestamp();
                    $expiry_limit = get_gateway_expiry_seconds();
                    if ($elapsed_seconds > $expiry_limit) { 
                        $alloc_id = $alloc['id'];
                        db_request('/allocated_numbers/' . $alloc_id . '/status', 'PUT', 'expired');
                    }
                }
            }
        }

        $refreshed_query = db_query('/allocated_numbers', 'userId', $user_id) ?: [];
        $refreshed_list = rows_to_list($refreshed_query);
        usort($refreshed_list, function($a, $b) {
            return strcmp(isset($b['createdAt']) ? $b['createdAt'] : '', isset($a['createdAt']) ? $a['createdAt'] : '');
        });

        echo json_encode(['status' => 'success', 'allocations' => $refreshed_list]);
        exit();

    case 'leaderboard':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Invalid API Key or Unauthorized access.']);
            exit();
        }

        $now = new DateTime('now', new DateTimeZone('UTC'));
        $today_limit = (clone $now)->modify('-25 hours')->format('Y-m-d H:i:s');
        $weekly_limit = (clone $now)->modify('-168 hours')->format('Y-m-d H:i:s');
        
        $pdo = get_db_connection();
        
        $stmtLife = $pdo->query("
            SELECT u.name, u.id_code, u.uid, COUNT(o.id) as count 
            FROM users u 
            JOIN otp_logs o ON u.uid = o.userId 
            GROUP BY u.uid 
            ORDER BY count DESC 
            LIMIT 100
        ");
        $l_rank = $stmtLife->fetchAll();
        
        $stmtWeek = $pdo->prepare("
            SELECT u.name, u.id_code, u.uid, COUNT(o.id) as count 
            FROM users u 
            JOIN otp_logs o ON u.uid = o.userId 
            WHERE o.createdAt >= ? 
            GROUP BY u.uid 
            ORDER BY count DESC 
            LIMIT 100
        ");
        $stmtWeek->execute([$weekly_limit]);
        $w_rank = $stmtWeek->fetchAll();
        
        $stmtToday = $pdo->prepare("
            SELECT u.name, u.id_code, u.uid, COUNT(o.id) as count 
            FROM users u 
            JOIN otp_logs o ON u.uid = o.userId 
            WHERE o.createdAt >= ? 
            GROUP BY u.uid 
            ORDER BY count DESC 
            LIMIT 100
        ");
        $stmtToday->execute([$today_limit]);
        $t_rank = $stmtToday->fetchAll();
        
        $stmtPersonal = $pdo->prepare("
            SELECT COUNT(id) FROM otp_logs WHERE userId = ?
        ");
        $stmtPersonal->execute([$user['uid']]);
        $user_otp_count = (int)$stmtPersonal->fetchColumn();
        
        $stmtPos = $pdo->prepare("
            SELECT COUNT(DISTINCT userId) + 1 
            FROM (
                SELECT userId, COUNT(id) as cnt 
                FROM otp_logs 
                GROUP BY userId
            ) as t 
            WHERE cnt > ?
        ");
        $stmtPos->execute([$user_otp_count]);
        $user_rank_position = (int)$stmtPos->fetchColumn();
        
        echo json_encode([
            'status' => 'success',
            'today' => $t_rank,
            'weekly' => $w_rank,
            'lifetime' => $l_rank,
            'user_rank' => $user_rank_position,
            'user_count' => $user_otp_count
        ]);
        exit();

    case 'agent-users':
        $user = get_current_user_optimized();
        if (!$user || $user['role'] !== 'agent') {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Agent access required']);
            exit();
        }
        $pdo = get_db_connection();
        $stmt = $pdo->prepare("SELECT * FROM users WHERE agent_uid = ? ORDER BY createdAt DESC");
        $stmt->execute([$user['uid']]);
        $sub_users = $stmt->fetchAll();
        $sub_users_clean = array_map(function($u) {
            return handle_row_types('users', $u);
        }, $sub_users);
        echo json_encode(['status' => 'success', 'users' => $sub_users_clean]);
        exit();

    case 'agent-stats':
        $user = get_current_user_optimized();
        if (!$user || $user['role'] !== 'agent') {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Agent access required']);
            exit();
        }
        $pdo = get_db_connection();
        $agent_uid = $user['uid'];
        $agent_max_rate = isset($user['otp_rate']) ? (float)$user['otp_rate'] : 0.63;

        $now = new DateTime('now', new DateTimeZone('UTC'));
        $today_str = $now->format('Y-m-d');
        $yesterday_str = (clone $now)->modify('-1 day')->format('Y-m-d');
        $days7_str = (clone $now)->modify('-7 days')->format('Y-m-d H:i:s');
        $days30_str = (clone $now)->modify('-30 days')->format('Y-m-d H:i:s');

        $stmtSub = $pdo->prepare("SELECT uid FROM users WHERE agent_uid = ?");
        $stmtSub->execute([$agent_uid]);
        $sub_uids = $stmtSub->fetchAll(PDO::FETCH_COLUMN);

        if (empty($sub_uids)) {
            echo json_encode([
                'status' => 'success',
                'today_success_otp' => 0, 'today_revenue' => 0.00,
                'yesterday_success' => 0, 'yesterday_revenue' => 0.00,
                'days7_success' => 0, 'days7_revenue' => 0.00,
                'days30_success' => 0, 'days30_revenue' => 0.00,
                'lifetime_success' => 0, 'lifetime_revenue' => 0.00,
                'top_services' => [], 'top_users' => [], 'unseen_users' => []
            ]);
            exit();
        }

        $in_clause = implode(',', array_fill(0, count($sub_uids), '?'));

        $stmtT = $pdo->prepare("SELECT COUNT(*), SUM(revenue) FROM otp_logs WHERE userId IN ($in_clause) AND DATE(createdAt) = ?");
        $stmtT->execute(array_merge($sub_uids, [$today_str]));
        $rowT = $stmtT->fetch(PDO::FETCH_NUM);
        $today_count = (int)$rowT[0];
        $today_user_rev = (float)$rowT[1];
        $today_agent_rev = max(0.00, ($today_count * $agent_max_rate) - $today_user_rev);

        $stmtY = $pdo->prepare("SELECT COUNT(*), SUM(revenue) FROM otp_logs WHERE userId IN ($in_clause) AND DATE(createdAt) = ?");
        $stmtY->execute(array_merge($sub_uids, [$yesterday_str]));
        $rowY = $stmtY->fetch(PDO::FETCH_NUM);
        $yesterday_count = (int)$rowY[0];
        $yesterday_user_rev = (float)$rowY[1];
        $yesterday_agent_rev = max(0.00, ($yesterday_count * $agent_max_rate) - $yesterday_user_rev);

        $stmt7 = $pdo->prepare("SELECT COUNT(*), SUM(revenue) FROM otp_logs WHERE userId IN ($in_clause) AND createdAt >= ?");
        $stmt7->execute(array_merge($sub_uids, [$days7_str]));
        $row7 = $stmt7->fetch(PDO::FETCH_NUM);
        $days7_count = (int)$row7[0];
        $days7_user_rev = (float)$row7[1];
        $days7_agent_rev = max(0.00, ($days7_count * $agent_max_rate) - $days7_user_rev);

        $stmt30 = $pdo->prepare("SELECT COUNT(*), SUM(revenue) FROM otp_logs WHERE userId IN ($in_clause) AND createdAt >= ?");
        $stmt30->execute(array_merge($sub_uids, [$days30_str]));
        $row30 = $stmt30->fetch(PDO::FETCH_NUM);
        $days30_count = (int)$row30[0];
        $days30_user_rev = (float)$row30[1];
        $days30_agent_rev = max(0.00, ($days30_count * $agent_max_rate) - $days30_user_rev);

        $stmtL = $pdo->prepare("SELECT COUNT(*), SUM(revenue) FROM otp_logs WHERE userId IN ($in_clause)");
        $stmtL->execute($sub_uids);
        $rowL = $stmtL->fetch(PDO::FETCH_NUM);
        $lifetime_count = (int)$rowL[0];
        $lifetime_user_rev = (float)$rowL[1];
        $lifetime_agent_rev = max(0.00, ($lifetime_count * $agent_max_rate) - $lifetime_user_rev);

        $stmtSvc = $pdo->prepare("SELECT service as name, COUNT(*) as count FROM otp_logs WHERE userId IN ($in_clause) GROUP BY service ORDER BY count DESC LIMIT 10");
        $stmtSvc->execute($sub_uids);
        $top_services = $stmtSvc->fetchAll();

        $stmtTopU = $pdo->prepare("SELECT u.name, u.id_code, COUNT(o.id) as count FROM users u JOIN otp_logs o ON u.uid = o.userId WHERE u.agent_uid = ? GROUP BY u.uid ORDER BY count DESC LIMIT 10");
        $stmtTopU->execute([$agent_uid]);
        $top_users = $stmtTopU->fetchAll();

        $stmtUnseen = $pdo->prepare("SELECT uid, name, email, createdAt FROM users WHERE agent_uid = ? AND status = 'pending' ORDER BY createdAt DESC");
        $stmtUnseen->execute([$agent_uid]);
        $unseen_users = $stmtUnseen->fetchAll();

        echo json_encode([
            'status' => 'success',
            'today_success_otp' => $today_count,
            'today_revenue' => round($today_agent_rev, 2),
            'yesterday_success' => $yesterday_count,
            'yesterday_revenue' => round($yesterday_agent_rev, 2),
            'days7_success' => $days7_count,
            'days7_revenue' => round($days7_agent_rev, 2),
            'days30_success' => $days30_count,
            'days30_revenue' => round($days30_agent_rev, 2),
            'lifetime_success' => $lifetime_count,
            'lifetime_revenue' => round($lifetime_agent_rev, 2),
            'top_services' => $top_services,
            'top_users' => $top_users,
            'unseen_users' => $unseen_users
        ]);
        exit();

    case 'agent-withdrawals':
        $user = get_current_user_optimized();
        if (!$user || $user['role'] !== 'agent') {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Agent access required']);
            exit();
        }
        $pdo = get_db_connection();
        $stmtSub = $pdo->prepare("SELECT uid FROM users WHERE agent_uid = ?");
        $stmtSub->execute([$user['uid']]);
        $sub_uids = $stmtSub->fetchAll(PDO::FETCH_COLUMN);

        if (empty($sub_uids)) {
            echo json_encode(['status' => 'success', 'withdrawals' => []]);
            exit();
        }

        $in_clause = implode(',', array_fill(0, count($sub_uids), '?'));
        $stmtW = $pdo->prepare("SELECT * FROM withdrawals WHERE userId IN ($in_clause) ORDER BY createdAt DESC");
        $stmtW->execute($sub_uids);
        $withdrawals = $stmtW->fetchAll();
        echo json_encode(['status' => 'success', 'withdrawals' => $withdrawals]);
        exit();

    case 'agent-update-user':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $user = get_current_user_optimized();
        if (!$user || $user['role'] !== 'agent') {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Agent access required']);
            exit();
        }
        $data = json_decode(file_get_contents('php://input'), true) ?: [];
        $target_uid = isset($data['uid']) ? trim($data['uid']) : '';

        $pdo = get_db_connection();
        $stmtCheck = $pdo->prepare("SELECT * FROM users WHERE uid = ? AND agent_uid = ? LIMIT 1");
        $stmtCheck->execute([$target_uid, $user['uid']]);
        $target_user = $stmtCheck->fetch();

        if (!$target_user) {
            echo json_encode(['status' => 'error', 'message' => 'Sub-user not found or unauthorized']);
            exit();
        }

        $updates = [];
        if (isset($data['status']) && in_array($data['status'], ['approved', 'pending', 'banned'])) {
            $updates['status'] = $data['status'];
        }
        if (isset($data['otp_rate'])) {
            $new_rate = (float)$data['otp_rate'];
            $agent_max_rate = (float)(isset($user['otp_rate']) ? $user['otp_rate'] : 0.63);
            if ($new_rate > $agent_max_rate) {
                echo json_encode(['status' => 'error', 'message' => "User rate cannot exceed your base agent rate (৳{$agent_max_rate})"]);
                exit();
            }
            $updates['otp_rate'] = $new_rate;
        }
        if (isset($data['password']) && !empty(trim($data['password']))) {
            $updates['password'] = trim($data['password']);
        }
        if (isset($data['withdraw_pin']) && !empty(trim($data['withdraw_pin']))) {
            $updates['withdraw_pin'] = trim($data['withdraw_pin']);
        }
        if (isset($data['api_key_approved'])) {
            $updates['api_key_approved'] = (bool)$data['api_key_approved'] ? 1 : 0;
        }
        if (isset($data['generate_api_key']) && $data['generate_api_key'] === true) {
            $updates['api_key'] = 'mino_live_' . bin2hex(random_bytes(16));
            $updates['api_key_approved'] = 1;
        }

        if (isset($data['transfer_amount']) && (float)$data['transfer_amount'] > 0) {
            $transfer = (float)$data['transfer_amount'];
            $agent_bal = (float)$user['balance'];
            if ($transfer > $agent_bal) {
                echo json_encode(['status' => 'error', 'message' => 'Insufficient agent wallet balance for transfer']);
                exit();
            }
            $stmtDeduct = $pdo->prepare("UPDATE users SET balance = balance - ? WHERE uid = ?");
            $stmtDeduct->execute([$transfer, $user['uid']]);

            $stmtAdd = $pdo->prepare("UPDATE users SET balance = balance + ? WHERE uid = ?");
            $stmtAdd->execute([$transfer, $target_uid]);
        }

        if (!empty($updates)) {
            $fields = [];
            $params = [];
            foreach ($updates as $col => $val) {
                $fields[] = "$col = ?";
                $params[] = $val;
            }
            $params[] = $target_uid;
            $sql = "UPDATE users SET " . implode(', ', $fields) . " WHERE uid = ?";
            $stmtUp = $pdo->prepare($sql);
            $stmtUp->execute($params);
        }

        echo json_encode(['status' => 'success', 'message' => 'Sub-user settings updated successfully']);
        exit();

    case 'agent-save-settings':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
            exit();
        }
        $user = get_current_user_optimized();
        if (!$user || $user['role'] !== 'agent') {
            http_response_code(401);
            echo json_encode(['status' => 'error', 'message' => 'Agent access required']);
            exit();
        }
        $data = json_decode(file_get_contents('php://input'), true) ?: [];
        $auto_approve = isset($data['agent_auto_approve']) ? ((int)$data['agent_auto_approve'] ? 1 : 0) : 1;
        $auto_rate = isset($data['agent_auto_rate']) ? (float)$data['agent_auto_rate'] : 0.40;

        $pdo = get_db_connection();
        $stmt = $pdo->prepare("UPDATE users SET agent_auto_approve = ?, agent_auto_rate = ? WHERE uid = ?");
        $stmt->execute([$auto_approve, $auto_rate, $user['uid']]);

        echo json_encode(['status' => 'success', 'message' => 'Agent settings saved successfully']);
        exit();

    default:
        http_response_code(404);
        echo json_encode(['status' => 'error', 'message' => 'Action path not found']);
        break;
}