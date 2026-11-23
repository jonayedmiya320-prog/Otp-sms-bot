<?php
require_once 'security.php';
handle_pre_requests(false);

$action = isset($_GET['action']) ? $_GET['action'] : '';

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

switch ($action) {
    case 'getnum':
        $rid = isset($_REQUEST['rid']) ? trim($_REQUEST['rid']) : '';
        if (empty($rid)) {
            $input = get_request_json();
            if (isset($input['rid'])) {
                $rid = trim($input['rid']);
            }
        }

        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Invalid API Key or Unauthorized']);
            exit();
        }

        if (empty($rid)) {
            echo json_encode(['status' => 'error', 'message' => 'Range ID missing']);
            exit();
        }

        $user_id = $user['uid'];
        
        $api_key_approved = isset($user['api_key_approved']) ? (bool)$user['api_key_approved'] : false;
        if (!$api_key_approved) {
            $cache_file = sys_get_temp_dir() . '/last_booking_' . md5($user_id) . '.txt';
            $last_booking_str = file_exists($cache_file) ? file_get_contents($cache_file) : (isset($user['last_booking_time']) ? $user['last_booking_time'] : '');
            
            $now = new DateTime('now', new DateTimeZone('UTC'));
            if (!empty($last_booking_str)) {
                $last_booking = parse_iso_datetime($last_booking_str);
                $elapsed = $now->getTimestamp() - $last_booking->getTimestamp();
                if ($elapsed < 8.0) {
                    $remaining = round(8.0 - $elapsed, 1);
                    http_response_code(429);
                    echo json_encode([
                        'status' => 'error', 
                        'message' => "Rate limit cooldown: Please wait {$remaining} seconds before requesting a new number."
                    ]);
                    exit();
                }
            }
            file_put_contents($cache_file, $now->format(DateTime::ATOM));
        }

        $alloc_res = gateway_allocate_number($rid);
        if (!$alloc_res['success']) {
            http_response_code(400);
            echo json_encode(['status' => 'error', 'message' => $alloc_res['error']]);
            exit();
        }

        $voltx_data = $alloc_res['data'];
        $data_payload = isset($voltx_data['data']) ? $voltx_data['data'] : [];
        $number = isset($data_payload['full_number']) ? $data_payload['full_number'] : (isset($data_payload['national_number']) ? $data_payload['national_number'] : (isset($data_payload['no_plus_number']) ? $data_payload['no_plus_number'] : ''));
        $country = isset($data_payload['country']) ? $data_payload['country'] : 'Guinea';
        $operator = isset($data_payload['operator']) ? $data_payload['operator'] : 'Mobile';

        $alloc_id = "alloc_" . bin2hex(random_bytes(8));
        $created_at = (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM);

        // ⚡ Direct Instant SQL Write
        $pdo = get_db_connection();
        $stmt_ins = $pdo->prepare("INSERT INTO allocated_numbers (id, userId, number, rid, status, country, operator, createdAt) VALUES (?, ?, ?, ?, 'active', ?, ?, ?)");
        $stmt_ins->execute([$alloc_id, $user_id, $number, $rid, $country, $operator, $created_at]);

        echo json_encode([
            'status' => 'success',
            'id' => $alloc_id,
            'number' => $number,
            'country' => $country,
            'operator' => $operator
        ]);
        break;

    case 'liveaccess':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Access Denied. Invalid or Missing API credentials.']);
            exit();
        }
        
        $res = gateway_liveaccess();
        http_response_code($res['code']);
        header("Content-Type: application/json");
        echo $res['data'];
        break;

    case 'success-otp':
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
            $service_rates_raw = db_request('/settings/service_rates') ?: [];
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
                                
                                $message = isset($otp_item['message']) ? $otp_item['message'] : '';
                                $otp_code = extract_otp_code($message);

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
                    if ($elapsed_seconds > 1080) { 
                        $alloc_id = $alloc['id'];
                        db_request('/allocated_numbers/' . $alloc_id . '/status', 'PUT', 'expired');
                    }
                }
            }
        }

        $all_logs_dict = db_request('/otp_logs') ?: [];
        $all_logs_list = rows_to_list($all_logs_dict);
        
        $user_logs = [];
        foreach ($all_logs_list as $log) {
            if (isset($log['userId']) && $log['userId'] === $user_id) {
                $user_logs[] = $log;
            }
        }
        usort($user_logs, function($a, $b) {
            return strcmp(isset($b['createdAt']) ? $b['createdAt'] : '', isset($a['createdAt']) ? $a['createdAt'] : '');
        });

        $data = [];
        foreach (array_slice($user_logs, 0, 20) as $d) {
            $data[] = [
                'number' => isset($d['number']) ? $d['number'] : '',
                'service' => isset($d['service']) ? $d['service'] : '',
                'otp_code' => isset($d['otp_code']) ? $d['otp_code'] : (isset($d['otpCode']) ? $d['otpCode'] : ''),
                'message' => isset($d['message']) ? $d['message'] : '',
                'revenue_earned' => isset($d['revenue']) ? $d['revenue'] : 0.00,
                'created_at' => isset($d['createdAt']) ? $d['createdAt'] : ''
            ];
        }

        echo json_encode(['status' => 'success', 'data' => $data]);
        break;

    case 'console':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Invalid API Key or Unauthorized access.']);
            exit();
        }

        try {
            $voltx_data = get_voltx_console_cached();
            $hits = [];
            
            if (is_array($voltx_data)) {
                if (isset($voltx_data['data'])) {
                    $data_obj = $voltx_data['data'];
                    if (is_array($data_obj) && isset($data_obj['hits'])) {
                        $hits = $data_obj['hits'];
                    } elseif (is_array($data_obj) && isset($data_obj['ranges'])) {
                        $hits = $data_obj['ranges'];
                    } elseif (is_array($data_obj)) {
                        $hits = $data_obj;
                    }
                } else {
                    $hits = isset($voltx_data['hits']) ? $voltx_data['hits'] : (isset($voltx_data['ranges']) ? $voltx_data['ranges'] : $voltx_data);
                }
            }

            $data = [];
            foreach ($hits as $hit) {
                if (!is_array($hit)) continue;
                
                $msg = isset($hit['message']) ? $hit['message'] : (isset($hit['msg']) ? $hit['msg'] : '');
                $single_range = isset($hit['range']) ? $hit['range'] : '';
                $sid = isset($hit['sid']) ? $hit['sid'] : 'Global';
                $time_val = isset($hit['time']) ? $hit['time'] : (isset($hit['last_at']) ? $hit['last_at'] : 0);
                
                if (!empty($single_range) && !empty($msg)) {
                    $c_name = get_country_from_range($single_range);
                    $data[] = [
                        'range' => $single_range,
                        'service' => $sid,
                        'message' => $msg,
                        'time' => $time_val,
                        'country' => $c_name
                    ];
                } else {
                    $ranges = isset($hit['ranges']) ? $hit['ranges'] : [];
                    if (is_array($ranges)) {
                        foreach ($ranges as $r) {
                            $c_name = get_country_from_range($r);
                            $data[] = [
                                'range' => $r,
                                'service' => $sid,
                                'message' => "Signal intercepted on range {$r} for {$sid}",
                                'time' => $time_val,
                                'country' => $c_name
                            ];
                        }
                    } elseif (is_string($ranges)) {
                        $c_name = get_country_from_range($ranges);
                        $data[] = [
                                'range' => $ranges,
                                'service' => $sid,
                                'message' => "Signal intercepted on range {$ranges} for {$sid}",
                                'time' => $time_val,
                                'country' => $c_name
                        ];
                    }
                }
            }
            echo json_encode(['status' => 'success', 'data' => $data]);
            exit();
        } catch (Exception $e) {}
        echo json_encode(['status' => 'success', 'data' => []]);
        break;

    case 'check':
        $user = get_current_user_optimized();
        if (!$user) {
            http_response_code(402);
            echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
            exit();
        }

        $target_number = isset($_REQUEST['number']) ? trim($_REQUEST['number']) : '';
        if (empty($target_number)) {
            echo json_encode(['status' => 'error', 'message' => 'Missing number parameter']);
            exit();
        }
        
        $clean_target = str_replace(['+', ' '], '', $target_number);
        
        $all_allocs_dict = db_query('/allocated_numbers', 'userId', $user['uid']) ?: [];
        $all_allocs_list = rows_to_list($all_allocs_dict);
        $user_id = $user['uid'];
        
        $matched_alloc = null;
        foreach ($all_allocs_list as $alloc) {
            $alloc_num = str_replace(['+', ' '], '', isset($alloc['number']) ? $alloc['number'] : '');
            if (!empty($alloc_num) && !empty($clean_target) && (strpos($clean_target, $alloc_num) !== false || strpos($alloc_num, $clean_target) !== false)) {
                $matched_alloc = $alloc;
                break;
            }
        }
        
        if (!$matched_alloc) {
            http_response_code(404);
            echo json_encode(['status' => 'error', 'message' => 'Number allocation not found for this user']);
            exit();
        }
        
        if (isset($matched_alloc['status']) && $matched_alloc['status'] === 'active') {
            try {
                $json_data = get_voltx_success_otp_cached();
                $otps = isset($json_data['data']['otps']) ? $json_data['data']['otps'] : [];
                foreach ($otps as $otp_item) {
                    $otp_num = str_replace(['+', ' '], '', isset($otp_item['number']) ? $otp_item['number'] : '');
                    $alloc_num = str_replace(['+', ' '], '', isset($matched_alloc['number']) ? $matched_alloc['number'] : '');
                    
                    if (!empty($otp_num) && !empty($alloc_num) && (strpos($clean_target, $otp_num) !== false || strpos($otp_num, $clean_target) !== false)) {
                        $message = isset($otp_item['message']) ? $otp_item['message'] : '';
                        $otp_code = extract_otp_code($message);
                                
                        $pdo = get_db_connection();
                        $stmt_up = $pdo->prepare("UPDATE allocated_numbers SET status = 'completed', otp = ?, message = ? WHERE id = ? AND status = 'active'");
                        $stmt_up->execute([$otp_code, $message, $matched_alloc['id']]);

                        if ($stmt_up->rowCount() > 0) {
                            $matched_alloc['status'] = 'completed';
                            $matched_alloc['otp'] = $otp_code;
                            $matched_alloc['message'] = $message;
                            
                            $service_rates_raw = db_request('/settings/service_rates') ?: [];
                            $service_rates = [];
                            foreach ($service_rates_raw as $k => $v) {
                                $service_rates[strtolower($k)] = $v;
                            }
                            
                            $service = 'generic';
                            $msg_lower = strtolower($message);
                            if (strpos($msg_lower, 'facebook') !== false || strpos($msg_lower, 'fb') !== false) $service = 'facebook';
                            elseif (strpos($msg_lower, 'instagram') !== false || strpos($msg_lower, 'ig') !== false) $service = 'instagram';
                            elseif (strpos($msg_lower, 'whatsapp') !== false || strpos($msg_lower, 'wa') !== false) $service = 'whatsapp';
                            elseif (strpos($msg_lower, 'telegram') !== false || strpos($msg_lower, 'tg') !== false) $service = 'telegram';
                            elseif (strpos($msg_lower, 'google') !== false || strpos($msg_lower, 'g-') !== false) $service = 'google';
                            
                            $otp_rate = isset($user['otp_rate']) ? (float)$user['otp_rate'] : 0.40;
                            $earned_revenue = get_scaled_service_rate($service, $otp_rate, $service_rates);
                            
                            $stmt_bal = $pdo->prepare("UPDATE users SET balance = balance + ? WHERE uid = ?");
                            $stmt_bal->execute([$earned_revenue, $user_id]);
                            
                            credit_agent_commission($pdo, $user_id, $earned_revenue);
                            
                            $otp_id = "otp_" . bin2hex(random_bytes(8));
                            db_request('/otp_logs/' . $otp_id, 'PUT', [
                                'userId' => $user_id,
                                'number' => $matched_alloc['number'],
                                'service' => $service,
                                'otpCode' => $otp_code,
                                'message' => $message,
                                'revenue' => $earned_revenue,
                                'createdAt' => (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM)
                            ]);
                        }
                        break;
                    }
                }
            } catch (Exception $sync_err) {}
        }
            
        echo json_encode([
            'status' => 'success',
            'number' => isset($matched_alloc['number']) ? $matched_alloc['number'] : '',
            'allocation_status' => isset($matched_alloc['status']) ? $matched_alloc['status'] : '',
            'otp_code' => isset($matched_alloc['otp']) ? $matched_alloc['otp'] : '',
            'full_sms' => isset($matched_alloc['message']) ? $matched_alloc['message'] : '',
            'created_at' => isset($matched_alloc['createdAt']) ? $matched_alloc['createdAt'] : ''
        ]);
        break;

    default:
        http_response_code(404);
        echo json_encode(['status' => 'error', 'message' => 'Action path not found']);
        break;
}