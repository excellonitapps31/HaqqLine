<?php
declare(strict_types=1);

/**
 * Append-only case spine: create, validated status transitions, conversation link.
 * Events live in cases.jsonl; get() folds to the latest snapshot per id.
 */
final class HaqqLineCaseStore
{
    public const STATUS_PENDING = 'pending_human';
    public const STATUS_IN_REVIEW = 'in_review';
    public const STATUS_CLOSED = 'closed';
    public const STATUS_RETURNED = 'returned';

    /** @var array<string, array<int, string>> */
    private static $transitions = array(
        self::STATUS_PENDING => array(self::STATUS_IN_REVIEW),
        self::STATUS_IN_REVIEW => array(self::STATUS_CLOSED, self::STATUS_RETURNED),
        self::STATUS_RETURNED => array(self::STATUS_IN_REVIEW),
        self::STATUS_CLOSED => array(),
    );

    /** @var string */
    private $dir;

    public function __construct(string $dataDir)
    {
        $this->dir = $dataDir;
        if (!is_dir($this->dir)) {
            @mkdir($this->dir, 0770, true);
        }
    }

    /**
     * @param array $extra
     * @return array
     */
    public function create(string $type, array $extra = array()): array
    {
        if ($type !== 'filing' && $type !== 'escalation') {
            throw new InvalidArgumentException('invalid_case_type');
        }
        $now = gmdate('c');
        $case = array(
            'id' => $this->nextId($type === 'filing' ? 'CASE-F' : 'CASE-E'),
            'type' => $type,
            'status' => self::STATUS_PENDING,
            'pack_id' => isset($extra['pack_id']) ? $extra['pack_id'] : null,
            'pack_version' => isset($extra['pack_version']) ? $extra['pack_version'] : null,
            'citation_id' => isset($extra['citation_id']) ? $extra['citation_id'] : null,
            'conversation_id' => isset($extra['conversation_id']) ? $extra['conversation_id'] : null,
            'channel' => isset($extra['channel']) ? $extra['channel'] : null,
            'packet' => isset($extra['packet']) && is_array($extra['packet']) ? $extra['packet'] : null,
            'reason' => isset($extra['reason']) ? $extra['reason'] : null,
            'created_at' => $now,
            'updated_at' => $now,
            'event' => 'created',
        );
        $this->appendEvent($case);
        return $this->publicView($case);
    }

    public function get(string $id): ?array
    {
        $snap = $this->latestSnapshot($id);
        return $snap === null ? null : $this->publicView($snap);
    }

    /**
     * @return array{ok:bool, case:?array, error:?string}
     */
    public function transition(string $id, string $toStatus): array
    {
        $fh = $this->openExclusive();
        try {
            $snap = $this->latestSnapshotLocked($id);
            if ($snap === null) {
                return array('ok' => false, 'case' => null, 'error' => 'not_found');
            }
            $from = (string) $snap['status'];
            $allowed = isset(self::$transitions[$from]) ? self::$transitions[$from] : array();
            if (!in_array($toStatus, $allowed, true)) {
                return array('ok' => false, 'case' => null, 'error' => 'illegal_transition');
            }
            $snap['status'] = $toStatus;
            $snap['updated_at'] = gmdate('c');
            $snap['event'] = 'status_changed';
            $snap['from_status'] = $from;
            $this->appendEventLocked($fh, $snap);
            return array('ok' => true, 'case' => $this->publicView($snap), 'error' => null);
        } finally {
            flock($fh, LOCK_UN);
            fclose($fh);
        }
    }

    /**
     * Attach a conversation id to an existing case, or create an escalation case.
     * @return array
     */
    public function linkConversation(string $conversationId, ?string $caseId = null, ?string $channel = null): array
    {
        $fh = $this->openExclusive();
        try {
            if ($caseId !== null && $caseId !== '') {
                $snap = $this->latestSnapshotLocked($caseId);
                if ($snap === null) {
                    return array();
                }
                $snap['conversation_id'] = $conversationId;
                if ($channel !== null && $channel !== '') {
                    $snap['channel'] = $channel;
                }
                $snap['updated_at'] = gmdate('c');
                $snap['event'] = 'conversation_linked';
                $this->appendEventLocked($fh, $snap);
                return $this->publicView($snap);
            }
            // Prefer most recent pending case without a conversation.
            $all = $this->foldAllLocked();
            $candidate = null;
            foreach (array_reverse($all) as $row) {
                if (
                    $row['status'] === self::STATUS_PENDING
                    && (empty($row['conversation_id']) || $row['conversation_id'] === null)
                ) {
                    $candidate = $row;
                    break;
                }
            }
            if ($candidate !== null) {
                $candidate['conversation_id'] = $conversationId;
                if ($channel !== null && $channel !== '') {
                    $candidate['channel'] = $channel;
                }
                $candidate['updated_at'] = gmdate('c');
                $candidate['event'] = 'conversation_linked';
                $this->appendEventLocked($fh, $candidate);
                return $this->publicView($candidate);
            }
            $now = gmdate('c');
            $case = array(
                'id' => $this->nextId('CASE-E'),
                'type' => 'escalation',
                'status' => self::STATUS_PENDING,
                'pack_id' => null,
                'pack_version' => null,
                'citation_id' => null,
                'conversation_id' => $conversationId,
                'channel' => $channel,
                'packet' => null,
                'reason' => 'post_call_without_prior_case',
                'created_at' => $now,
                'updated_at' => $now,
                'event' => 'created',
            );
            $this->appendEventLocked($fh, $case);
            return $this->publicView($case);
        } finally {
            flock($fh, LOCK_UN);
            fclose($fh);
        }
    }

