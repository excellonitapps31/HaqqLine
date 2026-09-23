<?php
declare(strict_types=1);

/**
 * Phase 11 SMS: transactional receipts + inbound STATUS/STOP/HELP.
 * Never a second agent brain. Dry-run writes sms-outbox.jsonl when not connected.
 */
final class HaqqLineSms
{
    /** @var string */
    private $dataDir;
    /** @var string */
    private $publicRoot;

    public function __construct(string $apiRoot)
    {
        $this->publicRoot = dirname(dirname($apiRoot));
        $this->dataDir = $this->publicRoot . '/api/data';
        if (!is_dir($this->dataDir)) {
            @mkdir($this->dataDir, 0770, true);
        }
    }

    /** @return array */
    public function config(): array
    {
        $path = $this->publicRoot . '/sms.json';
        if (!is_file($path)) {
            return array('connected' => false, 'phone_number' => '');
        }
        $raw = json_decode((string) file_get_contents($path), true);
        return is_array($raw) ? $raw : array('connected' => false);
    }

    public function isOptedOut(string $e164): bool
    {
        $file = $this->dataDir . '/sms-optout.jsonl';
        if (!is_file($file)) {
            return false;
        }
        $lines = file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if ($lines === false) {
            return false;
        }
        $norm = $this->normalizePhone($e164);
        $out = false;
        foreach ($lines as $line) {
            $row = json_decode($line, true);
            if (!is_array($row) || !isset($row['phone'])) {
                continue;
            }
            if ($this->normalizePhone((string) $row['phone']) !== $norm) {
                continue;
            }
            if (isset($row['action']) && $row['action'] === 'start') {
                $out = false;
            } else {
                $out = true;
            }
        }
        return $out;
    }

    /**
     * @param array $case
     * @return array{sent:bool, dry_run:bool, skipped:?string, body:?string}
     */
    public function notifyEvent(string $event, array $case, ?string $to): array
    {
        if ($event !== 'filing_queued' && $event !== 'escalated') {
            return array('sent' => false, 'dry_run' => true, 'skipped' => 'unknown_event', 'body' => null);
        }
        $to = $to !== null ? trim($to) : '';
        if ($to === '') {
            return array('sent' => false, 'dry_run' => true, 'skipped' => 'no_recipient', 'body' => null);
        }
        if ($this->isOptedOut($to)) {
            $this->appendOutbox(array(
                'event' => $event,
                'to' => $to,
                'case_id' => isset($case['id']) ? $case['id'] : null,
                'status' => 'skipped',
                'skipped' => 'opted_out',
                'dry_run' => true,
            ));
            return array('sent' => false, 'dry_run' => true, 'skipped' => 'opted_out', 'body' => null);
        }
        $caseId = isset($case['id']) ? (string) $case['id'] : '';
        $status = isset($case['status']) ? (string) $case['status'] : 'pending_human';
        if ($event === 'filing_queued') {
            $body = 'HaqqLine sandbox: filing queued. Case ' . $caseId . ' status ' . $status
                . '. Not a government service. Reply STOP to opt out. WhatsApp/web preferred for rights-check.';
        } else {
            $body = 'HaqqLine sandbox: escalated to human. Case ' . $caseId . ' status ' . $status
                . '. Not a government service. Reply STOP to opt out.';
        }
        return $this->sendOrOutbox($event, $to, $caseId, $body);
    }

    /**
     * Handle Twilio inbound SMS. Returns TwiML string.
     * @param array $params
     */
    public function handleInbound(array $params, HaqqLineCaseStore $cases): string
    {
        $from = isset($params['From']) ? trim((string) $params['From']) : '';
        $rawBody = isset($params['Body']) ? trim((string) $params['Body']) : '';
        $text = strtoupper(preg_replace('/\s+/', ' ', $rawBody) ?? '');
        $this->appendJsonl($this->dataDir . '/sms-inbound.jsonl', array(
            'from' => $from,
            'body' => $rawBody,
            'received_at' => gmdate('c'),
        ));

        if ($text === 'STOP' || $text === 'STOP ALL' || $text === 'UNSUBSCRIBE' || $text === 'CANCEL') {
            $this->appendJsonl($this->dataDir . '/sms-optout.jsonl', array(
                'phone' => $from,
                'action' => 'stop',
                'at' => gmdate('c'),
            ));
            return $this->twiml('HaqqLine sandbox: you are unsubscribed. No further SMS. Use Talk or WhatsApp on haqqline.excellonit.net.');
        }
        if ($text === 'START' || $text === 'UNSTOP') {
            $this->appendJsonl($this->dataDir . '/sms-optout.jsonl', array(
                'phone' => $from,
                'action' => 'start',
                'at' => gmdate('c'),
            ));
            return $this->twiml('HaqqLine sandbox: SMS receipts re-enabled. Not a government service.');
        }
        if ($text === 'HELP' || $text === 'INFO') {
            return $this->twiml($this->helpText());
        }
        if (preg_match('/^STATUS\s+(\S+)/i', $rawBody, $m)) {
            $id = $m[1];
            $case = $cases->get($id);
            if ($case === null) {
                return $this->twiml('HaqqLine sandbox: unknown case id. ' . $this->helpText());
            }
            return $this->twiml(
                'HaqqLine sandbox: case ' . $case['id'] . ' status ' . $case['status']
                . '. Not a government service. Full rights-check: Talk or WhatsApp on haqqline.excellonit.net.'
            );
        }
        return $this->twiml($this->helpText());
    }

