# 🎨 UX & Navigation Audit Checklist

**Frequency**: Quarterly or when adding major features
**Time Required**: 2-3 hours
**Priority**: 🟡 MEDIUM (Good UX = better engagement)

---

## Why This Matters

**Good UX in educational tools:**
- Students focus on learning, not fighting the interface
- Less confusion = more time learning chemistry
- Clear navigation = students find what they need
- Positive experience = students return voluntarily

---

## Quick Check (30 minutes)

### The 5-Second Test

**Show someone the site for 5 seconds**, then ask:
- What is this site for?
- Who is it for?
- What can you do here?

**Success:** They can answer all three correctly

### The 3-Click Rule

**Can you reach any content in ≤3 clicks?**
- Home → Games → Specific Game = 2 clicks ✅
- Home → Settings → Accessibility = 2 clicks ✅

### The Grandmother Test

**Would your grandmother understand:**
- How to start a game?
- How to get help?
- What the buttons do?

---

## Comprehensive Audit (3 hours)

### Part 1: Navigation (45 min)

#### A. Site Structure

- [ ] **Clear hierarchy**
  - Home → Year Selection → Games → Specific Game
  - Breadcrumbs show current location
  - Can always get back to home

- [ ] **Consistent navigation**
  - Same menu/nav on all pages
  - Logo links to home
  - Active page highlighted

- [ ] **Mobile menu**
  - Hamburger icon recognizable
  - Menu overlay clear
  - Easy to close
  - Touch targets ≥48px

#### B. Navigation Patterns

**Test:**
1. Start at home page
2. Navigate to each game
3. Use "back" button
4. Use breadcrumbs
5. Use main menu

**Check:**
- [ ] No dead ends (every page has next action)
- [ ] Back button works as expected
- [ ] Breadcrumbs accurate
- [ ] Menu always accessible
- [ ] No broken links

#### C. Search & Discovery

**For game library:**
- [ ] Games organized by year level
- [ ] Filters work (if applicable)
- [ ] Clear game descriptions
- [ ] Preview/demo available
- [ ] Recently played shown

### Part 2: User Flows (45 min)

#### Flow 1: New Student

**Scenario:** First time visiting, wants to practice molar mass

**Steps:**
1. Lands on home page
2. Sees year selection
3. Clicks "1. ár" (Year 1)
4. Finds "Mólmassi" game
5. Reads instructions
6. Starts game
7. Answers question
8. Gets feedback
9. Continues or stops

**Check at each step:**
- [ ] What to do next is obvious
- [ ] Instructions are clear
- [ ] Buttons labeled clearly
- [ ] Feedback is immediate
- [ ] Can pause/quit easily

#### Flow 2: Returning Student

**Scenario:** Played before, wants to continue where they left off

**Steps:**
1. Lands on home page
2. Sees "Continue Playing" or recent games
3. Clicks to resume
4. Game loads with progress
5. Continues learning

**Check:**
- [ ] Progress is saved
- [ ] Progress is visible
- [ ] Can resume easily
- [ ] Can start fresh if desired

#### Flow 3: Student Needs Help

**Scenario:** Stuck on a question, needs help

**Steps:**
1. Playing game
2. Sees "Hint" or "Help" button
3. Clicks it
4. Reads hint
5. Tries again OR sees solution
6. Continues

**Check:**
- [ ] Help is discoverable
- [ ] Help is relevant
- [ ] Help doesn't give away answer immediately
- [ ] Can close help easily
- [ ] Help in correct language

#### Flow 4: Teacher Checking Progress

**Scenario:** Teacher wants to see student progress

**Steps:**
1. Student shows progress screen
2. Teacher sees stats
3. Teacher understands performance

**Check:**
- [ ] Progress is clear
- [ ] Stats are meaningful
- [ ] Can export if needed
- [ ] Privacy respected

### Part 3: Visual Design (30 min)

#### A. Consistency

