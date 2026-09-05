<?php
declare(strict_types=1);

require __DIR__ . '/HaqqLineApi.php';

$api = new HaqqLineApi(__DIR__);
$api->handle();