    public function helpText(): string
    {
        return 'HaqqLine sandbox SMS: STATUS <case_id>, STOP, HELP. '
            . 'No rights-check over SMS. Continue on WhatsApp or Talk: https://haqqline.excellonit.net/ '
            . 'Not a government service.';
    }

    /**
     * @return array{sent:bool, dry_run:bool, skipped:?string, body:?string}
     */
    private function sendOrOutbox(string $event, string $to, string $caseId, string $body): array
    {
        $cfg = $this->config();
        $connected = !empty($cfg['connected']) && !empty($cfg['phone_number']);
        $sid = getenv('TWILIO_ACCOUNT_SID') ?: '';
        $token = getenv('TWILIO_AUTH_TOKEN') ?: '';
        $from = isset($cfg['phone_number']) ? (string) $cfg['phone_number'] : '';
        $dry = !$connected || $sid === '' || $token === '' || $from === '' || getenv('HAQQLINE_SMS_DRY_RUN') === '1';

        $row = array(
            'event' => $event,
            'to' => $to,
            'from' => $from,
            'case_id' => $caseId,
            'body' => $body,
            'status' => $dry ? 'outbox' : 'queued_send',
            'dry_run' => $dry,
            'timestamp' => gmdate('c'),
        );

        if (!$dry) {
            $ok = $this->twilioSend($sid, $token, $from, $to, $body);
            $row['status'] = $ok ? 'sent' : 'send_failed';
            $row['dry_run'] = false;
            $this->appendOutbox($row);
            return array('sent' => $ok, 'dry_run' => false, 'skipped' => $ok ? null : 'send_failed', 'body' => $body);
        }

        $this->appendOutbox($row);
        return array('sent' => false, 'dry_run' => true, 'skipped' => null, 'body' => $body);
    }

    private function twilioSend(string $sid, string $token, string $from, string $to, string $body): bool
    {
        $url = 'https://api.twilio.com/2010-04-01/Accounts/' . rawurlencode($sid) . '/Messages.json';
        $post = http_build_query(array('From' => $from, 'To' => $to, 'Body' => $body));
        $ctx = stream_context_create(array(
            'http' => array(
                'method' => 'POST',
                'header' => "Authorization: Basic " . base64_encode($sid . ':' . $token) . "\r\n"
                    . "Content-Type: application/x-www-form-urlencoded\r\n",
                'content' => $post,
                'timeout' => 20,
                'ignore_errors' => true,
            ),
        ));
        $raw = @file_get_contents($url, false, $ctx);
        if (!is_string($raw) || $raw === '') {
            return false;
        }
        $decoded = json_decode($raw, true);
        return is_array($decoded) && isset($decoded['sid']);
    }

    /** @param array $row */
    private function appendOutbox(array $row): void
    {
        if (!isset($row['timestamp'])) {
            $row['timestamp'] = gmdate('c');
        }
        $this->appendJsonl($this->dataDir . '/sms-outbox.jsonl', $row);
    }

    private function twiml(string $message): string
    {
        $esc = htmlspecialchars($message, ENT_XML1 | ENT_QUOTES, 'UTF-8');
        return '<?xml version="1.0" encoding="UTF-8"?><Response><Message>' . $esc . '</Message></Response>';
    }

    private function normalizePhone(string $phone): string
    {
        return preg_replace('/[^\d+]/', '', $phone) ?? $phone;
    }

    /** @param array $row */
    private function appendJsonl(string $file, array $row): void
    {
        $fh = fopen($file, 'ab');
        if ($fh === false) {
            return;
        }
        flock($fh, LOCK_EX);
        fwrite($fh, json_encode($row, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n");
        flock($fh, LOCK_UN);
        fclose($fh);
    }

    /**
     * Validate Twilio request signature when auth token is configured.
     */
    public function verifyTwilioSignature(string $url, array $params, string $signature, string $authToken): bool
    {
        if ($authToken === '' || $signature === '') {
            return false;
        }
        ksort($params);
        $data = $url;
        foreach ($params as $k => $v) {
            $data .= $k . $v;
        }
        $expected = base64_encode(hash_hmac('sha1', $data, $authToken, true));
        return hash_equals($expected, $signature);
    }
}
