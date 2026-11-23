<?php
// Fallback/Polyfill for getallheaders() on Litespeed/Nginx/Apache servers
if (!function_exists('getallheaders')) {
    function getallheaders() {
        $headers = [];
        foreach ($_SERVER as $name => $value) {
            if (substr($name, 0, 5) == 'HTTP_') {
                $header_name = str_replace(' ', '-', ucwords(strtolower(str_replace('_', ' ', substr($name, 5)))));
                $headers[$header_name] = $value;
            }
        }
        return $headers;
    }
}

// =========================================================================
// Configuration & Security Rules Helpers (MySQL Connected Version)
// =========================================================================
$mino_config = [];
$mino_config_file = __DIR__ . '/config.php';
if (is_file($mino_config_file)) {
    $loaded_config = require $mino_config_file;
    if (is_array($loaded_config)) {
        $mino_config = $loaded_config;
    }
}

$mino_config_value = static function (string $key, $default = '') use ($mino_config) {
    $env_key = strtoupper($key);
    $env_value = getenv($env_key);
    if ($env_value !== false && $env_value !== '') {
        return $env_value;
    }
    return array_key_exists($key, $mino_config) ? $mino_config[$key] : $default;
};

define('ADMIN_USER', (string)$mino_config_value('admin_user', 'Mino420@'));
define('ADMIN_PASS', (string)$mino_config_value('admin_pass', 'Mino420@admin'));
define('ADMIN_STATIC_TOKEN', 'admin_tkn_' . ADMIN_PASS);

define('DB_HOST', (string)$mino_config_value('db_host', 'localhost'));
define('DB_NAME', (string)$mino_config_value('db_name', 'murad'));
define('DB_USER', (string)$mino_config_value('db_user', 'murad'));
define('DB_PASS', (string)$mino_config_value('db_pass', 'murad'));

$COUNTRY_PREFIXES = [
    "1242" => "Bahamas", "1246" => "Barbados", "1264" => "Anguilla", "1268" => "Antigua and Barbuda",
    "1" => "USA/Canada", "20" => "Egypt", "212" => "Morocco", "213" => "Algeria",
    "216" => "Tunisia", "218" => "Libya", "220" => "Gambia", "221" => "Senegal",
    "222" => "Mauritania", "223" => "Mali", "224" => "Guinea", "225" => "Ivory Coast",
    "226" => "Burkina Faso", "227" => "Niger", "228" => "Togo", "229" => "Benin",
    "230" => "Mauritius", "231" => "Liberia", "232" => "Sierra Leone", "233" => "Ghana",
    "234" => "Nigeria", "235" => "Chad", "237" => "Cameroon", "241" => "Gabon",
    "242" => "Congo", "243" => "DR Congo", "244" => "Angola", "245" => "Guinea-Bissau",
    "249" => "Sudan", "250" => "Rwanda", "251" => "Ethiopia", "252" => "Somalia",
    "254" => "Kenya", "255" => "Tanzania", "256" => "Uganda", "257" => "Burundi",
    "258" => "Mozambique", "260" => "Zambia", "261" => "Madagascar", "263" => "Zimbabwe",
    "30" => "Greece", "31" => "Netherlands", "32" => "Belgium", "33" => "France",
    "34" => "Spain", "351" => "Portugal", "358" => "Finland", "370" => "Lithuania",
    "371" => "Latvia", "372" => "Estonia", "374" => "Armenia", "375" => "Belarus",
    "380" => "Ukraine", "40" => "Romania", "41" => "Switzerland", "43" => "Austria",
    "44" => "United Kingdom", "45" => "Denmark", "46" => "Sweden", "47" => "Norway",
    "48" => "Poland", "49" => "Germany", "51" => "Peru", "52" => "Mexico",
    "54" => "Argentina", "55" => "Brazil", "56" => "Chile", "57" => "Colombia",
    "60" => "Malaysia", "61" => "Australia", "62" => "Indonesia", "63" => "Philippines",
    "65" => "Singapore", "66" => "Thailand", "81" => "Japan", "82" => "South Korea",
    "84" => "Vietnam", "880" => "Bangladesh", "90" => "Turkey", "91" => "India",
    "92" => "Pakistan", "93" => "Afghanistan", "94" => "Sri Lanka", "95" => "Myanmar",
    "961" => "Lebanon", "962" => "Jordan", "963" => "Syria", "964" => "Iraq",
    "965" => "Kuwait", "966" => "Saudi Arabia", "971" => "UAE", "972" => "Israel",
    "974" => "Qatar", "977" => "Nepal", "992" => "Tajikistan", "993" => "Turkmenistan",
    "994" => "Azerbaijan", "995" => "Georgia", "996" => "Kyrgyzstan", "998" => "Uzbekistan"
];

function get_country_from_range($range) {
    global $COUNTRY_PREFIXES;
    $clean = preg_replace('/[^0-9]/', '', $range);
    for ($len = 4; $len >= 1; $len--) {
        $prefix = substr($clean, 0, $len);
        if (isset($COUNTRY_PREFIXES[$prefix])) {
            return $COUNTRY_PREFIXES[$prefix];
        }
    }
    return 'Unknown';
}

$raw_input = file_get_contents('php://input');
if (!empty($raw_input)) {
    $json_data = json_decode($raw_input, true);
    if (is_array($json_data)) {
        $_POST = array_merge($_POST, $json_data);
        foreach ($json_data as $key => $val) {
            if (!isset($_GET[$key])) {
                $_GET[$key] = $val;
            }
            if (!isset($_REQUEST[$key])) {
                $_REQUEST[$key] = $val;
            }
        }
    }
}

function get_scaled_service_rate($service, $user_otp_rate, $service_rates) {
    $service = strtolower($service);
    $svc_config = isset($service_rates[$service]) ? $service_rates[$service] : null;
    $svc_status = 'ON';
    $svc_rate = 0.40;

    if (is_array($svc_config)) {
        $svc_status = strtoupper(isset($svc_config['status']) ? $svc_config['status'] : 'ON');
        $svc_rate = (float)(isset($svc_config['rate']) ? $svc_config['rate'] : 0.40);
    } elseif ($svc_config !== null) {
        $svc_rate = (float)$svc_config;
    }

    if ($service === 'whatsapp' || $service === 'telegram' || $svc_status === 'OFF') {
        return 0.00;
    }

    $baseline = 0.40;
    $multiplier = $user_otp_rate / $baseline;
    return round($svc_rate * $multiplier, 2);
}

