<?php
/**
 * MINO SMS - Standalone API Endpoint for Gateway Live Access Status
 * Path: liveaccess.php
 */

require_once 'security.php';
handle_pre_requests(false);

$user = get_current_user_optimized();
if (!$user) {
    http_response_code(402);
    echo json_encode(['status' => 'error', 'message' => 'Access Denied. Invalid or Missing API credentials.']);
    exit();
}

try {
    $parsed = parse_live_access_response();
    header("Content-Type: application/json");
    echo json_encode($parsed, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Gateway fetch process failed: ' . $e->getMessage()]);
}
exit();