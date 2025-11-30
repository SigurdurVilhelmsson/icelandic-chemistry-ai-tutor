# 🎯 Master Checklist System

**Purpose**: Single command to check repository health and get prioritized tasks.

---

## Quick Start

Just ask Claude:

```
"Check my repository status"
```

Or run:

```bash
pnpm check:status
```

---

## 🔍 What Gets Checked

### 1. Security (Critical)
- [ ] Dependency vulnerabilities (`pnpm audit`)
- [ ] Exposed secrets (check for API keys in code)
- [ ] Security headers configured
- [ ] Environment variables secure

### 2. Code Quality
- [ ] ESLint passing (`pnpm lint`)
- [ ] Code formatted (`pnpm format:check`)
- [ ] TypeScript compiling (`pnpm type-check`)
- [ ] No dead code

### 3. Dependencies
- [ ] No outdated packages (`pnpm outdated`)
- [ ] No unused dependencies
- [ ] Breaking changes reviewed

### 4. Tests
- [ ] All tests passing (`pnpm test`)
- [ ] Coverage acceptable
- [ ] No failing builds

### 5. Documentation
- [ ] README current
- [ ] CHANGELOG updated
- [ ] Inline docs present
- [ ] Guides accurate

### 6. Git Health
- [ ] No uncommitted changes
- [ ] Branch up to date
- [ ] No merge conflicts

### 7. Build
- [ ] Build succeeds (`pnpm build`)
- [ ] Bundle size acceptable
- [ ] No build warnings

### 8. Performance (Periodic)
- [ ] Lighthouse score > 90
- [ ] Bundle size < 500KB
- [ ] Core Web Vitals passing

### 9. Accessibility (Periodic)
- [ ] axe audit passing
- [ ] Keyboard navigation works
- [ ] Screen reader compatible

### 10. UX (Periodic)
- [ ] Mobile responsive
- [ ] Navigation clear
- [ ] User flows complete

---

## 🤖 Automation Levels

### ✅ Level 1: GitHub Actions (Fully Automated)

These run automatically on every push:

```yaml
# .github/workflows/health-check.yml
- Type checking
- Linting
- Tests
- Build verification
- Security audit
```

**You don't do anything** - GitHub tells you if there's a problem.

### ✅ Level 2: Claude-Assisted Checks (Ask Claude)

These run when you ask Claude:

```
"Check my repository status"
```

Claude will:
1. Run all checks (`pnpm audit`, `git status`, etc.)
2. Update REPOSITORY-STATUS.md
3. List what needs attention
4. Prioritize tasks

**No manual commands** - just ask Claude!

### ✅ Level 3: Scheduled Reminders (GitHub Issues)

These create automatic reminder issues:

```yaml
# Monthly on 1st: Create maintenance reminder
# Quarterly: Create audit reminder
# Weekly: Check for stale PRs
```

**GitHub creates issues** - you just work through them.

### ⚠️ Level 4: Local Testing (When Needed)

These need a local environment:

- Running dev server (`pnpm dev`)
- Browser testing
- Visual checks

**Use GitHub Codespaces or local clone when needed.**

---

## 📋 Child Checklists

### Security Audit Checklist
Location: `docs/checklists/SECURITY-CHECKLIST.md`

Quick version:
```bash
pnpm audit                    # Check vulnerabilities
grep -r "API_KEY" src/       # Check for exposed secrets
pnpm check:security          # Run security checks
```

### Code Quality Checklist
Location: `docs/checklists/CODE-QUALITY-CHECKLIST.md`

Quick version:
```bash
pnpm lint                    # Check linting
pnpm format:check           # Check formatting
pnpm type-check             # Check types
pnpm check:quality          # Run all quality checks
```

### Documentation Checklist
Location: `docs/checklists/DOCUMENTATION-CHECKLIST.md`

Quick version:
- [ ] README has current info
- [ ] Scripts are documented
- [ ] CHANGELOG is updated
- [ ] Inline docs exist

### Accessibility Checklist
Location: `docs/checklists/ACCESSIBILITY-CHECKLIST.md`

Quick version:
- [ ] Run axe DevTools
- [ ] Check keyboard navigation
- [ ] Test screen reader
- [ ] Verify color contrast

---

## 🎯 Usage Patterns

### Daily (5 minutes)
Ask Claude:
```
"Quick status check - what's broken?"
```

Claude checks:
- Git status
- CI/CD status
- Any new issues

### Weekly (15 minutes)
Ask Claude:
```
"Weekly health check"
```

Claude runs:
- Security audit
- Dependency check
- Documentation review
- Updates dashboard

