# ⚡ Quick Daily Check (5 Minutes)

**Purpose**: Morning routine to check repository health
**Time**: 5 minutes
**When**: Daily before starting work (or ask Claude anytime)

---

## Just Ask Claude

The easiest way:

```
"Good morning! Quick status check."
```

Claude will:
1. Check Git status
2. Check CI/CD status
3. List any urgent issues
4. Suggest what to work on today

---

## Manual Check (If You Prefer)

### 1. Git Status (1 min)

```bash
git status
```

**Check for:**
- [ ] No unexpected changes
- [ ] Branch is correct
- [ ] No conflicts

### 2. CI/CD Status (1 min)

**Check GitHub Actions:**
- Visit: https://github.com/[your-repo]/actions
- [ ] Latest commit has ✅ green check
- [ ] No failing builds

**Or from terminal:**
```bash
gh run list --limit 1
```

### 3. Quick Security Check (1 min)

```bash
pnpm audit --audit-level=critical
```

**Expected**: "0 vulnerabilities"

### 4. Any New Issues? (1 min)

**Check GitHub:**
- [ ] Any new issues assigned to you
- [ ] Any new comments
- [ ] Any urgent PRs

**Or from terminal:**
```bash
gh issue list --assignee @me
```

### 5. What's Next? (1 min)

**Check your work board:**
- [ ] What did I commit to working on?
- [ ] Any blockers?
- [ ] Any quick wins available?

---

## Red Flags 🚨

**Stop and fix immediately if you see:**

- 🔴 CI/CD failing
- 🔴 Critical security vulnerability
- 🔴 Merge conflicts
- 🔴 Production is down

---

## Green Light ✅

**You're good to work if:**

- ✅ Git status clean (or expected changes only)
- ✅ CI/CD passing
- ✅ No critical security issues
- ✅ No blockers

---

## Example Output

### Good Status:
```
✅ Git: Working directory clean
✅ CI/CD: Latest build passing
✅ Security: No vulnerabilities
✅ Issues: 0 urgent

🎯 Today's focus: [Your planned work]

Ready to code! 🚀
```

### Needs Attention:
```
✅ Git: 2 uncommitted changes (expected)
⚠️  CI/CD: Build failing (need to fix)
✅ Security: No vulnerabilities
✅ Issues: 0 urgent

🔧 Fix failing build before continuing
  - Check error logs
  - Run tests locally
  - Fix and commit

Estimated time: 15-30 minutes
```

---

## ADHD-Friendly Tips

### Make It a Habit

**Same time every day:**
- ☕ Make coffee
- 💻 Open Claude Code
- 🤖 Ask: "Good morning! Quick status check."
- ✅ Review Claude's response
- 🚀 Start working

### Visual Cue

Add to your browser bookmarks bar:
```
🔍 Daily Check → Open Claude + ask status
```

### 5-Minute Timer

Set a timer for 5 minutes. When it goes off, you're done checking - start working!

### Don't Get Stuck

If anything is broken:
- ⏱️ Quick fix (<15 min)? Fix it now.
- 🕐 Longer fix? Note it, work on planned task, fix later.

**Don't let checking turn into fixing everything!**

---

## Automation

**Even easier - let GitHub remind you:**

Create issue template that reminds you:

```markdown
## 📅 Daily Standup - [Date]

### Morning Check
- [ ] Git status
- [ ] CI/CD status
- [ ] Security audit
- [ ] Review issues

### Today's Focus
[What you plan to work on]

### Blockers
[Anything blocking you]
```

---

## End of Day (Bonus 2 Minutes)

Before closing:

```bash
git status          # Anything to commit?
git add .           # Stage changes
git commit -m "..." # Commit work
git push            # Push to GitHub
```

**Or ask Claude:**
```
"End of day - commit my work"
```

---

**Remember**: This should take **5 minutes max**. If it takes longer, you're overthinking it! 🎯
