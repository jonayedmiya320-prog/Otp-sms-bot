<?php
/**
 * MINO SMS - Standalone API Endpoint for Personal Successful OTP Records List
 * Path: success_otp.php
 */

require_once 'security.php';
handle_pre_requests(false);

$user = get_current_user_optimized();
if (!$user) {
    http_response_code(402);
    echo json_encode(['status' => 'error', 'message' => 'Unauthorized access.']);
    exit();
}

$user_id = $user['uid'];
$otp_rate = isset($user['otp_rate']) ? (float)$user['otp_rate'] : 0.40;

// ⚡ CRUCIAL FIX: Sync user's active OTPs directly with Voltx/Yesms gateway EVEN IF PANEL IS CLOSED!
sync_user_active_otps($user_id, $otp_rate);

$pdo = get_db_connection();
$stmt = $pdo->prepare("SELECT * FROM otp_logs WHERE userId = ? ORDER BY createdAt DESC LIMIT 50");
$stmt->execute([$user_id]);
$user_logs = $stmt->fetchAll();

$data = [];
foreach ($user_logs as $d) {
    $data[] = [
        'number' => isset($d['number']) ? $d['number'] : '',
        'service' => isset($d['service']) ? $d['service'] : '',
        'otp_code' => isset($d['otpCode']) ? $d['otpCode'] : (isset($d['otp_code']) ? $d['otp_code'] : ''),
        'message' => isset($d['message']) ? $d['message'] : '',
        'revenue_earned' => (float)(isset($d['revenue']) ? $d['revenue'] : 0.00),
        'created_at' => isset($d['createdAt']) ? $d['createdAt'] : ''
    ];
}

echo json_encode(['status' => 'success', 'data' => $data]);
exit();