### Monthly (30 minutes)
Ask Claude:
```
"Monthly maintenance check"
```

Claude runs full audit including:
- All weekly checks
- Performance check
- Dependency updates
- Close old issues

### Quarterly (2 hours)
Ask Claude:
```
"Quarterly deep audit"
```

Claude guides you through:
- Accessibility audit
- UX review
- Tech stack review
- Major refactoring needs

---

## 💬 Example Conversations

### Quick Check (Morning Routine)

**You**: "Good morning! Check my repository status."

**Claude**:
```
🟢 Repository Health: Good

Quick Status:
✅ Security: No vulnerabilities
✅ Code Quality: All checks passing
✅ Tests: 12/12 passing
⚠️ Dependencies: 3 updates available (low priority)

Recommended Today:
- Optional: Update dependencies (15 min)

No critical issues. Ready to work! 🎉
```

### After a Break

**You**: "I haven't worked on this in 2 weeks. What needs attention?"

**Claude**:
```
📊 Status After 14 Days

Critical:
🔴 None

Warnings:
🟡 Monthly security audit overdue
🟡 5 dependencies have updates

Quick Wins (30 min):
1. Run security audit: pnpm audit
2. Update dependencies: pnpm update
3. Update REPOSITORY-STATUS.md

I'll walk you through these if you'd like!
```

### Before Starting Work

**You**: "I have 1 hour to work. What should I focus on?"

**Claude**:
```
🎯 1-Hour Focus Session

High Impact Tasks:
1. Complete accessibility audit (45 min) ⭐ RECOMMENDED
   - Would improve UX significantly
   - Been pending for 2 weeks

2. Update dependencies + test (30 min)
   - 5 updates available
   - All backwards compatible

3. Add missing inline documentation (60 min)
   - Currently at 75%, target is 90%

Which sounds most interesting to you?
```

---

## 🔧 Setup (One-Time)

### 1. Add Scripts to package.json

```json
{
  "scripts": {
    "check:status": "node scripts/check-status.mjs",
    "check:security": "pnpm audit && echo 'Security check complete'",
    "check:quality": "pnpm type-check && pnpm lint && pnpm format:check",
    "check:deps": "pnpm outdated || true",
    "check:all": "pnpm check:security && pnpm check:quality && pnpm check:deps"
  }
}
```

### 2. Create Check Script

```javascript
// scripts/check-status.mjs
import { execSync } from 'child_process';
import fs from 'fs';

console.log('🔍 Running repository health checks...\n');

// Security
console.log('🔒 Security...');
try {
  execSync('pnpm audit --audit-level=moderate', { stdio: 'inherit' });
  console.log('✅ No vulnerabilities\n');
} catch (e) {
  console.log('⚠️  Vulnerabilities found\n');
}

// Quality
console.log('💻 Code Quality...');
try {
  execSync('pnpm type-check && pnpm lint', { stdio: 'inherit' });
  console.log('✅ All checks passing\n');
} catch (e) {
  console.log('❌ Quality checks failed\n');
}

// Dependencies
console.log('📦 Dependencies...');
try {
  const outdated = execSync('pnpm outdated', { encoding: 'utf-8' });
  if (outdated) {
    console.log('⚠️  Updates available\n');
  }
} catch (e) {
  console.log('✅ All dependencies current\n');
}

console.log('\n✨ Health check complete!');
console.log('See REPOSITORY-STATUS.md for details.');
```

### 3. Set Up GitHub Actions

Already done! Your CI/CD workflow runs automatically.

### 4. Create Checklist Folder

```bash
mkdir -p docs/checklists
```

---

## 🎮 ADHD-Friendly Features

### Visual Progress
- ✅ Status dashboard with colors and emojis
- ✅ Progress bars
- ✅ Clear "wins" section

### No Decision Paralysis
- ✅ Claude tells you what to do next
- ✅ Prioritized task lists
- ✅ Time estimates for each task

### Small Chunks
- ✅ 5-minute quick checks
- ✅ 15-minute weekly checks
- ✅ 30-minute monthly checks

### Motivation
- ✅ Celebrates wins
- ✅ Shows progress over time
- ✅ Gamification elements

### Accessibility
- ✅ Works from anywhere (web-based)
- ✅ No complex setup
- ✅ Just ask Claude

---

## 🚀 Next Steps

1. **I'll create the check script** (2 minutes)
2. **I'll create the child checklists** (10 minutes)
3. **I'll set up the automation** (5 minutes)
4. **You just ask "Check my repository status"** going forward!

Would you like me to set this up now?