function hash_user_password($password) {
    $password = (string)$password;
    if ($password === '') {
        return '';
    }

    $password_info = password_get_info($password);
    if (!empty($password_info['algo'])) {
        return $password;
    }

    return password_hash($password, PASSWORD_DEFAULT);
}

function verify_user_password($password, $stored_password) {
    return is_string($stored_password)
        && $stored_password !== ''
        && password_verify((string)$password, $stored_password);
}

function public_user_data($user) {
    if (!is_array($user)) {
        return $user;
    }

    unset($user['password']);
    return $user;
}

function migrate_plaintext_user_passwords($pdo) {
    $stmt = $pdo->query("SELECT uid, password FROM users WHERE password IS NOT NULL AND password <> ''");
    $rows = $stmt->fetchAll();
    $update = $pdo->prepare("UPDATE users SET password = ? WHERE uid = ?");

    foreach ($rows as $row) {
        $stored_password = (string)($row['password'] ?? '');
        if ($stored_password === '') {
            continue;
        }

        $password_info = password_get_info($stored_password);
        if (empty($password_info['algo'])) {
            $update->execute([password_hash($stored_password, PASSWORD_DEFAULT), $row['uid']]);
        }
    }
}

function database_schema_is_ready($pdo) {
    $stmt = $pdo->query("
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name IN (
            'users',
            'allocated_numbers',
            'otp_logs',
            'withdrawals',
            'settings',
            'live_console',
            'withdrawal_methods'
          )
    ");

    return (int)$stmt->fetchColumn() === 7;
}

function get_db_connection() {
    static $pdo = null;
    if ($pdo === null) {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4";
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
            PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
        ];
        try {
            $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
            
            $lock_suffix = substr(hash('sha256', DB_HOST . '|' . DB_NAME . '|' . DB_USER), 0, 16);
            $lock_file = sys_get_temp_dir() . '/mino_db_schema_ready_' . $lock_suffix . '.lock';
            if (!file_exists($lock_file) || !database_schema_is_ready($pdo)) {
                $pdo->exec("CREATE TABLE IF NOT EXISTS users (
                    uid VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    email VARCHAR(255) UNIQUE,
                    password VARCHAR(255),
                    api_key VARCHAR(255),
                    api_key_approved TINYINT DEFAULT 0,
                    balance DECIMAL(10,2) DEFAULT 0.00,
                    otp_rate DECIMAL(10,2) DEFAULT 0.40,
                    wallet_address VARCHAR(255) DEFAULT '',
                    id_code VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'approved',
                    createdAt VARCHAR(100),
                    role VARCHAR(50) DEFAULT 'user',
                    agent_uid VARCHAR(255) DEFAULT NULL,
                    agent_limit INT DEFAULT 120,
                    withdraw_pin VARCHAR(10) DEFAULT NULL,
                    agent_auto_approve TINYINT DEFAULT 1,
                    agent_auto_rate DECIMAL(10,2) DEFAULT 0.40,
                    telegram_username VARCHAR(255) DEFAULT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

                $pdo->exec("CREATE TABLE IF NOT EXISTS allocated_numbers (
                    id VARCHAR(255) PRIMARY KEY,
                    userId VARCHAR(255),
                    number VARCHAR(100),
                    rid VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'active',
                    country VARCHAR(100),
                    operator VARCHAR(100),
                    createdAt VARCHAR(100),
                    otp VARCHAR(255) DEFAULT '',
                    message TEXT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

                $pdo->exec("CREATE TABLE IF NOT EXISTS otp_logs (
                    id VARCHAR(255) PRIMARY KEY,
                    userId VARCHAR(255),
                    number VARCHAR(100),
                    service VARCHAR(100),
                    otpCode VARCHAR(100),
                    message TEXT,
                    revenue DECIMAL(10,2) DEFAULT 0.00,
                    createdAt VARCHAR(100)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

                $pdo->exec("CREATE TABLE IF NOT EXISTS withdrawals (
                    id VARCHAR(255) PRIMARY KEY,
                    userId VARCHAR(255),
                    userEmail VARCHAR(255),
                    userName VARCHAR(255),
                    amount DECIMAL(10,2) DEFAULT 0.00,
                    method VARCHAR(100),
                    address VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'pending',
                    createdAt VARCHAR(100)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

                $pdo->exec("CREATE TABLE IF NOT EXISTS settings (
                    setting_key VARCHAR(255) PRIMARY KEY,
                    setting_value TEXT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

                $pdo->exec("CREATE TABLE IF NOT EXISTS live_console (
                    id VARCHAR(255) PRIMARY KEY,
                    type VARCHAR(100),
                    message TEXT,
                    service VARCHAR(100),
                    createdAt VARCHAR(100)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

                $pdo->exec("CREATE TABLE IF NOT EXISTS withdrawal_methods (
                    id VARCHAR(55) PRIMARY KEY,
                    method_name VARCHAR(255) NOT NULL,
                    instructions VARCHAR(255) DEFAULT ''
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci");

                $stmtM = $pdo->query("SELECT COUNT(*) FROM withdrawal_methods");
                if ($stmtM->fetchColumn() == 0) {
                    $default_methods = [
                        ['m_1', 'Bkash', 'Bkash Personal Number দিন'],
                        ['m_2', 'Nagad', 'Nagad Personal Number দিন'],
                        ['m_3', 'Rocket', 'Rocket Personal Number দিন'],
                        ['m_4', 'USDT (TRC20)', 'USDT TRC20 Wallet Address দিন'],
                        ['m_5', 'Binance Pay ID', 'Binance Pay ID দিন']
                    ];
                    $stmtIns = $pdo->prepare("INSERT INTO withdrawal_methods (id, method_name, instructions) VALUES (?, ?, ?)");
                    foreach ($default_methods as $dm) {
                        $stmtIns->execute($dm);
                    }
                }

                file_put_contents($lock_file, date('Y-m-d H:i:s'));
            }

            migrate_plaintext_user_passwords($pdo);

        } catch (\PDOException $e) {
            http_response_code(500);
            echo json_encode(['status' => 'error', 'message' => 'Database connection failed: ' . $e->getMessage()]);
            exit();
        }
    }
    return $pdo;
}

function get_active_gateway_config() {
    try {
        $pdo = get_db_connection();
        $stmt = $pdo->query("SELECT * FROM settings");
        $settings_rows = $stmt->fetchAll();
        $db_settings = [];
        foreach ($settings_rows as $row) {
            $db_settings[$row['setting_key']] = json_decode($row['setting_value'], true);
        }
        return [
            'active_gateway' => isset($db_settings['active_gateway']) ? $db_settings['active_gateway'] : "voltx",
            'voltx_api_key' => isset($db_settings['voltx_api_key']) ? $db_settings['voltx_api_key'] : "M9JBBKWUL33",
            'voltx_base_url' => isset($db_settings['voltx_base_url']) ? $db_settings['voltx_base_url'] : "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api",
            'yesms_api_key' => isset($db_settings['yesms_api_key']) ? $db_settings['yesms_api_key'] : "2517fa2553351295",
            'yesms_base_url' => isset($db_settings['yesms_base_url']) ? $db_settings['yesms_base_url'] : "https://yesms.online/api"
        ];
    } catch (Exception $e) {
        return [
            'active_gateway' => 'voltx',
            'voltx_api_key' => 'M9JBBKWUL33',
            'voltx_base_url' => 'https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api',
            'yesms_api_key' => '2517fa2553351295',
            'yesms_base_url' => 'https://yesms.online/api'
        ];
    }
}

function get_gateway_expiry_seconds() {
    $cfg = get_active_gateway_config();
    return ($cfg['active_gateway'] === 'yesms') ? 1680 : 1190;
}

function credit_agent_commission($pdo, $user_id, $earned_revenue) {
    try {
        $stmtUser = $pdo->prepare("SELECT agent_uid FROM users WHERE uid = ? LIMIT 1");
        $stmtUser->execute([$user_id]);
        $agent_uid = $stmtUser->fetchColumn();
        
        if (!empty($agent_uid)) {
            $stmtAgent = $pdo->prepare("SELECT uid, otp_rate FROM users WHERE uid = ? AND role = 'agent' LIMIT 1");
            $stmtAgent->execute([$agent_uid]);
            $agent = $stmtAgent->fetch();
            if ($agent) {
                $agent_max_rate = isset($agent['otp_rate']) ? (float)$agent['otp_rate'] : 0.63;
                $commission = max(0.00, $agent_max_rate - (float)$earned_revenue);
                if ($commission > 0) {
                    $stmtComm = $pdo->prepare("UPDATE users SET balance = balance + ? WHERE uid = ?");
                    $stmtComm->execute([$commission, $agent['uid']]);
                }
            }
        }
    } catch (Exception $e) {}
}

function sync_user_active_otps($user_id, $otp_rate = 0.40) {
    $pdo = get_db_connection();
    
    $stmtAll = $pdo->prepare("SELECT * FROM allocated_numbers WHERE userId = ? AND status = 'active'");
    $stmtAll->execute([$user_id]);
    $active_allocs = $stmtAll->fetchAll();

    if (!empty($active_allocs)) {
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
                    
                    foreach ($active_allocs as &$alloc) {
                        if ($alloc['status'] !== 'active') continue;
                        
                        $alloc_num = str_replace(['+', ' '], '', isset($alloc['number']) ? $alloc['number'] : '');
                        if (!empty($otp_num) && !empty($alloc_num) && (strpos($alloc_num, $otp_num) !== false || strpos($otp_num, $alloc_num) !== false)) {
                            
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

                            $stmt_up = $pdo->prepare("UPDATE allocated_numbers SET status = 'completed', otp = ?, message = ? WHERE id = ? AND status = 'active'");
                            $stmt_up->execute([$otp_code, $message, $alloc['id']]);

                            if ($stmt_up->rowCount() > 0) {
                                $alloc['status'] = 'completed';

                                $stmt_bal = $pdo->prepare("UPDATE users SET balance = balance + ? WHERE uid = ?");
                                $stmt_bal->execute([$earned_revenue, $user_id]);

                                credit_agent_commission($pdo, $user_id, $earned_revenue);
                                
                                $otp_id = "otp_" . bin2hex(random_bytes(8));
                                $created_at = (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM);
                                
                                $stmt_log = $pdo->prepare("INSERT INTO otp_logs (id, userId, number, service, otpCode, message, revenue, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
                                $stmt_log->execute([$otp_id, $user_id, $alloc['number'], $service, $otp_code, $message, $earned_revenue, $created_at]);
                            }
                        }
                    }
                }
            }
        } catch (Exception $e) {}
    }

    $now = new DateTime('now', new DateTimeZone('UTC'));
    foreach ($active_allocs as $alloc) {
        if ($alloc['status'] === 'active') {
            $created_at_str = isset($alloc['createdAt']) ? $alloc['createdAt'] : '';
            if (!empty($created_at_str)) {
                $created_at = parse_iso_datetime($created_at_str);
                $elapsed_seconds = $now->getTimestamp() - $created_at->getTimestamp();
                $expiry_limit = get_gateway_expiry_seconds();
                if ($elapsed_seconds > $expiry_limit) { 
                    $stmt_exp = $pdo->prepare("UPDATE allocated_numbers SET status = 'expired' WHERE id = ?");
                    $stmt_exp->execute([$alloc['id']]);
                }
            }
        }
    }
}

function gateway_allocate_number($rid) {
    $cfg = get_active_gateway_config();
    $max_attempts = 2;
    $last_error = "No number available on range {$rid}";

    for ($attempt = 1; $attempt <= $max_attempts; $attempt++) {
        $ch = curl_init();

        if ($cfg['active_gateway'] === 'yesms') {
            $url = rtrim($cfg['yesms_base_url'], '/') . '/allocate_number';
            $headers = [
                'authkey: ' . $cfg['yesms_api_key'],
                'Content-Type: application/json'
            ];
            $payload = ['range_id' => $rid];
        } else {
            $url = rtrim($cfg['voltx_base_url'], '/') . '/getnum';
            $headers = [
                'mauthapi: ' . $cfg['voltx_api_key'],
                'Content-Type: application/json'
            ];
            $payload = ['rid' => $rid];
        }

        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);

        $res_raw = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curl_err = curl_error($ch);
        curl_close($ch);

        if ($http_code === 200 && !empty($res_raw)) {
            $json_res = json_decode($res_raw, true);
            if (is_array($json_res)) {
                $d_payload = isset($json_res['data']) ? $json_res['data'] : $json_res;
                $full_num = '';
                if (is_array($d_payload)) {
                    if (!empty($d_payload['full_number'])) $full_num = trim($d_payload['full_number']);
                    elseif (!empty($d_payload['number'])) $full_num = trim($d_payload['number']);
                    elseif (!empty($d_payload['national_number'])) $full_num = trim($d_payload['national_number']);
                    elseif (!empty($d_payload['no_plus_number'])) $full_num = trim($d_payload['no_plus_number']);
                }
                if (empty($full_num) && !empty($json_res['number'])) {
                    $full_num = trim($json_res['number']);
                }

                if (!empty($full_num)) {
                    $country = !empty($d_payload['country']) ? $d_payload['country'] : get_country_from_range($rid);
                    $operator = !empty($d_payload['operator']) ? $d_payload['operator'] : 'Mobile';
                    return [
                        'success' => true,
                        'data' => [
                            'meta' => ['status' => 'ok', 'code' => 200],
                            'data' => [
                                'full_number' => $full_num,
                                'national_number' => !empty($d_payload['national_number']) ? $d_payload['national_number'] : $full_num,
                                'no_plus_number' => ltrim($full_num, '+'),
                                'country' => $country,
                                'operator' => $operator
                            ]
                        ]
                    ];
                }

                if (!empty($json_res['message'])) {
                    $last_error = $json_res['message'];
                } elseif (!empty($json_res['msg'])) {
                    $last_error = $json_res['msg'];
                } elseif (!empty($json_res['error'])) {
                    $last_error = $json_res['error'];
                }
            }
        } else {
            if (!empty($curl_err)) {
                $last_error = "Gateway Timeout/Error: " . $curl_err;
            } elseif ($http_code > 0) {
                $last_error = "Gateway returned HTTP " . $http_code;
            }
        }

        if ($attempt < $max_attempts) {
            usleep(250000);
        }
    }

    return [
        'success' => false,
        'data' => null,
        'error' => $last_error
    ];
}

function gateway_liveaccess() {
    $cfg = get_active_gateway_config();

    if ($cfg['active_gateway'] === 'yesms') {
        $url = rtrim($cfg['yesms_base_url'], '/') . '/live_access_data';
        $headers = ['authkey: ' . $cfg['yesms_api_key']];
    } else {
        $url = rtrim($cfg['voltx_base_url'], '/') . '/liveaccess';
        $headers = ['mauthapi: ' . $cfg['voltx_api_key']];
    }

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_TIMEOUT, 8);
    curl_setopt($ch, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);
    curl_setopt($ch, CURLOPT_TCP_NODELAY, 1);
    $res_raw = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    return ['code' => $http_code, 'data' => $res_raw];
}

function get_voltx_success_otp_cached() {
    $cfg = get_active_gateway_config();
    $cache_file = sys_get_temp_dir() . '/otp_retrieval_success_cache.json';
    
    if (file_exists($cache_file) && (time() - filemtime($cache_file)) < 1.0) {
        $data = json_decode(file_get_contents($cache_file), true);
        if (is_array($data)) {
            return $data;
        }
    }
    
    if ($cfg['active_gateway'] === 'yesms') {
        $url = rtrim($cfg['yesms_base_url'], '/') . '/user_numbers';
        $headers = ['authkey: ' . $cfg['yesms_api_key']];
    } else {
        $url = rtrim($cfg['voltx_base_url'], '/') . '/success-otp';
        $headers = ['mauthapi: ' . $cfg['voltx_api_key']];
    }

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_TIMEOUT, 8);
    curl_setopt($ch, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);
    curl_setopt($ch, CURLOPT_TCP_NODELAY, 1);
    $res_raw = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http_code === 200) {
        $json_data = json_decode($res_raw, true);
        if (is_array($json_data)) {
            if ($cfg['active_gateway'] === 'yesms') {
                $mapped_otps = [];
                if (isset($json_data['logs']) && is_array($json_data['logs'])) {
                    foreach ($json_data['logs'] as $log) {
                        $mapped_otps[] = [
                            'number' => isset($log['number']) ? $log['number'] : '',
                            'otp' => isset($log['otp_code']) ? $log['otp_code'] : '',
                            'message' => isset($log['full_message']) ? $log['full_message'] : (isset($log['message']) ? $log['message'] : '')
                        ];
                    }
                }
                $mapped_res = [
                    'meta' => ['status' => 'ok', 'code' => 200],
                    'data' => ['otps' => $mapped_otps]
                ];
                file_put_contents($cache_file, json_encode($mapped_res));
                return $mapped_res;
            } else {
                file_put_contents($cache_file, $res_raw);
                return $json_data;
            }
        }
    }
    
    if (file_exists($cache_file)) {
        return json_decode(file_get_contents($cache_file), true);
    }
    return [];
}

function get_voltx_console_cached() {
    $cfg = get_active_gateway_config();
    $cache_file = sys_get_temp_dir() . '/global_active_console_cache.json';
    
    if (file_exists($cache_file) && (time() - filemtime($cache_file)) < 1.0) {
        $data = json_decode(file_get_contents($cache_file), true);
        if (is_array($data)) {
            return $data;
        }
    }
    
    if ($cfg['active_gateway'] === 'yesms') {
        $url = rtrim($cfg['yesms_base_url'], '/') . '/console_data';
        $headers = ['authkey: ' . $cfg['yesms_api_key']];
    } else {
        $url = rtrim($cfg['voltx_base_url'], '/') . '/console';
        $headers = ['mauthapi: ' . $cfg['voltx_api_key']];
    }

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_TIMEOUT, 8);
    curl_setopt($ch, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);
    curl_setopt($ch, CURLOPT_TCP_NODELAY, 1);
    $res_raw = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http_code === 200) {
        $json_data = json_decode($res_raw, true);
        if (is_array($json_data)) {
            if ($cfg['active_gateway'] === 'yesms') {
                $table = isset($json_data['table']) ? $json_data['table'] : [];
                $hits = [];
                foreach ($table as $row) {
                    $range = isset($row[0]) ? $row[0] : '';
                    $raw_c = isset($row[1]) ? trim(str_replace(['🏳️', '🚩', '🏁', '🔥'], '', $row[1])) : '';
                    $msg = isset($row[2]) ? $row[2] : '';
                    $svc = isset($row[3]) && !empty($row[3]) ? $row[3] : 'Global';
                    
                    if ($svc === 'Global' && !empty($msg)) {
                        $msg_lower = strtolower($msg);
                        if (strpos($msg_lower, 'whatsapp') !== false || strpos($msg_lower, 'wa') !== false) $svc = 'WhatsApp';
                        elseif (strpos($msg_lower, 'telegram') !== false || strpos($msg_lower, 'tg') !== false) $svc = 'Telegram';
                        elseif (strpos($msg_lower, 'facebook') !== false || strpos($msg_lower, 'fb') !== false) $svc = 'Facebook';
                        elseif (strpos($msg_lower, 'instagram') !== false || strpos($msg_lower, 'ig') !== false) $svc = 'Instagram';
                        elseif (strpos($msg_lower, 'google') !== false || strpos($msg_lower, 'g-') !== false) $svc = 'Google';
                    }

                    $hits[] = [
                        'range' => $range,
                        'country' => !empty($raw_c) ? $raw_c : get_country_from_range($range),
                        'message' => $msg,
                        'service' => $svc,
                        'time' => isset($row[4]) ? $row[4] : time()
                    ];
                }
                $mapped_res = ['hits' => $hits];
                file_put_contents($cache_file, json_encode($mapped_res));
                return $mapped_res;
            } else {
                file_put_contents($cache_file, $res_raw);
                return $json_data;
            }
        }
    }
    
    if (file_exists($cache_file)) {
        return json_decode(file_get_contents($cache_file), true);
    }
    return [];
}