- [ ] **Colors**
  - Kvenno orange (#f36b22) used consistently
  - Color meanings consistent (green=correct, red=wrong)
  - Sufficient contrast

- [ ] **Typography**
  - Consistent font sizes
  - Hierarchy clear (headings vs body)
  - Readable (not too small)
  - Line height comfortable

- [ ] **Spacing**
  - Consistent padding/margins
  - White space used effectively
  - Not too cramped or too sparse

- [ ] **Components**
  - Buttons look like buttons
  - Links look like links
  - Inputs look clickable
  - Disabled states clear

#### B. Visual Hierarchy

**Test:** Blur your eyes - can you still understand the layout?

- [ ] Most important content stands out
- [ ] Clear sections/grouping
- [ ] Logical reading order
- [ ] Call-to-action buttons prominent

#### C. Responsive Design

**Test on:**
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Phone (375x667)
- [ ] Large phone (414x896)

**Check:**
- [ ] No horizontal scrolling
- [ ] Touch targets ≥48px on mobile
- [ ] Text readable without zoom
- [ ] Images scale appropriately
- [ ] Navigation works on all sizes

### Part 4: Content & Copy (30 min)

#### A. Clarity

**Instructions:**
- [ ] Written in clear Icelandic
- [ ] Short sentences
- [ ] Active voice
- [ ] No jargon (or jargon explained)
- [ ] Examples provided

**Labels:**
- [ ] Buttons describe action ("Byrja leik" not "OK")
- [ ] Form labels clear
- [ ] Error messages helpful
- [ ] Success messages encouraging

#### B. Tone

**For student audience:**
- [ ] Encouraging, not condescending
- [ ] Friendly but professional
- [ ] Age-appropriate
- [ ] Supports learning (not just testing)

#### C. Language

**Bilingual considerations:**
- [ ] Primary language (Icelandic) complete
- [ ] English translation complete
- [ ] Polish translation (if applicable)
- [ ] Language switcher obvious
- [ ] Language persists across pages

### Part 5: Interaction Design (30 min)

#### A. Feedback

**Every action gets feedback:**
- [ ] Buttons show pressed state
- [ ] Hover states clear
- [ ] Loading states for slow operations
- [ ] Success/error messages
- [ ] Progress indicators

**Test:**
- Click a button - does something happen immediately?
- Submit a form - do you know it's processing?
- Make an error - is it explained clearly?

#### B. Error Prevention

- [ ] Confirm destructive actions (delete, reset)
- [ ] Validate input as user types
- [ ] Disable buttons that shouldn't be clicked
- [ ] Prevent double-submission
- [ ] Save progress automatically

#### C. Error Recovery

**When errors happen:**
- [ ] Error message is clear and helpful
- [ ] Suggests how to fix
- [ ] Doesn't lose user's work
- [ ] Easy to try again
- [ ] Can contact for help

### Part 6: Game-Specific UX (30 min)

#### A. Game Entry

- [ ] Clear game title
- [ ] Difficulty level shown
- [ ] Time estimate given
- [ ] Instructions before starting
- [ ] Can preview without playing
- [ ] Start button obvious

#### B. During Gameplay

- [ ] Current question/level clear
- [ ] Progress indicator visible
- [ ] Score displayed (if applicable)
- [ ] Timer visible (if applicable)
- [ ] Can pause
- [ ] Can quit
- [ ] Can get hints
- [ ] Can see solutions
- [ ] Keyboard shortcuts available

#### C. Feedback & Results

- [ ] Immediate feedback (correct/incorrect)
- [ ] Explanation provided
- [ ] Encouraging messages
- [ ] Final score/results clear
- [ ] Can review mistakes
- [ ] Can try again
- [ ] Can see progress over time

#### D. Settings & Preferences

- [ ] Easy to find
- [ ] Language selection
- [ ] Difficulty level
- [ ] Sound on/off
- [ ] Accessibility options
- [ ] Settings persist

---

## Common UX Issues in Educational Games

### Issue: Instructions too long

**Problem:** Students skip reading, then get confused

**Fix:**
- Keep instructions to 3-5 sentences
- Use "Show me" demo instead
- Progressive disclosure (explain as you go)

### Issue: Unclear feedback

**Problem:** Student doesn't know if answer is right

**Fix:**
```typescript
// ❌ Bad
<div>{isCorrect ? '✓' : '✗'}</div>

// ✅ Good
<div className={isCorrect ? 'success' : 'error'}>
  {isCorrect
    ? 'Rétt! Þetta er mólmassi vatns.'
    : 'Rangt. Reyndu aftur! Muna: H₂O = 2(1) + 16'
  }
</div>
```

### Issue: Lost progress

**Problem:** Student accidentally closes tab, loses all work

**Fix:**
- Auto-save every answer
- Confirm before quitting mid-game
- "Resume where you left off" on return

### Issue: No sense of progress

**Problem:** Student doesn't know how they're improving

**Fix:**
- Show progress bars
- Track streak (e.g., "5 in a row!")
- Display improvement over time
- Celebrate milestones

### Issue: Too easy to make mistakes

**Problem:** Fat-finger clicks on mobile

**Fix:**
- Larger touch targets (≥48px)
- Spacing between buttons
- Confirm for destructive actions
- Undo option where possible

---

## Mobile-Specific Checks

### Touch Interactions

- [ ] Touch targets ≥48px × 48px
- [ ] Spacing between clickable elements
- [ ] Swipe gestures (if used) are discoverable
- [ ] No hover-only interactions
- [ ] No tiny text inputs

### Screen Real Estate

- [ ] Important content above fold
- [ ] Not too much scrolling required
- [ ] Modal dialogs fit on screen
- [ ] Landscape mode works

### Performance on Mobile

- [ ] Animations smooth (60 FPS)
- [ ] No jank while scrolling
- [ ] Fast response to taps
- [ ] Doesn't feel sluggish

---

## Gamification Done Right

### Good Gamification

✅ **Progress tracking** - Shows improvement
✅ **Achievements** - Celebrates milestones
✅ **Streaks** - Encourages consistency
✅ **Badges** - Recognizes completion
✅ **Choice** - Student picks difficulty

### Bad Gamification

❌ **Leaderboards** - Creates pressure/comparison
❌ **Time pressure** - Causes anxiety
❌ **Mandatory challenges** - Removes autonomy
❌ **Punishment** - Negative reinforcement

---

## User Testing

### Hallway Testing

**Grab 3-5 students, ask them to:**
1. Find a specific game
2. Play one round
3. Check their progress

**Observe:**
- Where do they get confused?
- What do they click first?
- Do they read instructions?
- What do they say out loud?

**Document:**
- Pain points
- Unexpected behavior
- Feature requests
- Praise (what works)

### Task-Based Testing

**Give specific tasks:**
- "Find the molar mass game"
- "Change the language to English"
- "Turn on high contrast mode"
- "See how many games you've completed"

**Success metrics:**
- Task completion rate
- Time to complete
- Number of errors
- Confidence rating

---

## Icelandic Education Context

**Consider:**
- [ ] Students familiar with Icelandic UI
- [ ] Chemistry terms in Icelandic
- [ ] School environment (desktop computers)
- [ ] Age range (15-18 years old)
- [ ] Mixed ability levels
- [ ] Supports independent learning

---

## Status Update

After completing checklist:

```markdown
# UX Audit - [Date]

## Overall Rating: [X/10]

## Navigation
- ✅ Strengths: [List]
- ⚠️ Issues: [List]

## User Flows
- ✅ Works well: [Flows]
- ⚠️ Needs work: [Flows]

## Visual Design
- ✅ Strengths: [List]
- ⚠️ Issues: [List]

## Content & Copy
- ✅ Clear: [Examples]
- ⚠️ Confusing: [Examples]

## Game UX
- ✅ Good: [Features]
- ⚠️ Problems: [Features]

## User Testing Results
- Participants: [X]
- Success rate: [X%]
- Key findings: [List]

## Priority Fixes
1. [Issue] - Impact: High/Medium/Low
2. [Issue] - Impact: High/Medium/Low

## Next Steps
- [ ] Fix high-priority issues
- [ ] Re-test with users
- [ ] Next audit: [date]
```

---

## Resources

- [Nielsen Norman Group](https://www.nngroup.com/)
- [Laws of UX](https://lawsofux.com/)
- [UX Checklist](https://uxchecklist.github.io/)
- [Material Design Guidelines](https://m3.material.io/)

---

**Last Audit**: [Date]
**Next Audit**: [Date + 3 months]
**User Satisfaction**: [X/10]
**Task Success Rate**: [X%]
