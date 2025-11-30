# Documentation Audit - Quick Prompt

**Copy this entire prompt to Claude Code in any kvenno.app repository:**

---

## DOCUMENTATION AUDIT REQUEST

Perform a comprehensive documentation audit and cleanup for this repository (part of kvenno.app ecosystem).

### Repository Context
- **Type:** [ChemistryGames / LabReports / AI Tutor / Landing / Other]
- **Purpose:** [Brief description]
- **Deploys to:** [kvenno.app/path]
- **Related repos:** [Other kvenno.app components]

### Phase 1: Audit (Do First)

1. Find all `.md`, `.txt`, and documentation `.html` files in root and `/docs/`
2. Classify each file:
   - ✅ **Up-to-date & Essential** - Keep as-is
   - 🔄 **Outdated (Update)** - Needs updates but keep
   - 📦 **Outdated (Archive)** - Historical value, move to archive
   - 🗑️ **Irrelevant** - Delete or archive

3. Create classification table with:
   - File name, size, category, reasoning, recommendation

4. **STOP and wait for approval before proceeding**

### Phase 2: Cleanup (After Approval)

**High Priority:**
1. Create `docs/archive/` structure and move historical docs
2. Create/update `CHANGELOG.md` (Keep a Changelog format)
3. Create `docs/README.md` as documentation hub
4. Update root `README.md` to reference new structure
5. Verify deployment paths match kvenno.app structure

**Medium Priority:**
6. Update files marked "Outdated (Update)"
7. Create quick reference guides if needed
8. Add cross-references to related kvenno.app repos
9. Fix any broken links

### Standards

**Commit Format:**
```
docs: reorganize documentation structure

- Archive [description]
- Add/update [files]
- Fix [issues]
```

**Required in docs/README.md:**
- Link to related kvenno.app repositories
- Reference to KVENNO-STRUCTURE.md
- Deployment location on kvenno.app
- Quick links for common tasks

### Deliverables

- Classification table
- Archive structure with historical docs
- Documentation hub (docs/README.md)
- CHANGELOG.md (if applicable)
- Updated README.md
- Summary of changes

### Reference

See ChemistryGames repository for successful implementation example.

---

**After pasting this prompt:**
1. Fill in the Repository Context section
2. Let Claude analyze and create the classification table
3. Review table before approving cleanup
4. Execute cleanup phases
5. Commit and push

**Estimated time:** 30 min (small repo) to 2-3 hours (large repo)
