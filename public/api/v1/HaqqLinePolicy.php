<?php
declare(strict_types=1);

/**
 * Server-side policy for HaqqLine tools.
 * The LLM may propose; this class decides what is executable.
 */
final class HaqqLinePolicy
{
    public const NODE_INTAKE = 'Intake';
    public const NODE_RULE_MATCH = 'RuleMatch';
    public const NODE_FILING = 'Filing';
    public const NODE_ESCALATE = 'Escalate';

    /** @var array<string, array<int, string>> */
    private static $allow = array(
        self::NODE_INTAKE => array('lookup_rera_band', 'lookup_ejari'),
        self::NODE_RULE_MATCH => array('lookup_rera_band', 'lookup_ejari', 'escalate_human'),
        self::NODE_FILING => array('lookup_rera_band', 'lookup_ejari', 'submit_to_human_queue'),
        self::NODE_ESCALATE => array('escalate_human'),
    );

    /** @var array<int, string> */
    private static $forbiddenKeys = array(
        'pin', 'password', 'otp', 'one_time_code', 'passcode', 'cvv', 'ssn',
    );

    /**
     * @param array $body
     * @return array{ok:bool, reason:?string, detail:?string}
     */
    public static function evaluate(string $tool, array $body, ?string $workflowNode): array
    {
        if ($tool === 'decide_case') {
            return self::deny('decide_case_forbidden', 'There is no decide_case tool; outcomes are human-only.');
        }

        $cred = self::findForbiddenCredentialKey($body);
        if ($cred !== null) {
            return self::deny('forbidden_credential_field', 'Request must not include ' . $cred);
        }

        if ($workflowNode !== null && $workflowNode !== '') {
            if (!isset(self::$allow[$workflowNode])) {
                return self::deny('unknown_workflow_node', 'Unknown workflow node: ' . $workflowNode);
            }
            if (!in_array($tool, self::$allow[$workflowNode], true)) {
                return self::deny(
                    'tool_not_allowed_for_node',
                    $tool . ' is not allowed in workflow node ' . $workflowNode
                );
            }
        }

        if ($tool === 'submit_to_human_queue') {
            if (!isset($body['caller_confirmed']) || $body['caller_confirmed'] !== true) {
                return self::deny('confirmation_required', 'submit_to_human_queue requires caller_confirmed: true');
            }
            if (isset($body['invented']) && $body['invented'] === true) {
                return self::deny('invent_index_forbidden', 'Filings must not invent an index');
            }
            if (isset($body['packet']) && is_array($body['packet'])) {
                $nested = self::findForbiddenCredentialKey($body['packet']);
                if ($nested !== null) {
                    return self::deny('forbidden_credential_field', 'Packet must not include ' . $nested);
                }
            }
        }

        return array('ok' => true, 'reason' => null, 'detail' => null);
    }

    /** @return array{ok:bool, reason:string, detail:string} */
    private static function deny(string $reason, string $detail): array
    {
        return array('ok' => false, 'reason' => $reason, 'detail' => $detail);
    }

    /** @param array $body */
    private static function findForbiddenCredentialKey(array $body): ?string
    {
        foreach ($body as $key => $value) {
            $lower = strtolower((string) $key);
            if (in_array($lower, self::$forbiddenKeys, true)) {
                return $lower;
            }
            if (is_array($value)) {
                $nested = self::findForbiddenCredentialKey($value);
                if ($nested !== null) {
                    return $nested;
                }
            }
        }
        return null;
    }

    /** @return array<string, array<int, string>> */
    public static function allowlist(): array
    {
        return self::$allow;
    }

    /** @return array<int, string> */
    public static function reasonCodes(): array
    {
        return array(
            'confirmation_required',
            'tool_not_allowed_for_node',
            'forbidden_credential_field',
            'decide_case_forbidden',
            'invent_index_forbidden',
            'unknown_workflow_node',
        );
    }
}
