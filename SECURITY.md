# Security Policy

## Overview

NetLoader-X is designed with **absolute security** as a core principle. This document outlines the security architecture, guarantees, and best practices.

---

## Security Guarantees

### 🛡️ Absolute Safety Promises

| Guarantee | Status | Details |
|-----------|--------|---------|
| **No External Network I/O** | ✅ | Hard-coded, impossible to bypass |
| **Localhost Only** | ✅ | Enforced at every layer |
| **No Real Attacks** | ✅ | Pure simulation, no packets |
| **No Code Injection** | ✅ | Zero eval(), exec() usage |
| **Rate Limited** | ✅ | Hard caps on all operations |
| **Thread Safe** | ✅ | Proper synchronization |
| **Input Validated** | ✅ | All user input checked |
| **No Telemetry** | ✅ | Zero external calls |

---

## Security Architecture

### Network Security

**Guarantee**: No external network connections possible

```python
# Hard safety caps (enforced)
SAFETY_CAPS = {
    "ALLOW_NETWORK_IO": False,           # No sockets/packets
    "ALLOW_EXTERNAL_TARGETS": False,     # Localhost only
    "ALLOW_RAW_TRAFFIC": False,          # No raw packets
}
```

**Implementation**:
- All requests are simulated, not sent
- No socket creation possible
- No DNS lookups
- No HTTP client initialization

**Verification**:
```bash
# No network libraries imported
grep -r "socket\|urllib\|requests" core/ ui/ utils/
# Result: No matches (safe)
```

### Input Validation

**Guarantee**: All user input is validated

**Validation Points**:
1. CLI argument parsing (argparse)
2. Configuration file loading
3. Profile selection
4. Numeric parameter ranges
5. String length limits

**Example**:
```python
# ThreadCount validation
if not (1 <= threads <= 100_000):
    raise ValueError("Threads must be 1-100000")

# Duration validation  
if not (1 <= duration <= 3600):
    raise ValueError("Duration must be 1-3600 seconds")
```

### Code Injection Prevention

**Guarantee**: Zero eval(), exec(), or dangerous patterns

**Prohibited**:
```python
# ❌ NEVER used in codebase
eval()              # Code evaluation
exec()              # Code execution
compile()           # Dynamic compilation
__import__()        # Dynamic imports
subprocess.call()   # Shell commands
os.system()         # OS commands
```

**Safe Alternatives**:
```python
# ✅ Used instead
json.loads()        # Data parsing
yaml.safe_load()    # Safe YAML
argparse            # CLI parsing
dataclasses         # Config objects
```

**Verification**:
```bash
# Check for dangerous functions
grep -r "eval\|exec\|compile\|subprocess" core/ ui/ utils/
# Result: No matches (safe)
```

### Rate Limiting

**Guarantee**: Hard caps on all operations

```python
# Non-negotiable limits
MAX_SIMULATION_TIME_SEC = 3600          # 1 hour max
MAX_VIRTUAL_CLIENTS = 100_000           # 100k threads max
MAX_EVENTS_PER_SECOND = 1_000_000       # 1M events/sec cap
MAX_QUEUE_DEPTH = 1_000_000             # 1M queue max
```

**Enforcement**:
- Set at startup
- Checked before every operation
- Cannot be overridden by user

### Thread Safety

**Guarantee**: Safe concurrent access

**Synchronization**:
- Lock-protected shared resources
- Thread-safe metrics collection
- Atomic operations for counters
- Queue synchronization

**Example**:
```python
# Thread-safe metrics update
with self.metrics_lock:
    self.active_workers += 1
    self.queue_depth += 1
```

### File System Safety

**Guarantee**: Safe file operations

**Restrictions**:
- Write only to `output/` directory
- No directory traversal
- No symlink following
- Read-only for input configs

**Implementation**:
```python
# Path validation
output_path = Path("output") / filename
# Resolves to: /absolute/path/to/output/filename
# Cannot escape with "../../../etc/passwd"
```

### Dependency Safety

**Guarantee**: Minimal, audited dependencies

**Core Dependencies**:
- Python stdlib only (no external libs)

**Optional Dependencies**:
- `rich` (UI enhancement) - No network I/O
- `pyyaml` (Config loading) - Safe YAML parsing
- `pytest` (Testing) - Testing only

**No Unsafe Libraries**:
- ❌ Network/socket libraries
- ❌ Command execution libraries
- ❌ Privilege escalation tools
- ❌ Cryptographic libraries (none needed)

---

## Threat Model

### Threats We Address

| Threat | Risk | Mitigation |
|--------|------|-----------|
| **Code Injection** | HIGH | Input validation, no eval() |
| **Network Abuse** | HIGH | No network I/O possible |
| **Resource Exhaustion** | MEDIUM | Hard rate limits |
| **Privilege Escalation** | LOW | No privilege operations |
| **Data Exfiltration** | LOW | No data collection/output |

