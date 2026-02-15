# Analyst Reason Codes (EITL Feedback Taxonomy)

Use these codes in `data/feedback/labels.csv` to standardize analyst feedback.

## Labels
- MALICIOUS
- BENIGN
- UNCLEAR

## Reason Codes

### Benign operational causes
- BENIGN_SCHEDULED_TASK
- BENIGN_ADMIN_ACTIVITY
- BENIGN_SOFTWARE_INSTALL
- BENIGN_IT_AUTOMATION
- BENIGN_BACKUP_SECURITY_TOOL
- BENIGN_USER_PRODUCTIVITY

### Data / visibility issues
- DATA_GAP_MISSING_CONTEXT
- DATA_MAPPING_ERROR
- DATA_HOST_ROLE_WRONG
- DATA_TIME_WINDOW_MISMATCH

### Suspicious but not confirmed
- SUSPICIOUS_NEEDS_HUNT
- SUSPICIOUS_RARE_PARENT_CHILD
- SUSPICIOUS_RARE_TRANSITIONS
- SUSPICIOUS_NEW_BINARY
- SUSPICIOUS_NETWORK_ANOMALY

### Confirmed malicious technique (MITRE-aligned)
- MAL_EXECUTION_LOLBIN
- MAL_CREDENTIAL_ACCESS
- MAL_LATERAL_MOVEMENT
- MAL_PERSISTENCE
- MAL_DEFENSE_EVASION
- MAL_C2_BEACONING
- MAL_EXFILTRATION

### False positive pattern identifiers (for allowlisting)
- FP_KNOWN_TOOL_<TOOLNAME>
- FP_VENDOR_AGENT_<VENDOR>

## CSV schema
Minimum: unit_id,label,reason_code
Recommended: notes,analyst,timestamp,mitre_technique,confidence,related_case_id
