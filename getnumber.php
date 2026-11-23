<?php
/**
 * MINO SMS - Standalone API Endpoint for Instant Number Booking
 * Path: getnumber.php
 */

require_once 'security.php';
handle_pre_requests(false);

// Accepts rid in POST/GET/JSON
$request_input = get_request_json();
$rid = isset($_REQUEST['rid']) ? trim($_REQUEST['rid']) : (isset($_REQUEST['range_id']) ? trim($_REQUEST['range_id']) : (isset($request_input['rid']) ? trim($request_input['rid']) : (isset($request_input['range_id']) ? trim($request_input['range_id']) : '')));

$user = get_current_user_optimized();
if (!$user) {
    http_response_code(402);
    echo json_encode(['status' => 'error', 'message' => 'Invalid API Key or Unauthorized access.']);
    exit();
}

if (empty($rid)) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Range ID (rid) parameter is required.']);
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

// Ultra Fast Gateway Allocation Call
$alloc_res = gateway_allocate_number($rid);
if (!$alloc_res['success']) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => $alloc_res['error']]);
    exit();
}

$voltx_data = $alloc_res['data'];
$data_payload = isset($voltx_data['data']) ? $voltx_data['data'] : [];
$number = isset($data_payload['full_number']) ? $data_payload['full_number'] : (isset($data_payload['national_number']) ? $data_payload['national_number'] : '');
$country = isset($data_payload['country']) ? $data_payload['country'] : get_country_from_range($rid);
$operator = isset($data_payload['operator']) ? $data_payload['operator'] : 'Mobile';

$alloc_id = "alloc_" . bin2hex(random_bytes(8));
$created_at = (new DateTime('now', new DateTimeZone('UTC')))->format(DateTime::ATOM);

// ⚡ Direct High-Speed SQL Insert (Instant Database Write)
$pdo = get_db_connection();
$stmt_ins = $pdo->prepare("INSERT INTO allocated_numbers (id, userId, number, rid, status, country, operator, createdAt) VALUES (?, ?, ?, ?, 'active', ?, ?, ?)");
$stmt_ins->execute([$alloc_id, $user_id, $number, $rid, $country, $operator, $created_at]);

// Lightning Fast Json Output
echo json_encode([
    'status' => 'success',
    'id' => $alloc_id,
    'number' => $number,
    'country' => $country,
    'operator' => $operator,
    'meta' => [
        'status' => 'ok',
        'code' => 200
    ],
    'data' => [
        'full_number' => $number,
        'national_number' => isset($data_payload['national_number']) ? $data_payload['national_number'] : $number,
        'no_plus_number' => ltrim($number, '+'),
        'country' => $country,
        'operator' => $operator
    ]
]);
exit();