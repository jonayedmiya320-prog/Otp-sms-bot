<?php
/**
 * MINO SMS - Standalone API Endpoint for OTP Check & Balance Reward Credit
 * Path: check.php
 */

require_once 'security.php';
handle_pre_requests(false);

$user = get_current_user_optimized();
if (!$user) {
    http_response_code(402);
    echo json_encode(['status' => 'error', 'message' => 'Unauthorized or invalid API key.']);
    exit();
}

$target_number = isset($_REQUEST['number']) ? trim($_REQUEST['number']) : (isset($_REQUEST['full_number']) ? trim($_REQUEST['full_number']) : '');
if (empty($target_number)) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Missing number parameter.']);
    exit();
}

$user_id = $user['uid'];
$otp_rate = isset($user['otp_rate']) ? (float)$user['otp_rate'] : 0.40;

// ⚡ CRUCIAL FIX: Sync user's active OTPs directly with Voltx/Yesms gateway EVEN IF PANEL IS CLOSED!
sync_user_active_otps($user_id, $otp_rate);

$clean_target = str_replace(['+', ' '], '', $target_number);

$pdo = get_db_connection();
$stmt = $pdo->prepare("SELECT * FROM allocated_numbers WHERE userId = ? ORDER BY createdAt DESC");
$stmt->execute([$user_id]);
$all_allocs = $stmt->fetchAll();

$matched_alloc = null;
foreach ($all_allocs as $alloc) {
    $alloc_num = str_replace(['+', ' '], '', isset($alloc['number']) ? $alloc['number'] : '');
    if (!empty($alloc_num) && !empty($clean_target) && (strpos($clean_target, $alloc_num) !== false || strpos($alloc_num, $clean_target) !== false)) {
        $matched_alloc = $alloc;
        break;
    }
}

if (!$matched_alloc) {
    http_response_code(404);
    echo json_encode(['status' => 'error', 'message' => 'Number allocation not found for this user.']);
    exit();
}

echo json_encode([
    'status' => 'success',
    'number' => isset($matched_alloc['number']) ? $matched_alloc['number'] : '',
    'allocation_status' => isset($matched_alloc['status']) ? $matched_alloc['status'] : '',
    'otp_code' => isset($matched_alloc['otp']) ? $matched_alloc['otp'] : '',
    'full_sms' => isset($matched_alloc['message']) ? $matched_alloc['message'] : '',
    'created_at' => isset($matched_alloc['createdAt']) ? $matched_alloc['createdAt'] : ''
]);
exit();