# ♿ Accessibility Audit Checklist

**Frequency**: Quarterly (every 3 months)
**Time Required**: 1-2 hours
**Priority**: 🟡 HIGH (Educational sites must be accessible)

---

## Why This Matters

Educational content **must be accessible** to all students, including those with:
- Visual impairments
- Motor disabilities
- Hearing impairments
- Cognitive differences
- Assistive technology users

**Legal requirement**: Many jurisdictions require educational content to meet WCAG 2.1 AA standards.

---

## Quick Check (30 minutes)

### 1. Install Tools

**Browser Extensions:**
- [axe DevTools](https://www.deque.com/axe/devtools/) (Chrome/Firefox)
- [WAVE](https://wave.webaim.org/extension/) (Chrome/Firefox)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) (built into Chrome)

### 2. Run Automated Audit (10 min)

**Using axe DevTools:**
1. Open your site in browser
2. Open DevTools (F12)
3. Click "axe DevTools" tab
4. Click "Scan ALL of my page"
5. Review issues

**Using Lighthouse:**
1. Open DevTools (F12)
2. Click "Lighthouse" tab
3. Select "Accessibility" only
4. Click "Analyze page load"
5. Aim for score >90

### 3. Fix Critical Issues (20 min)

Focus on:
- Missing alt text on images
- Low color contrast
- Missing form labels
- Missing ARIA labels
- Heading hierarchy issues

---

## Comprehensive Audit (2 hours)

### Part 1: Automated Testing (30 min)

Run all these tools on main pages:
- [ ] axe DevTools
- [ ] WAVE
- [ ] Lighthouse
- [ ] [ANDI](https://www.ssa.gov/accessibility/andi/help/install.html) (bookmarklet)

**Pages to test:**
- [ ] Home page
- [ ] Game selection page
- [ ] At least 3 different games
- [ ] Settings/help pages

### Part 2: Manual Testing (1.5 hours)

#### A. Keyboard Navigation (20 min)

**Unplug your mouse!** Navigate entire site with keyboard only.

- [ ] **Tab key**: Can reach all interactive elements
- [ ] **Shift+Tab**: Can go backwards
- [ ] **Enter/Space**: Can activate buttons/links
- [ ] **Arrow keys**: Can navigate menus/lists
- [ ] **Escape**: Can close dialogs/modals
- [ ] **Focus visible**: Clear visual indicator on focused element
- [ ] **Focus trap**: Modals trap focus (can't tab outside)
- [ ] **Skip links**: "Skip to main content" link present

**Test each game:**
- Can you play the entire game with keyboard only?
- All buttons reachable?
- Game controls clearly labeled?

#### B. Screen Reader Testing (30 min)

**Screen Readers:**
- **Windows**: NVDA (free) or JAWS
- **Mac**: VoiceOver (built-in, Cmd+F5)
- **Linux**: Orca

**Test:**
- [ ] Page title announced
- [ ] Headings announced correctly
- [ ] Buttons/links have clear labels
- [ ] Form fields have labels
- [ ] Error messages are announced
- [ ] Dynamic content updates announced
- [ ] Images have meaningful alt text
- [ ] Game state changes announced

**Game-specific:**
- [ ] Score updates announced
- [ ] Correct/incorrect feedback announced
- [ ] Timer updates announced (if applicable)
- [ ] Hint button clearly labeled

#### C. Visual Testing (20 min)

**Color Contrast:**
- [ ] Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [ ] Text on background: At least 4.5:1 ratio
- [ ] Large text (18pt+): At least 3:1 ratio
- [ ] Interactive elements: At least 3:1 ratio

**Color Blindness:**
- [ ] Use [Color Oracle](https://colororacle.org/) to simulate
- [ ] Information not conveyed by color alone
- [ ] Red/green indicators have additional cues (icons, text)

**Zoom Testing:**
- [ ] Zoom to 200%: Content still usable
- [ ] No horizontal scrolling
- [ ] No content cut off
- [ ] Touch targets still reachable

#### D. Content & Structure (20 min)

**Headings:**
- [ ] Only one `<h1>` per page
- [ ] Headings in logical order (h1 → h2 → h3, no skipping)
- [ ] Headings describe content sections

**Images:**
- [ ] All images have alt text
- [ ] Decorative images have empty alt (`alt=""`)
- [ ] Complex images (charts/diagrams) have detailed descriptions

**Forms:**
- [ ] All inputs have associated labels
- [ ] Required fields marked
- [ ] Error messages clear and helpful
- [ ] Submit button clearly labeled

**Language:**
- [ ] `<html lang="is">` or `lang="en"` set
- [ ] Language changes marked (`<span lang="en">`)
- [ ] Text readable (avoid jargon, explain terms)

#### E. Interactive Elements (20 min)

**Buttons:**
- [ ] All buttons have clear labels
- [ ] Icon-only buttons have `aria-label`
- [ ] Disabled state clearly indicated
- [ ] Can be activated with keyboard

**Links:**
- [ ] Link text describes destination
- [ ] Avoid "click here" or "read more"
- [ ] External links indicated

**Modals/Dialogs:**
- [ ] Focus moves to modal when opened
- [ ] Focus trapped inside modal
- [ ] Can close with Escape key
- [ ] Focus returns to trigger on close
- [ ] Modal has `role="dialog"` and `aria-labelledby`

**Dynamic Content:**
- [ ] Loading states announced (`aria-live`)
- [ ] Error messages announced
- [ ] Success messages announced
- [ ] Progress updates announced

---

## WCAG 2.1 AA Quick Checklist

### Perceivable

- [ ] **1.1.1** - Non-text content has text alternatives
- [ ] **1.3.1** - Info and relationships can be programmatically determined
- [ ] **1.4.3** - Color contrast minimum (4.5:1)
- [ ] **1.4.11** - Non-text contrast (3:1)

### Operable

- [ ] **2.1.1** - All functionality available via keyboard
- [ ] **2.1.2** - No keyboard trap
- [ ] **2.4.1** - Skip navigation links
- [ ] **2.4.3** - Focus order is logical
- [ ] **2.4.7** - Focus indicator visible

### Understandable

- [ ] **3.1.1** - Language of page identified
- [ ] **3.2.1** - Focus doesn't cause unexpected context change
- [ ] **3.3.1** - Error identification
- [ ] **3.3.2** - Labels or instructions provided

### Robust

- [ ] **4.1.2** - Name, role, value for all UI components
- [ ] **4.1.3** - Status messages announced

---

## Common Issues in Educational Games

### Issue: Score updates not announced
**Problem**: Screen reader users don't know score changed
**Fix:**
```html
<div aria-live="polite" aria-atomic="true">
  Score: <span id="score">{score}</span>
</div>
```

### Issue: Timer not accessible
**Problem**: Visual-only timer
**Fix:**
```html
<div role="timer" aria-live="off" aria-atomic="true">
  <span class="sr-only">Time remaining: </span>
  <span id="timer">{time}</span>
</div>
<!-- Update aria-live to "assertive" at 10 seconds -->
```

### Issue: Drag-and-drop only
**Problem**: Requires mouse
**Fix:** Provide keyboard alternative (select + Enter)

### Issue: Color-only feedback
**Problem**: Red for wrong, green for correct
**Fix:** Add icons (✓/✗) and text labels

### Issue: Auto-playing content
**Problem**: Distracting for screen reader users
**Fix:** Provide pause/stop controls

---

## Tools & Resources

### Testing Tools

**Free:**
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [NVDA Screen Reader](https://www.nvaccess.org/)

**Paid:**
- [JAWS Screen Reader](https://www.freedomscientific.com/products/software/jaws/)
- [Tenon.io](https://tenon.io/)

### Documentation

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Resources](https://webaim.org/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [React Accessibility](https://react.dev/learn/accessibility)

### Iceland-Specific

- [Icelandic Web Accessibility Guidelines](https://www.skrifstofa.is/)

---

## Fixing Common Issues

### Low Color Contrast

**Before:**
```css
.button {
  background: #f36b22; /* Kvenno orange */
  color: #fff; /* White text - ratio: 3.4:1 ❌ */
}
```

**After:**
```css
.button {
  background: #d85a12; /* Darker orange */
  color: #fff; /* White text - ratio: 4.6:1 ✅ */
}
```

### Missing Alt Text

**Before:**
```html
<img src="molecule.png">
```

**After:**
```html
<img src="molecule.png" alt="Water molecule showing two hydrogen atoms bonded to one oxygen atom">
```

### Poor Button Labels

**Before:**
```html
<button>→</button>
```

**After:**
```html
<button aria-label="Next question">→</button>
```

### Missing Form Labels

**Before:**
```html
<input type="text" placeholder="Your answer">
```

**After:**
```html
<label for="answer">Your answer:</label>
<input type="text" id="answer" placeholder="Enter molar mass">
```

---

## Status Update

After completing checklist:

```markdown
# Accessibility Audit - [Date]

## Summary
- **Score**: [X/100]
- **WCAG Level**: [AA/AAA/Partial]
- **Critical Issues**: [X]
- **Moderate Issues**: [X]

## Issues Found
1. [Issue description]
   - Severity: Critical/Moderate/Minor
   - Location: [Page/Component]
   - Fix: [How to fix]
   - Status: Fixed/Pending/Deferred

## Next Steps
- [ ] Fix critical issues (by [date])
- [ ] Fix moderate issues (by [date])
- [ ] Next audit: [date]
```

---

## Quick Wins for Icelandic Sites

Since Kvenno.app is primarily in Icelandic:

- [ ] Set `<html lang="is">`
- [ ] Provide Icelandic screen reader support
- [ ] Ensure special characters (þ, ð, æ, ö) work with screen readers
- [ ] Bilingual content has proper language tags
- [ ] Error messages in clear Icelandic

---

## Quarterly Review

Every 3 months:
1. Run full accessibility audit
2. Test with real screen reader users (if possible)
3. Review and fix all critical issues
4. Document improvements
5. Update this checklist based on findings

---

**Last Audit**: [Date]
**Next Audit**: [Date + 3 months]
**Issues Found**: [Count]
**Issues Fixed**: [Count]
**Current Score**: [X/100]