    /** @return array<int, array> */
    public function eventsFor(string $id): array
    {
        $path = $this->file();
        if (!is_file($path)) {
            return array();
        }
        $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if ($lines === false) {
            return array();
        }
        $out = array();
        foreach ($lines as $line) {
            $row = json_decode($line, true);
            if (is_array($row) && isset($row['id']) && $row['id'] === $id) {
                $out[] = $row;
            }
        }
        return $out;
    }

    /** @param array $case */
    private function publicView(array $case): array
    {
        return array(
            'id' => $case['id'],
            'type' => $case['type'],
            'status' => $case['status'],
            'pack_id' => isset($case['pack_id']) ? $case['pack_id'] : null,
            'pack_version' => isset($case['pack_version']) ? $case['pack_version'] : null,
            'citation_id' => isset($case['citation_id']) ? $case['citation_id'] : null,
            'conversation_id' => isset($case['conversation_id']) ? $case['conversation_id'] : null,
            'channel' => isset($case['channel']) ? $case['channel'] : null,
            'packet' => isset($case['packet']) ? $case['packet'] : null,
            'reason' => isset($case['reason']) ? $case['reason'] : null,
            'created_at' => $case['created_at'],
            'updated_at' => $case['updated_at'],
        );
    }

    private function file(): string
    {
        return $this->dir . '/cases.jsonl';
    }

    /** @return resource */
    private function openExclusive()
    {
        $path = $this->file();
        $fh = fopen($path, 'c+');
        if ($fh === false) {
            throw new RuntimeException('case_store_unavailable');
        }
        flock($fh, LOCK_EX);
        return $fh;
    }

    /** @param array $case */
    private function appendEvent(array $case): void
    {
        $fh = $this->openExclusive();
        try {
            $this->appendEventLocked($fh, $case);
        } finally {
            flock($fh, LOCK_UN);
            fclose($fh);
        }
    }

    /**
     * @param resource $fh
     * @param array $case
     */
    private function appendEventLocked($fh, array $case): void
    {
        fseek($fh, 0, SEEK_END);
        fwrite($fh, json_encode($case, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n");
        fflush($fh);
    }

    private function latestSnapshot(string $id): ?array
    {
        $fh = $this->openExclusive();
        try {
            return $this->latestSnapshotLocked($id);
        } finally {
            flock($fh, LOCK_UN);
            fclose($fh);
        }
    }

    private function latestSnapshotLocked(string $id): ?array
    {
        $all = $this->foldAllLocked();
        return isset($all[$id]) ? $all[$id] : null;
    }

    /** @return array<string, array> */
    private function foldAllLocked(): array
    {
        $path = $this->file();
        if (!is_file($path) || filesize($path) === 0) {
            return array();
        }
        $raw = file_get_contents($path);
        if (!is_string($raw) || $raw === '') {
            return array();
        }
        $out = array();
        foreach (explode("\n", $raw) as $line) {
            $line = trim($line);
            if ($line === '') {
                continue;
            }
            $row = json_decode($line, true);
            if (!is_array($row) || !isset($row['id'])) {
                continue;
            }
            $id = (string) $row['id'];
            if (!isset($out[$id])) {
                $out[$id] = $row;
                continue;
            }
            // Merge status / conversation from later events; keep created_at.
            $prev = $out[$id];
            if (isset($row['status'])) {
                $prev['status'] = $row['status'];
            }
            if (array_key_exists('conversation_id', $row)) {
                $prev['conversation_id'] = $row['conversation_id'];
            }
            if (array_key_exists('channel', $row)) {
                $prev['channel'] = $row['channel'];
            }
            if (isset($row['updated_at'])) {
                $prev['updated_at'] = $row['updated_at'];
            }
            if (isset($row['event'])) {
                $prev['event'] = $row['event'];
            }
            $out[$id] = $prev;
        }
        return $out;
    }

    private function nextId(string $prefix): string
    {
        try {
            $rand = bin2hex(random_bytes(3));
        } catch (Exception $e) {
            $rand = substr(sha1(uniqid('', true)), 0, 6);
        }
        return $prefix . '-' . gmdate('YmdHis') . '-' . $rand;
    }
}
