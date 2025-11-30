# Documentation Audit Guide for Kvenno.app Repositories

**Version:** 1.0
**Created:** 2025-11-29
**Purpose:** Standardized documentation cleanup process for all kvenno.app ecosystem repositories

This guide provides a repeatable process for auditing and cleaning up documentation across all repositories in the kvenno.app ecosystem (ChemistryGames, LabReports, AI Tutor, Landing Pages, etc.).

---

## 📋 Copy-Paste Prompt for Claude Code

Use this prompt in any kvenno.app repository to initiate a documentation audit:

```markdown
# Documentation Audit Request

I need you to perform a comprehensive documentation audit and cleanup for this repository, which is part of the kvenno.app ecosystem.

## Context

**Repository Type:** [Fill in: ChemistryGames / LabReports / AI Tutor / Landing Page / Other]
**Primary Purpose:** [Brief description of what this repo does]
**Deployment Location:** [e.g., kvenno.app/1-ar/games/ or kvenno.app/2-ar/lab-reports/]
**Related Repos:** [List other kvenno.app repos this connects to]

## Audit Scope

Focus on **non-code documentation** files in the root directory and `/docs/` folder:
- Markdown files (*.md)
- Text files (*.txt)
- HTML documentation (404.html, index.html if static)
- License files
- Changelog files

**Exclude from audit:**
- Source code files
- Configuration files (package.json, tsconfig.json, vite.config.ts, etc.)
- Git files (.gitignore, .gitattributes)
- IDE files (.vscode/, .idea/)
- Build outputs (dist/, build/, node_modules/)

## Classification Criteria

Classify each document into one of these categories:

### 1. ✅ Up-to-date & Essential
- Currently accurate and actively used
- Referenced by other documentation or workflows
- Required for legal/licensing
- Core documentation (README, LICENSE, etc.)

### 2. ⚠️ Outdated (Should Update & Keep)
- Contains valuable information but needs updates
- Referenced but contains stale information
- Core documentation that's behind current state

### 3. 📦 Outdated (Should Archive)
- Historical value but no longer active
- Completed project phases or migrations
- Superseded by newer documentation
- Keep for reference but move to archive

### 4. 🗑️ Irrelevant/Redundant (Should Delete)
- Duplicates existing documentation
- No longer relevant to project
- Temporary files that weren't cleaned up
- Outdated with no historical value

## Requested Actions

### Phase 1: Audit and Report
1. **Find all documentation files** in root and docs/ directories
2. **Read and analyze** each file's content and relevance
3. **Create a classification table** with:
   - File name and path
   - Size/line count
   - Category (Up-to-date / Outdated-Update / Outdated-Archive / Irrelevant)
   - Reasoning for classification
   - Recommended action

4. **Present the table** and wait for approval before proceeding

### Phase 2: Execute Cleanup (After Approval)

#### High Priority:
1. **Create archive structure:**
   ```
   docs/
   ├── README.md (documentation hub)
   └── archive/
       └── [context-specific folders]
   ```

2. **Move historical documents** to appropriate archive folders

3. **Create/Update CHANGELOG.md** (if doesn't exist):
   - Follow [Keep a Changelog](https://keepachangelog.com/) format
   - Document current version and major milestones
   - Include links to kvenno.app ecosystem

4. **Create/Update docs/README.md** as documentation hub:
   - Organize all active documentation by category
   - Link to related kvenno.app repositories
   - Quick links for common tasks
   - Reference to archived documentation

5. **Update root README.md** to reference new structure

#### Medium Priority:
6. **Review and update** any files marked "Outdated (Update)"

7. **Verify deployment documentation** matches current kvenno.app structure

8. **Create quick reference guides** if missing (condense long docs)

9. **Add cross-repository references** to other kvenno.app components

## Kvenno.app Ecosystem Context

This repository is part of the kvenno.app platform for Kvennaskólinn í Reykjavík:

### Site Structure
```
kvenno.app/
├── / (Landing page)
├── /1-ar/ (1st year hub)
│   ├── /1-ar/games/
│   └── /1-ar/ai-tutor/
├── /2-ar/ (2nd year hub)
│   ├── /2-ar/lab-reports/
│   ├── /2-ar/games/
│   └── /2-ar/ai-tutor/
└── /3-ar/ (3rd year hub)
    ├── /3-ar/lab-reports/
    ├── /3-ar/games/
    └── /3-ar/ai-tutor/
