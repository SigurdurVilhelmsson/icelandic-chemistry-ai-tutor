# 📚 Documentation Checklist

**Frequency**: Monthly + after major changes
**Time Required**: 30-60 minutes
**Priority**: 🟡 MEDIUM

---

## Quick Check (10 minutes)

### Essential Files Current?

- [ ] **README.md** reflects current state
- [ ] **Package.json scripts** are documented
- [ ] **CHANGELOG.md** has recent changes (if maintained)
- [ ] **No broken links** in main docs

```bash
# Quick README review
cat README.md | head -50

# Check for TODO markers
grep -r "TODO\|FIXME\|XXX" *.md
```

---

## Comprehensive Check (60 minutes)

### 1. README.md (15 min)

- [ ] **Project title & description** accurate
- [ ] **Badges** current (if used):
  - Build status
  - Version
  - License
  - Test coverage

- [ ] **Features section** lists all major features
- [ ] **Installation instructions** work:
  - Prerequisites listed
  - Step-by-step install
  - Test on clean environment

- [ ] **Usage examples** are current:
  - Code examples work
  - Screenshots up-to-date (if used)
  - Links to live demos work

- [ ] **Available scripts** documented:
  ```markdown
  ## Available Scripts

  - `pnpm dev` - Start development server
  - `pnpm build` - Build for production
  - `pnpm test` - Run tests
  - `pnpm lint` - Lint code
  ```

- [ ] **Project structure** explained:
  ```markdown
  ## Project Structure

  ```
  src/
    components/  # Reusable UI components
    utils/       # Utility functions
    types/       # TypeScript types
  ```
  ```

- [ ] **Contributing section** (if public):
  - How to contribute
  - Code of conduct
  - Development setup

- [ ] **License** mentioned
- [ ] **Contact/Support** info included

**Red Flags**:
- 🔴 README says "Coming soon"
- 🔴 Installation instructions don't work
- 🔴 Code examples throw errors
- 🔴 No description of what the project does

---

### 2. Development Documentation (15 min)

- [ ] **DEVELOPMENT.md exists** and covers:
  - [ ] Quick start
  - [ ] Prerequisites
  - [ ] Installation
  - [ ] Running locally
  - [ ] Available scripts (detailed)
  - [ ] Development workflow
  - [ ] Testing procedures
  - [ ] Troubleshooting

- [ ] **DEBUGGING.md exists** (if applicable):
  - [ ] VSCode debugging setup
  - [ ] Browser DevTools usage
  - [ ] Common debugging scenarios
  - [ ] Performance debugging

- [ ] **Architecture/Design docs** (if complex project):
  - High-level architecture
  - Key design decisions
  - Data flow diagrams

**Red Flags**:
- 🔴 No development documentation
- 🔴 "See README" with no actual info
- 🔴 Outdated setup instructions

---

### 3. CHANGELOG.md (10 min)

If you maintain a changelog:

