# 🔒 Security Audit Checklist

**Frequency**: Weekly (automated) + Monthly (manual review)
**Time Required**: 15-30 minutes
**Priority**: 🔴 CRITICAL

---

## Quick Check (5 minutes)

Run automated security audit:

```bash
pnpm audit
```

**If vulnerabilities found:**
```bash
pnpm audit --fix  # Fix automatically
pnpm audit        # Verify fixes
```

---

## Comprehensive Check (30 minutes)

### 1. Dependencies (10 min)

- [ ] **Run audit**: `pnpm audit`
- [ ] **Check for critical vulnerabilities** (fix immediately)
- [ ] **Review moderate vulnerabilities** (plan to fix)
- [ ] **Document any unfixable issues** (add to security notes)

### 2. Secrets & Environment Variables (5 min)

- [ ] **No API keys in code**:
  ```bash
  grep -r "API_KEY\|SECRET\|PASSWORD" src/
  ```

- [ ] **`.env` files not committed**:
  ```bash
  git ls-files | grep "\.env$"
  # Should return nothing
  ```

- [ ] **`.env.example` is current**:
  - Check it has all required variables
  - No actual values, only placeholders

### 3. Dependencies Review (5 min)

- [ ] **No suspicious packages**
  - Review new dependencies
  - Check package popularity/maintenance

- [ ] **Lockfile is committed**
  ```bash
  git ls-files | grep "pnpm-lock.yaml"
  ```

### 4. Code Security (10 min)

#### For React/Frontend:

- [ ] **XSS Prevention**
  - Using React (auto-escapes by default) ✅
  - No `dangerouslySetInnerHTML` without sanitization
  - User input is validated

- [ ] **Sanitize user input**:
  ```typescript
  // ❌ Bad
  <div>{userInput}</div>

  // ✅ Good (React auto-escapes)
  <div>{userInput}</div>

  // If using dangerouslySetInnerHTML:
  import DOMPurify from 'dompurify';
  <div dangerouslySetInnerHTML={{
    __html: DOMPurify.sanitize(userInput)
  }} />
  ```

- [ ] **CSRF tokens for forms** (if using server-side forms)

#### For Node.js/Backend:

- [ ] **Input validation** on all endpoints
- [ ] **Rate limiting** configured
- [ ] **CORS** configured properly
- [ ] **Helmet.js** for security headers
- [ ] **SQL injection prevention** (use parameterized queries)

---

## Monthly Deep Check (Additional 15 min)

### 1. Review Security Headers

Check response headers:

```bash
curl -I https://your-site.com
```

Should include:
- [ ] `X-Frame-Options: SAMEORIGIN` or `DENY`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] `Strict-Transport-Security` (if HTTPS)

### 2. Review Authentication (if applicable)

- [ ] Passwords hashed with bcrypt/argon2
- [ ] Session tokens are secure
- [ ] Token expiration configured
- [ ] 2FA available (if handling sensitive data)

### 3. Check for Known Issues

Visit:
- [ ] https://www.cvedetails.com/ - Check for CVEs in your stack
- [ ] https://snyk.io/vuln/ - Vulnerability database

---

## Red Flags (Fix Immediately) 🚨

- 🔴 **Critical vulnerability** in `pnpm audit`
- 🔴 **API keys or passwords in code**
- 🔴 **`.env` file committed to Git**
- 🔴 **No input validation on user forms**
- 🔴 **Using `eval()` or similar dangerous functions**
- 🔴 **Outdated framework with known vulnerabilities**

---

## Common Vulnerabilities to Check

### 1. Dependency Vulnerabilities
**Check**: `pnpm audit`
**Fix**: `pnpm audit --fix` or update manually

### 2. Exposed Secrets
**Check**: Search codebase for secrets
**Fix**: Remove, use environment variables

### 3. XSS (Cross-Site Scripting)
**Check**: Look for unsanitized user input
**Fix**: Sanitize or use React (auto-escapes)

### 4. CSRF (Cross-Site Request Forgery)
**Check**: Forms without CSRF tokens
**Fix**: Add CSRF token to forms

### 5. SQL Injection
**Check**: String concatenation in queries
**Fix**: Use parameterized queries

### 6. Outdated Dependencies
**Check**: `pnpm outdated`
**Fix**: Update dependencies carefully

---

## GitHub Security Features

Enable these in repository settings:

- [ ] **Dependabot alerts** enabled
- [ ] **Dependabot security updates** enabled
- [ ] **Code scanning** enabled (GitHub Advanced Security)
- [ ] **Secret scanning** enabled

---

## Automation Setup

### GitHub Actions (Weekly Auto-Check)

Already configured in `.github/workflows/ci.yml`:
```yaml
- name: Security Audit
  run: pnpm audit --audit-level=moderate
```

### Dependabot (Auto-Updates)

Already configured in `.github/dependabot.yml`:
```yaml
updates:
  - package-ecosystem: "npm"
    schedule:
      interval: "weekly"
```

---

## Status Update

After completing checklist:

```bash
# Update status
Date: [Today's date]
Critical Issues: [0]
Warnings: [0]
Status: 🟢 Secure

# Or ask Claude:
"I completed the security checklist. Update the status."
```

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [React Security Best Practices](https://react.dev/learn/security)
- [npm Security Advisories](https://www.npmjs.com/advisories)

---

## Next Steps

After completing this checklist:

1. Update `REPOSITORY-STATUS.md`
2. Document any issues found
3. Create GitHub issues for any deferred fixes
4. Schedule next security audit (1 week)

---

**Last Completed**: [Date]
**Completed By**: [Name]
**Issues Found**: [Count]
**All Clear**: ✅ Yes / ❌ No
