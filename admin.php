<?php
// Buffer API output so PHP notices or hosting-layer whitespace can never
// corrupt the JSON response consumed by the dashboard fetch request.
ob_start();

require_once 'security.php';
handle_pre_requests(true);

$action = isset($_GET['action']) ? $_GET['action'] : '';
if ($action === '') {
    // Some Apache/aaPanel configurations do not populate $_GET consistently
    // when a PHP file is requested through a rewrite. Recover the action from
    // the original query string before falling through to the HTML page.
    $raw_query = isset($_SERVER['QUERY_STRING']) ? (string)$_SERVER['QUERY_STRING'] : '';
    if ($raw_query === '' && isset($_SERVER['REQUEST_URI'])) {
        $raw_query = (string)parse_url($_SERVER['REQUEST_URI'], PHP_URL_QUERY);
    }
    if ($raw_query !== '') {
        $parsed_query = [];
        parse_str($raw_query, $parsed_query);
        if (isset($parsed_query['action'])) {
            $action = (string)$parsed_query['action'];
        }
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($action)) {
    switch ($action) {
        case 'login':
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $username = isset($data['username']) ? trim($data['username']) : '';
            $password = isset($data['password']) ? trim($data['password']) : '';
            
            if (empty($username) || empty($password)) {
                $username = isset($_POST['username']) ? trim($_POST['username']) : '';
                $password = isset($_POST['password']) ? trim($_POST['password']) : '';
            }

            if ($username === ADMIN_USER && $password === ADMIN_PASS) {
                echo json_encode(['status' => 'success', 'token' => ADMIN_STATIC_TOKEN]);
            } else {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Invalid Admin Credentials']);
            }
            exit();

        case 'users-update':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $uid = isset($data['uid']) ? $data['uid'] : '';
            if (empty($uid)) {
                http_response_code(400);
                echo json_encode(['status' => 'error', 'message' => 'User ID is required']);
                exit();
            }
            
            $updates = [];
            if (isset($data['status']) && in_array($data['status'], ['approved', 'pending', 'banned'])) {
                $updates['status'] = $data['status'];
            }
            if (isset($data['balance'])) {
                $updates['balance'] = (float)$data['balance'];
            }
            if (isset($data['otp_rate'])) {
                $updates['otp_rate'] = (float)$data['otp_rate'];
            }
            if (isset($data['wallet_address'])) {
                $updates['wallet_address'] = trim($data['wallet_address']);
            }
            if (isset($data['api_key'])) {
                $updates['api_key'] = trim($data['api_key']);
            }
            if (isset($data['api_key_approved'])) {
                $updates['api_key_approved'] = (bool)$data['api_key_approved'];
            }
            if (isset($data['password'])) {
                $new_password = trim((string)$data['password']);
                if ($new_password !== '') {
                    $updates['password'] = hash_user_password($new_password);
                }
            }
            if (isset($data['role'])) {
                $updates['role'] = trim($data['role']);
            }
            if (isset($data['agent_limit'])) {
                $updates['agent_limit'] = (int)$data['agent_limit'];
            }
            if (isset($data['agent_uid'])) {
                $updates['agent_uid'] = trim($data['agent_uid']);
            }
                
            if (!empty($updates)) {
                db_request('/users/' . $uid, 'PATCH', $updates);
                
                // Save Audit Trail Log
                $console_id = "con_" . bin2hex(random_bytes(8));
                db_request('/live_console/' . $console_id, 'PUT', [
                    'type' => 'admin_action',
                    'message' => "Admin updated details for account with UID: {$uid}",
                    'service' => 'System',
                    'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
                ]);
            }
                
            echo json_encode(['status' => 'success', 'message' => 'User updated successfully']);
            exit();

        case 'users-delete':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $uid = isset($data['uid']) ? $data['uid'] : '';
            if (empty($uid)) {
                http_response_code(400);
                echo json_encode(['status' => 'error', 'message' => 'User ID is required']);
                exit();
            }
            
            db_request('/users/' . $uid, 'DELETE');

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin permanently deleted user with UID: {$uid}",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'message' => 'User deleted successfully']);
            exit();

        // =========================================================================
        // AGENT ADMINISTRATION MODULE
        // =========================================================================
        case 'agents-create':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $name = isset($data['name']) ? trim($data['name']) : '';
            $email = isset($data['email']) ? trim($data['email']) : '';
            $password = isset($data['password']) ? trim($data['password']) : '';
            $limit = isset($data['agent_limit']) ? (int)$data['agent_limit'] : 120;
            $rate = isset($data['otp_rate']) ? (float)$data['otp_rate'] : 0.63;

            if (empty($name) || empty($email) || empty($password)) {
                echo json_encode(['status' => 'error', 'message' => 'Name, Email and Password are required.']);
                exit();
            }

            $all_users = db_request('/users') ?: [];
            foreach ($all_users as $u) {
                if (isset($u['email']) && $u['email'] === $email) {
                    echo json_encode(['status' => 'error', 'message' => 'Email address already exists in database.']);
                    exit();
                }
            }

            $uid = "agt_" . bin2hex(random_bytes(8));
            $agent_data = [
                'uid' => $uid,
                'name' => $name,
                'email' => $email,
                'password' => hash_user_password($password),
                'api_key' => '',
                'api_key_approved' => false,
                'balance' => 0.00,
                'otp_rate' => $rate,
                'wallet_address' => '',
                'id_code' => "AGNT-" . rand(1000, 9999),
                'status' => 'approved',
                'role' => 'agent',
                'agent_limit' => $limit,
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ];

            db_request('/users/' . $uid, 'PUT', $agent_data);
            
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin created new official agent: {$name} ({$email})",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'message' => 'Official Agent created successfully!']);
            exit();

        case 'toggle-maintenance':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $val = (bool)(isset($data['maintenance_mode']) ? $data['maintenance_mode'] : false);
            db_request('/settings/maintenance_mode', 'PUT', $val);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin toggled system maintenance mode to " . ($val ? "ON" : "OFF"),
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'maintenance_mode' => $val]);
            exit();

        case 'announcement':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $msg = isset($data['announcement']) ? trim($data['announcement']) : '';
            db_request('/settings/announcement', 'PUT', $msg);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin modified global system banner announcement: '{$msg}'",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'message' => 'Announcement updated']);
            exit();

        case 'service-rates':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $rates = isset($data['rates']) ? $data['rates'] : [];
            $sanitized_rates = [];
            $default_services = ['facebook', 'instagram', 'whatsapp', 'telegram', 'google', 'generic'];
            foreach ($default_services as $svc) {
                if (isset($rates[$svc])) {
                    $v = $rates[$svc];
                    if (is_array($v)) {
                        $sanitized_rates[$svc] = [
                            'rate' => (float)(isset($v['rate']) ? $v['rate'] : 0.40),
                            'status' => strtoupper(isset($v['status']) ? $v['status'] : 'ON')
                        ];
                    } else {
                        $sanitized_rates[$svc] = [
                            'rate' => (float)$v,
                            'status' => 'ON'
                        ];
                    }
                } else {
                    $sanitized_rates[$svc] = [
                        'rate' => 0.40,
                        'status' => ($svc === 'whatsapp' || $svc === 'telegram') ? 'OFF' : 'ON'
                    ];
                }
            }
            db_request('/settings/service_rates', 'PUT', $sanitized_rates);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin adjusted global service rate rules",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'message' => 'Service payout rates successfully updated', 'rates' => $sanitized_rates]);
            exit();

        case 'withdrawals-action':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $wd_id = isset($data['id']) ? $data['id'] : '';
            $action_val = isset($data['action']) ? $data['action'] : ''; 
            
            if (empty($wd_id) || !in_array($action_val, ['approved', 'rejected'])) {
                http_response_code(400);
                echo json_encode(['status' => 'error', 'message' => 'Invalid parameters']);
                exit();
            }
            
            $wd_data = db_request('/withdrawals/' . $wd_id);
            if (!$wd_data) {
                http_response_code(404);
                echo json_encode(['status' => 'error', 'message' => 'Request not found']);
                exit();
            }
            
            if (isset($wd_data['status']) && $wd_data['status'] !== 'pending') {
                http_response_code(400);
                echo json_encode(['status' => 'error', 'message' => 'Request already processed']);
                exit();
            }
            
            if ($action_val === 'rejected') {
                $user_data = db_request('/users/' . $wd_data['userId']);
                if ($user_data) {
                    $new_bal = (float)(isset($user_data['balance']) ? $user_data['balance'] : 0) + (float)$wd_data['amount'];
                    db_request('/users/' . $wd_data['userId'] . '/balance', 'PUT', $new_bal);
                }
            }
                
            db_request('/withdrawals/' . $wd_id . '/status', 'PUT', $action_val);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin changed withdrawal request ID {$wd_id} to state: {$action_val}",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'message' => "Withdrawal {$action_val} successfully"]);
            exit();

        case 'bulk-balance-adjust':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $amount = isset($data['amount']) ? (float)$data['amount'] : 0.0;
            $type = isset($data['type']) ? $data['type'] : 'add'; 
            
            if ($amount <= 0) {
                echo json_encode(['status' => 'error', 'message' => 'Amount must be greater than 0']);
                exit();
            }
            
            $pdo = get_db_connection();
            if ($type === 'add') {
                $stmt = $pdo->prepare("UPDATE users SET balance = balance + ? WHERE status = 'approved' AND role = 'user'");
            } else {
                $stmt = $pdo->prepare("UPDATE users SET balance = balance - ? WHERE status = 'approved' AND role = 'user'");
            }
            $stmt->execute([$amount]);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin executed bulk balance update. Adjusted ৳{$amount} ({$type}) for all approved user accounts.",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'message' => 'Bulk balance successfully adjusted']);
            exit();

        case 'toggle-auto-approve-account':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $val = (bool)(isset($data['auto_approve_account']) ? $data['auto_approve_account'] : false);
            db_request('/settings/auto_approve_account', 'PUT', $val);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin adjusted account auto-approval status to " . ($val ? "ACTIVE" : "INACTIVE"),
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'auto_approve_account' => $val]);
            exit();

        case 'update-global-base-rate':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $new_rate = isset($data['rate']) ? (float)$data['rate'] : 0.40;
            
            $pdo = get_db_connection();
            $stmt = $pdo->prepare("UPDATE users SET otp_rate = ? WHERE role = 'user'");
            $stmt->execute([$new_rate]);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin reset global baseline OTP payout rate of all users to: ৳{$new_rate}",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);
            
            echo json_encode(['status' => 'success', 'message' => 'Global base rate updated successfully']);
            exit();

        case 'refund-allocation':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $alloc_id = isset($data['id']) ? $data['id'] : '';
            
            if (empty($alloc_id)) {
                echo json_encode(['status' => 'error', 'message' => 'Allocation ID required']);
                exit();
            }
            
            $alloc = db_request('/allocated_numbers/' . $alloc_id, 'GET');
            if ($alloc && isset($alloc['status']) && $alloc['status'] === 'active') {
                db_request('/allocated_numbers/' . $alloc_id . '/status', 'PUT', 'expired');
                
                $console_id = "con_" . bin2hex(random_bytes(8));
                db_request('/live_console/' . $console_id, 'PUT', [
                    'type' => 'revoked',
                    'message' => "Order " . $alloc_id . " manually revoked and marked as expired by Admin",
                    'service' => isset($alloc['operator']) ? $alloc['operator'] : 'Mobile',
                    'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
                ]);
                
                echo json_encode(['status' => 'success', 'message' => 'Allocation marked expired and refunded']);
                exit();
            }
            echo json_encode(['status' => 'error', 'message' => 'Allocation not active or not found']);
            exit();

        case 'update-gateway-config':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            
            $gateway = isset($data['active_gateway']) ? trim($data['active_gateway']) : 'voltx';
            $voltx_key = isset($data['voltx_api_key']) ? trim($data['voltx_api_key']) : 'M9JBBKWUL33';
            $voltx_url = isset($data['voltx_base_url']) ? trim($data['voltx_base_url']) : 'https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api';
            
            $yesms_key = isset($data['yesms_api_key']) ? trim($data['yesms_api_key']) : '2517fa2553351295';
            $yesms_url = isset($data['yesms_base_url']) ? trim($data['yesms_base_url']) : 'https://yesms.online/api';

            db_request('/settings/active_gateway', 'PUT', $gateway);
            db_request('/settings/voltx_api_key', 'PUT', $voltx_key);
            db_request('/settings/voltx_base_url', 'PUT', $voltx_url);
            db_request('/settings/yesms_api_key', 'PUT', $yesms_key);
            db_request('/settings/yesms_base_url', 'PUT', $yesms_url);

            // Save Audit Trail Log
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin updated global active SMS backend API Key / Endpoints to: " . strtoupper($gateway),
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);
            
            echo json_encode([
                'status' => 'success', 
                'message' => 'Gateway configuration updated successfully',
                'active_gateway' => $gateway
            ]);
            exit();

        case 'quick-fund-inject':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $id_code = isset($data['id_code']) ? trim($data['id_code']) : '';
            $amount = isset($data['amount']) ? (float)$data['amount'] : 0.0;
            $type = isset($data['type']) ? $data['type'] : 'add';

            if (empty($id_code) || $amount <= 0) {
                echo json_encode(['status' => 'error', 'message' => 'Invalid parameters. Valid ID and Amount required.']);
                exit();
            }

            $pdo = get_db_connection();
            $stmt = $pdo->prepare("SELECT * FROM users WHERE id_code = ?");
            $stmt->execute([$id_code]);
            $user_data = $stmt->fetch();

            if (!$user_data) {
                echo json_encode(['status' => 'error', 'message' => 'No user found with matching ID Code.']);
                exit();
            }

            $new_bal = $type === 'add' ? (float)$user_data['balance'] + $amount : max(0.0, (float)$user_data['balance'] - $amount);
            $stmt_up = $pdo->prepare("UPDATE users SET balance = ? WHERE id_code = ?");
            $stmt_up->execute([$new_bal, $id_code]);

            // Save log to console Audit Trail
            $console_id = "con_" . bin2hex(random_bytes(8));
            db_request('/live_console/' . $console_id, 'PUT', [
                'type' => 'admin_action',
                'message' => "Admin adjusted account fund of {$user_data['name']} ({$id_code}). Amount adjusted: ৳{$amount} ({$type}). New wallet value: ৳{$new_bal}",
                'service' => 'System',
                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
            ]);

            echo json_encode(['status' => 'success', 'message' => "Wallet balance modified successfully! New balance of {$id_code}: ৳{$new_bal}"]);
            exit();

        case 'clean-expired-allocations':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $pdo = get_db_connection();
            $now = new DateTime('now', new DateTimeZone('UTC'));
            $cutoff = $now->sub(new DateInterval('PT18M'))->format(DateTime::ATOM);
            
            $stmt = $pdo->prepare("UPDATE allocated_numbers SET status = 'expired' WHERE status = 'active' AND createdAt < ?");
            $stmt->execute([$cutoff]);
            $count = $stmt->rowCount();

            if ($count > 0) {
                $console_id = "con_" . bin2hex(random_bytes(8));
                db_request('/live_console/' . $console_id, 'PUT', [
                    'type' => 'admin_action',
                    'message' => "Admin ran system wide clean-up: marked {$count} stale bookings older than 18m as Expired",
                    'service' => 'System',
                    'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
                ]);
            }

            echo json_encode(['status' => 'success', 'message' => "Sweep executed. Swept {$count} stale active reservations."]);
            exit();

        case 'test-voltx-range':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $rid = isset($data['rid']) ? trim($data['rid']) : '';
            if (empty($rid)) {
                echo json_encode(['status' => 'error', 'message' => 'Range ID is required']);
                exit();
            }

            $alloc_res = gateway_allocate_number($rid);
            echo json_encode([
                'status' => 'success',
                'available' => $alloc_res['success'],
                'response' => $alloc_res
            ]);
            exit();

        case 'add-withdrawal-method':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $name = isset($data['method_name']) ? trim($data['method_name']) : '';
            $instr = isset($data['instructions']) ? trim($data['instructions']) : '';

            if (empty($name)) {
                echo json_encode(['status' => 'error', 'message' => 'Method name is required']);
                exit();
            }
            $pdo = get_db_connection();
            $mid = "m_" . bin2hex(random_bytes(6));
            $stmt = $pdo->prepare("INSERT INTO withdrawal_methods (id, method_name, instructions) VALUES (?, ?, ?)");
            $stmt->execute([$mid, $name, $instr]);

            echo json_encode(['status' => 'success', 'message' => 'Withdrawal method added successfully!']);
            exit();

        case 'delete-withdrawal-method':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = json_decode(file_get_contents('php://input'), true) ?: [];
            $mid = isset($data['id']) ? trim($data['id']) : '';

            $pdo = get_db_connection();
            $stmt = $pdo->prepare("DELETE FROM withdrawal_methods WHERE id = ?");
            $stmt->execute([$mid]);

            echo json_encode(['status' => 'success', 'message' => 'Withdrawal method removed successfully!']);
            exit();
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'GET' && !empty($action)) {
    switch ($action) {
        case 'dashboard-all':
            header('Content-Type: application/json; charset=utf-8');
            if (!verify_admin()) {
                http_response_code(401);
                ob_clean();
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            try {
                // Read the dashboard collections directly from the connected
                // MySQL database.
                $pdo = get_db_connection();
                $dashboard_issues = [];
                $db_data = [
                    'users' => get_dashboard_rows_safe($pdo, 'users', 'uid', $dashboard_issues),
                    'allocated_numbers' => get_dashboard_rows_safe($pdo, 'allocated_numbers', 'id', $dashboard_issues),
                    'otp_logs' => get_dashboard_rows_safe($pdo, 'otp_logs', 'id', $dashboard_issues),
                    'withdrawals' => get_dashboard_rows_safe($pdo, 'withdrawals', 'id', $dashboard_issues),
                    'settings' => get_dashboard_settings_safe($pdo, $dashboard_issues)
                ];
                $dashboard_counts = [
                    'users' => get_dashboard_count_safe($pdo, 'users', $dashboard_issues),
                    'allocated_numbers' => get_dashboard_count_safe($pdo, 'allocated_numbers', $dashboard_issues),
                    'otp_logs' => get_dashboard_count_safe($pdo, 'otp_logs', $dashboard_issues),
                    'withdrawals' => get_dashboard_count_safe($pdo, 'withdrawals', $dashboard_issues),
                    'pending_users' => get_dashboard_pending_user_count_safe($pdo, $dashboard_issues)
                ];
                
                $users_dict = isset($db_data['users']) ? $db_data['users'] : [];
                $users_list = rows_to_list($users_dict);
                usort($users_list, function($a, $b) {
                    return strcmp(isset($b['createdAt']) ? $b['createdAt'] : '', isset($a['createdAt']) ? $a['createdAt'] : '');
                });
                
                $allocs_dict = isset($db_data['allocated_numbers']) ? $db_data['allocated_numbers'] : [];
                $allocs_list = rows_to_list($allocs_dict);
                usort($allocs_list, function($a, $b) {
                    return strcmp(isset($b['createdAt']) ? $b['createdAt'] : '', isset($a['createdAt']) ? $a['createdAt'] : '');
                });
                
                $otp_logs_dict = isset($db_data['otp_logs']) ? $db_data['otp_logs'] : [];
                $otp_logs_list = rows_to_list($otp_logs_dict);
                usort($otp_logs_list, function($a, $b) {
                    return strcmp(isset($b['createdAt']) ? $b['createdAt'] : '', isset($a['createdAt']) ? $a['createdAt'] : '');
                });
                
                $withdrawals_dict = isset($db_data['withdrawals']) ? $db_data['withdrawals'] : [];
                $withdrawals_list = rows_to_list($withdrawals_dict);
                usort($withdrawals_list, function($a, $b) {
                    return strcmp(isset($b['createdAt']) ? $b['createdAt'] : '', isset($a['createdAt']) ? $a['createdAt'] : '');
                });
                
                $settings = isset($db_data['settings']) ? $db_data['settings'] : [];
                $m_mode = isset($settings['maintenance_mode']) ? $settings['maintenance_mode'] : false;
                $auto_approve_account = isset($settings['auto_approve_account']) ? $settings['auto_approve_account'] : false;
                $announcement = isset($settings['announcement']) ? $settings['announcement'] : '';
                $raw_rates = isset($settings['service_rates']) ? $settings['service_rates'] : [];
                
                $active_gateway = isset($settings['active_gateway']) ? $settings['active_gateway'] : 'voltx';
                $voltx_api_key = isset($settings['voltx_api_key']) ? $settings['voltx_api_key'] : 'M9JBBKWUL33';
                $voltx_base_url = isset($settings['voltx_base_url']) ? $settings['voltx_base_url'] : 'https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api';

                $yesms_api_key = isset($settings['yesms_api_key']) ? $settings['yesms_api_key'] : '2517fa2553351295';
                $yesms_base_url = isset($settings['yesms_base_url']) ? $settings['yesms_base_url'] : 'https://yesms.online/api';

                $methods_list = get_dashboard_methods_safe($pdo, $dashboard_issues);

                $default_services = ['facebook', 'instagram', 'whatsapp', 'telegram', 'google', 'generic'];
                $rates = [];
                foreach ($default_services as $svc) {
                    $rates[$svc] = [
                        'rate' => 0.40,
                        'status' => ($svc === 'whatsapp' || $svc === 'telegram') ? 'OFF' : 'ON'
                    ];
                    if (isset($raw_rates[$svc])) {
                        $item = $raw_rates[$svc];
                        if (is_array($item)) { 
                            if (isset($item['rate'])) $rates[$svc]['rate'] = (float)$item['rate'];
                            if (isset($item['status'])) $rates[$svc]['status'] = strtoupper($item['status']);
                        } else {
                            $rates[$svc]['rate'] = (float)$item;
                        }
                    }
                }

                $pending_users = $dashboard_counts['pending_users'];
                if ($pending_users === null) {
                    $pending_users = 0;
                    foreach ($users_list as $u) {
                        if (isset($u['status']) && $u['status'] === 'pending') {
                            $pending_users++;
                        }
                    }
                }
                
                ob_clean();
                echo json_encode([
                    'status' => 'success',
                    'stats' => [
                        'total_users' => $dashboard_counts['users'] ?? count($users_list),
                        'pending_users' => $pending_users,
                        'total_allocations' => $dashboard_counts['allocated_numbers'] ?? count($allocs_list),
                        'total_otps' => $dashboard_counts['otp_logs'] ?? count($otp_logs_list),
                        'total_withdrawals' => $dashboard_counts['withdrawals'] ?? count($withdrawals_list),
                        'maintenance_mode' => (bool)$m_mode,
                        'auto_approve_account' => (bool)$auto_approve_account,
                        'announcement' => $announcement,
                        'active_gateway' => $active_gateway,
                        'voltx_api_key' => $voltx_api_key,
                        'voltx_base_url' => $voltx_base_url,
                        'yesms_api_key' => $yesms_api_key,
                        'yesms_base_url' => $yesms_base_url
                    ],
                    'users' => $users_list,
                    'allocations' => $allocs_list,
                    'otp_logs' => $otp_logs_list,
                    'withdrawals' => $withdrawals_list,
                    'rates' => $rates,
                    'withdrawal_methods' => $methods_list,
                    'warnings' => $dashboard_issues
                ]);
            } catch (Throwable $e) {
                http_response_code(500);
                ob_clean();
                echo json_encode([
                    'status' => 'error',
                    'message' => 'Admin database connection could not be opened. Check config.php database host, name, username, and password.',
                    'diagnostic' => dashboard_database_error_message($e),
                    'error_code' => $e->getCode()
                ]);
            }
            exit();

        case 'backup':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $data = db_request('/') ?: [];
            echo json_encode(['status' => 'success', 'data' => $data]);
            exit();

        case 'user-status':
            if (!verify_admin()) {
                http_response_code(401);
                echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
                exit();
            }
            $target_uid = isset($_GET['uid']) ? trim($_GET['uid']) : '';
            if (empty($target_uid)) {
                echo json_encode(['status' => 'error', 'message' => 'Missing target UID']);
                exit();
            }
            $pdo = get_db_connection();
            
            $stmt = $pdo->prepare("SELECT * FROM users WHERE uid = ?");
            $stmt->execute([$target_uid]);
            $u = $stmt->fetch();
            if (!$u) {
                echo json_encode(['status' => 'error', 'message' => 'User not found']);
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
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MINO SMS - MASTER ADMIN PANEL</title>

  <!-- Mino SMS Favicon SVG -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><path d='M10 50 L90 10 L60 90 L45 55 Z' fill='%232b537c'/><path d='M45 55 L90 10 L60 90 Z' fill='%231d3b5b'/><path d='M25 42 L42 22 M30 52 L48 32' stroke='%23f98012' stroke-width='4' stroke-linecap='round'/></svg>">

  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vue/3.3.4/vue.global.prod.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    [v-cloak] { display: none; }
    .fade-enter-active {
      animation: fadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .animate-bounce-in {
      animation: bounceIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    @keyframes bounceIn {
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: scale(1); }
    }
  </style>
</head>
<body class="bg-slate-100 text-slate-707 font-sans select-none pb-12">
  
  <div id="admin-app" v-cloak>

    <!-- Loading Screen Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-slate-50 flex flex-col items-center justify-center space-y-4 z-50">
      <div class="h-12 w-12 border-4 border-rose-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-xs font-black text-rose-600 uppercase tracking-widest animate-pulse">MINO MASTER ADMIN LOADING...</p>
    </div>

    <div v-cloak v-else>

      <!-- Toast Notifications -->
      <div v-if="toast" class="fixed top-5 left-1/2 -translate-x-1/2 bg-[#0088CC] text-white font-black text-xs px-5 py-3 rounded-2xl shadow-xl z-[9999] transition animate-bounce flex items-center gap-2">
        <i class="fa-solid fa-circle-check"></i> {{ toastMessage }}
      </div>

      <!-- Admin Login Form -->
      <div v-if="!adminToken" class="min-h-screen flex items-center justify-center p-4">
        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm max-w-sm w-full space-y-6">
          <div class="text-center space-y-2">
            
            <!-- BRANDING LOGO IN LOGIN -->
            <div class="flex items-center justify-center gap-2">
              <svg class="h-10 w-auto" viewBox="0 0 280 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 48 L78 12 L50 82 L38 52 Z" fill="#2b537c"/>
                <path d="M38 52 L78 12 L50 82 Z" fill="#1d3b5b"/>
                <path d="M22 38 L38 20 M26 48 L44 30" stroke="#f98012" stroke-width="4" stroke-linecap="round"/>
                <text x="90" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#1d3b5b">Mino</text>
                <text x="175" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#f98012">SMS</text>
              </svg>
            </div>
            
            <span class="px-3 py-1 bg-rose-600 rounded-xl text-white font-black text-xs mx-auto shadow-sm w-max inline-block uppercase">MASTER ADMIN PANEL</span>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Authorized Access Only</p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="text-xs font-bold text-slate-500">Admin Username</label>
              <input type="text" required v-model="username" class="w-full mt-1.5 p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold outline-none focus:border-rose-600 transition" />
            </div>
            <div>
              <label class="text-xs font-bold text-slate-500">Admin Password</label>
              <input type="password" required v-model="password" class="w-full mt-1.5 p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:border-rose-600 transition" />
            </div>

            <button type="submit" :disabled="authLoading" class="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-3.5 rounded-xl text-sm shadow-md transition disabled:bg-slate-300">
              LOGGING IN...
            </button>
          </form>
        </div>
      </div>

      <!-- Master Admin Dashboard Area -->
      <div v-else class="min-h-screen flex flex-col md:flex-row">
        
        <!-- Sidebar Navigation Drawer -->
        <aside class="hidden md:flex w-64 bg-slate-900 text-slate-300 flex-col shrink-0">
          <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
            
            <!-- MINO SMS BRAND LOGO IN SIDEBAR -->
            <div class="flex items-center gap-2">
              <svg class="h-8 w-auto" viewBox="0 0 280 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 48 L78 12 L50 82 L38 52 Z" fill="#3b82f6"/>
                <path d="M38 52 L78 12 L50 82 Z" fill="#1d4ed8"/>
                <path d="M22 38 L38 20 M26 48 L44 30" stroke="#f98012" stroke-width="4" stroke-linecap="round"/>
                <text x="90" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#ffffff">Mino</text>
                <text x="175" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#f98012">SMS</text>
              </svg>
            </div>

            <span class="px-2 py-0.5 bg-rose-600 rounded text-white font-black text-[10px]">ADMIN</span>
          </div>

          <nav class="flex-1 p-4 space-y-1 overflow-y-auto max-h-[80vh]">
            <button @click="currentTab = 'dashboard'" :class="currentTab === 'dashboard' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition text-left">
              <i class="fa-solid fa-chart-line"></i> Dashboard Overview
            </button>
            <button @click="currentTab = 'users'" :class="currentTab === 'users' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition text-left">
              <i class="fa-solid fa-users"></i> User Administration
            </button>
            <button @click="currentTab = 'agents'" :class="currentTab === 'agents' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition text-left">
              <i class="fa-solid fa-user-tie"></i> Agent Administration
            </button>
            <button @click="currentTab = 'withdrawals'" :class="currentTab === 'withdrawals' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition text-left">
              <i class="fa-solid fa-money-bill-transfer"></i> Withdrawal Requests
            </button>
            <button @click="currentTab = 'allocations'" :class="currentTab === 'allocations' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition text-left">
              <i class="fa-solid fa-mobile-screen"></i> Number Tracking Logs
            </button>
            <button @click="currentTab = 'otp-logs'" :class="currentTab === 'otp-logs' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition text-left">
              <i class="fa-solid fa-envelope-open-text"></i> Global OTP logs
            </button>

            <!-- Advanced Analytics Tabs -->
            <div class="pt-4 border-t border-slate-800 space-y-1">
              <span class="px-4 text-[9px] uppercase font-black text-rose-500 tracking-wider">Advanced Analytics</span>
              <button @click="currentTab = 'top-number-user'" :class="currentTab === 'top-number-user' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition text-left">
                <i class="fa-solid fa-phone-volume"></i> Top Number User
              </button>
              <button @click="currentTab = 'top-otp-user'" :class="currentTab === 'top-otp-user' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition text-left">
                <i class="fa-solid fa-envelope-circle-check"></i> Top OTP User
              </button>
              <button @click="currentTab = 'inactive-user'" :class="currentTab === 'inactive-user' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition text-left">
                <i class="fa-solid fa-user-slash"></i> Inactive User
              </button>
              <button @click="currentTab = 'top-service'" :class="currentTab === 'top-service' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition text-left">
                <i class="fa-solid fa-sliders"></i> Top Service
              </button>
            </div>

            <div class="pt-4 border-t border-slate-800 space-y-1">
              <span class="px-4 text-[9px] uppercase font-black text-amber-500 tracking-wider">Security Hub</span>
              <button @click="currentTab = 'security-hub'" :class="currentTab === 'security-hub' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition text-left">
                <i class="fa-solid fa-shield-halved"></i> Ban & Verification Center
              </button>
            </div>

            <button @click="currentTab = 'settings'" :class="currentTab === 'settings' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800 text-slate-400'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition text-left mt-3">
              <i class="fa-solid fa-gears"></i> System Settings & Controls
            </button>
          </nav>

          <div class="p-4 border-t border-slate-800 flex items-center justify-between bg-slate-950 text-xs font-bold">
            <span>ADMIN PORTAL</span>
            <button @click="logOut" class="text-rose-400 hover:text-rose-600 font-black transition-all"><i class="fa-solid fa-right-from-bracket"></i> LOGOUT</button>
          </div>
        </aside>

        <!-- Slide-out Mobile Admin Menu Drawer -->
        <transition enter-active-class="transition ease-out duration-300 animate-slide-right" enter-from-class="-translate-x-full" enter-to-class="translate-x-0" leave-active-class="transition ease-in duration-200" leave-from-class="translate-x-0" leave-to-class="-translate-x-full">
          <aside v-if="mobileMenuOpen" class="fixed inset-y-0 left-0 w-64 bg-slate-900 text-slate-300 flex flex-col z-50 md:hidden shadow-2xl">
            <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div class="flex items-center gap-2">
                <svg class="h-7 w-auto" viewBox="0 0 280 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 48 L78 12 L50 82 L38 52 Z" fill="#3b82f6"/>
                  <path d="M38 52 L78 12 L50 82 Z" fill="#1d4ed8"/>
                  <path d="M22 38 L38 20 M26 48 L44 30" stroke="#f98012" stroke-width="4" stroke-linecap="round"/>
                  <text x="90" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#ffffff">Mino</text>
                  <text x="175" y="55" font-family="Arial, sans-serif" font-weight="900" font-size="34" fill="#f98012">SMS</text>
                </svg>
              </div>
              <button @click="mobileMenuOpen = false" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>

            <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
              <button @click="navigateMobile('dashboard')" :class="currentTab === 'dashboard' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-left">
                <i class="fa-solid fa-chart-line"></i> Dashboard Overview
              </button>
              <button @click="navigateMobile('users')" :class="currentTab === 'users' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-left">
                <i class="fa-solid fa-users"></i> User Administration
              </button>
              <button @click="navigateMobile('agents')" :class="currentTab === 'agents' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-left">
                <i class="fa-solid fa-user-tie"></i> Agent Administration
              </button>
              <button @click="navigateMobile('withdrawals')" :class="currentTab === 'withdrawals' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-left">
                <i class="fa-solid fa-money-bill-transfer"></i> Withdrawal Requests
              </button>
              <button @click="navigateMobile('allocations')" :class="currentTab === 'allocations' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-left">
                <i class="fa-solid fa-mobile-screen"></i> Number Tracking Logs
              </button>
              <button @click="navigateMobile('otp-logs')" :class="currentTab === 'otp-logs' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-left">
                <i class="fa-solid fa-envelope-open-text"></i> Global OTP logs
              </button>

              <div class="pt-4 border-t border-slate-800 space-y-1">
                <span class="px-4 text-[9px] uppercase font-black text-rose-500 tracking-wider">Advanced Analytics</span>
                <button @click="navigateMobile('top-number-user')" :class="currentTab === 'top-number-user' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold text-left">
                  <i class="fa-solid fa-phone-volume"></i> Top Number User
                </button>
                <button @click="navigateMobile('top-otp-user')" :class="currentTab === 'top-otp-user' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold text-left">
                  <i class="fa-solid fa-envelope-circle-check"></i> Top OTP User
                </button>
                <button @click="navigateMobile('inactive-user')" :class="currentTab === 'inactive-user' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold text-left">
                  <i class="fa-solid fa-user-slash"></i> Inactive User
                </button>
                <button @click="navigateMobile('top-service')" :class="currentTab === 'top-service' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold text-left">
                  <i class="fa-solid fa-sliders"></i> Top Service
                </button>
              </div>

              <div class="pt-4 border-t border-slate-800 space-y-1">
                <span class="px-4 text-[9px] uppercase font-black text-amber-500 tracking-wider">Security Hub</span>
                <button @click="navigateMobile('security-hub')" :class="currentTab === 'security-hub' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold text-left">
                  <i class="fa-solid fa-shield-halved"></i> Ban & Verification Center
                </button>
              </div>

              <button @click="navigateMobile('settings')" :class="currentTab === 'settings' ? 'bg-rose-600 text-white' : 'hover:bg-slate-800'" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-left mt-3">
                <i class="fa-solid fa-gears"></i> System Settings & Controls
              </button>
            </nav>

            <div class="p-4 border-t border-slate-800 flex items-center justify-between bg-slate-950 text-xs font-bold">
              <span>ADMIN MOBILE</span>
              <button @click="logOut" class="text-rose-400 font-black">LOGOUT</button>
            </div>
          </aside>
        </transition>

        <div v-if="mobileMenuOpen" @click="mobileMenuOpen = false" class="fixed inset-0 bg-black/50 backdrop-blur-xs z-40 md:hidden"></div>

        <!-- Main Content Area -->
        <main class="flex-1 p-4 md:p-8 space-y-6 overflow-y-auto">
          
          <header class="flex justify-between items-center border-b border-slate-200 pb-4">
            <div class="flex items-center gap-3">
              <button @click="mobileMenuOpen = true" class="md:hidden text-slate-707 bg-white shadow-xs border p-2.5 rounded-xl focus:outline-none transition active:scale-95">
                <i class="fa-solid fa-bars text-lg"></i>
              </button>
              <h2 class="text-md md:text-lg font-black text-slate-900 capitalize">{{ currentTab.replace(/-/g, ' ') }} Management</h2>
            </div>
            <div class="text-xs font-black bg-rose-100 text-rose-600 px-3 py-1.5 rounded-full shadow-sm uppercase tracking-wider">
              Live Master Admin
            </div>
          </header>

          <div v-if="dashboardError" class="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-2xl text-xs font-bold flex items-start gap-2">
            <i class="fa-solid fa-circle-exclamation mt-0.5"></i>
            <span>{{ dashboardError }}</span>
          </div>

          <!-- ==================== Tab 1: Dashboard Overview ==================== -->
          <div v-if="currentTab === 'dashboard'" class="fade-enter-active space-y-6">
            
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div class="bg-white p-5 rounded-2xl border shadow-xs flex flex-col justify-between">
                <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wide">Total Users</p>
                <h3 class="text-2xl font-black text-slate-900 mt-2">{{ stats.total_users }}</h3>
              </div>
              <div class="bg-white p-5 rounded-2xl border border-blue-200 bg-blue-50/10 shadow-xs flex flex-col justify-between">
                <p class="text-[10px] text-blue-600 font-bold uppercase tracking-wide">Total API Users</p>
                <h3 class="text-2xl font-black text-blue-600 mt-2">{{ apiUsersCount }}</h3>
              </div>
              <div class="bg-white p-5 rounded-2xl border border-purple-200 bg-purple-50/15 shadow-xs flex flex-col justify-between">
                <p class="text-[10px] text-purple-600 font-bold uppercase tracking-wide">Official Agents</p>
                <h3 class="text-2xl font-black text-purple-600 mt-2">{{ agentsCount }}</h3>
              </div>
              <div class="bg-white p-5 rounded-2xl border border-amber-200 bg-amber-50/20 shadow-xs flex flex-col justify-between">
                <p class="text-[10px] text-amber-600 font-bold uppercase tracking-wide">Pending Accounts</p>
                <h3 class="text-2xl font-black text-amber-600 mt-2">{{ stats.pending_users }}</h3>
              </div>
              <div class="bg-white p-5 rounded-2xl border border-rose-200 bg-rose-50/20 shadow-xs flex flex-col justify-between animate-pulse">
                <p class="text-[10px] text-rose-600 font-bold uppercase tracking-wide">Pending Withdrawals</p>
                <h3 class="text-2xl font-black text-rose-600 mt-2">{{ pendingWithdrawalsCount }}</h3>
              </div>
            </div>

            <!-- Direct Dashboard Quick Fund Injector -->
            <div class="bg-white p-6 rounded-3xl border border-indigo-150 shadow-xs space-y-4">
              <h4 class="font-bold text-xs text-indigo-600 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-bolt-lightning"></i> Direct Quick Fund Injector
              </h4>
              <p class="text-[10px] text-slate-400 font-semibold">
                ম্যানুয়াল ইউজার এডিটিং সহজ করতে ডিরেক্ট আইডি কোড ব্যবহার করে যেকোনো ইউজারের ব্যালেন্স এডজাস্ট করুন।
              </p>
              <div class="flex flex-wrap gap-2 items-center">
                <input type="text" v-model="quickFundIdCode" placeholder="User ID Code (e.g. MINO-4240)" class="p-2.5 bg-slate-50 border rounded-xl text-xs font-bold outline-none focus:border-indigo-500 w-52" />
                <select v-model="quickFundType" class="p-2.5 bg-slate-50 border rounded-xl text-xs font-bold outline-none">
                  <option value="add">Add Fund (+)</option>
                  <option value="deduct">Deduct Fund (-)</option>
                </select>
                <input type="number" step="0.1" v-model="quickFundAmount" placeholder="Amount (৳)" class="p-2.5 bg-slate-50 border rounded-xl text-xs font-bold outline-none focus:border-indigo-500 w-28" />
                <button @click="executeQuickFund" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition shadow-sm active:scale-95">
                  Inject Balance
                </button>
              </div>
            </div>

            <!-- Date Filter Stats Row -->
            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b pb-3">
                <div>
                  <h4 class="font-bold text-xs text-slate-400 uppercase tracking-widest">Time-Based Range Conversion (All Users)</h4>
                  <p class="text-[10px] text-slate-400 font-semibold">নির্দিষ্ট সময়ে নেটওয়ার্কে নেওয়া নম্বর, ওটিপি এবং কনভার্সন রেট রিপোর্ট</p>
                </div>
                <div class="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-xl">
                  <button v-for="t in ['today', 'yesterday', '7days', '15days', '30days', 'lifetime']" :key="t" @click="adminTimeFilter = t" :class="adminTimeFilter === t ? 'bg-rose-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-200'" class="px-2.5 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-wider transition">
                    {{ t === '7days' ? '7 Days' : t === '15days' ? '15 Days' : t === '30days' ? '30 Days' : t }}
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div class="bg-slate-50 p-4 rounded-xl border">
                  <span class="text-[9px] text-slate-400 font-bold block uppercase">Numbers Booked</span>
                  <span class="text-xl font-black text-slate-800 block mt-1">{{ adminPeriodStats.total }}</span>
                </div>
                <div class="bg-emerald-50/50 p-4 rounded-xl border border-emerald-100">
                  <span class="text-[9px] text-emerald-600 font-bold block uppercase">Success OTPs</span>
                  <span class="text-xl font-black text-emerald-600 block mt-1">{{ adminPeriodStats.success }}</span>
                </div>
                <div class="bg-indigo-50/50 p-4 rounded-xl border border-indigo-100">
                  <span class="text-[9px] text-indigo-600 font-bold block uppercase">Success Rate</span>
                  <span class="text-xl font-black text-indigo-600 block mt-1">{{ adminPeriodStats.successRate }}%</span>
                </div>
                <div class="bg-rose-50/50 p-4 rounded-xl border border-rose-100">
                  <span class="text-[9px] text-rose-600 font-bold block uppercase">Failed Numbers</span>
                  <span class="text-xl font-black text-rose-600 block mt-1">{{ adminPeriodStats.failed }}</span>
                </div>
                <div class="bg-slate-50 p-4 rounded-xl border">
                  <span class="text-[9px] text-slate-500 font-bold block uppercase">Failed Rate</span>
                  <span class="text-xl font-black text-slate-600 block mt-1">{{ adminPeriodStats.failRate }}%</span>
                </div>
              </div>
            </div>

            <!-- Recent Live OTP Logs Section -->
            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <div class="flex justify-between items-center border-b pb-3">
                <h4 class="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <i class="fa-solid fa-envelope-open-text text-rose-600"></i> Recent OTP Logs
                </h4>
                <span class="text-[10px] text-slate-400 font-semibold">সর্বশেষ ১০টি ওটিপি রিসিভ রিপোর্ট</span>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b text-slate-400 uppercase tracking-wider font-bold">
                      <th class="p-3">User</th>
                      <th class="p-3">Number</th>
                      <th class="p-3">Service</th>
                      <th class="p-3">OTP Code</th>
                      <th class="p-3">Logged At</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="otpLogs.length === 0">
                      <td colspan="5" class="p-4 text-center text-slate-400">No OTP logs available.</td>
                    </tr>
                    <tr v-else-if="otpLogs" v-for="log in otpLogs.slice(0, 10)" :key="log.id || log.createdAt" class="hover:bg-slate-50/50">
                      <td class="p-3">
                        <p class="font-black text-slate-900">{{ getUserName(log.userId) }}</p>
                        <p class="text-[10px] text-[#0088CC]">{{ getUserIdCode(log.userId) }}</p>
                      </td>
                      <td class="p-3 font-mono cursor-pointer hover:text-indigo-600" @click="copyToClipboard(log.number, 'Number Copied', 'dash_num_' + (log.id||log.number))">{{ log.number }}</td>
                      <td class="p-3 uppercase text-[#0088CC]">{{ log.service }}</td>
                      <td class="p-3 font-black text-emerald-600 font-mono cursor-pointer hover:underline" @click="copyToClipboard(log.otpCode, 'OTP Code Copied', 'dash_otp_' + (log.id||log.otpCode))">{{ log.otpCode }}</td>
                      <td class="p-3 text-[10px] text-slate-400 font-mono">{{ formatTimestamp(log.createdAt) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- System Audit Trail Logs View -->
            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h4 class="font-bold text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-clock-rotate-left text-amber-600"></i> System Audit Trail Logs
              </h4>
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b text-slate-400 uppercase tracking-wider font-bold">
                      <th class="p-3">Action Description</th>
                      <th class="p-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="auditLogs.length === 0">
                      <td colspan="2" class="p-4 text-center text-slate-400">No admin audit events captured.</td>
                    </tr>
                    <tr v-else v-for="log in auditLogs.slice(0, 15)" :key="log.id" class="hover:bg-slate-50/50">
                      <td class="p-3 text-slate-900 select-all font-mono leading-relaxed">{{ log.message }}</td>
                      <td class="p-3 text-[10px] text-slate-400 font-mono">{{ formatTimestamp(log.createdAt) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 2: User Administration ==================== -->
          <div v-if="currentTab === 'users'" class="fade-enter-active space-y-4">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <input type="text" v-model="searchQuery" placeholder="Search users by name, email..." class="w-full sm:w-80 p-3 bg-white border rounded-2xl text-xs font-semibold outline-none focus:border-rose-600" />
              
              <button @click="exportUsersToCSV" class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition flex items-center gap-1">
                <i class="fa-solid fa-file-csv"></i> Export Users CSV
              </button>
            </div>

            <div class="bg-white rounded-3xl border shadow-xs overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider font-bold">
                      <th class="p-4">User & ID Code</th>
                      <th class="p-4">Assigned Agent</th>
                      <th class="p-4">Email (Click to Copy)</th>
                      <th class="p-4">Balance</th>
                      <th class="p-4">OTP Rate (৳)</th>
                      <th class="p-4">API Key</th>
                      <th class="p-4">Status</th>
                      <th class="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-semibold text-slate-707">
                    <tr v-if="filteredUsersList.length === 0">
                      <td colspan="8" class="p-8 text-center text-slate-400 font-bold">No users match your criteria.</td>
                    </tr>
                    <tr v-else v-for="u in filteredUsersList" :key="u.uid" class="hover:bg-slate-50/50 transition">
                      <td class="p-4">
                        <p class="font-black text-slate-900 text-sm">{{ u.name }}</p>
                        <p class="text-[10px] text-[#0088CC] cursor-pointer" @click="copyToClipboard(u.id_code, 'ID Code Copied', 'id_copy_' + u.uid)">{{ u.id_code }}</p>
                        <span class="text-[9px] text-slate-400 cursor-pointer" @click="copyToClipboard(u.uid, 'UID Copied', 'uid_copy_' + u.uid)">UID: {{ u.uid }}</span>
                      </td>
                      <td class="p-4">
                        <span class="bg-purple-100 text-purple-800 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase">
                          {{ getAgentName(u.agent_uid) }}
                        </span>
                      </td>
                      <td class="p-4 cursor-pointer hover:text-rose-600" @click="copyToClipboard(u.email, 'Email Address Copied', 'email_copy_' + u.uid)">
                        <p class="font-bold text-slate-800">{{ u.email }}</p>
                        <p class="text-[10px] text-slate-400">Password is securely stored</p>
                        <span v-if="copiedStates['email_copy_' + u.uid]" class="text-[8px] text-emerald-600 font-black block">Copied!</span>
                      </td>
                      <td class="p-4 font-black text-slate-800">৳ {{ parseFloat(u.balance).toFixed(2) }}</td>
                      <td class="p-4 font-bold text-slate-800">৳ {{ parseFloat(u.otp_rate).toFixed(2) }}</td>
                      <td class="p-4">
                        <span v-if="u.api_key_approved" class="text-emerald-600 font-bold text-[10px] cursor-pointer" @click="copyToClipboard(u.api_key, 'API Key Copied', 'key_copy_' + u.uid)"><i class="fa-solid fa-circle-check"></i> Approved</span>
                        <span v-else-if="u.api_key" class="text-amber-600 font-bold text-[10px] animate-pulse"><i class="fa-solid fa-circle-question"></i> Pending</span>
                        <span v-else class="text-slate-400 text-[10px]">No Key</span>
                      </td>
                      <td class="p-4">
                        <span v-if="u.status === 'approved'" class="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Approved</span>
                        <span v-else-if="u.status === 'pending'" class="bg-amber-100 text-amber-800 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Pending</span>
                        <span v-else class="bg-rose-100 text-rose-800 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Banned</span>
                      </td>
                      <td class="p-4 text-right space-x-1 whitespace-nowrap">
                        <button @click="viewUserStatus(u.uid)" class="bg-teal-50 hover:bg-teal-100 text-teal-700 text-[11px] font-bold px-3 py-1.5 rounded-xl transition">View Status</button>
                        <button @click="openEditModal(u)" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-bold px-3 py-1.5 rounded-xl transition">Edit</button>
                        <button @click="deleteUser(u.uid)" class="bg-rose-50 hover:bg-rose-100 text-rose-700 text-[11px] font-bold px-3 py-1.5 rounded-xl transition">Delete</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 2.5: Agent Administration ==================== -->
          <div v-if="currentTab === 'agents'" class="fade-enter-active space-y-4">
            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h3 class="font-black text-xs text-indigo-600 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-plus"></i> Create New Official Agent
              </h3>
              
              <div class="grid md:grid-cols-2 gap-4 text-xs font-bold">
                <div>
                  <label class="text-slate-500">Agent Full Name</label>
                  <input type="text" v-model="newAgent.name" placeholder="Mino Agent" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl" />
                </div>
                <div>
                  <label class="text-slate-500">Agent Email</label>
                  <input type="email" v-model="newAgent.email" placeholder="agent@minosms.xyz" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl" />
                </div>
                <div>
                  <label class="text-slate-500">Agent Password</label>
                  <input type="password" v-model="newAgent.password" placeholder="Enter a secure password" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl" />
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <label class="text-slate-500">User Quota Limit</label>
                    <input type="number" v-model.number="newAgent.limit" placeholder="120" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl" />
                  </div>
                  <div>
                    <label class="text-slate-500">Agent Base Rate (৳)</label>
                    <input type="number" step="0.01" v-model.number="newAgent.rate" placeholder="0.63" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl" />
                  </div>
                </div>
              </div>

              <div class="flex justify-end">
                <button @click="createAgent" class="bg-indigo-600 hover:bg-indigo-700 text-white font-black text-xs px-6 py-3 rounded-xl transition active:scale-95">
                  Register Agent
                </button>
              </div>
            </div>

            <!-- Agents List -->
            <div class="bg-white rounded-3xl border shadow-xs overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b text-slate-400 uppercase font-bold">
                      <th class="p-4">Agent details</th>
                      <th class="p-4">Agent Mail</th>
                      <th class="p-4">Quota Utilized</th>
                      <th class="p-4">Base Rate (৳)</th>
                      <th class="p-4">Status</th>
                      <th class="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="agentsList.length === 0">
                      <td colspan="6" class="p-8 text-center text-slate-400 font-bold">No agents currently created.</td>
                    </tr>
                    <tr v-else v-for="agent in agentsList" :key="agent.uid" class="hover:bg-slate-50/50">
                      <td class="p-4">
                        <p class="font-black text-slate-900 text-sm">{{ agent.name }}</p>
                        <p class="text-[10px] text-slate-400">ID Code: {{ agent.id_code }}</p>
                      </td>
                      <td class="p-4 cursor-pointer hover:text-rose-600" @click="copyToClipboard(agent.email, 'Email Address Copied', 'email_copy_' + agent.uid)">
                        <span class="bg-indigo-100 text-indigo-800 text-[10px] font-bold px-2.5 py-1 rounded-full select-all font-mono">
                          {{ agent.email }}
                        </span>
                        <span v-if="copiedStates['email_copy_' + agent.uid]" class="text-[8px] text-emerald-600 block mt-1">Copied!</span>
                      </td>
                      <td class="p-4">
                        <div class="flex items-center gap-2">
                          <span class="font-bold text-slate-800">{{ getAgentUserCount(agent.uid) }} / {{ agent.agent_limit || 120 }} used</span>
                        </div>
                      </td>
                      <td class="p-4 font-black">৳ {{ parseFloat(agent.otp_rate || 0.63).toFixed(2) }}</td>
                      <td class="p-4">
                        <span v-if="agent.status === 'approved'" class="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Active</span>
                        <span v-else class="bg-rose-100 text-rose-800 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Suspended</span>
                      </td>
                      <td class="p-4 text-right space-x-1 whitespace-nowrap">
                        <button @click="viewUserStatus(agent.uid)" class="bg-teal-50 hover:bg-teal-100 text-teal-700 text-[11px] font-bold px-3 py-1.5 rounded-xl transition">View Status</button>
                        <button @click="openEditModal(agent)" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-bold px-3 py-1.5 rounded-xl transition">Edit Agent</button>
                        <button @click="deleteUser(agent.uid)" class="bg-rose-50 hover:bg-rose-100 text-rose-700 text-[11px] font-bold px-3 py-1.5 rounded-xl transition">Remove</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 3: Withdrawal Requests ==================== -->
          <div v-if="currentTab === 'withdrawals'" class="fade-enter-active space-y-4">
            <div class="bg-white rounded-3xl border shadow-xs overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider font-bold">
                      <th class="p-4">User & Account Details</th>
                      <th class="p-4">Amount Requested</th>
                      <th class="p-4">Method</th>
                      <th class="p-4">Destination Wallet Address</th>
                      <th class="p-4">Status</th>
                      <th class="p-4">Requested At</th>
                      <th class="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-semibold text-slate-707">
                    <tr v-if="withdrawals.length === 0">
                      <td colspan="7" class="p-8 text-center text-slate-400 font-bold">No withdrawal requests found.</td>
                    </tr>
                    <tr v-else-if="withdrawals" v-for="wd in withdrawals" :key="wd.id" class="hover:bg-slate-50/50 transition">
                      <td class="p-4">
                        <p class="font-black text-slate-900 text-sm">{{ wd.userName }}</p>
                        <p class="text-[10px] text-slate-400 mt-0.5">{{ wd.userEmail }}</p>
                      </td>
                      <td class="p-4 font-black text-rose-600 text-sm">৳ {{ parseFloat(wd.amount || 0).toFixed(2) }}</td>
                      <td class="p-4 font-black text-indigo-600 uppercase">{{ wd.method }}</td>
                      <td class="p-4 font-mono select-all text-slate-800 break-all max-w-xs cursor-pointer hover:text-indigo-600" @click="copyToClipboard(wd.address, 'Wallet Address Copied', 'wd_addr_' + wd.id)">{{ wd.address }}</td>
                      <td class="p-4">
                        <span v-if="wd.status === 'approved'" class="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Approved</span>
                        <span v-else-if="wd.status === 'pending'" class="bg-amber-100 text-amber-808 text-[10px] font-black px-2.5 py-1 rounded-full uppercase animate-pulse">Pending</span>
                        <span v-else class="bg-rose-100 text-rose-800 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Rejected</span>
                      </td>
                      <td class="p-4 font-mono text-slate-400 text-[10px]">{{ formatTimestamp(wd.createdAt) }}</td>
                      <td class="p-4 text-right space-x-1 whitespace-nowrap">
                        <button v-if="wd.status === 'pending'" @click="processWithdrawal(wd.id, 'approved')" class="bg-[#0088CC] text-white text-[10px] font-black px-3 py-1.5 rounded-xl transition">Approve</button>
                        <button v-if="wd.status === 'pending'" @click="processWithdrawal(wd.id, 'rejected')" class="bg-rose-600 hover:bg-rose-700 text-white text-[10px] font-black px-3 py-1.5 rounded-xl transition">Reject</button>
                        <span v-else class="text-slate-400 italic">Completed</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 4: Number Tracking Logs ==================== -->
          <div v-if="currentTab === 'allocations'" class="fade-enter-active space-y-4">
            <div class="bg-white rounded-3xl border shadow-xs overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider font-bold">
                      <th class="p-4">User</th>
                      <th class="p-4">Allocated Number</th>
                      <th class="p-4">Range ID</th>
                      <th class="p-4">Country & Provider</th>
                      <th class="p-4">Status</th>
                      <th class="p-4">Created At</th>
                      <th class="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-semibold text-slate-707">
                    <tr v-if="allocations.length === 0">
                      <td colspan="7" class="p-8 text-center text-slate-400 font-bold">No active or historic allocations found.</td>
                    </tr>
                    <tr v-else v-for="a in allocations" :key="a.id">
                      <td class="p-4">
                        <p class="font-black text-slate-900">{{ getUserName(a.userId) }}</p>
                        <p class="text-[10px] text-slate-400 font-mono">{{ getUserIdCode(a.userId) }}</p>
                      </td>
                      <td class="p-4 font-black text-slate-900 text-sm font-mono cursor-pointer hover:text-indigo-600" @click="copyToClipboard(a.number, 'Number Copied', 'alloc_num_' + a.id)">{{ a.number }}</td>
                      <td class="p-4 font-mono font-bold text-[#0088CC] cursor-pointer" @click="copyToClipboard(a.rid, 'Range ID Copied', 'alloc_rid_' + a.id)">{{ a.rid }}</td>
                      <td class="p-4">
                        <p class="font-bold text-slate-800">{{ a.country }}</p>
                        <p class="text-[10px] text-slate-400 mt-0.5 uppercase">{{ a.operator }}</p>
                      </td>
                      <td class="p-4">
                        <span v-if="a.status === 'active'" class="bg-amber-100 text-amber-808 text-[9px] font-black px-2 py-0.5 rounded uppercase">ACTIVE</span>
                        <span v-else-if="a.status === 'completed'" class="bg-emerald-100 text-emerald-800 text-[9px] font-black px-2 py-0.5 rounded uppercase">SUCCESS</span>
                        <span v-else class="bg-slate-100 text-slate-500 text-[9px] font-black px-2 py-0.5 rounded uppercase">EXPIRED</span>
                      </td>
                      <td class="p-4 font-mono text-slate-400 text-[10px]">{{ formatTimestamp(a.createdAt) }}</td>
                      <td class="p-4 text-right whitespace-nowrap">
                        <button v-if="a.status === 'active'" @click="refundAllocation(a.id)" class="bg-rose-100 hover:bg-rose-200 text-rose-700 text-[10px] font-bold px-3 py-1.5 rounded-xl transition">Refund & Cancel</button>
                        <span v-else class="text-slate-400 italic text-[10px]">-</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 5: Global OTP logs ==================== -->
          <div v-if="currentTab === 'otp-logs'" class="fade-enter-active space-y-4">
            <div class="bg-white rounded-3xl border shadow-xs overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider font-bold">
                      <th class="p-4">User</th>
                      <th class="p-4">Number</th>
                      <th class="p-4">Service</th>
                      <th class="p-4">OTP Code</th>
                      <th class="p-4">SMS Content</th>
                      <th class="p-4">Revenue</th>
                      <th class="p-4">Logged At</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-semibold text-slate-707">
                    <tr v-if="otpLogs.length === 0">
                      <td colspan="7" class="p-8 text-center text-slate-400 font-bold">No global OTP logs recorded.</td>
                    </tr>
                    <tr v-else v-for="log in otpLogs" :key="log.createdAt">
                      <td class="p-4">
                        <p class="font-black text-slate-900">{{ getUserName(log.userId) }}</p>
                        <p class="text-[10px] text-[#0088CC]">{{ getUserIdCode(log.userId) }}</p>
                      </td>
                      <td class="p-4 font-black text-slate-900 font-mono cursor-pointer hover:text-indigo-600" @click="copyToClipboard(log.number, 'Number Copied', 'log_num_' + log.createdAt)">{{ log.number }}</td>
                      <td class="p-4 uppercase text-[#0088CC] font-black text-[10px]">{{ log.service }}</td>
                      <td class="p-4 font-black text-emerald-600 text-sm font-mono cursor-pointer hover:underline" @click="copyToClipboard(log.otpCode, 'OTP Code Copied', 'log_otp_' + log.createdAt)">{{ log.otpCode }}</td>
                      <td class="p-4 text-slate-500 leading-relaxed max-w-xs truncate cursor-pointer hover:text-slate-900" @click="copyToClipboard(log.message, 'SMS Message Copied', 'log_msg_' + log.createdAt)" :title="log.message">{{ log.message }}</td>
                      <td class="p-4 font-black text-slate-900">৳ {{ parseFloat(log.revenue || 0).toFixed(2) }}</td>
                      <td class="p-4 font-mono text-slate-400 text-[10px]">{{ formatTimestamp(log.createdAt) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 6: Top Number User ==================== -->
          <div v-if="currentTab === 'top-number-user'" class="fade-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border shadow-xs">
              <h3 class="font-black text-sm text-slate-800 flex items-center gap-2 mb-4">
                <i class="fa-solid fa-phone text-rose-600"></i> Top User - Number Booking Count
              </h3>
              <div class="overflow-x-auto font-bold">
                <table class="w-full text-left text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b font-bold text-slate-400 uppercase">
                      <th class="p-4">Rank</th>
                      <th class="p-4">Name</th>
                      <th class="p-4">ID Code</th>
                      <th class="p-4">Numbers Taken</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="topNumberUsers.length === 0">
                      <td colspan="4" class="p-8 text-center text-slate-400 font-bold">No booking logs found.</td>
                    </tr>
                    <tr v-else v-for="(worker, idx) in topNumberUsers" :key="idx" class="hover:bg-slate-50">
                      <td class="p-4 font-black">#{{ idx + 1 }}</td>
                      <td class="p-4 font-black text-slate-900">{{ worker.name }}</td>
                      <td class="p-4 text-[#0088CC] cursor-pointer" @click="copyToClipboard(worker.id_code, 'ID Code Copied', 'top_num_id_' + idx)">{{ worker.id_code }}</td>
                      <td class="p-4 text-sm font-black">{{ worker.count }} numbers</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 7: Top OTP User ==================== -->
          <div v-if="currentTab === 'top-otp-user'" class="fade-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border shadow-xs">
              <h3 class="font-black text-sm text-slate-800 flex items-center gap-2 mb-4">
                <i class="fa-solid fa-envelope-circle-check text-rose-600"></i> Top User - Successful OTP Count
              </h3>
              <div class="overflow-x-auto font-bold">
                <table class="w-full text-left text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b font-bold text-slate-400 uppercase">
                      <th class="p-4">Rank</th>
                      <th class="p-4">Name</th>
                      <th class="p-4">ID Code</th>
                      <th class="p-4">Successful OTPs</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="topOtpUsers.length === 0">
                      <td colspan="4" class="p-8 text-center text-slate-400 font-bold">No successful OTP logs found.</td>
                    </tr>
                    <tr v-else v-for="(worker, idx) in topOtpUsers" :key="idx" class="hover:bg-slate-50">
                      <td class="p-4 font-black">#{{ idx + 1 }}</td>
                      <td class="p-4 font-black text-slate-900">{{ worker.name }}</td>
                      <td class="p-4 text-[#0088CC] cursor-pointer" @click="copyToClipboard(worker.id_code, 'ID Code Copied', 'top_otp_id_' + idx)">{{ worker.id_code }}</td>
                      <td class="p-4 text-sm font-black text-emerald-600">{{ worker.count }} OTPs</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 8: Inactive User ==================== -->
          <div v-if="currentTab === 'inactive-user'" class="fade-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border shadow-xs">
              <h3 class="font-black text-sm text-slate-800 flex items-center gap-2 mb-4">
                <i class="fa-solid fa-user-slash text-rose-600"></i> Inactive Users (0 Number Booking History)
              </h3>
              <div class="overflow-x-auto font-bold">
                <table class="w-full text-left text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b font-bold text-slate-400 uppercase">
                      <th class="p-4">Name</th>
                      <th class="p-4">Email</th>
                      <th class="p-4">ID Code</th>
                      <th class="p-4">Registration Date</th>
                      <th class="p-4">Status</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="inactiveUsersList.length === 0">
                      <td colspan="5" class="p-8 text-center text-slate-400 font-bold">No inactive users found.</td>
                    </tr>
                    <tr v-else v-for="user in inactiveUsersList" :key="user.uid" class="hover:bg-slate-50">
                      <td class="p-4 font-black text-slate-900">{{ user.name }}</td>
                      <td class="p-4 font-mono select-all cursor-pointer hover:text-indigo-600" @click="copyToClipboard(user.email, 'Email Copied', 'inact_email_' + user.uid)">{{ user.email }}</td>
                      <td class="p-4 text-[#0088CC] cursor-pointer" @click="copyToClipboard(user.id_code, 'ID Code Copied', 'inact_id_' + user.uid)">{{ user.id_code }}</td>
                      <td class="p-4 text-slate-400 font-mono">{{ formatTimestamp(user.createdAt) }}</td>
                      <td class="p-4 font-black text-rose-600 uppercase">{{ user.status }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 9: Top Service ==================== -->
          <div v-if="currentTab === 'top-service'" class="fade-enter-active space-y-4">
            <div class="bg-white p-5 rounded-3xl border shadow-xs">
              <h3 class="font-black text-sm text-slate-800 flex items-center gap-2 mb-4">
                <i class="fa-solid fa-sliders text-rose-600"></i> Top Performing Services & OTP Ratio
              </h3>
              <div class="overflow-x-auto font-bold">
                <table class="w-full text-left text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b font-bold text-slate-400 uppercase">
                      <th class="p-4">Rank</th>
                      <th class="p-4">Service Name</th>
                      <th class="p-4">Total Successful OTPs</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold text-slate-707">
                    <tr v-if="topServicesList.length === 0">
                      <td colspan="3" class="p-8 text-center text-slate-400 font-bold">No service activity found.</td>
                    </tr>
                    <tr v-else-if="topServicesList" v-for="(service, idx) in topServicesList" :key="idx" class="hover:bg-slate-50">
                      <td class="p-4 font-black">#{{ idx + 1 }}</td>
                      <td class="p-4 font-black text-slate-900 uppercase">{{ service.name }}</td>
                      <td class="p-4 font-black text-[#0088CC] text-sm">{{ service.count }} successful transactions</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 10: Ban & Verification Center ==================== -->
          <div v-if="currentTab === 'security-hub'" class="fade-enter-active space-y-6">
            <div class="bg-white p-6 rounded-3xl border border-rose-150 shadow-xs space-y-4">
              <h4 class="font-bold text-sm text-rose-600 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-user-shield"></i> Account Security Hub
              </h4>
              <p class="text-[10px] text-slate-400 font-medium leading-relaxed">
                পেন্ডিং ও ব্লকড অ্যাকাউন্টগুলোকে দ্রুত সনাক্ত ও পরিচালনা করার ডেডিকেটেড অ্যাডমিন সিকিউরিটি হাব।
              </p>

              <div class="overflow-x-auto mt-4 font-bold">
                <table class="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr class="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider font-bold">
                      <th class="p-4">User</th>
                      <th class="p-4">Email</th>
                      <th class="p-4">Status</th>
                      <th class="p-4 text-right">Instant Quick Controls</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 font-semibold text-slate-707">
                    <tr v-if="restrictedUsers.length === 0">
                      <td colspan="4" class="p-8 text-center text-slate-400 font-bold">No accounts are currently pending or banned! All is secure.</td>
                    </tr>
                    <tr v-else v-for="u in restrictedUsers" :key="u.uid" class="hover:bg-slate-50/50">
                      <td class="p-4">
                        <p class="font-black text-slate-900 text-sm">{{ u.name }}</p>
                        <p class="text-[10px] text-[#0088CC] cursor-pointer" @click="copyToClipboard(u.id_code, 'ID Code Copied', 'sec_id_' + u.uid)">{{ u.id_code }}</p>
                      </td>
                      <td class="p-4 font-mono text-slate-600 cursor-pointer hover:text-indigo-600" @click="copyToClipboard(u.email, 'Email Copied', 'sec_email_' + u.uid)">{{ u.email }}</td>
                      <td class="p-4">
                        <span v-if="u.status === 'pending'" class="bg-amber-100 text-amber-808 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Pending</span>
                        <span v-else class="bg-rose-100 text-rose-808 text-[10px] font-black px-2.5 py-1 rounded-full uppercase">Banned</span>
                      </td>
                      <td class="p-4 text-right space-x-1 whitespace-nowrap">
                        <button v-if="u.status === 'pending' || u.status === 'banned'" @click="updateUserStatusDirect(u.uid, 'approved')" class="bg-emerald-600 hover:bg-emerald-700 text-white text-[10px] font-bold px-3 py-1.5 rounded-xl transition shadow-xs">Approve Account</button>
                        <button v-if="u.status === 'pending'" @click="updateUserStatusDirect(u.uid, 'banned')" class="bg-rose-600 hover:bg-rose-700 text-white text-[10px] font-bold px-3 py-1.5 rounded-xl transition shadow-xs">Ban User</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ==================== Tab 11: System Settings & Controls ==================== -->
          <div v-if="currentTab === 'settings'" class="fade-enter-active space-y-6">
            
            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-3">
              <h3 class="font-black text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-heart-pulse text-rose-600"></i> Database Health & Monitor Status
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-bold">
                <div class="bg-slate-50 p-3 rounded-xl border">
                  <span class="text-[9px] font-bold text-slate-400 block uppercase">SYSTEM STATUS</span>
                  <span class="text-sm font-black text-slate-800">Optimized MySQL</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border">
                  <span class="text-[9px] font-bold text-slate-400 block uppercase">AUTO BACKUP ENGINE</span>
                  <span class="text-sm font-black text-emerald-600">Active</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border">
                  <span class="text-[9px] font-bold text-slate-400 block uppercase">TOTAL CONSOLE DATA</span>
                  <span class="text-sm font-black text-rose-600">{{ otpLogs.length }} units</span>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border">
                  <span class="text-[9px] font-bold text-slate-400 block uppercase">ALLOCATION COUNTER</span>
                  <span class="text-sm font-black text-[#0088CC]">{{ stats.total_allocations }} orders</span>
                </div>
              </div>
            </div>

            <div class="bg-white p-6 rounded-3xl border border-rose-100 bg-rose-50/5 shadow-xs space-y-3">
              <h3 class="font-black text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-broom text-rose-600"></i> Sweep & Garbage Clean Utilities
              </h3>
              <p class="text-[10px] text-slate-400 font-semibold leading-relaxed">
                প্যানেলের ১৮ মিনিটের বেশি সময় ধরে ঝুলে থাকা পেন্ডিং অর্ডারগুলো রিমুভ করে গেটওয়ে মেমোরি খালি করতে নিচের বাটনটি চাপুন।
              </p>
              <button @click="executeStaleSweep" class="bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs px-5 py-3 rounded-xl transition shadow-xs active:scale-95 w-max block font-bold">
                Run Allocation Clean Sweep
              </button>
            </div>

            <div class="bg-white p-6 rounded-3xl border border-indigo-150 shadow-xs space-y-4">
              <h3 class="font-black text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-flask text-indigo-600"></i> Admin Gateway Live Test Lab
              </h3>
              <p class="text-[10px] text-slate-400 font-semibold leading-relaxed">
                কোনো ইউজারের নম্বর রিকোয়েস্ট ছাড়াই সরাসরি মেইন গেটওয়ে এপিআই থেকে রেঞ্জ সোর্স চেক করতে আইডি লিখুন।
              </p>
              <div class="flex gap-2 text-xs">
                <input type="text" v-model="testRangeId" placeholder="Range ID (e.g. 2250789XXX)" class="p-2.5 border rounded-xl font-bold outline-none tracking-wider text-indigo-600" />
                <button @click="testVoltxRange" :disabled="testLoading" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-5 py-2.5 rounded-xl transition active:scale-95 disabled:bg-slate-200 shadow-sm font-bold">
                  {{ testLoading ? 'Querying...' : 'Execute Check' }}
                </button>
              </div>
              <div v-if="testResult" class="mt-4 p-4 bg-slate-900 text-emerald-400 rounded-2xl font-mono text-[10px] select-all leading-relaxed overflow-x-auto">
                <span class="text-white block font-bold mb-2">Gate Status: {{ testResult.gateway_status }}</span>
                {{ JSON.stringify(testResult.raw_payload, null, 2) }}
              </div>
            </div>

            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h3 class="font-black text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-tower-broadcast text-rose-600"></i> SMS Gateway Manager
              </h3>
              <p class="text-[10px] text-slate-400 font-semibold leading-relaxed">
                আপনার ওয়েবসাইটের মেইন ব্যাকএন্ড গেটওয়ে নির্ধারণ করুন।
              </p>

              <div class="space-y-4 font-bold">
                <div>
                  <label class="text-xs font-bold text-slate-500">Select Primary SMS Backend Provider</label>
                  <select v-model="gatewayConfig.active_gateway" class="w-full mt-1.5 p-3.5 bg-slate-50 border rounded-xl text-sm font-bold">
                    <option value="voltx">Voltx SMS Gateways</option>
                    <option value="yesms">Yesms Online API Provider</option>
                  </select>
                </div>

                <div v-if="gatewayConfig.active_gateway === 'voltx'" class="bg-slate-50 p-4 rounded-xl border border-rose-300">
                  <h4 class="font-black text-xs text-rose-600 uppercase mb-3">Voltx Backend Configurations</h4>
                  <div class="grid md:grid-cols-2 gap-3 text-xs font-bold">
                    <div>
                      <label>Voltx Base URL</label>
                      <input type="text" v-model="gatewayConfig.voltx_base_url" class="w-full mt-1.5 p-3 bg-white border rounded-xl font-mono" />
                    </div>
                    <div>
                      <label>Voltx API Key</label>
                      <input type="text" v-model="gatewayConfig.voltx_api_key" class="w-full mt-1.5 p-3 bg-white border rounded-xl font-mono" />
                    </div>
                  </div>
                </div>

                <div v-if="gatewayConfig.active_gateway === 'yesms'" class="bg-slate-50 p-4 rounded-xl border border-blue-300">
                  <h4 class="font-black text-xs text-blue-600 uppercase mb-3">Yesms Backend Configurations</h4>
                  <div class="grid md:grid-cols-2 gap-3 text-xs font-bold">
                    <div>
                      <label>Yesms Base URL</label>
                      <input type="text" v-model="gatewayConfig.yesms_base_url" class="w-full mt-1.5 p-3 bg-white border rounded-xl font-mono" />
                    </div>
                    <div>
                      <label>Yesms authkey (API Private Key)</label>
                      <input type="text" v-model="gatewayConfig.yesms_api_key" class="w-full mt-1.5 p-3 bg-white border rounded-xl font-mono" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="flex justify-end pt-2">
                <button @click="saveGatewaySettings" class="bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold px-5 py-2.5 rounded-xl transition shadow-xs active:scale-95 font-bold">
                  Save Gateway Configs
                </button>
              </div>
            </div>

            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h3 class="font-black text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-wallet text-indigo-600"></i> Configure User Withdrawal Payment Methods
              </h3>
              
              <div class="bg-slate-50 p-4 rounded-2xl border flex flex-col sm:flex-row gap-3 text-xs font-bold">
                <div class="flex-1">
                  <label>Method Name</label>
                  <input type="text" v-model="newMethodName" placeholder="Bkash / USDT (TRC20)" class="w-full mt-1 p-2.5 bg-white border rounded-xl" />
                </div>
                <div class="flex-1">
                  <label>Instruction Info</label>
                  <input type="text" v-model="newMethodInstruction" placeholder="Bkash personal account number দিন" class="w-full mt-1 p-2.5 bg-white border rounded-xl" />
                </div>
                <button @click="createWithdrawalMethod" class="bg-indigo-600 text-white px-5 rounded-xl text-xs font-black shrink-0 mt-5 h-10 font-bold">Add Method</button>
              </div>

              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs font-bold">
                  <thead>
                    <tr class="bg-slate-50 border-b font-bold text-slate-400 uppercase">
                      <th class="p-3">Method Name</th>
                      <th class="p-3">Instructions</th>
                      <th class="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y font-semibold">
                    <tr v-for="m in withdrawalMethods" :key="m.id" class="hover:bg-slate-50">
                      <td class="p-3 font-bold text-slate-800">{{ m.method_name }}</td>
                      <td class="p-3 text-slate-500">{{ m.instructions }}</td>
                      <td class="p-3 text-right">
                        <button @click="deleteWithdrawalMethod(m.id)" class="text-rose-600 hover:text-rose-800 font-bold">Remove</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h3 class="font-black text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-shield-halved text-rose-600"></i> Automation, Maintenance & Payout Controls
              </h3>
              <div class="grid md:grid-cols-3 gap-4 font-bold">
                
                <div class="bg-slate-50 p-4 rounded-xl border border-rose-200 space-y-2">
                  <p class="font-black text-xs text-slate-800">Maintenance Mode</p>
                  <p class="text-[10px] text-slate-400">অন করা থাকলে ইউজাররা সাইটে প্রবেশ করতে পারবে না এবং সার্ভিস লক হয়ে যাবে।</p>
                  <button @click="toggleMaintenanceMode" :class="stats.maintenance_mode ? 'bg-rose-600 text-white' : 'bg-slate-200 text-slate-600 border'" class="px-4 py-2 rounded-xl text-xs font-black transition active:scale-95">
                    {{ stats.maintenance_mode ? 'ON (SYSTEM LOCKED)' : 'OFF (SYSTEM LIVE)' }}
                  </button>
                </div>

                <div class="bg-slate-50 p-4 rounded-xl border space-y-2">
                  <p class="font-black text-xs text-slate-800">Auto Account Approval</p>
                  <p class="text-[10px] text-slate-400">অন করা থাকলে নতুন ইউজার রেজিস্ট্রেশন করা মাত্রই স্বয়ংক্রিয়ভাবে অ্যাকাউন্ট সচল হয়ে যাবে।</p>
                  <button @click="toggleAutoApproveAccount" :class="stats.auto_approve_account ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-600'" class="px-4 py-2 rounded-xl text-xs font-black transition">
                    {{ stats.auto_approve_account ? 'ON (AUTO)' : 'OFF (MANUAL)' }}
                  </button>
                </div>

                <div class="bg-slate-50 p-4 rounded-xl border space-y-2">
                  <p class="font-black text-xs text-slate-800">Global Reset Users Payout Rate</p>
                  <p class="text-[10px] text-slate-400">এক ক্লিকে সকল ইউজারের বেস ওটিপি রেট একসাথে পরিবর্তন করুন।</p>
                  <div class="flex gap-2">
                    <input type="number" step="0.01" v-model="globalBaseRateInput" class="p-2 border rounded-lg text-xs font-bold w-24" placeholder="0.40" />
                    <button @click="saveGlobalBaseRate" class="bg-rose-600 text-white px-3 py-2 rounded-xl text-xs font-black transition active:scale-95">Apply All</button>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4 font-bold">
              <h3 class="font-black text-xs text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-money-bill-trend-up text-rose-600"></i> Bulk Balance Fund Adjuster
              </h3>
              <p class="text-[10px] text-slate-400 font-semibold leading-relaxed">
                প্যানেলে থাকা সমস্ত এপ্রুভড একটিভ ইউজারদের অ্যাকাউন্টে একসাথে নির্দিষ্ট পরিমাণ ব্যালেন্স যুক্ত বা কর্তন করুন।
              </p>
              <div class="flex flex-wrap gap-2 items-center bg-slate-50 p-4 rounded-2xl border">
                <select v-model="bulkActionType" class="p-2 bg-white border rounded-xl text-xs font-bold outline-none">
                  <option value="add">Add Fund (৳)</option>
                  <option value="deduct">Deduct Fund (৳)</option>
                </select>
                <input type="number" step="1" v-model="bulkActionAmount" class="p-2 bg-white border rounded-xl text-xs font-bold w-28" placeholder="Amount (৳)" />
                <button @click="executeBulkBalance" class="bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs px-4 py-2 rounded-xl transition active:scale-95">
                  Execute Adjusted Fund
                </button>
              </div>
            </div>
            
            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h3 class="font-black text-xs text-rose-600 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-coins"></i> Service OTP Payout Config (৳)
              </h3>
              <p class="text-[10px] text-slate-400 font-semibold leading-relaxed">
                প্রতিটি সার্ভিসের রেট এবং একটিভ স্ট্যাটাস কনফিগার করুন। কোনো সার্ভিস অফ থাকলে ওটিপি হিট হলেও ব্যালেন্স যোগ হবে না।
              </p>
              
              <div class="space-y-3.5 font-bold">
                <div v-for="(svcConfig, svcName) in serviceRates" :key="svcName" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-150">
                  <span class="text-xs font-black uppercase text-slate-800 tracking-wide">
                    {{ svcName }}
                  </span>
                  <div class="flex items-center gap-3 w-full sm:w-auto">
                    <div class="flex items-center bg-white border rounded-xl px-2.5 py-1">
                      <span class="text-[10px] font-bold text-slate-400 mr-1.5">৳</span>
                      <input type="number" step="0.01" v-model.number="svcConfig.rate" class="w-16 text-xs font-black text-slate-800 outline-none" placeholder="0.40" />
                    </div>
                    <button @click="svcConfig.status = (svcConfig.status === 'ON' ? 'OFF' : 'ON')" :class="svcConfig.status === 'ON' ? 'bg-emerald-600 text-white border-emerald-700' : 'bg-rose-600 text-white border-rose-700'" class="px-3.5 py-1.5 rounded-xl text-[10px] font-black border transition select-none tracking-wider">
                      {{ svcConfig.status === 'ON' ? 'ACTIVE (ON)' : 'MUTED (OFF)' }}
                    </button>
                  </div>
                </div>
              </div>

              <button @click="saveServiceRates" class="bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold px-5 py-2.5 rounded-xl transition shadow-xs active:scale-95 font-bold">
                Save Service Controls
              </button>
            </div>

            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h3 class="font-black text-xs text-rose-600 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-bullhorn"></i> Global Announcement Control Banner
              </h3>
              <textarea v-model="announcementInput" rows="2" placeholder="Enter notice updates..." class="w-full p-3 bg-slate-50 border rounded-xl text-xs outline-none focus:border-rose-600 font-semibold"></textarea>
              <button @click="updateAnnouncement" class="bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition font-bold">
                Publish Banner Update
              </button>
            </div>

            <div class="bg-white p-6 rounded-3xl border shadow-xs space-y-4">
              <h3 class="font-black text-xs text-rose-600 uppercase tracking-widest flex items-center gap-2">
                <i class="fa-solid fa-database"></i> Database Backup & Security Monitoring
              </h3>
              
              <div class="grid md:grid-cols-2 gap-4 text-xs font-semibold">
                <div class="bg-slate-50 p-4 rounded-xl border flex flex-col justify-between">
                  <div>
                    <p class="font-black text-slate-800">One-Click Database Export (JSON)</p>
                    <p class="text-[10px] text-slate-400 mt-1">Safely back up the entire database structural tree instantly.</p>
                  </div>
                  <button @click="downloadBackup" class="w-max mt-3 bg-rose-600 hover:bg-rose-700 text-white font-bold px-4 py-2 rounded-xl transition font-bold">
                    Download JSON Backup
                  </button>
                </div>

                <div class="bg-slate-50 p-4 rounded-xl border">
                  <p class="font-black text-slate-808">Operational Configurations Active</p>
                  <ul class="text-[10px] text-slate-500 mt-2 list-disc list-inside space-y-1">
                    <li><strong>Rule 11:</strong> Verification check active on database operations.</li>
                    <li><strong>Rule 12:</strong> Default signup state holds as Pending for admin validation.</li>
                    <li><strong>Rule 13:</strong> Realtime fallback routing config dynamically mapped.</li>
                    <li><strong>Rule 14:</strong> Custom OTP custom rates configurable per unique User ID.</li>
                    <li><strong>Rule 15:</strong> Password override structures active on backend user structures.</li>
                    <li><strong>Rule 16:</strong> Automatic database backup generators and sync loops.</li>
                    <li><strong>Rule 17:</strong> Global maintenance status checks enabled on before_request scopes.</li>
                    <li><strong>Rule 18:</strong> Signal Intercept radars mapped to VOLTX streams.</li>
                    <li><strong>Rule 19:</strong> Safe environment private credentials decoded during start cycles.</li>
                    <li><strong>Rule 20:</strong> Dynamic 18-minute allocation countdown timer actively enforced.</li>
                  </ul>
                </div>
              </div>
            </div>

          </div>

        </main>
      </div>

      <!-- Account Edit Details Modal -->
      <div v-if="editUser" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-[99999]">
        <div class="bg-white p-6 rounded-3xl border shadow-2xl max-w-md w-full space-y-4 animate-bounce-in max-h-[85vh] overflow-y-auto">
          <div class="flex justify-between items-center border-b pb-2">
            <h3 class="font-black text-slate-900 text-sm">Edit Account: {{ editUser.name }}</h3>
            <button @click="editUser = null" class="text-slate-400 hover:text-rose-600 transition"><i class="fa-solid fa-xmark text-lg"></i></button>
          </div>

          <div class="space-y-3 text-xs font-bold">
            <div>
              <label class="text-slate-400">Account Type (Role)</label>
              <select v-model="editUser.role" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm outline-none focus:border-rose-600">
                <option value="user">User (সাধারণ অ্যাকাউন্ট)</option>
                <option value="agent">Agent (অফিসিয়াল এজেন্ট)</option>
              </select>
            </div>
            <div v-if="editUser.role === 'agent'">
              <label class="text-slate-400">User Quota Limit</label>
              <input type="number" v-model.number="editUser.agent_limit" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm font-black outline-none focus:border-rose-600" />
            </div>
            <div v-if="editUser.role === 'user'">
              <label class="text-slate-400">Assigned Agent</label>
              <select v-model="editUser.agent_uid" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm outline-none focus:border-rose-600">
                <option v-for="agt in agentsList" :key="agt.uid" :value="agt.uid">{{ agt.name }} ({{ agt.email }})</option>
              </select>
            </div>
            <div>
              <label class="text-slate-400">Manual Balance Edit (৳)</label>
              <input type="number" step="0.01" v-model="editUser.balance" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm font-black outline-none focus:border-rose-600" />
            </div>
            <div>
              <label class="text-slate-400">Base OTP Rate (৳)</label>
              <input type="number" step="0.01" v-model="editUser.otp_rate" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm font-black outline-none focus:border-rose-600" />
            </div>
            <div>
              <label class="text-slate-400">Reset Password</label>
              <input type="password" v-model="editUser.password" placeholder="Leave blank to keep current password" autocomplete="new-password" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm outline-none focus:border-rose-600" />
            </div>
            <div>
              <label class="text-slate-400">Saved Wallet Address</label>
              <input type="text" v-model="editUser.wallet_address" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm outline-none focus:border-rose-600" />
            </div>
            <div>
              <label class="text-slate-400">API Key Override</label>
              <input type="text" v-model="editUser.api_key" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm outline-none font-mono focus:border-rose-600" />
            </div>
            <div>
              <label class="text-slate-400">API Key Approved Status</label>
              <select v-model="editUser.api_key_approved" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm outline-none focus:border-rose-600">
                <option :value="true">Approved (Active Key)</option>
                <option :value="false">Pending Approval (Disabled)</option>
              </select>
            </div>
            <div>
              <label class="text-slate-400">Account Authorization Status</label>
              <select v-model="editUser.status" class="w-full mt-1.5 p-3 bg-slate-50 border rounded-xl text-sm outline-none focus:border-rose-600">
                <option value="approved">Approved (Active)</option>
                <option value="pending">Pending (Awaiting Approval)</option>
                <option value="banned">Banned (Disabled)</option>
              </select>
            </div>
          </div>

          <div class="flex gap-2 pt-2">
            <button @click="editUser = null" class="bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold py-3 rounded-xl text-xs transition flex-1 font-bold">Cancel</button>
            <button @click="saveUserChanges" class="bg-rose-600 hover:bg-rose-700 text-white font-bold py-3 rounded-xl text-xs transition flex-1 font-bold">Save Changes</button>
          </div>
        </div>
      </div>

      <!-- Live User Status Overview Modal -->
      <div v-if="activeUserStatus" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-[99999]">
        <div class="bg-white p-6 rounded-3xl border shadow-2xl max-w-sm w-full space-y-4 animate-bounce-in text-xs font-sans">
          <div class="flex justify-between items-center border-b pb-2">
            <h3 class="font-black text-slate-808 text-sm">Account Live Status Summary</h3>
            <button @click="activeUserStatus = null" class="text-slate-400 hover:text-rose-600"><i class="fa-solid fa-xmark text-lg"></i></button>
          </div>

          <div class="space-y-3 font-semibold text-slate-707">
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">User Name</span>
              <span class="font-bold text-slate-800">{{ activeUserStatus.name }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">ID Code</span>
              <span class="font-mono text-indigo-600 cursor-pointer" @click="copyToClipboard(activeUserStatus.id_code, 'ID Code Copied', 'sum_id')">{{ activeUserStatus.id_code }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Email Address</span>
              <span class="select-all text-slate-800 cursor-pointer hover:text-indigo-600" @click="copyToClipboard(activeUserStatus.email, 'Email Copied', 'sum_email')">{{ activeUserStatus.email }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Joined Date</span>
              <span class="font-mono">{{ activeUserStatus.join_date }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Account Age</span>
              <span class="font-bold text-slate-800">{{ activeUserStatus.account_age }}</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Today's OTP Hits</span>
              <span class="bg-indigo-100 text-indigo-707 px-2.5 py-0.5 rounded-full font-mono">{{ activeUserStatus.today_otp }} OTPs</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Yesterday's OTP Hits</span>
              <span class="bg-slate-100 text-slate-707 px-2.5 py-0.5 rounded-full font-mono">{{ activeUserStatus.yesterday_otp }} OTPs</span>
            </div>
            <div class="flex justify-between border-b pb-1">
              <span class="text-slate-404">Account Balance</span>
              <span class="text-emerald-600 font-bold text-sm font-mono">৳ {{ activeUserStatus.balance }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-404">System Status</span>
              <span class="uppercase font-black text-indigo-600">{{ activeUserStatus.account_status }}</span>
            </div>
          </div>

          <button @click="activeUserStatus = null" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl font-bold">Close Summary</button>
        </div>
      </div>

    </div>
  </div>

  <script>
    const { createApp, ref, onMounted, computed } = Vue;

    createApp({
      setup() {
        const loading = ref(true);
        const authLoading = ref(false);
        const adminToken = ref(localStorage.getItem('mino_admin_token') || '');
        const username = ref('');
        const password = ref('');
        const currentTab = ref('dashboard');
        const searchQuery = ref('');
        const mobileMenuOpen = ref(false);

        const announcementInput = ref('');
        const adminTimeFilter = ref('lifetime');

        const serviceRates = ref({
          facebook: { rate: 0.40, status: 'ON' },
          instagram: { rate: 0.40, status: 'ON' },
          whatsapp: { rate: 0.00, status: 'OFF' },
          telegram: { rate: 0.00, status: 'OFF' },
          google: { rate: 0.40, status: 'ON' },
          generic: { rate: 0.40, status: 'ON' }
        });

        const stats = ref({
          total_users: 0,
          pending_users: 0,
          total_allocations: 0,
          total_otps: 0,
          total_withdrawals: 0,
          maintenance_mode: false,
          auto_approve_account: false,
          announcement: '',
          active_gateway: 'voltx'
        });
        const dashboardError = ref('');

        const gatewayConfig = ref({
          active_gateway: 'voltx',
          voltx_base_url: '',
          voltx_api_key: '',
          yesms_base_url: '',
          yesms_api_key: ''
        });

        const users = ref([]);
        const allocations = ref([]);
        const otpLogs = ref([]);
        const withdrawals = ref([]);
        const withdrawalMethods = ref([]);
        const editUser = ref(null);
        const activeUserStatus = ref(null);

        const newMethodName = ref('');
        const newMethodInstruction = ref('');

        const toast = ref(false);
        const toastMessage = ref('');
        const copiedStates = ref({});

        const globalBaseRateInput = ref(0.40);
        const bulkActionType = ref('add');
        const bulkActionAmount = ref('');

        const quickFundIdCode = ref('');
        const quickFundType = ref('add');
        const quickFundAmount = ref('');

        const testRangeId = ref('880X01');
        const testLoading = ref(false);
        const testResult = ref(null);

        const newAgent = ref({
          name: '',
          email: '',
          password: '',
          limit: 120,
          rate: 0.63
        });

        const triggerToast = (msg) => {
          toastMessage.value = msg;
          toast.value = true;
          setTimeout(() => { toast.value = false; }, 2200);
        };

        const copyToClipboard = (text, title = "Copied to Clipboard", key = null) => {
          if (!text) return;
          navigator.clipboard.writeText(text);
          triggerToast(title + ": " + text);
          if (key) {
            copiedStates.value[key] = true;
            setTimeout(() => { copiedStates.value[key] = false; }, 2000);
          }
        };

        const getUserName = (userId) => {
          if (!userId) return 'System';
          const found = users.value.find(u => (u.uid === userId || u.id === userId));
          return found ? found.name : 'Unknown User';
        };

        const getUserIdCode = (userId) => {
          if (!userId) return 'N/A';
          const found = users.value.find(u => (u.uid === userId || u.id === userId));
          return found ? found.id_code : 'N/A';
        };

        const handleLogin = async () => {
          if (!username.value || !password.value) return;
          authLoading.value = true;
          try {
            const res = await fetch('admin.php?action=login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ username: username.value, password: password.value })
            });
            const data = await res.json();
            if (data.status === 'success') {
              adminToken.value = data.token;
              localStorage.setItem('mino_admin_token', data.token);
              triggerToast("Portal Access Granted! 🔓");
              fetchDashboardData();
            } else {
              alert(data.message || 'Invalid admin credentials entered.');
            }
          } catch (e) {
            alert("Server connection failed.");
          }
          authLoading.value = false;
        };

        const logOut = () => {
          localStorage.removeItem('mino_admin_token');
          adminToken.value = '';
          triggerToast("Logged out securely. 🔒");
        };

        const navigateMobile = (tabName) => {
          currentTab.value = tabName;
          mobileMenuOpen.value = false;
        };

        const fetchDashboardData = async () => {
          if (!adminToken.value) {
            loading.value = false;
            return;
          }
          try {
            const res = await fetch('admin.php?action=dashboard-all&format=json', {
              cache: 'no-store',
              headers: {
                'Authorization': `Bearer ${adminToken.value}`,
                'X-Admin-Token': adminToken.value,
                'Accept': 'application/json'
              }
            });
            if (res.status === 401) { 
              logOut(); 
              loading.value = false;
              return; 
            }
            const responseText = await res.text();
            let data = null;
            try {
              data = JSON.parse(responseText);
            } catch (parseError) {
              throw new Error(`Server returned HTTP ${res.status} instead of JSON.`);
            }
            if (data.status === 'success') {
              const warnings = Array.isArray(data.warnings) ? data.warnings : [];
              dashboardError.value = warnings.length
                ? `Some dashboard data could not be read: ${warnings.join(' | ')}`
                : '';
              stats.value = { ...stats.value, ...(data.stats || {}) };
              users.value = Array.isArray(data.users) ? data.users : Object.values(data.users || {});
              allocations.value = Array.isArray(data.allocations) ? data.allocations : Object.values(data.allocations || {});
              otpLogs.value = Array.isArray(data.otp_logs) ? data.otp_logs : Object.values(data.otp_logs || {});
              withdrawals.value = Array.isArray(data.withdrawals) ? data.withdrawals : Object.values(data.withdrawals || {});
              serviceRates.value = data.rates || serviceRates.value;
              withdrawalMethods.value = Array.isArray(data.withdrawal_methods) ? data.withdrawal_methods : Object.values(data.withdrawal_methods || {});
              announcementInput.value = (data.stats && data.stats.announcement) ? data.stats.announcement : '';
              
              if (data.stats) {
                gatewayConfig.value.active_gateway = data.stats.active_gateway || 'voltx';
                gatewayConfig.value.voltx_api_key = data.stats.voltx_api_key || 'M9JBBKWUL33';
                gatewayConfig.value.voltx_base_url = data.stats.voltx_base_url || 'https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api';
                gatewayConfig.value.yesms_api_key = data.stats.yesms_api_key || '2517fa2553351295';
                gatewayConfig.value.yesms_base_url = data.stats.yesms_base_url || 'https://yesms.online/api';
              }
            } else {
              dashboardError.value = [data.message, data.diagnostic].filter(Boolean).join(' ');
            }
          } catch (e) {
            dashboardError.value = e && e.message
              ? e.message
              : 'Admin data could not be loaded. Please verify the database configuration.';
          }
          loading.value = false;
        };

        const filterByDate = (items, filterType, dateKey = 'createdAt') => {
          const list = items || [];
          const now = new Date();
          const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
          const yesterdayStart = todayStart - 24 * 60 * 60 * 1000;
          const sevenDaysAgo = todayStart - 7 * 24 * 60 * 60 * 1000;
          const fifteenDaysAgo = todayStart - 15 * 24 * 60 * 60 * 1000;
          const thirtyDaysAgo = todayStart - 30 * 24 * 60 * 60 * 1000;

          return list.filter(item => {
            if (!item || !item[dateKey]) return false;
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

        const agentsCount = computed(() => {
          return users.value.filter(u => u && u.role === 'agent').length;
        });

        const agentsList = computed(() => {
          return users.value.filter(u => u && u.role === 'agent');
        });

        const getAgentName = (agentUid) => {
          if (!agentUid) return 'No Agent';
          const found = users.value.find(u => u.uid === agentUid);
          return found ? found.name : 'Unknown Agent';
        };

        const getAgentUserCount = (agentUid) => {
          return users.value.filter(u => u.agent_uid === agentUid && u.role === 'user').length;
        };

        const createAgent = async () => {
          if (!newAgent.value.name || !newAgent.value.email || !newAgent.value.password) {
            alert("Please fill in all agent registration fields.");
            return;
          }
          try {
            const res = await fetch('admin.php?action=agents-create', {
              method: 'POST',
              headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify({
                name: newAgent.value.name,
                email: newAgent.value.email,
                password: newAgent.value.password,
                agent_limit: newAgent.value.limit,
                otp_rate: newAgent.value.rate
              })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast(data.message);
              newAgent.value = { name: '', email: '', password: '', limit: 120, rate: 0.63 };
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch(e) {
            alert("Agent registration process failed.");
          }
        };

        const apiUsersCount = computed(() => {
          const list = users.value || [];
          return list.filter(u => u && (u.api_key_approved === true || u.api_key)).length;
        });

        const pendingWithdrawalsCount = computed(() => {
          const list = withdrawals.value || [];
          return list.filter(w => w && w.status === 'pending').length;
        });

        const filteredAllocationsForAdmin = computed(() => {
          return filterByDate(allocations.value || [], adminTimeFilter.value, 'createdAt');
        });

        const adminPeriodStats = computed(() => {
          const list = filteredAllocationsForAdmin.value || [];
          const total = list.length;
          const success = list.filter(a => a && a.status === 'completed').length;
          const failed = list.filter(a => a && a.status === 'expired').length;
          const successRate = total > 0 ? ((success / total) * 100).toFixed(1) : '0.0';
          const failRate = total > 0 ? ((failed / total) * 100).toFixed(1) : '0.0';
          return { total, success, failed, successRate, failRate };
        });

        const topNumberUsers = computed(() => {
          const list = allocations.value || [];
          const counts = {};
          list.forEach(a => {
            if (a && a.userId) {
              counts[a.userId] = (counts[a.userId] || 0) + 1;
            }
          });
          
          const uList = users.value || [];
          const userMap = new Map();
          uList.forEach(u => {
            if (u) {
              const uIdentifier = u.uid || u.id;
              if (uIdentifier) userMap.set(uIdentifier, u);
            }
          });

          const result = Object.keys(counts).map(uid => {
            const uObj = userMap.get(uid);
            return {
              name: uObj ? uObj.name : 'Unknown User',
              id_code: uObj ? uObj.id_code : 'N/A',
              count: counts[uid]
            };
          });
          result.sort((a, b) => b.count - a.count);
          return result.slice(0, 100);
        });

        const topOtpUsers = computed(() => {
          const list = otpLogs.value || [];
          const counts = {};
          list.forEach(log => {
            if (log && log.userId) {
              counts[log.userId] = (counts[log.userId] || 0) + 1;
            }
          });
          
          const uList = users.value || [];
          const userMap = new Map();
          uList.forEach(u => {
            if (u) {
              const uIdentifier = u.uid || u.id;
              if (uIdentifier) userMap.set(uIdentifier, u);
            }
          });

          const result = Object.keys(counts).map(uid => {
            const uObj = userMap.get(uid);
            return {
              name: uObj ? uObj.name : 'Unknown User',
              id_code: uObj ? uObj.id_code : 'N/A',
              count: counts[uid]
            };
          });
          result.sort((a, b) => b.count - a.count);
          return result.slice(0, 100);
        });

        const inactiveUsersList = computed(() => {
          const uList = users.value || [];
          const allocList = allocations.value || [];
          
          const activeUserIds = new Set();
          allocList.forEach(a => {
            if (a && a.userId) {
              activeUserIds.add(a.userId);
            }
          });

          return uList.filter(u => {
            if (!u || u.role !== 'user') return false;
            const uIdentifier = u.uid || u.id;
            return !activeUserIds.has(uIdentifier);
          });
        });

        const topServicesList = computed(() => {
          const list = otpLogs.value || [];
          const counts = {};
          list.forEach(log => {
            if (log) {
              const svc = log.service || 'generic';
              counts[svc] = (counts[svc] || 0) + 1;
            }
          });
          const result = Object.keys(counts).map(svc => {
            return {
              name: svc,
              count: counts[svc]
            };
          });
          result.sort((a, b) => b.count - a.count);
          return result;
        });

        const auditLogs = computed(() => {
          const list = otpLogs.value || [];
          return list.filter(l => l.type === 'admin_action');
        });

        const restrictedUsers = computed(() => {
          const list = users.value || [];
          return list.filter(u => u && (u.status === 'pending' || u.status === 'banned'));
        });

        const toggleMaintenanceMode = async () => {
          const currentMode = stats.value.maintenance_mode;
          try {
            const res = await fetch('admin.php?action=toggle-maintenance', {
              method: 'POST',
              headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify({ maintenance_mode: !currentMode })
            });
            const data = await res.json();
            if (data.status === 'success') {
              stats.value.maintenance_mode = data.maintenance_mode;
              triggerToast(`Maintenance mode turned ${data.maintenance_mode ? 'ON' : 'OFF'}. 🛠️`);
            }
          } catch (e) {}
        };

        const updateAnnouncement = async () => {
          try {
            const res = await fetch('admin.php?action=announcement', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify({ announcement: announcementInput.value })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast("Global notice updated! 📢");
            }
          } catch (e) {}
        };

        const saveServiceRates = async () => {
          try {
            const res = await fetch('admin.php?action=service-rates', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify({ rates: serviceRates.value })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast("Service payout rates successfully updated! 💰");
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch (e) {}
        };

        const processWithdrawal = async (id, action) => {
          if (!confirm("Are you sure you want to change this withdrawal request status to " + action + "?")) return;
          try {
            const res = await fetch('admin.php?action=withdrawals-action', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify({ id, action })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast("Withdrawal request has been marked as " + action);
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch (e) {}
        };

        const downloadBackup = async () => {
          try {
            const res = await fetch('admin.php?action=backup', {
              headers: { 'Authorization': `Bearer ${adminToken.value}` }
            });
            const data = await res.json();
            if (data.status === 'success') {
              const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data.data, null, 2));
              const downloadAnchor = document.createElement('a');
              downloadAnchor.setAttribute("href", dataStr);
              downloadAnchor.setAttribute("download", "mino_backup_" + new Date().toISOString().slice(0,10) + ".json");
              document.body.appendChild(downloadAnchor);
              downloadAnchor.click();
              downloadAnchor.remove();
              triggerToast("Database JSON export download initiated! 📥");
            }
          } catch (e) {}
        };

        const exportUsersToCSV = () => {
          let csvContent = "data:text/csv;charset=utf-8,";
          csvContent += "Name,Email,Balance,Status,Role,OTP Rate\n";
          
          users.value.forEach(u => {
            if (u) {
              csvContent += '"' + u.name + '","' + u.email + '",' + u.balance + ',"' + u.status + '","' + u.role + '",' + u.otp_rate + '\n';
            }
          });

          const encodedUri = encodeURI(csvContent);
          const link = document.createElement("a");
          link.setAttribute("href", encodedUri);
          link.setAttribute("download", "mino_users_export_" + new Date().toISOString().slice(0,10) + ".csv");
          document.body.appendChild(link);
          link.click();
          link.remove();
          triggerToast("User database exported to CSV! 📊");
        };

        const filteredUsersList = computed(() => {
          const list = users.value || [];
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

        const openEditModal = (u) => {
          editUser.value = { ...u };
        };

        const saveUserChanges = async () => {
          if (!editUser.value) return;
          try {
            const res = await fetch('admin.php?action=users-update', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify(editUser.value)
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast("Account details successfully updated! ✅");
              editUser.value = null;
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch (e) {}
        };

        const deleteUser = async (uid) => {
          if (!confirm("Are you sure you want to permanently delete this account?")) return;
          try {
            const res = await fetch('admin.php?action=users-delete', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify({ uid })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast("Account permanently removed. 🗑️");
              fetchDashboardData();
            }
          } catch (e) {}
        };

        const formatTimestamp = (isoString) => {
          if (!isoString) return '';
          try {
            const d = new Date(isoString);
            return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          } catch (e) {
            return '';
          }
        };

        const executeBulkBalance = async () => {
          if (!bulkActionAmount.value || bulkActionAmount.value <= 0) return alert("Valid amount is required.");
          if (!confirm(`Are you sure you want to ${bulkActionType.value} ৳${bulkActionAmount.value} to all approved accounts?`)) return;
          try {
            const res = await fetch('admin.php?action=bulk-balance-adjust', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ amount: bulkActionAmount.value, type: bulkActionType.value })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast(data.message);
              bulkActionAmount.value = '';
              fetchDashboardData();
            } else { alert(data.message); }
          } catch(e) {}
        };

        const toggleAutoApproveAccount = async () => {
          const currentMode = stats.value.auto_approve_account;
          try {
            const res = await fetch('admin.php?action=toggle-auto-approve-account', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ auto_approve_account: !currentMode })
            });
            const data = await res.json();
            if (data.status === 'success') {
              stats.value.auto_approve_account = data.auto_approve_account;
              triggerToast(`Auto Account Approval is now ${data.auto_approve_account ? 'ON' : 'OFF'}`);
            }
          } catch(e) {}
        };

        const saveGlobalBaseRate = async () => {
          if (globalBaseRateInput.value <= 0) return alert("Enter a valid rate.");
          try {
            const res = await fetch('admin.php?action=update-global-base-rate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ rate: globalBaseRateInput.value })
            });
            const data = await res.json();
            if (data.status === 'success') { 
              triggerToast(data.message);
              fetchDashboardData();
            }
          } catch(e) {}
        };

        const refundAllocation = async (id) => {
          if (!confirm("Are you sure you want to cancel this order and refund the user?")) return;
          try {
            const res = await fetch('admin.php?action=refund-allocation', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ id })
            });
            const data = await res.json();
            if (data.status === 'success') { 
              triggerToast(data.message);
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch(e) {}
        };

        const saveGatewaySettings = async () => {
          try {
            const res = await fetch('admin.php?action=update-gateway-config', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken.value}`
              },
              body: JSON.stringify({
                active_gateway: gatewayConfig.value.active_gateway,
                voltx_api_key: gatewayConfig.value.voltx_api_key,
                voltx_base_url: gatewayConfig.value.voltx_base_url,
                yesms_api_key: gatewayConfig.value.yesms_api_key,
                yesms_base_url: gatewayConfig.value.yesms_base_url
              })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast("Gateway configurations updated successfully! 📡");
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch (e) {
            alert("Failed to save gateway configurations.");
          }
        };

        const executeQuickFund = async () => {
          if (!quickFundIdCode.value.trim() || quickFundAmount.value <= 0) {
            return alert("Valid ID Code and positive fund amount required.");
          }
          try {
            const res = await fetch('admin.php?action=quick-fund-inject', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({
                id_code: quickFundIdCode.value,
                amount: quickFundAmount.value,
                type: quickFundType.value
              })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast(data.message);
              quickFundIdCode.value = '';
              quickFundAmount.value = '';
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch(e) {
            alert("Fund injection procedure failed.");
          }
        };

        const executeStaleSweep = async () => {
          if (!confirm("Are you sure you want to wipe clean and expire all active orders older than 18 minutes?")) return;
          try {
            const res = await fetch('admin.php?action=clean-expired-allocations', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` }
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast(data.message);
              fetchDashboardData();
            }
          } catch(e) {
            alert("Stale sweep failed.");
          }
        };

        const testVoltxRange = async () => {
          if (!testRangeId.value.trim()) return alert("Valid Range ID required.");
          testLoading.value = true;
          testResult.value = null;
          try {
            const res = await fetch('admin.php?action=test-voltx-range', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ rid: testRangeId.value })
            });
            const data = await res.json();
            if (data.status === 'success') {
              testResult.value = data;
              triggerToast("Gateway response received!");
            }
          } catch(e) {
            alert("Gateway range check failed.");
          }
          testLoading.value = false;
        };

        const updateUserStatusDirect = async (uid, newStatus) => {
          if (!confirm(`Are you sure you want to change account status to: ${newStatus}?`)) return;
          try {
            const res = await fetch('admin.php?action=users-update', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ uid: uid, status: newStatus })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast("User authorization updated!");
              fetchDashboardData();
            } else {
              alert(data.message);
            }
          } catch(e) {
            alert("Status update failed.");
          }
        };

        const createWithdrawalMethod = async () => {
          if (!newMethodName.value.trim()) return;
          try {
            const res = await fetch('admin.php?action=add-withdrawal-method', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ method_name: newMethodName.value, instructions: newMethodInstruction.value })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast(data.message);
              newMethodName.value = '';
              newMethodInstruction.value = '';
              fetchDashboardData();
            }
          } catch(e) {}
        };

        const deleteWithdrawalMethod = async (id) => {
          if (!confirm("Are you sure you want to delete this payment method?")) return;
          try {
            const res = await fetch('admin.php?action=delete-withdrawal-method', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${adminToken.value}` },
              body: JSON.stringify({ id: id })
            });
            const data = await res.json();
            if (data.status === 'success') {
              triggerToast(data.message);
              fetchDashboardData();
            }
          } catch(e) {}
        };

        const viewUserStatus = async (uid) => {
          try {
            const res = await fetch('admin.php?action=user-status&uid=' + uid, {
              headers: { 'Authorization': `Bearer ${adminToken.value}` }
            });
            const data = await res.json();
            if (data.status === 'success') {
              activeUserStatus.value = data.data;
            } else {
              alert(data.message);
            }
          } catch(e) {}
        };

        onMounted(() => {
          fetchDashboardData();
          setInterval(fetchDashboardData, 10000); 
        });

        return {
          loading, authLoading, adminToken, username, password, currentTab, searchQuery, mobileMenuOpen,
          stats, users, allocations, otpLogs, withdrawals, editUser, activeUserStatus, toast, toastMessage, announcementInput, adminTimeFilter, dashboardError,
          serviceRates, saveServiceRates, navigateMobile, apiUsersCount, pendingWithdrawalsCount,
          adminPeriodStats, topNumberUsers, topOtpUsers, inactiveUsersList, topServicesList,
          handleLogin, logOut, toggleMaintenanceMode, updateAnnouncement, processWithdrawal, downloadBackup, exportUsersToCSV,
          filteredUsersList, openEditModal, saveUserChanges, deleteUser, formatTimestamp,
          getUserName, getUserIdCode,
          globalBaseRateInput, bulkActionType, bulkActionAmount,
          executeBulkBalance, toggleAutoApproveAccount, saveGlobalBaseRate, refundAllocation,
          gatewayConfig, saveGatewaySettings,
          quickFundIdCode, quickFundType, quickFundAmount, executeQuickFund,
          testRangeId, testLoading, testResult, testVoltxRange,
          executeStaleSweep, restrictedUsers, auditLogs, updateUserStatusDirect,
          agentsCount, agentsList, getAgentName, getAgentUserCount, newAgent, createAgent,
          withdrawalMethods, newMethodName, newMethodInstruction, createWithdrawalMethod, deleteWithdrawalMethod,
          viewUserStatus, copiedStates, copyToClipboard
        };
      }
    }).mount('#admin-app');
  </script>
</body>
</html>