function parse_live_access_response() {
    $res = gateway_liveaccess();
    $raw_data = isset($res['data']) ? $res['data'] : '';
    $json = json_decode($raw_data, true);

    $formatted_services = [];
    $now_ms = round(microtime(true) * 1000);

    if (is_array($json)) {
        if (isset($json['data']['services']) && is_array($json['data']['services'])) {
            $formatted_services = $json['data']['services'];
        } 
        elseif (isset($json['ranges']) && is_array($json['ranges'])) {
            foreach ($json['ranges'] as $sid => $range_list) {
                $clean_ranges = [];
                if (is_array($range_list)) {
                    foreach ($range_list as $r) {
                        if (is_string($r)) {
                            if (strpos($r, '|') !== false) {
                                $parts = explode('|', $r);
                                $clean_ranges[] = trim($parts[1]);
                            } else {
                                $clean_ranges[] = trim($r);
                            }
                        }
                    }
                }
                $formatted_services[] = [
                    'last_at' => $now_ms - rand(10, 500),
                    'ranges' => array_values(array_unique($clean_ranges)),
                    'sid' => ucfirst($sid)
                ];
            }
        }
        elseif (isset($json['services']) && is_array($json['services'])) {
            foreach ($json['services'] as $svc) {
                $formatted_services[] = [
                    'last_at' => isset($svc['last_at']) ? (int)$svc['last_at'] : $now_ms,
                    'ranges' => isset($svc['ranges']) && is_array($svc['ranges']) ? array_values($svc['ranges']) : [],
                    'sid' => isset($svc['sid']) ? $svc['sid'] : (isset($svc['name']) ? $svc['name'] : 'Generic')
                ];
            }
        }
    }

    if (empty($formatted_services)) {
        $formatted_services = [
            [
                'last_at' => $now_ms,
                'ranges' => ["26138XXX", "26134XXX", "2250778XXX", "2290192XXX", "375336XXX"],
                'sid' => "WhatsApp"
            ],
            [
                'last_at' => $now_ms - 100,
                'ranges' => ["37495XXX", "2290124XXX", "26134XXX", "22465XXX"],
                'sid' => "Facebook"
            ]
        ];
    }

    $rid = "MK" . strtoupper(bin2hex(random_bytes(4)));

    return [
        "meta" => [
            "code" => 200,
            "status" => "ok"
        ],
        "data" => [
            "cached" => true,
            "services" => $formatted_services
        ],
        "message" => "ok",
        "rid" => $rid
    ];
}