```

### Key Documentation to Reference
- **KVENNO-STRUCTURE.md** - Site-wide design system and architecture
- **DEPLOYMENT.md** - Deployment to kvenno.app server
- **Authentication** - Azure AD setup (if applicable)
- **API** - Backend API structure (if applicable)

### Required Cross-References
When creating/updating documentation, include links to:
1. Related kvenno.app repositories (if applicable)
2. Shared design system (KVENNO-STRUCTURE.md)
3. Deployment structure (where this deploys on kvenno.app)
4. Authentication setup (if using Azure AD)

## Standards to Follow

### Commit Messages
Use conventional commits format:
```
docs: reorganize documentation structure

- Archive completed [project phase] documentation
- Add CHANGELOG.md for version tracking
- Create docs/README.md as documentation hub
- Update main README with new structure
```

### Documentation Style
- Use clear headings and table of contents
- Include last updated date
- Add "Maintained by" footer
- Use markdown best practices
- Keep language professional and concise

### File Naming
- Use kebab-case for new files: `creating-new-game.md`
- Keep existing naming conventions for core files (README, LICENSE, etc.)
- Group related docs in subdirectories

## Deliverables

After completing the audit and cleanup:

1. **Classification Table** - Show what was found and categorized
2. **Archive Structure** - Organized historical documentation
3. **Documentation Hub** (docs/README.md) - Central navigation
4. **CHANGELOG.md** - Version history (if created/updated)
5. **Updated README.md** - References to new structure
6. **Git Commits** - Clean, descriptive commit messages
7. **Summary Report** - What was accomplished and recommendations

## Success Criteria

- ✅ All documentation files classified and organized
- ✅ Historical docs archived but accessible
- ✅ Active documentation is current and accurate
- ✅ Clear navigation structure for developers
- ✅ Cross-references to kvenno.app ecosystem
- ✅ Changes committed and pushed to branch
- ✅ No broken links in documentation
- ✅ Deployment paths verified and documented

## Example Output

See the ChemistryGames repository for a reference implementation:
- Classification table with 12 files analyzed
- Archive structure created (`docs/archive/completed-migrations/`)
- Documentation hub with organized links
- CHANGELOG.md with version 2.0.0
- Quick reference guide (condensed from 1200-line migration guide)
- Updated IMPROVEMENTS.md with completion status

## Additional Instructions

- **Do not** modify source code or configuration files
- **Do not** delete files without explicit approval
- **Ask for clarification** if classification is ambiguous
- **Preserve historical context** - archive, don't delete
- **Maintain consistency** with other kvenno.app repos
- **Test all links** after reorganization
- **Commit frequently** with descriptive messages

---

**Note:** This audit process was successfully executed on ChemistryGames repository (2025-11-29). The methodology is proven and can be adapted to any repository in the kvenno.app ecosystem.
```

---

## 🎯 Quick Start for New Repository Audit

1. **Copy the prompt above** (everything in the markdown code block)
2. **Fill in the Context section** with repository-specific information
3. **Paste into Claude Code** in the target repository
4. **Review the classification table** before approving cleanup
5. **Execute the cleanup** in phases (High Priority → Medium Priority)
6. **Commit and push** when complete

---

## 📊 Metrics to Track

For consistency across repositories, track these metrics:

| Metric | Description |
|--------|-------------|
| **Active Docs** | Number of current, active documentation files |
| **Archived Docs** | Number of historical documents preserved |
| **Deleted Docs** | Number of truly redundant files removed |
| **New Docs Created** | CHANGELOG, quick references, hubs created |
| **Total Size** | Combined size of documentation |
| **Broken Links Fixed** | Links updated to match new structure |

---

## 🔧 Repository-Specific Adaptations

### For React/Vite Applications (LabReports, AI Tutor)
Additional considerations:
- Check for outdated component documentation
- Verify API endpoint documentation
- Review environment variable documentation
- Check deployment build instructions

### For Static Sites (Landing Pages)
Additional considerations:
- Verify HTML documentation accuracy
- Check asset path documentation
- Review SEO/metadata documentation
- Verify nginx configuration docs

