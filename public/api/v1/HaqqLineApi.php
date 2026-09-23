<?php
declare(strict_types=1);

final class HaqqLineApi
{
    /** @var string */
    private $root;
    /** @var array */
    private $config;
    /** @var array */
    private $areas;
    /** @var array */
    private $ejari;

    public function __construct(string $root)
    {
        $this->root = $root;
        $this->config = $this->readJson($root . '/pack/config.json');
        $this->areas = $this->readJson($root . '/pack/areas.json');
        $this->ejari = $this->readJson($root . '/pack/ejari.json');
    }

    /** @var string */
    private $rawInput = '';

    public function handle(): void
    {
        $method = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : 'GET';
        $path = $this->path();
        $this->rawInput = (string) file_get_contents('php://input');

        if ($method === 'OPTIONS') {
            $this->send(204, null);
            return;
        }

        if ($method === 'GET' && ($path === '/api/v1/health' || $path === '/health')) {
            $this->send(200, array(
                'status' => 'ok',
                'service' => 'haqqline',
                'phase' => 7,
                'pack_id' => $this->config['pack_id'],
                'pack_version' => isset($this->config['pack_version']) ? $this->config['pack_version'] : null,
                'citation_id' => isset($this->config['citation_id']) ? $this->config['citation_id'] : null,
                'environment' => 'sandbox',
            ));
            return;
        }

        if ($method === 'POST' && $path === '/api/v1/webhooks/elevenlabs') {
            $this->elevenLabsWebhook();
            return;
        }

        $auth = $this->authenticate();
        if ($auth !== true) {
            return;
        }
        if (!$this->rateLimit()) {
            return;
        }

        if ($method === 'GET' && $path === '/api/v1/audit') {
            $this->send(200, array('entries' => $this->readAuditTail(20)));
            return;
        }

        if ($method === 'GET' && $path === '/api/v1/conversations') {
            $this->send(200, array('entries' => $this->readJsonlTail($this->dataDir() . '/conversations.jsonl', 10)));
            return;
        }

        if ($method !== 'POST') {
            $this->send(405, array('error' => 'method_not_allowed'));
            return;
        }

        $body = $this->jsonBody();
        $node = $this->workflowNode();

        if ($path === '/api/v1/tools/decide_case') {
            $this->policyDeny('decide_case', $body, $node, array(
                'ok' => false,
                'reason' => 'decide_case_forbidden',
                'detail' => 'There is no decide_case tool; outcomes are human-only.',
            ));
            return;
        }
        if ($path === '/api/v1/tools/lookup_rera_band') {
            if (!$this->policyAllow('lookup_rera_band', $body, $node)) {
                return;
            }
            $this->lookupRera($body);
            return;
        }
        if ($path === '/api/v1/tools/lookup_ejari') {
            if (!$this->policyAllow('lookup_ejari', $body, $node)) {
                return;
            }
            $this->lookupEjari($body);
            return;
        }
        if ($path === '/api/v1/tools/submit_to_human_queue') {
            if (!$this->policyAllow('submit_to_human_queue', $body, $node)) {
                return;
            }
            $this->submitQueue($body);
            return;
        }
        if ($path === '/api/v1/tools/escalate_human') {
            if (!$this->policyAllow('escalate_human', $body, $node)) {
                return;
            }
            $this->escalate($body);
            return;
        }

        $this->send(404, array('error' => 'not_found'));
    }

    private function workflowNode(): ?string
    {
        $header = isset($_SERVER['HTTP_X_HAQQLINE_WORKFLOW_NODE'])
            ? trim((string) $_SERVER['HTTP_X_HAQQLINE_WORKFLOW_NODE'])
            : '';
        return $header === '' ? null : $header;
    }

    /** @param array $body */
    private function policyAllow(string $tool, array $body, ?string $node): bool
    {
        $result = HaqqLinePolicy::evaluate($tool, $body, $node);
        if ($result['ok'] === true) {
            return true;
        }
        $this->policyDeny($tool, $body, $node, $result);
        return false;
    }

    /**
     * @param array $body
     * @param array $result
     */
    private function policyDeny(string $tool, array $body, ?string $node, array $result): void
    {
        $reason = isset($result['reason']) ? (string) $result['reason'] : 'policy_denied';
        $payload = array(
            'error' => $reason,
            'policy_denied' => true,
            'reason' => $reason,
            'detail' => isset($result['detail']) ? $result['detail'] : null,
            'tool' => $tool,
            'workflow_node' => $node,
        );
        $code = ($reason === 'confirmation_required') ? 400 : 403;
        $this->audit($tool, $code, array(
            'policy_denied' => true,
            'reason' => $reason,
            'workflow_node' => $node,
        ));
        $this->send($code, $payload);
    }