function db_request($path, $method = 'GET', $data = null) {
    $pdo = get_db_connection();
    $path = trim($path, '/');
    $parts = explode('/', $path);
    $method = strtoupper($method);

    if ($method !== 'GET') {
        $temp_dir = rtrim(sys_get_temp_dir(), '/');
        $cache_files = glob($temp_dir . '/fb_cache_*.json');
        if (is_array($cache_files)) {
            foreach ($cache_files as $file) {
                @unlink($file);
            }
        }
    }

    if (empty($path)) {
        if ($method === 'GET') {
            return [
                'users' => get_all_rows($pdo, 'users', 'uid'),
                'allocated_numbers' => get_all_rows($pdo, 'allocated_numbers', 'id'),
                'otp_logs' => get_all_rows($pdo, 'otp_logs', 'id'),
                'withdrawals' => get_all_rows($pdo, 'withdrawals', 'id'),
                'settings' => get_settings_assoc($pdo)
            ];
        }
    }

    $table = $parts[0];
    $id = isset($parts[1]) ? $parts[1] : null;
    $sub = isset($parts[2]) ? $parts[2] : null;

    if ($table === 'settings') {
        if ($id === null) {
            if ($method === 'GET') {
                return get_settings_assoc($pdo);
            }
        } else {
            if ($method === 'GET') {
                $stmt = $pdo->prepare("SELECT setting_value FROM settings WHERE setting_key = ?");
                $stmt->execute([$id]);
                $val = $stmt->fetchColumn();
                return $val !== false ? json_decode($val, true) : null;
            } elseif ($method === 'PUT') {
                $stmt = $pdo->prepare("INSERT INTO settings (setting_key, setting_value) VALUES (?, ?) ON DUPLICATE KEY UPDATE setting_value = ?");
                $json_val = json_encode($data);
                $stmt->execute([$id, $json_val, $json_val]);
                return $data;
            }
        }
    }

    $valid_tables = ['users', 'allocated_numbers', 'otp_logs', 'withdrawals', 'live_console'];
    if (!in_array($table, $valid_tables)) {
        return null;
    }

    $primary_keys = [
        'users' => 'uid',
        'allocated_numbers' => 'id',
        'otp_logs' => 'id',
        'withdrawals' => 'id',
        'live_console' => 'id'
    ];
    $pk = $primary_keys[$table];

    if ($id === null) {
        if ($method === 'GET') {
            return get_all_rows($pdo, $table, $pk);
        }
    } else {
        if ($sub === null) {
            if ($method === 'GET') {
                $stmt = $pdo->prepare("SELECT * FROM $table WHERE $pk = ?");
                $stmt->execute([$id]);
                $row = $stmt->fetch();
                return $row ? handle_row_types($table, $row) : null;
            } elseif ($method === 'PUT' || $method === 'PATCH') {
                if (is_array($data)) {
                    $data[$pk] = $id;
                    save_row($pdo, $table, $pk, $data);
                }
                return $data;
            } elseif ($method === 'DELETE') {
                $stmt = $pdo->prepare("DELETE FROM $table WHERE $pk = ?");
                $stmt->execute([$id]);
                return ['status' => 'success'];
            }
        } else {
            if ($method === 'PUT' || $method === 'PATCH') {
                $allowed_columns = [
                    'users' => ['balance', 'wallet_address', 'status', 'api_key_approved', 'api_key', 'password', 'role', 'agent_uid', 'agent_limit', 'otp_rate', 'withdraw_pin', 'agent_auto_approve', 'agent_auto_rate', 'telegram_username'],
                    'allocated_numbers' => ['status', 'otp', 'message'],
                    'withdrawals' => ['status']
                ];
                if (isset($allowed_columns[$table]) && in_array($sub, $allowed_columns[$table])) {
                    if ($sub === 'password') {
                        $val = hash_user_password($data);
                    } elseif ($sub === 'api_key_approved' || $sub === 'agent_auto_approve') {
                        $val = $data ? 1 : 0;
                    } elseif ($sub === 'balance' || $sub === 'otp_rate' || $sub === 'agent_auto_rate') {
                        $val = (float)$data;
                    } elseif ($sub === 'agent_limit') {
                        $val = (int)$data;
                    } else {
                        $val = $data;
                    }
                    $stmt = $pdo->prepare("UPDATE $table SET $sub = ? WHERE $pk = ?");
                    $stmt->execute([$val, $id]);
                    return $data;
                }
            }
        }
    }
    return null;
}

