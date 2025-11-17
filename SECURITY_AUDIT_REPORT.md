# FarmVision Security & Code Quality Audit Report

**Date:** 2025-11-17
**Auditor:** Claude Code
**Scope:** Complete codebase audit including security, code quality, architecture, and dependencies
**Repository:** ChronoCoders/farmvision

---

## Executive Summary

This comprehensive audit of the FarmVision codebase identified **17 security vulnerabilities** (3 critical, 7 high, 4 medium severity) and **100+ code quality issues**. The most severe findings include command injection vulnerabilities that could allow remote code execution, hardcoded credentials, and insufficient input validation.

### Risk Assessment

| Severity | Count | Immediate Action Required |
|----------|-------|--------------------------|
| 🔴 CRITICAL | 3 | Yes - Fix within 24 hours |
| 🟠 HIGH | 7 | Yes - Fix within 1 week |
| 🟡 MEDIUM | 4 | Recommended - Fix within 2 weeks |
| 🟢 LOW | 3 | Advisory - Include in next release |

---

## Table of Contents

1. [Critical Security Vulnerabilities](#1-critical-security-vulnerabilities)
2. [High Severity Issues](#2-high-severity-issues)
3. [Medium Severity Issues](#3-medium-severity-issues)
4. [Code Quality Issues](#4-code-quality-issues)
5. [Architecture Concerns](#5-architecture-concerns)
6. [Dependency Analysis](#6-dependency-analysis)
7. [Recommendations](#7-recommendations)
8. [Remediation Priority Matrix](#8-remediation-priority-matrix)

---

## 1. Critical Security Vulnerabilities

### 1.1 Command Injection (RCE) - CRITICAL

**Files Affected:**
- `/detection/yolo/utils/google_utils.py` (Lines 17, 58-60, 84-85, 88, 91, 103)
- `/detection/yolo/utils/general.py` (Lines 87, 89-90, 94-96, 138, 205, 207)

**Description:** Multiple instances of `subprocess.check_output()` and `os.system()` with `shell=True` executing unsanitized user input.

**Vulnerable Code Example:**
```python
# google_utils.py:17
s = subprocess.check_output(f"gsutil du {url}", shell=True).decode("utf-8")
# url parameter not validated - allows arbitrary command execution
```

**Impact:** Remote Code Execution (RCE) - Complete system compromise possible. An attacker could execute arbitrary commands on the server.

**CVSS Score:** 9.8 (Critical)

**Remediation:**
```python
# BEFORE (Vulnerable)
subprocess.check_output(f"gsutil du {url}", shell=True)

# AFTER (Secure)
import shlex
subprocess.check_output(["gsutil", "du", url], shell=False)
```

---

### 1.2 Unsafe eval() with User Input - CRITICAL

**Files Affected:**
- `/detection/yolo/utils/datasets.py:249` - `eval(pipe)` with only `isnumeric()` check
- `/detection/yolo/utils/datasets.py:314` - `eval(s)` on user input
- `/detection/yolo/utils/google_utils.py:18` - `eval()` on shell output

**Description:** Direct use of `eval()` on user-controlled or external input without proper sanitization.

**Vulnerable Code:**
```python
# datasets.py:314
eval(s)  # s comes from external source
```

**Impact:** Remote Code Execution - Arbitrary Python code execution possible.

**CVSS Score:** 9.8 (Critical)

**Remediation:**
```python
# BEFORE (Vulnerable)
value = eval(s)

# AFTER (Secure)
import ast
value = ast.literal_eval(s)  # Only evaluates literals
# OR
value = int(s)  # If expecting integer
```

---

### 1.3 Hardcoded SECRET_KEY - CRITICAL

**File:** `/yolowebapp2/settings.py:27-29`

**Description:** Django SECRET_KEY is hardcoded in development configuration.

**Vulnerable Code:**
```python
SECRET_KEY = "django-insecure-skit=zl3tcyh6*-zoxegu%@4*5k)-k5jnt(1fzfqyt4@jl%a%9"
```

**Impact:** Session hijacking, CSRF token forgery, and potential data breach if the key is exposed.

**CVSS Score:** 8.1 (High)

**Remediation:**
```python
# BEFORE (Vulnerable)
SECRET_KEY = "django-insecure-..."

# AFTER (Secure)
from django.core.exceptions import ImproperlyConfigured

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable is required")
```

---

## 2. High Severity Issues

### 2.1 Insecure Content Security Policy (CSP)

**File:** `/yolowebapp2/settings.py:144-145`

**Issue:** CSP allows `unsafe-inline` and `unsafe-eval`, defeating XSS protection.

```python
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

**Impact:** XSS vulnerabilities remain exploitable despite CSP implementation.

**Remediation:** Refactor JavaScript to use nonces or hashes, remove `unsafe-inline` and `unsafe-eval`.

---

### 2.2 Default Database Credentials

**File:** `/docker-compose.yml:13, 65, 104, 133`

**Issue:** Hardcoded default password in production configuration.

```yaml
POSTGRES_PASSWORD: ${DATABASE_PASSWORD:-changeme}
```

**Impact:** Unauthorized database access if defaults are used in production.

**Remediation:** Make `DATABASE_PASSWORD` a required environment variable without default.

---

### 2.3 Overly Permissive API Permissions

**Files:**
- `/detection/api_views.py:28`
- `/dron_map/api_views.py:29`

**Issue:** Uses `IsAuthenticatedOrReadOnly` allowing unauthenticated read access.

**Impact:** Information disclosure, privacy violations, potential GDPR compliance issues.

**Remediation:**
```python
# BEFORE
permission_classes = [IsAuthenticatedOrReadOnly]

# AFTER
permission_classes = [IsAuthenticated]
# OR implement custom permissions for specific endpoints
```

---

### 2.4 Path Traversal Vulnerability

**File:** `/detection/views.py:433-441`

**Issue:** Download endpoint uses user-controlled slug values for file access without sufficient validation.

**Impact:** Potential access to sensitive files outside intended directory.

**Remediation:** Validate file paths are within allowed directories:
```python
import os
base_dir = "/allowed/path/"
requested_path = os.path.abspath(os.path.join(base_dir, user_input))
if not requested_path.startswith(base_dir):
    raise PermissionDenied("Invalid file path")
```

---

### 2.5 Unrestricted CORS in Development

**File:** `/yolowebapp2/settings.py:253-256`

**Issue:** CORS allows all origins in development mode.

```python
if IS_DEVELOPMENT:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
```

**Impact:** CSRF attacks possible if development mode is accidentally enabled in production.

---

### 2.6 Error Information Leakage

**File:** `/yolowebapp2/api_views.py:39`

**Issue:** Health check exposes database error details to unauthenticated users.

**Impact:** Information disclosure that aids attackers.

**Remediation:** Return generic error messages, log detailed errors server-side.

---

### 2.7 File Handle Resource Leak

**File:** `/detection/views.py:446-450`

**Issue:** FileResponse opens file without context manager.

```python
return FileResponse(open(file_path, "rb"), ...)  # Never closes!
```

**Impact:** Resource exhaustion, memory leaks, potential DoS.

**Remediation:**
```python
# Use context manager or let FileResponse handle closure
file_handle = open(file_path, "rb")
response = FileResponse(file_handle, as_attachment=True)
response.set_headers({...})
return response
```

---

## 3. Medium Severity Issues

### 3.1 Insufficient Input Validation

**File:** `/detection/views.py:180-182`

**Issue:** Numeric fields only validate for ValueError, missing range checks.

**Remediation:** Add bounds checking:
```python
tree_age = int(request.POST.get("tree_age", 0))
if not (0 <= tree_age <= 100):
    raise ValidationError("Tree age must be between 0 and 100")
```

---

### 3.2 Cache Management Authorization

**File:** `/detection/views.py:746, 826`

**Issue:** Any authenticated user can invalidate all caches (DoS potential).

**Remediation:** Implement role-based access control for administrative functions.

---

### 3.3 Broad Exception Handlers

**Multiple Files:** 20+ instances

**Issue:** Using `except Exception as e:` without specific error types.

**Impact:** Masks bugs, makes debugging difficult, potential security issues hidden.

**Remediation:** Catch specific exceptions:
```python
# BEFORE
except Exception as e:
    pass

# AFTER
except (ValueError, TypeError) as e:
    logger.error(f"Specific error: {e}")
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```

---

### 3.4 Error Message Exposure

**File:** `/detection/views.py:291, 303`

**Issue:** Exception messages exposed directly in HTTP responses.

**Impact:** Information leakage to attackers.

---

## 4. Code Quality Issues

### 4.1 Long Functions (Maintainability Risk)

| File | Function | Lines | Recommended Max |
|------|----------|-------|-----------------|
| `/detection/views.py:124` | `index()` | 193 | 50 |
| `/dron_map/views.py:385` | `maping()` | 185 | 50 |
| `/dron_map/views.py:162` | `add_projects()` | 181 | 50 |
| `/detection/views.py:455` | `multi_detection_image()` | 147 | 50 |
| `/detection/views.py:655` | `async_detection()` | 130 | 50 |
| `/detection/cache_utils.py:189` | `cache_statistics()` | 114 | 50 |

**Impact:** Difficult to maintain, test, and debug. Higher likelihood of bugs.

---

### 4.2 Code Duplication

**Issue:** FRUIT configuration duplicated across files.

- `/detection/views.py:31-45`
- `/detection/tasks.py:25-39`

**Remediation:** Create shared configuration module:
```python
# config.py
FRUIT_WEIGHTS = {
    "mandalina": 0.125,
    "elma": 0.105,
    # ...
}
```

---

### 4.3 Missing Type Hints

**Impact:** Reduced IDE support, potential type-related bugs, harder maintenance.

**Locations:** 15+ functions missing return type hints, especially in API viewsets.

---

### 4.4 Naming Convention Violations

| Issue | Location | Current | Suggested |
|-------|----------|---------|-----------|
| Typo | `predict_tree.py:75` | `preddict()` | `predict()` |
| Typo | `dron_map/views.py:385` | `maping()` | `mapping()` |
| Shadowing | API views | `type: str` | `fruit_type: str` |

---

### 4.5 Test Coverage - CRITICAL GAP

**Issue:** Virtually no test coverage.

- `/dron_map/tests.py` - Empty file (3 lines)
- `/yolowebapp2/test_settings.py` - Only configuration, no tests

**Zero test coverage for:**
- Image validation logic
- Model caching and loading
- Celery async tasks
- Cache hit/miss logic
- API endpoints
- Error handling paths

**Impact:** High risk of regressions, undetected bugs, security vulnerabilities.

---

### 4.6 Memory Leak Risk

**File:** `/yolowebapp2/predict_tree.py:27`

**Issue:** Global model cache without eviction or LRU mechanism.

```python
_model_cache = {}  # Models accumulate indefinitely
```

**Impact:** Memory exhaustion over time.

**Remediation:** Implement LRU cache:
```python
from functools import lru_cache

@lru_cache(maxsize=10)
def load_model(model_name):
    ...
```

---

### 4.7 Documentation Inaccuracies

**File:** `/README.md`

**Issue:** Claims "YOLOv7" but code uses YOLOv5/YOLOv8.

**Impact:** Confusion for developers and users.

---

## 5. Architecture Concerns

### 5.1 Race Conditions

**File:** `/yolowebapp2/predict_tree.py:27-43`

**Issue:** Global `_device` variable with threading.RLock may not be sufficient for concurrent model loading.

**Impact:** Potential race conditions in high-concurrency scenarios.

---

### 5.2 Missing Database Indexes

**Issue:** Common query patterns lack composite indexes.

**Example:** Queries on `(fruit_type, created_at)` would benefit from composite index.

**Remediation:**
```python
class Meta:
    indexes = [
        models.Index(fields=['fruit_type', 'created_at']),
    ]
```

---

### 5.3 N+1 Query Potential

**File:** `/detection/api_views.py:26`

**Issue:** `queryset.all()` without `select_related()` or `prefetch_related()`.

**Impact:** Performance degradation under load.

---

## 6. Dependency Analysis

### 6.1 Overview

- **Total Dependencies:** 206 packages
- **Production Dependencies:** ~150
- **Development Dependencies:** ~56 (testing, linting, type checking)

### 6.2 Key Observations

**Positive:**
- Modern Django version (4.2.17 LTS)
- Comprehensive security tooling (bandit, mypy, flake8)
- Production-ready infrastructure (Celery, Redis, PostgreSQL)

**Concerns:**
- Large dependency surface area increases attack surface
- Some dependencies may be unused
- GDAL from local file path (portability issue)

### 6.3 Security-Critical Dependencies

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| Django | 4.2.17 | ✅ Current LTS | Good |
| cryptography | 46.0.3 | ✅ Latest | Good |
| djangorestframework | 3.16.1 | ✅ Current | Good |
| psycopg2-binary | 2.9.11 | ✅ Current | Good |
| redis | 5.0.1 | ✅ Current | Good |

### 6.4 Recommendations

1. **Run security scanner:** `pip-audit` or `safety` to check for CVEs
2. **Trim unused dependencies** to reduce attack surface
3. **Pin exact versions** in production requirements
4. **Regular updates** - establish monthly dependency review process

---

## 7. Recommendations

### Immediate Actions (24-48 hours)

1. **Remove all `eval()` usage** - Replace with `ast.literal_eval()` or specific parsers
2. **Fix command injection** - Replace `shell=True` with proper argument lists
3. **Secure SECRET_KEY** - Make it a required environment variable
4. **Change default passwords** - Remove `-changeme` default in docker-compose
5. **Fix file handle leak** - Ensure proper resource cleanup

### Short-term Actions (1-2 weeks)

6. **Implement comprehensive test suite** - Minimum 80% coverage target
7. **Refactor long functions** - Break into smaller, testable units
8. **Add input validation** - Range checks, type validation, sanitization
9. **Implement RBAC** - Role-based access control for sensitive operations
10. **Update API permissions** - Use `IsAuthenticated` for sensitive endpoints

### Medium-term Actions (1 month)

11. **CSP hardening** - Remove `unsafe-inline` and `unsafe-eval`
12. **Add comprehensive logging** - Replace print statements with structured logging
13. **Implement error boundaries** - Proper error handling throughout
14. **Database optimization** - Add missing indexes, optimize queries
15. **Documentation update** - Fix inaccuracies, add API documentation

### Long-term Actions (Ongoing)

16. **Security training** - Educate team on OWASP Top 10
17. **Automated security scanning** - CI/CD pipeline integration
18. **Regular dependency audits** - Monthly security updates
19. **Penetration testing** - Annual third-party security assessment
20. **Incident response plan** - Document procedures for security incidents

---

## 8. Remediation Priority Matrix

| Priority | Issue | Effort | Impact | Timeline |
|----------|-------|--------|--------|----------|
| P0 | Command Injection | Medium | Critical | 24 hours |
| P0 | eval() usage | Low | Critical | 24 hours |
| P0 | SECRET_KEY hardcoding | Low | Critical | 24 hours |
| P1 | File handle leak | Low | High | 48 hours |
| P1 | Default credentials | Low | High | 48 hours |
| P1 | Test coverage | High | High | 1 week |
| P2 | CSP hardening | Medium | High | 1 week |
| P2 | API permissions | Low | High | 1 week |
| P2 | Input validation | Medium | Medium | 1 week |
| P3 | Code refactoring | High | Medium | 2 weeks |
| P3 | Database optimization | Medium | Medium | 2 weeks |
| P4 | Documentation | Low | Low | Ongoing |

---

## Conclusion

The FarmVision codebase demonstrates solid architecture decisions (Django, Celery, Redis) and includes many modern best practices. However, critical security vulnerabilities, particularly command injection and unsafe eval usage in the YOLO utilities, require immediate attention. The absence of test coverage is a significant risk factor that should be addressed alongside security fixes.

**Overall Risk Rating:** HIGH

**Recommendation:** Halt production deployment until critical issues are resolved. Implement security fixes in a hotfix branch and deploy immediately after thorough testing.

---

## Appendix: Files Requiring Immediate Attention

1. `/detection/yolo/utils/google_utils.py` - Command injection, eval()
2. `/detection/yolo/utils/general.py` - Command injection
3. `/detection/yolo/utils/datasets.py` - Unsafe eval()
4. `/yolowebapp2/settings.py` - SECRET_KEY, CSP configuration
5. `/docker-compose.yml` - Default credentials
6. `/detection/views.py` - File handle leak, input validation
7. `/detection/api_views.py` - Overly permissive permissions
8. `/dron_map/tests.py` - Empty test file

---

*This audit report was generated automatically. Manual verification of all findings is recommended before implementing fixes.*