- [ ] **Format follows** [Keep a Changelog](https://keepachangelog.com/):
  ```markdown
  ## [Unreleased]

  ## [1.2.0] - 2025-11-29
  ### Added
  - New feature X

  ### Changed
  - Updated Y

  ### Fixed
  - Bug Z
  ```

- [ ] **Latest changes documented**
- [ ] **Dates are accurate**
- [ ] **Links to releases/PRs** (if applicable)
- [ ] **Breaking changes** clearly marked

If you don't maintain a changelog:
- [ ] Consider starting one
- [ ] Or use GitHub Releases instead

**Red Flags**:
- 🔴 Last update is 6+ months old
- 🔴 Missing breaking changes
- 🔴 Vague entries ("Fixed stuff")

---

### 4. API Documentation (10 min)

For libraries/shared components:

- [ ] **All public APIs documented**:
  ```typescript
  /**
   * Formats a date to YYYY-MM-DD format
   * @param date - The date to format
   * @returns Formatted date string
   * @example
   * formatDate(new Date('2025-01-15')) // '2025-01-15'
   */
  export function formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }
  ```

- [ ] **Component props documented** (React):
  ```typescript
  interface ButtonProps {
    /** Button text */
    label: string;
    /** Click handler */
    onClick: () => void;
    /** Button variant */
    variant?: 'primary' | 'secondary';
  }
  ```

- [ ] **README or separate API.md** has:
  - Component/function list
  - Props/parameters
  - Return values
  - Usage examples

- [ ] **Types are exported**:
  ```typescript
  export type { User, UserRole };
  ```

**Red Flags**:
- 🔴 No JSDoc comments
- 🔴 Props undocumented
- 🔴 No usage examples
- 🔴 Types not exported

---

### 5. Inline Documentation (10 min)

- [ ] **Complex functions have comments**:
  - Why (not what) comments
  - Algorithm explanations
  - Edge cases noted

- [ ] **No misleading comments**:
  ```typescript
  // ❌ Bad: Comment doesn't match code
  // Add user to database
  deleteUser(userId);

  // ✅ Good: Comment matches code
  // Remove user from database and cascade delete related data
  deleteUser(userId);
  ```

- [ ] **TODO comments tracked**:
  ```bash
  # Find all TODOs
  grep -r "TODO" src/ --include="*.ts" --include="*.tsx"

  # Create issues for old TODOs
  ```

- [ ] **Complex regex/algorithms explained**:
  ```typescript
  // Match email format: username@domain.extension
  // Allows dots, hyphens in username
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  ```

**Red Flags**:
- 🔴 Commented-out code (remove it)
- 🔴 Comments contradict code
- 🔴 100+ TODO comments
- 🔴 No comments on complex logic

---

### 6. Configuration Documentation (5 min)

- [ ] **Environment variables documented**:
  - `.env.example` exists
  - All variables listed
  - Description of each
  - Example values provided

  ```bash
  # .env.example
  # API endpoint URL
  API_URL=https://api.example.com

  # API key (get from dashboard)
  API_KEY=your_api_key_here
  ```

- [ ] **Config files explained**:
  - Why each config exists
  - Key settings documented
  - Links to official docs

**Red Flags**:
- 🔴 No `.env.example`
- 🔴 Undocumented env vars
- 🔴 Config files with no comments

---

### 7. Troubleshooting Guide (5 min)

- [ ] **Common issues documented**:
  ```markdown
  ## Common Issues

  ### "Command not found: pnpm"
  **Solution**: Install pnpm globally:
  ```bash
  npm install -g pnpm
  ```

  ### "Port 3000 already in use"
  **Solution**: Kill the process or use different port:
  ```bash
  PORT=3001 pnpm dev
  ```
  ```

- [ ] **Error messages explained**
- [ ] **Links to external resources**
- [ ] **How to get help** (Discord, GitHub Issues, etc.)

---

## Monthly Deep Check (Additional 30 min)

### 8. Link Checking

- [ ] **No broken links**:
  ```bash
  # Install markdown-link-check
  pnpm add -D markdown-link-check

  # Check all markdown files
  find . -name "*.md" -exec markdown-link-check {} \;
  ```

- [ ] **Internal links work**:
  - Links to other docs
  - Links to code files
  - Anchor links

- [ ] **External links current**:
  - Official documentation links
  - Resource links
  - Example/demo links

### 9. Screenshot/Asset Review

- [ ] **Screenshots current**:
  - UI hasn't changed significantly
  - No outdated branding
  - High quality images

- [ ] **Diagrams up-to-date**:
  - Architecture diagrams
  - Flow charts
  - Entity relationships

- [ ] **Assets optimized**:
  - Images compressed
  - Reasonable file sizes
  - Proper formats (PNG for UI, JPG for photos)

### 10. Consistency Check

- [ ] **Terminology consistent**:
  - Use same terms throughout
  - Define acronyms on first use
  - Consistent capitalization

- [ ] **Formatting consistent**:
  - Headers follow same pattern
  - Code blocks use same language tags
  - Lists formatted same way

- [ ] **Voice/tone consistent**:
  - Active voice preferred
  - Clear, concise language
  - Professional but friendly

---

## Documentation Templates

### README Template

```markdown
# Project Name

Brief description (1-2 sentences)

## Features

- Feature 1
- Feature 2
- Feature 3

## Quick Start

1. Install dependencies: `pnpm install`
2. Start dev server: `pnpm dev`
3. Visit: http://localhost:3000

## Installation

[Detailed instructions]

## Usage

[Code examples]

## Available Scripts

[Script documentation]

## Contributing

[How to contribute]

## License

[License info]
```

### JSDoc Template

```typescript
/**
 * Brief description of what function does
 *
 * Longer description if needed. Explain:
 * - What it does
 * - Why it exists
 * - Any gotchas
 *
 * @param paramName - Description
 * @param optionalParam - Description (optional)
 * @returns Description of return value
 * @throws {ErrorType} When error occurs
 *
 * @example
 * ```typescript
 * // Example usage
 * const result = myFunction('value');
 * console.log(result); // Expected output
 * ```
 */
```

---

## Automation

### GitHub Actions (Optional)

Check docs in CI:

```yaml
- name: Check links
  run: |
    pnpm add -D markdown-link-check
    find . -name "*.md" -exec markdown-link-check {} \;

- name: Check for broken references
  run: |
    # Custom script to check internal links
```

### Pre-commit Hook (Optional)

Update docs on commit:

```bash
# .husky/pre-commit
# Update date in CHANGELOG
sed -i "s/## \[Unreleased\]/## [Unreleased]\n\n### Changed\n- $(date +%Y-%m-%d)/" CHANGELOG.md
```

---

## Quick Wins

**If you have 5 minutes**:
- [ ] Review README.md intro
- [ ] Check for TODO comments in docs

**If you have 15 minutes**:
- [ ] Update CHANGELOG.md with recent changes
- [ ] Fix broken links in README

**If you have 30 minutes**:
- [ ] Review all available scripts in README
- [ ] Update .env.example
- [ ] Add JSDoc to 3-5 functions

**If you have 1 hour**:
- [ ] Full documentation audit
- [ ] Update all guides
- [ ] Add missing inline docs
- [ ] Create/update diagrams

---

## Tools & Resources

### Documentation Tools

- **JSDoc**: Inline code documentation
- **TypeDoc**: Generate API docs from TypeScript
- **Docusaurus**: Full documentation site
- **VitePress**: Lightweight docs site
- **README templates**: [awesome-readme](https://github.com/matiassingers/awesome-readme)

### Markdown Tools

- **markdown-link-check**: Check for broken links
- **markdownlint**: Lint markdown files
- **Prettier**: Format markdown consistently

### Commands Quick Reference

```bash
# Find TODOs
grep -r "TODO" src/ --include="*.ts" --include="*.tsx"

# Check links
pnpm add -D markdown-link-check
markdown-link-check README.md

# Count documentation
find . -name "*.md" -exec wc -l {} + | tail -1

# Find files without JSDoc
# (Custom script needed)
```

---

## Red Flags Summary 🚨

Stop and fix immediately if you see:

- 🔴 README doesn't explain what project does
- 🔴 Installation instructions don't work
- 🔴 No development documentation
- 🔴 Code examples throw errors
- 🔴 100+ TODO comments in code
- 🔴 Comments contradict code
- 🔴 No API documentation for library
- 🔴 Screenshots show old UI

---

## Integration with Master Checklist

This checklist is referenced by:
- `REPOSITORY-STATUS.md` (Documentation section)
- `docs/MASTER-CHECKLIST-SYSTEM.md`
- Monthly maintenance schedule

**Ask Claude**:
```
"Review documentation"
"Check if README is current"
"Add JSDoc to new functions"
"Update CHANGELOG"
```

---

## Status Update Template

After completing checklist:

```markdown
## Documentation Status

**Date**: [Date]
**README**: ✅ Current
**Dev Docs**: ✅ Up to date
**CHANGELOG**: ✅ Updated
**Inline Docs**: 🟡 85% coverage
**Broken Links**: ✅ 0 found
**Overall**: 🟢 Good

**Actions Taken**:
- Updated README with new scripts
- Added JSDoc to 8 functions
- Fixed 3 broken links
- Updated .env.example

**Next Actions**:
- Increase inline doc coverage to 90%
- Add architecture diagram
```

---

## Documentation Coverage Goals

### Minimum (Acceptable)
- ✅ README with install/usage
- ✅ Available scripts documented
- ✅ Basic troubleshooting

### Good
- ✅ All above
- ✅ DEVELOPMENT.md guide
- ✅ CHANGELOG maintained
- ✅ Major functions have JSDoc
- ✅ .env.example current

### Excellent
- ✅ All above
- ✅ Comprehensive guides (DEVELOPMENT, DEBUGGING)
- ✅ 90%+ inline doc coverage
- ✅ Architecture documentation
- ✅ API documentation
- ✅ Contributing guide
- ✅ No broken links

---

**Last Updated**: 2025-11-29
**Next Review**: [Date + 1 month]