function db_query($path, $index_on, $equals_to) {
    $pdo = get_db_connection();
    $path = trim($path, '/');
    $parts = explode('/', $path);
    $table = $parts[0];
    
    $valid_tables = ['users', 'allocated_numbers', 'otp_logs', 'withdrawals'];
    if (!in_array($table, $valid_tables)) {
        return [];
    }
    
    $primary_keys = [
        'users' => 'uid',
        'allocated_numbers' => 'id',
        'otp_logs' => 'id',
        'withdrawals' => 'id'
    ];
    $pk = $primary_keys[$table];
    
    $stmt = $pdo->prepare("SELECT * FROM $table WHERE $index_on = ?");
    $stmt->execute([$equals_to]);
    $rows = $stmt->fetchAll();
    
    $res = [];
    foreach ($rows as $row) {
        $row = handle_row_types($table, $row);
        $res[$row[$pk]] = $row;
    }
    return $res;
}

function get_all_rows($pdo, $table, $pk) {
    $stmt = $pdo->query("SELECT * FROM $table");
    $rows = $stmt->fetchAll();
    $res = [];
    foreach ($rows as $row) {
        $row = handle_row_types($table, $row);
        if (isset($row[$pk]) && $row[$pk] !== '') {
            $res[$row[$pk]] = $row;
        }
    }
    return $res;
}

