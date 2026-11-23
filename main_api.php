<?php
/**
 * MINO SMS - Live Signal Console API Endpoint
 * Path: main_api.php
 */

require_once 'security.php';
handle_pre_requests(false);

$action = isset($_GET['action']) ? $_GET['action'] : '';

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

switch ($action) {
    case 'live-console':
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
                if (isset($voltx_data['hits'])) {
                    $hits = $voltx_data['hits'];
                } elseif (isset($voltx_data['data'])) {
                    $data_obj = $voltx_data['data'];
                    if (is_array($data_obj) && isset($data_obj['hits'])) {
                        $hits = $data_obj['hits'];
                    } elseif (is_array($data_obj) && isset($data_obj['ranges'])) {
                        $hits = $data_obj['ranges'];
                    } elseif (is_array($data_obj)) {
                        $hits = $data_obj;
                    }
                } else {
                    $hits = isset($voltx_data['ranges']) ? $voltx_data['ranges'] : $voltx_data;
                }
            }

            $data = [];
            foreach ($hits as $hit) {
                if (!is_array($hit)) continue;
                
                $msg = isset($hit['message']) ? $hit['message'] : (isset($hit['msg']) ? $hit['msg'] : '');
                $single_range = isset($hit['range']) ? $hit['range'] : '';
                
                // সার্ভিস নাম ডিটেকশন ও ফলব্যাক
                $sid = isset($hit['service']) && !empty($hit['service']) ? $hit['service'] : (isset($hit['sid']) && !empty($hit['sid']) ? $hit['sid'] : '');
                
                if (empty($sid) || strtolower($sid) === 'global' || strtolower($sid) === 'unknown') {
                    $msg_lower = strtolower($msg);
                    if (strpos($msg_lower, 'whatsapp') !== false || strpos($msg_lower, 'wa') !== false) $sid = 'WhatsApp';
                    elseif (strpos($msg_lower, 'telegram') !== false || strpos($msg_lower, 'tg') !== false) $sid = 'Telegram';
                    elseif (strpos($msg_lower, 'facebook') !== false || strpos($msg_lower, 'fb') !== false) $sid = 'Facebook';
                    elseif (strpos($msg_lower, 'instagram') !== false || strpos($msg_lower, 'ig') !== false) $sid = 'Instagram';
                    elseif (strpos($msg_lower, 'google') !== false || strpos($msg_lower, 'g-') !== false) $sid = 'Google';
                    else $sid = 'SMS Service';
                }

                // কান্ট্রি নাম ডিটেকশন ও ফলব্যাক
                $c_name = isset($hit['country']) && !empty($hit['country']) ? $hit['country'] : get_country_from_range($single_range);
                if (empty($c_name) || strtolower($c_name) === 'unknown') {
                    $c_name = 'International';
                }

                $time_val = isset($hit['time']) ? $hit['time'] : (isset($hit['last_at']) ? $hit['last_at'] : time());

                if (!empty($single_range)) {
                    $data[] = [
                        'range' => $single_range,
                        'service' => $sid,
                        'message' => $msg,
                        'time' => $time_val,
                        'country' => $c_name
                    ];
                }
            }
            echo json_encode(['status' => 'success', 'data' => $data]);
            exit();
        } catch (Exception $e) {
            echo json_encode(['status' => 'success', 'data' => []]);
        }
        break;

    default:
        http_response_code(404);
        echo json_encode(['status' => 'error', 'message' => 'Action path not found']);
        break;
}