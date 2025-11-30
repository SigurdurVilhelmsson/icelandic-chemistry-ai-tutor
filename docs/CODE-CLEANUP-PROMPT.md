# Code Cleanup Audit - Quick Prompt

Use this prompt to perform a comprehensive code cleanup audit on any Kvenno.app repository.

---

## Quick Prompt for Claude

```
I need you to perform a comprehensive code cleanup audit on this repository following the Kvenno.app standards.

Please work through these phases systematically:

PHASE 1: Code Quality & Standards
- Set up ESLint and Prettier configurations
- Add code quality scripts to package.json
- Fix all linting and formatting issues
- Ensure TypeScript strict mode where applicable
- Remove unused dependencies and dead code

PHASE 2: Development Workflows
- Create/update development scripts (dev, build, test, lint, format)
- Set up pre-commit hooks (optional but recommended)
- Create GitHub Actions CI/CD workflow
- Add DEVELOPMENT.md guide with workflow documentation
- Configure VSCode workspace settings and extensions

PHASE 3: Debugging Infrastructure
- Set up VSCode debugging configurations
- Add error boundaries (for React projects)
- Create DEBUGGING.md guide
- Ensure source maps are enabled
- Add performance monitoring utilities

PHASE 4: Project Organization
- Review and optimize project structure
- Ensure consistent file naming conventions
- Organize imports and exports
- Clean up build outputs and ignore patterns
- Update .gitignore appropriately

PHASE 5: Testing & Validation
- Set up testing infrastructure (if not present)
- Add test scripts and examples
- Create validation script that runs all checks
- Document testing procedures

PHASE 6: Documentation Updates
- Update README.md with current setup
- Document all available scripts
- Add troubleshooting section
- Update dependency documentation
- Ensure all guides are current

After each phase:
1. Update a CLEANUP-PLAN.md file to track progress
2. Commit changes with clear messages
3. Wait for confirmation before proceeding

Follow the detailed guide in docs/CODE-CLEANUP-GUIDE.md for specifics.
```

---

## Alternative: Incremental Cleanup

If you want to focus on specific areas:

```
Focus on [PHASE_NAME] from the code cleanup audit:
- Review the CODE-CLEANUP-GUIDE.md
- Complete all tasks for this phase
- Update CLEANUP-PLAN.md
- Commit and push changes
```

---

## Files to Reference

- `docs/CODE-CLEANUP-GUIDE.md` - Detailed cleanup guide
- `CLEANUP-PLAN.md` - Track progress (created during audit)
- `.eslintrc.js` - ESLint configuration
- `.prettierrc` - Prettier configuration
- `package.json` - Scripts and dependencies
- `.vscode/` - VSCode configurations

---

## Expected Outcomes

After cleanup:
- ✅ Consistent code style across entire codebase
- ✅ Automated quality checks (CI/CD)
- ✅ Comprehensive development workflows
- ✅ Professional debugging setup
- ✅ Well-organized project structure
- ✅ Complete and accurate documentation
- ✅ Testing infrastructure in place
- ✅ Easy onboarding for new developers

---

## Notes

- This process typically takes 2-4 hours depending on repository size
- All changes should be committed incrementally
- Test after each phase to ensure nothing breaks
- Adapt the guide to fit the specific technology stack
- Skip phases that don't apply (e.g., React error boundaries for non-React projects)