function get_settings_assoc($pdo) {
    $stmt = $pdo->query("SELECT * FROM settings");
    $rows = $stmt->fetchAll();
    $res = [];
    foreach ($rows as $row) {
        if (!isset($row['setting_key']) || $row['setting_key'] === '') {
            continue;
        }
        $decoded = json_decode((string)($row['setting_value'] ?? ''), true);
        $res[$row['setting_key']] = json_last_error() === JSON_ERROR_NONE
            ? $decoded
            : ($row['setting_value'] ?? null);
    }
    return $res;
}

function get_dashboard_rows_safe($pdo, $table, $pk, &$issues) {
    try {
        return get_all_rows($pdo, $table, $pk);
    } catch (Throwable $e) {
        $issues[] = $table . ': ' . dashboard_database_error_message($e);
        return [];
    }
}

function get_dashboard_count_safe($pdo, $table, &$issues) {
    try {
        $stmt = $pdo->query("SELECT COUNT(*) FROM `$table`");
        return (int)$stmt->fetchColumn();
    } catch (Throwable $e) {
        $issues[] = $table . ' count: ' . dashboard_database_error_message($e);
        return null;
    }
}

function get_dashboard_pending_user_count_safe($pdo, &$issues) {
    try {
        $stmt = $pdo->query("SELECT COUNT(*) FROM `users` WHERE `status` = 'pending'");
        return (int)$stmt->fetchColumn();
    } catch (Throwable $e) {
        $issues[] = 'users pending count: ' . dashboard_database_error_message($e);
        return null;
    }
}

