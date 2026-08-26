# MuleShield Pro V2 — Security Hardening Report

This document details the security audit and hardening measures implemented for the MuleShield Pro V2 microservices.

---

## 1. Authentication & Session Security
* **Vulnerability Identified:** The initial implementation used plain, unsalted SHA-256 for user password hashing and comparison, rendering user accounts highly susceptible to brute-force and precomputed rainbow table attacks.
* **Remediation:**
  * Upgraded password hashing mechanism to use Flask/Werkzeug's secure hashing utilities (`generate_password_hash` and `check_password_hash`).
  * Werkzeug automatically generates a cryptographically secure salt and utilizes strong algorithms (such as scrypt or PBKDF2 with SHA-256) by default.
  * Added validation in the test suite (`tests/test_rbac.py`) to verify that the upgraded password hashing processes work seamlessly during login/logout/session checks.
* **Token Lifetime:** JWT tokens are configured with a strict expiration time of **2 hours**, reducing the window of opportunity if a token is intercepted.

---

## 2. Authorization & Privilege Escalation (RBAC)
* **Vulnerability Identified:** The public `/api/auth/signup` endpoint allowed guest users to pass a custom `role` parameter (including `ADMIN` or `INVESTIGATOR`), leading to a critical privilege escalation risk.
* **Remediation:**
  * Restructured the `/api/auth/signup` handler to restrict self-registration roles.
  * Users are only allowed to self-register as `ANALYST` or `VIEWER`.
  * Attempts to register as `ADMIN`, `INVESTIGATOR`, or other privileged roles are rejected with a `400 Bad Request` status.
  * Privileged accounts (e.g., `ADMIN`, `INVESTIGATOR`) can only be created by an authenticated `ADMIN` through the secure administrative user management endpoint `/api/admin/users`.

---

## 3. CORS origin controls
* **Vulnerability Identified:** All services initialized CORS wide open (`CORS(app)`), which sets the wildcard origin `Access-Control-Allow-Origin: *`. This allows any malicious website to read responses from the gateway.
* **Remediation:**
  * Configured dynamic CORS origin verification on the API Gateway and downstream services (ML, Graph, Reporting).
  * If the environment variable `CORS_ALLOWED_ORIGINS` is configured, it will be parsed and enforced.
  * In development mode (`FLASK_ENV == "development"`), it defaults to allowing access for local development (`http://localhost:3000`).
  * In production, requests from unconfigured origins are rejected.

---

## 4. Rate Limiting
* **Vulnerability Identified:** Critical auth endpoints (`/api/auth/signup` and `/api/auth/login`) lacked rate limiting, making them vulnerable to automated brute-force password guessing and denial-of-service (DoS) attempts.
* **Remediation:**
  * Implemented an in-memory, lightweight `RateLimiter` within `backend/main.py`.
  * Applied the `@rate_limit_auth` decorator to `/api/auth/signup` and `/api/auth/login`.
  * Restricts incoming requests to a maximum of **10 requests per minute** per client IP address. Exceeding this limit triggers a `429 Too Many Requests` response.

---

## 5. Secrets Protection
* **Vulnerability Identified:** The system utilized a default fallback signature key (`muleshield-secure-secret-2026-xyz`) for signing JWT tokens.
* **Remediation:**
  * Introduced active startup configuration checks.
  * When `FLASK_ENV == "production"`, the API gateway logs a high-severity security alert if the default fallback secret is detected.
  * Database credentials and signing keys are excluded from the codebase and loaded exclusively via environment variables orConfigMaps/Secrets in Kubernetes.

---

## 6. Information Disclosure (Error Handling)
* **Vulnerability Identified:** Stack traces and internal exception messages (`str(e)`) were directly returned in HTTP 500 responses, exposing database schema properties, internal directory names, and code structures.
* **Remediation:**
  * Wrapped database transactions and query blocks in secure try-except handlers.
  * In production mode, raw exception tracebacks are suppressed in HTTP 500 error responses and replaced with generic, secure notifications (e.g., `"An internal database error occurred."`), while details are still output to stderr/logging for administrative inspection.

---

## 7. Security Verification Results
The test suite includes dedicated RBAC, auth, rate limiting, and role privilege tests. All tests pass successfully:

* **Command:** `python -m unittest tests/test_rbac.py`
* **Test Case Count:** 11 tests
* **Result:** `OK` (all tests passed)