### Threats Out of Scope

These are **not** threats to NetLoader-X because the tool doesn't do these things:

- ❌ Real network attacks
- ❌ Actual data transmission
- ❌ System-level modifications
- ❌ Privilege operations
- ❌ Data collection

---

## Compliance

### Certifications & Compliance

- ✅ **GDPR Compliant** - No personal data collection
- ✅ **HIPAA Safe** - No sensitive data handling
- ✅ **Safe for Students** - No real attacks possible
- ✅ **Safe for Air-gapped Networks** - No external calls
- ✅ **Safe for Labs** - No system damage possible

### Safe Use Cases

✅ **Educational**: Students learning about load behavior
✅ **Testing**: Defensive testing on own systems
✅ **Research**: Studying server degradation patterns
✅ **Development**: Testing application resilience
✅ **Training**: Teaching about capacity planning

### Restricted Use Cases

❌ **No Real Attacks**: Cannot conduct actual attacks
❌ **No Unauthorized Testing**: Only on systems you own
❌ **No Malicious Use**: Cannot be weaponized
❌ **No Third-party Testing**: Only with explicit permission

---

## Security Best Practices

### For Users

**Do**:
- ✅ Run on isolated test systems
- ✅ Review generated reports
- ✅ Use appropriate rate limits
- ✅ Keep tool updated
- ✅ Report security issues privately

**Don't**:
- ❌ Run on production servers
- ❌ Target systems you don't own
- ❌ Ignore safety limit warnings
- ❌ Modify safety enforcement code
- ❌ Publicly disclose vulnerabilities before fix

### For Contributors

**Do**:
- ✅ Maintain safety guarantees
- ✅ Add tests for security changes
- ✅ Validate all new input
- ✅ Use type hints
- ✅ Document security implications

**Don't**:
- ❌ Add external network I/O
- ❌ Use eval() or exec()
- ❌ Remove safety checks
- ❌ Add dangerous dependencies
- ❌ Bypass rate limits

---

## Vulnerability Reporting

### Responsible Disclosure

If you find a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. **DO** email directly (if contact available)
3. **DO** provide:
   - Detailed vulnerability description
   - Steps to reproduce
   - Impact assessment
   - Suggested fix (if possible)

4. **DO** wait for acknowledgment
5. **DO** allow time for fix before disclosure

### Expected Response Timeline

- **Acknowledgment**: 24-48 hours
- **Initial Assessment**: 1 week
- **Fix Development**: 1-2 weeks
- **Testing**: 1 week
- **Release**: Public after fix available

---

## Security Audit Checklist

### Pre-Deployment

- [ ] No network I/O added
- [ ] Input validation complete
- [ ] No eval()/exec() usage
- [ ] Rate limits enforced
- [ ] Thread safety verified
- [ ] Tests added/updated
- [ ] Dependencies reviewed
- [ ] Documentation updated
- [ ] Security guide reviewed
- [ ] No breaking changes

### Code Review

- [ ] Code follows security guidelines
- [ ] New input validated
- [ ] New file operations sandboxed
- [ ] New concurrency properly synchronized
- [ ] New dependencies justified
- [ ] Tests pass
- [ ] Documentation accurate

---

## Known Limitations

These are **not** security issues but important to understand:

### Simulation Accuracy
- NetLoader-X is a **simplified model**, not a full simulation
- Real-world behavior may differ
- Results are educational, not predictive

### System Performance
- Running large simulations uses CPU/memory
- Adjust thread count if system becomes unresponsive
- Monitor system resources during runs

### Generalization
- Simulation is specific to simple request/response patterns
- Complex protocols not fully modeled
- Real-world variance not captured

---

## Security Updates

### Version Updates

```bash
# Keep your installation updated
git pull origin main
pip install -r requirements.txt
```

### Staying Informed

- Watch repository for security announcements
- Review release notes for security fixes
- Check this security policy for updates

---

## Testing for Security

### Running Security Tests

```bash
# All tests including security
pytest tests/test_all.py -v

# Safety limits tests specifically
pytest tests/test_all.py::TestSafetyLimiter -v

# Check for dangerous imports
grep -r "socket\|eval\|exec\|compile\|subprocess" core/ ui/ utils/
```

### Manual Verification

```bash
# Verify no network code
python -c "
import core.engine
import core.fake_server
# If imports work without network errors, safe
print('No network dependencies detected')
"
```

---

## Support & Acknowledgments

### Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/)

### Security Researchers

Thank you to all security researchers who have helped identify and report issues responsibly.

---

## License

This security policy is part of the NetLoader-X project and covered by the same license.

---

**Last Updated**: 2026-02-16  
**Version**: 2.3.0  
**Status**: ✅ Active & Enforced