function get_dashboard_settings_safe($pdo, &$issues) {
    try {
        return get_settings_assoc($pdo);
    } catch (Throwable $e) {
        $issues[] = 'settings: ' . dashboard_database_error_message($e);
        return [];
    }
}

function get_dashboard_methods_safe($pdo, &$issues) {
    try {
        $stmt = $pdo->query("SELECT * FROM withdrawal_methods");
        return $stmt->fetchAll();
    } catch (Throwable $e) {
        $issues[] = 'withdrawal_methods: ' . dashboard_database_error_message($e);
        return [];
    }
}

function dashboard_database_error_message($error) {
    $message = trim((string)$error->getMessage());
    $message = preg_replace('/\s+/', ' ', $message);
    if ($message === '') {
        return 'query failed';
    }
    $message = preg_replace('/(?:password|pwd|pass)\s*=\s*[^;\s]+/i', 'password=[hidden]', $message);
    $message = preg_replace('/\/[^ ]+\/(?:config|security)\.php(?::\d+)?/i', '[path hidden]', $message);
    return substr($message, 0, 180);
}

function handle_row_types($table, $row) {
    if ($table === 'users') {
        $row['balance'] = (float)($row['balance'] ?? 0);
        $row['otp_rate'] = (float)($row['otp_rate'] ?? 0.40);
        $row['agent_limit'] = (int)(isset($row['agent_limit']) ? $row['agent_limit'] : 120);
        $row['api_key_approved'] = (bool)($row['api_key_approved'] ?? false);
        $row['agent_auto_approve'] = (bool)(isset($row['agent_auto_approve']) ? $row['agent_auto_approve'] : true);
        $row['agent_auto_rate'] = (float)(isset($row['agent_auto_rate']) ? $row['agent_auto_rate'] : 0.40);
        $row = public_user_data($row);
    } elseif ($table === 'otp_logs') {
        $row['revenue'] = (float)($row['revenue'] ?? 0);
    } elseif ($table === 'withdrawals') {
        $row['amount'] = (float)($row['amount'] ?? 0);
    }
    return $row;
}

function save_row($pdo, $table, $pk, $data) {
    $allowed_columns = [
        'users' => ['uid', 'name', 'email', 'password', 'api_key', 'api_key_approved', 'balance', 'otp_rate', 'wallet_address', 'id_code', 'status', 'createdAt', 'role', 'agent_uid', 'agent_limit', 'withdraw_pin', 'agent_auto_approve', 'agent_auto_rate', 'telegram_username'],
        'allocated_numbers' => ['id', 'userId', 'number', 'rid', 'status', 'country', 'operator', 'createdAt', 'otp', 'message'],
        'otp_logs' => ['id', 'userId', 'number', 'service', 'otpCode', 'message', 'revenue', 'createdAt'],
        'withdrawals' => ['id', 'userId', 'userEmail', 'userName', 'amount', 'method', 'address', 'status', 'createdAt'],
        'live_console' => ['id', 'type', 'message', 'service', 'createdAt']
    ];

    $valid_cols = $allowed_columns[$table];
    $clean_data = [];
    foreach ($data as $k => $v) {
        if (in_array($k, $valid_cols)) {
            $clean_data[$k] = $v;
        }
    }

    if ($table === 'users' && array_key_exists('password', $clean_data)) {
        $clean_data['password'] = hash_user_password($clean_data['password']);
    }

    $stmt = $pdo->prepare("SELECT * FROM $table WHERE $pk = ?");
    $stmt->execute([$clean_data[$pk]]);
    $existing = $stmt->fetch();

    if ($existing) {
        $merged = array_merge($existing, $clean_data);
        if ($table === 'users') {
            $merged['api_key_approved'] = empty($merged['api_key_approved']) ? 0 : 1;
            $merged['agent_auto_approve'] = empty($merged['agent_auto_approve']) ? 0 : 1;
        }
        $fields = [];
        $values = [];
        foreach ($merged as $col => $val) {
            if ($col === $pk || !in_array($col, $valid_cols)) continue;
            $fields[] = "$col = ?";
            $values[] = $val;
        }
        $values[] = $clean_data[$pk];
        $sql = "UPDATE $table SET " . implode(', ', $fields) . " WHERE $pk = ?";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($values);
    } else {
        if ($table === 'users') {
            $clean_data['api_key_approved'] = empty($clean_data['api_key_approved']) ? 0 : 1;
            $clean_data['agent_auto_approve'] = empty($clean_data['agent_auto_approve']) ? 0 : 1;
        }
        $cols = array_keys($clean_data);
        $placeholders = array_fill(0, count($cols), '?');
        $sql = "INSERT INTO $table (" . implode(', ', $cols) . ") VALUES (" . implode(', ', $placeholders) . ")";
        $stmt = $pdo->prepare($sql);
        $stmt->execute(array_values($clean_data));
    }
}

function db_request_cached($path, $method = 'GET', $data = null, $cache_time = 0) {
    return db_request($path, $method, $data);
}

function rows_to_list($data) {
    if (empty($data) || !is_array($data)) return [];
    $lst = [];
    foreach ($data as $k => $v) {
        if (is_array($v)) {
            $v['id'] = $k;
            $lst[] = $v;
        } else {
            $lst[] = $v;
        }
    }
    return $lst;
}

function parse_iso_datetime($dt_str) {
    if (empty($dt_str)) return new DateTime('now', new DateTimeZone('UTC'));
    if (substr($dt_str, -1) === 'Z') {
        $dt_str = substr($dt_str, 0, -1) . '+00:00';
    }
    try {
        return new DateTime($dt_str);
    } catch (Exception $e) {
        return new DateTime('now', new DateTimeZone('UTC'));
    }
}

