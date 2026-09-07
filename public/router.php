<?php
declare(strict_types=1);

$uri = parse_url(isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '/', PHP_URL_PATH);
if (!is_string($uri)) {
    $uri = '/';
}

if ($uri === '/play' || $uri === '/play/') {
    header('Content-Type: text/html; charset=utf-8');
    readfile(__DIR__ . '/play/index.html');
    return true;
}

if ($uri === '/health') {
    header('Content-Type: application/json; charset=utf-8');
    readfile(__DIR__ . '/health.json');
    return true;
}

if ($uri === '/api/v1/docs' || $uri === '/api/v1/docs/') {
    header('Content-Type: text/html; charset=utf-8');
    readfile(__DIR__ . '/api/v1/docs/index.html');
    return true;
}

$apiPrefixes = array(
    '/api/v1/tools',
    '/api/v1/health',
    '/api/v1/audit',
    '/api/v1/conversations',
    '/api/v1/webhooks',
);
foreach ($apiPrefixes as $prefix) {
    if ($uri === $prefix || strpos($uri, $prefix . '/') === 0) {
        require __DIR__ . '/api/v1/index.php';
        return true;
    }
}

$file = __DIR__ . $uri;
if ($uri !== '/' && is_file($file)) {
    return false;
}

return false;