### For Monorepos (ChemistryGames)
Additional considerations:
- Document workspace structure
- Explain shared dependencies
- Create per-package documentation
- Maintain migration guides

---

## 📚 Template Files

### Template: CHANGELOG.md

```markdown
# Changelog

All notable changes to [Repository Name] will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Documentation cleanup and reorganization

---

## [Current Version] - YYYY-MM-DD

### Summary
[Brief description of current state]

### Added
[New features]

### Changed
[Changes to existing features]

### Fixed
[Bug fixes]

### Deployment
- Deployed to: [kvenno.app path]
- Related repos: [List kvenno.app repos]

---

**Maintained by:** Sigurður E. Vilhelmsson, Kvennaskólinn í Reykjavík
```

### Template: docs/README.md

```markdown
# [Repository Name] Documentation

Welcome to the [Repository Name] documentation hub.

---

## 📚 Active Documentation

### Core Documentation
- **[Main README](../README.md)** - Repository overview
- **[CHANGELOG](../CHANGELOG.md)** - Version history
- **[LICENSE](../LICENSE)** - MIT License

### Development Guides
- **[Development Guide](../DEVELOPMENT.md)** - Setup and workflow
- **[Deployment Guide](../DEPLOYMENT.md)** - Deploy to kvenno.app

### Kvenno.app Integration
- **[KVENNO-STRUCTURE.md](../KVENNO-STRUCTURE.md)** - Site-wide structure
- Part of: [Link to kvenno.app section]
- Related repos: [Links to other kvenno.app repos]

---

## 🗂️ Archived Documentation

Historical documentation from completed phases:
- [Link to archive folders]

---

## 🚀 Quick Links

### For Developers
1. [Setup instructions]
2. [Common tasks]
3. [Troubleshooting]

### For Deployment
1. [Build process]
2. [Deploy to kvenno.app]
3. [Environment variables]

---

**Last Updated:** YYYY-MM-DD
**Maintained by:** Sigurður E. Vilhelmsson, Kvennaskólinn í Reykjavík
```

---

## ✅ Checklist for Each Repository

Use this checklist to ensure consistency across all kvenno.app repositories:

- [ ] README.md exists and is up-to-date
- [ ] CHANGELOG.md exists and follows Keep a Changelog format
- [ ] LICENSE file exists (MIT License)
- [ ] docs/README.md exists as documentation hub
- [ ] Historical docs archived in docs/archive/
- [ ] KVENNO-STRUCTURE.md exists or is referenced
- [ ] DEPLOYMENT.md documents kvenno.app deployment
- [ ] Cross-references to related kvenno.app repos
- [ ] No broken documentation links
- [ ] All deployment paths verified
- [ ] Commit messages follow conventional commits
- [ ] Branch pushed to remote

---

## 🎓 Lessons Learned from ChemistryGames Audit

### What Worked Well
1. **Classification first, action second** - Getting approval on the table prevented mistakes
2. **Archive, don't delete** - Historical docs have value for context
3. **Create hubs** - Central documentation index makes navigation easy
4. **Quick references** - Condensed guides are more useful than long ones
5. **Track improvements** - IMPROVEMENTS.md with completion status is valuable

### What to Watch For
1. **Deployment path mismatches** - Verify repo paths match server paths
2. **Circular references** - Ensure documentation links don't create loops
3. **Stale examples** - Code examples in docs can become outdated quickly
4. **Cross-repo dependencies** - Document dependencies on other kvenno.app repos
5. **Version drift** - Keep CHANGELOG.md updated with each release

### Time Estimates
- **Small repo** (<10 docs): 30-60 minutes
- **Medium repo** (10-20 docs): 1-2 hours
- **Large repo** (20+ docs): 2-3 hours

---

## 📞 Support

If you encounter issues during the audit process:
1. Reference the ChemistryGames repository for examples
2. Check this guide for templates and standards
3. Ensure Claude Code has context about kvenno.app ecosystem
4. Review classification criteria if uncertain about a file

---

**Guide Version:** 1.0
**Last Updated:** 2025-11-29
**Maintainer:** Sigurður E. Vilhelmsson, Kvennaskólinn í Reykjavík

**Reference Implementation:** ChemistryGames repository documentation audit (2025-11-29)