function mask_number($number) {
    if (empty($number)) return '';
    $length = strlen($number);
    if ($length < 8) return $number;
    return substr($number, 0, 6) . '****' . substr($number, -3);
}

function extract_otp_code($message) {
    $message_clean = str_replace(["\r", "\n"], " ", $message);
    if (preg_match('/\b\d{2,6}[-\s\/]\d{2,6}\b/', $message_clean, $matches)) {
        return $matches[0];
    }
    if (preg_match('/\b\d{4,12}\b/', $message_clean, $matches)) {
        return $matches[0];
    }
    if (preg_match_all('/\d+/', $message_clean, $matches)) {
        $longest = '';
        foreach ($matches[0] as $digit_str) {
            if (strlen($digit_str) > strlen($longest)) {
                $longest = $digit_str;
            }
        }
        if (strlen($longest) >= 4 && strlen($longest) <= 12) {
            return $longest;
        }
    }
    return "N/A";
}

function get_bearer_token() {
    $headers = array_change_key_case(getallheaders(), CASE_LOWER);
    $auth_header = isset($headers['authorization']) ? trim((string)$headers['authorization']) : '';

    if ($auth_header === '' && isset($headers['x-admin-token'])) {
        return trim((string)$headers['x-admin-token']);
    }

    if ($auth_header === '' && isset($_SERVER['HTTP_AUTHORIZATION'])) {
        $auth_header = trim((string)$_SERVER['HTTP_AUTHORIZATION']);
    }
    if ($auth_header === '' && isset($_SERVER['REDIRECT_HTTP_AUTHORIZATION'])) {
        $auth_header = trim((string)$_SERVER['REDIRECT_HTTP_AUTHORIZATION']);
    }
    if ($auth_header === '' && isset($_SERVER['HTTP_X_ADMIN_TOKEN'])) {
        return trim((string)$_SERVER['HTTP_X_ADMIN_TOKEN']);
    }

    if (preg_match('/^Bearer\\s+(.+)$/i', $auth_header, $matches)) {
        return trim($matches[1]);
    }
    return '';
}

function get_request_json() {
    static $decoded = null;
    static $loaded = false;
    if (!$loaded) {
        $loaded = true;
        $raw = file_get_contents('php://input');
        $value = json_decode($raw, true);
        $decoded = is_array($value) ? $value : [];
    }
    return $decoded;
}

function get_api_key_from_request($headers = null) {
    if (!is_array($headers)) {
        $headers = array_change_key_case(getallheaders(), CASE_LOWER);
    }

    $header_names = ['x-mino-api-key', 'x-api-key', 'mauthapi', 'authkey'];
    foreach ($header_names as $header_name) {
        if (isset($headers[$header_name]) && trim((string)$headers[$header_name]) !== '') {
            return trim((string)$headers[$header_name]);
        }
    }

    $request_names = ['api_key', 'apiKey', 'authkey', 'mauthapi', 'key'];
    foreach ($request_names as $request_name) {
        if (isset($_REQUEST[$request_name]) && trim((string)$_REQUEST[$request_name]) !== '') {
            return trim((string)$_REQUEST[$request_name]);
        }
    }

    $bearer = get_bearer_token();
    if ($bearer !== '') {
        return $bearer;
    }

    $authorization = isset($headers['authorization']) ? trim((string)$headers['authorization']) : '';
    if (preg_match('/^Api-Key\\s+(.+)$/i', $authorization, $matches)) {
        return trim($matches[1]);
    }

    $input = get_request_json();
    foreach ($request_names as $request_name) {
        if (isset($input[$request_name]) && trim((string)$input[$request_name]) !== '') {
            return trim((string)$input[$request_name]);
        }
    }

    return '';
}

function get_current_user_optimized() {
    $headers = array_change_key_case(getallheaders(), CASE_LOWER);
    $token = get_bearer_token();
    $api_key = get_api_key_from_request($headers);
    if (!empty($token)) {
        $pdo = get_db_connection();
        $stmt = $pdo->prepare("SELECT * FROM users WHERE uid = ? LIMIT 1");
        $stmt->execute([$token]);
        $mysql_user = $stmt->fetch();
        if ($mysql_user) {
            $mysql_user = handle_row_types('users', $mysql_user);
            if (strtolower(trim((string)($mysql_user['status'] ?? ''))) === 'approved') {
                return $mysql_user;
            }
        }

        $user = db_request('/users/' . $token, 'GET');
        if ($user && strtolower(trim((string)($user['status'] ?? ''))) === 'approved') {
            return $user;
        }
    }

    if (!empty($api_key)) {
        $pdo = get_db_connection();
        $stmt = $pdo->prepare("SELECT * FROM users WHERE api_key = ? LIMIT 1");
        $stmt->execute([$api_key]);
        $u_data = $stmt->fetch();
        if ($u_data) {
            $u_data = handle_row_types('users', $u_data);
            if (isset($u_data['status']) && $u_data['status'] === 'approved' && isset($u_data['api_key_approved']) && $u_data['api_key_approved'] === true) {
                return $u_data;
            }
        }
    }
    return null;
}

function verify_admin() {
    $token = get_bearer_token();
    return $token !== '' && hash_equals(ADMIN_STATIC_TOKEN, $token);
}

function is_maintenance() {
    try {
        $val = db_request_cached('/settings/maintenance_mode', 'GET', null, 5);
        return (bool)$val;
    } catch (Exception $e) {
        return false;
    }
}

function handle_pre_requests($is_admin_route = false) {
    header("Access-Control-Allow-Origin: *");
    header("Access-Control-Allow-Headers: Content-Type, X-MINO-API-KEY, X-API-KEY, Authorization, authkey, mauthapi");
    header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
    header("Cache-Control: no-cache, no-store, must-revalidate");
    header("Pragma: no-cache");
    header("Expires: 0");

    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        exit(0);
    }

    if (!$is_admin_route) {
        if (is_maintenance()) {
            http_response_code(503);
            echo json_encode(['status' => 'error', 'message' => 'System is under maintenance']);
            exit();
        }
    }
}