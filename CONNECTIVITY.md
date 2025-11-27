# Connectivity Quick Guide

This document helps you interpret the app + validator connectivity diagnostics fast.

## 1. Variants
| Variant | Meaning | When Used |
| ------- | ------- | --------- |
| env | Honors current env vars + CA overrides | First pass shows how your environment behaves |
| system | Ignores REQUESTS_CA_BUNDLE / SSL_CERT_FILE; uses system trust (certifi_win32 on Windows) | Detects if custom bundle is breaking trust |
| insecure | Disables verification (only when explicitly toggled) | Confirms pure network reachability when TLS fails |

## 2. Classifications
| Class | Description | Common Fix |
| ----- | ----------- | ---------- |
| ssl | Certificate chain / interception issue | Remove bad override; append corporate root certs |
| timeout | Slow or blocked path | Increase timeout/backoff; check VPN/firewall |
| proxy | Proxy misconfig / blocked CONNECT | Fix HTTP(S)_PROXY / NO_PROXY values |
| dns | Name cannot resolve | Flush DNS; fix hosts file / corporate DNS |
| network | Connection reset/refused | Local firewall / endpoint issue |
| other | Uncategorized error | Inspect detail text |

## 3. Key Environment Vars
| Variable | Default | Purpose |
| -------- | ------- | ------- |
| CONNECTION_TEST_TIMEOUT | 5 | Seconds per HTTP attempt |
| CONNECTION_TEST_RETRIES | 2 | Extra attempts per variant |
| CONNECTION_TEST_BACKOFF | 0.5 | Initial exponential backoff base |
| AUTO_OFFLINE_FAIL_THRESHOLD | 3 | Fail streak before auto offline |
| ALLOW_INSECURE_SSL | (unset) | If true, insecure variant allowed |

## 4. Typical Diagnostic Patterns
| Pattern | Interpretation | Action |
| ------- | ------------- | ------ |
| env: ssl fails; system: OK | Your override bundle invalid | Remove REQUESTS_CA_BUNDLE or fix bundle |
| env/system: ssl fails; insecure: OK | Missing corporate root CA | Append full chain to certifi bundle or install to store |
| env/system: timeouts | Network/Firewall slowness | Higher timeout; network trace; allowlist domains |
| proxy classified errors only | Proxy blocking CONNECT | Validate proxy host/port; adjust NO_PROXY |

## 5. Auto Offline Degrade
After N consecutive connection failures (threshold configurable) auto mode switches to offline and records the reason in `last_offline_reason`.

## 6. Provider Self-Test
Run: `python -X utf8 tools/self_test.py` → JSON reporting provider statuses, latency or skip reasons.

## 7. Quick Remediation Flow
1. Run validator: `python -X utf8 tools/validate_project.py`
2. Check `summary.likely_root_cause`
3. Compare variant differences
4. Apply fix from table above
5. Re-run validator until env variant matches system

## 8. Safe Corporate CA Append
```
python - <<'PY'
import certifi, pathlib
bundle = pathlib.Path(certifi.where())
print('Bundle:', bundle)
# Append corporate_root.pem to bundle (make backup first)
PY
```
Append (do NOT replace) PEM blocks, then re-run tests.

## 9. Glossary
- Variant: Trust configuration mode tested.
- Classification: Category assigned to a failure.
- Fail Streak: Consecutive failed test cycles triggering offline degrade.

---
For deeper detail see `TROUBLESHOOTING.md`.