    private function path(): string
    {
        $uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '/';
        $path = parse_url($uri, PHP_URL_PATH);
        if (!is_string($path) || $path === '') {
            return '/';
        }
        if (strpos($path, '/api/v1/index.php') === 0) {
            $path = '/api/v1' . substr($path, strlen('/api/v1/index.php'));
        }
        return rtrim($path, '/') === '' ? '/' : rtrim($path, '/');
    }

    private function authenticate()
    {
        $header = isset($_SERVER['HTTP_AUTHORIZATION']) ? $_SERVER['HTTP_AUTHORIZATION'] : '';
        $key = '';
        if (stripos($header, 'Bearer ') === 0) {
            $key = trim(substr($header, 7));
        }
        if ($key === '' && isset($_SERVER['HTTP_X_API_KEY'])) {
            $key = trim((string) $_SERVER['HTTP_X_API_KEY']);
        }
        if ($key !== (string) $this->config['demo_api_key']) {
            $this->send(401, array('error' => 'unauthorized'));
            return false;
        }
        return true;
    }

    private function rateLimit(): bool
    {
        $limit = (int) $this->config['rate_limit_per_minute'];
        $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '0.0.0.0';
        $bucket = preg_replace('/[^a-zA-Z0-9._-]/', '_', $ip);
        $file = $this->dataDir() . '/rate-' . $bucket . '.json';
        $now = time();
        $window = array();
        $fh = fopen($file, 'c+');
        if ($fh === false) {
            $this->send(503, array('error' => 'rate_store_unavailable'));
            return false;
        }
        flock($fh, LOCK_EX);
        $raw = stream_get_contents($fh);
        if (is_string($raw) && $raw !== '') {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) {
                $window = $decoded;
            }
        }
        $window = array_values(array_filter($window, function ($t) use ($now) {
            return is_int($t) && $t > $now - 60;
        }));
        if (count($window) >= $limit) {
            flock($fh, LOCK_UN);
            fclose($fh);
            $this->send(429, array('error' => 'rate_limited', 'retry_after_seconds' => 30));
            return false;
        }
        $window[] = $now;
        ftruncate($fh, 0);
        rewind($fh);
        fwrite($fh, json_encode($window));
        flock($fh, LOCK_UN);
        fclose($fh);
        return true;
    }

    private function lookupRera(array $body): void
    {
        $area = isset($body['area']) ? (string) $body['area'] : '';
        if (!isset($this->areas[$area])) {
            $payload = array(
                'error' => 'unknown_area',
                'escalate' => true,
                'area' => $area,
                'disclaimer' => $this->config['disclaimer'],
            );
            $payload = $this->withPackCitation($payload);
            $this->audit('lookup_rera_band', 404, $payload);
            $this->send(404, $payload);
            return;
        }
        $current = isset($body['current_rent']) ? (float) $body['current_rent'] : 0.0;
        $proposed = isset($body['proposed_rent']) ? (float) $body['proposed_rent'] : 0.0;
        if ($current <= 0 || $proposed <= 0) {
            $this->send(400, array('error' => 'invalid_rent'));
            return;
        }
        $index = (float) $this->areas[$area]['index_aed'];
        $pct = $this->permittedIncreasePct($current, $index);
        $cap = round($current * (1 + $pct / 100), 2);
        $payload = array(
            'source' => $this->config['pack_id'],
            'pack_id' => $this->config['pack_id'],
            'pack_version' => isset($this->config['pack_version']) ? $this->config['pack_version'] : null,
            'citation_id' => isset($this->config['citation_id']) ? $this->config['citation_id'] : $this->config['pack_id'],
            'area' => $area,
            'area_label' => $this->areas[$area]['label'],
            'index_aed' => $index,
            'permitted_increase_pct' => $pct,
            'permitted_new_rent_aed' => $cap,
            'proposed_is_within_band' => $proposed <= $cap + 0.005,
            'disclaimer' => $this->config['disclaimer'],
        );
        $this->audit('lookup_rera_band', 200, array(
            'area' => $area,
            'within' => $payload['proposed_is_within_band'],
            'citation_id' => $payload['citation_id'],
        ));
        $this->send(200, $payload);
    }

    private function lookupEjari(array $body): void
    {
        $id = isset($body['ejari_id']) ? strtoupper(trim((string) $body['ejari_id'])) : '';
        if ($id === '') {
            $this->send(400, array('error' => 'ejari_id_required'));
            return;
        }
        if (!isset($this->ejari[$id])) {
            $payload = array(
                'ejari_id' => $id,
                'found' => false,
                'invented' => false,
                'disclaimer' => $this->config['disclaimer'],
            );
            $payload = $this->withPackCitation($payload);
            $this->audit('lookup_ejari', 200, array('ejari_id' => $id, 'found' => false));
            $this->send(200, $payload);
            return;
        }
        $row = $this->ejari[$id];
        $payload = array(
            'ejari_id' => $id,
            'found' => true,
            'invented' => false,
            'area' => $row['area'],
            'annual_rent_aed' => $row['annual_rent_aed'],
            'start' => $row['start'],
            'end' => $row['end'],
            'status' => $row['status'],
            'source' => $this->config['pack_id'],
            'disclaimer' => $this->config['disclaimer'],
        );
        $payload = $this->withPackCitation($payload);
        $this->audit('lookup_ejari', 200, array('ejari_id' => $id, 'found' => true));
        $this->send(200, $payload);
    }

    private function submitQueue(array $body): void
    {
        // Confirmation and credential checks already enforced by HaqqLinePolicy.
        $item = array(
            'id' => $this->nextId('RDC-SANDBOX'),
            'status' => 'pending_human',
            'packet' => isset($body['packet']) && is_array($body['packet']) ? $body['packet'] : array(),
            'created_at' => gmdate('c'),
        );
        $this->appendJsonl($this->dataDir() . '/queue.jsonl', $item);
        $this->audit('submit_to_human_queue', 200, array('id' => $item['id'], 'status' => 'pending_human'));
        $this->send(200, $item);
    }

    private function escalate(array $body): void
    {
        $reason = isset($body['reason']) ? (string) $body['reason'] : 'unspecified';
        $item = array(
            'id' => $this->nextId('ESC-SANDBOX'),
            'status' => 'pending_human',
            'reason' => $reason,
            'created_at' => gmdate('c'),
        );
        $this->appendJsonl($this->dataDir() . '/escalations.jsonl', $item);
        $this->audit('escalate_human', 200, array('id' => $item['id']));
        $this->send(200, $item);
    }

    private function permittedIncreasePct(float $current, float $index): int
    {
        $gap = ($index - $current) / $current;
        if ($gap < 0.10) {
            return 0;
        }
        if ($gap < 0.20) {
            return 5;
        }
        if ($gap < 0.30) {
            return 10;
        }
        if ($gap < 0.40) {
            return 15;
        }
        return 20;
    }

    private function elevenLabsWebhook(): void
    {
        $secret = $this->webhookSecret();
        if ($secret === '') {
            $this->send(503, array('error' => 'webhook_secret_missing'));
            return;
        }
        $header = isset($_SERVER['HTTP_ELEVENLABS_SIGNATURE']) ? (string) $_SERVER['HTTP_ELEVENLABS_SIGNATURE'] : '';
        if (!$this->verifyElevenLabsSignature($this->rawInput, $header, $secret)) {
            $this->send(401, array('error' => 'invalid_signature'));
            return;
        }
        $event = json_decode($this->rawInput, true);
        if (!is_array($event)) {
            $this->send(400, array('error' => 'invalid_json'));
            return;
        }
        $type = isset($event['type']) ? (string) $event['type'] : '';
        $data = isset($event['data']) && is_array($event['data']) ? $event['data'] : array();
        $conversationId = isset($data['conversation_id']) ? (string) $data['conversation_id'] : '';
        $stored = array(
            'id' => $conversationId !== '' ? $conversationId : $this->nextId('CALL'),
            'type' => $type,
            'agent_id' => isset($data['agent_id']) ? $data['agent_id'] : null,
            'status' => isset($data['status']) ? $data['status'] : null,
            'transcript' => isset($data['transcript']) ? $data['transcript'] : array(),
            'analysis' => isset($data['analysis']) ? $data['analysis'] : null,
            'received_at' => gmdate('c'),
        );
        $this->appendJsonl($this->dataDir() . '/conversations.jsonl', $stored);
        $this->audit('post_call_transcription', 200, array(
            'conversation_id' => $stored['id'],
            'type' => $type,
        ));
        $this->send(200, array('received' => true, 'id' => $stored['id']));
    }

    private function webhookSecret(): string
    {
        $file = $this->dataDir() . '/elevenlabs_webhook.secret';
        if (!is_file($file)) {
            return '';
        }
        $raw = file_get_contents($file);
        return is_string($raw) ? trim($raw) : '';
    }

    private function verifyElevenLabsSignature(string $rawBody, string $sigHeader, string $secret): bool
    {
        if ($sigHeader === '' || $secret === '') {
            return false;
        }
        $timestamp = null;
        $signature = null;
        foreach (explode(',', $sigHeader) as $part) {
            $part = trim($part);
            if (strpos($part, 't=') === 0) {
                $timestamp = substr($part, 2);
            } elseif (strpos($part, 'v0=') === 0) {
                $signature = $part;
            }
        }
        if ($timestamp === null || $signature === null || !ctype_digit($timestamp)) {
            return false;
        }
        if (abs(time() - (int) $timestamp) > 30 * 60) {
            return false;
        }
        $digest = 'v0=' . hash_hmac('sha256', $timestamp . '.' . $rawBody, $secret);
        return hash_equals($digest, $signature);
    }

    private function jsonBody(): array
    {
        $raw = $this->rawInput;
        if (trim($raw) === '') {
            return array();
        }
        $data = json_decode($raw, true);
        return is_array($data) ? $data : array();
    }

    private function readJsonlTail(string $file, int $limit): array
    {
        if (!is_file($file)) {
            return array();
        }
        $lines = file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if ($lines === false) {
            return array();
        }
        $slice = array_slice($lines, -1 * $limit);
        $out = array();
        foreach ($slice as $line) {
            $row = json_decode($line, true);
            if (is_array($row)) {
                $out[] = $row;
            }
        }
        return $out;
    }

    /** @param array $payload */
    private function withPackCitation(array $payload): array
    {
        $payload['pack_id'] = $this->config['pack_id'];
        $payload['pack_version'] = isset($this->config['pack_version']) ? $this->config['pack_version'] : null;
        $payload['citation_id'] = isset($this->config['citation_id'])
            ? $this->config['citation_id']
            : $this->config['pack_id'];
        return $payload;
    }

    private function send(int $code, $payload): void
    {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
        header('X-Robots-Tag: noindex');
        header('Access-Control-Allow-Origin: https://haqqline.excellonit.net');
        header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Api-Key, X-HaqqLine-Workflow-Node');
        header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
        if ($payload === null) {
            return;
        }
        echo json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    }

    private function audit(string $tool, int $status, array $result): void
    {
        $entry = array(
            'id' => $this->nextId('AUD'),
            'tool' => $tool,
            'status' => $status,
            'result' => $result,
            'timestamp' => gmdate('c'),
        );
        $this->appendJsonl($this->dataDir() . '/audit.jsonl', $entry);
    }

    private function readAuditTail(int $limit): array
    {
        $file = $this->dataDir() . '/audit.jsonl';
        if (!is_file($file)) {
            return array();
        }
        $lines = file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if ($lines === false) {
            return array();
        }
        $slice = array_slice($lines, -1 * $limit);
        $out = array();
        foreach ($slice as $line) {
            $row = json_decode($line, true);
            if (is_array($row)) {
                $out[] = $row;
            }
        }
        return $out;
    }

    private function appendJsonl(string $file, array $row): void
    {
        $fh = fopen($file, 'ab');
        if ($fh === false) {
            return;
        }
        flock($fh, LOCK_EX);
        fwrite($fh, json_encode($row, JSON_UNESCAPED_SLASHES) . "\n");
        flock($fh, LOCK_UN);
        fclose($fh);
    }

    private function nextId(string $prefix): string
    {
        try {
            $hex = bin2hex(random_bytes(4));
        } catch (Exception $e) {
            $hex = substr(md5((string) microtime(true)), 0, 8);
        }
        return $prefix . '-' . strtoupper($hex);
    }

    private function dataDir(): string
    {
        $dir = dirname($this->root) . '/data';
        if (!is_dir($dir)) {
            mkdir($dir, 0700, true);
        }
        return $dir;
    }

    private function readJson(string $path): array
    {
        $raw = file_get_contents($path);
        $data = is_string($raw) ? json_decode($raw, true) : null;
        return is_array($data) ? $data : array();
    }
}
