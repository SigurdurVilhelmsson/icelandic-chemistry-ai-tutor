# ⚡ Performance Audit Checklist

**Frequency**: Quarterly
**Time Required**: 1-2 hours
**Priority**: 🟡 MEDIUM (Fast sites = better learning)

---

## Why This Matters

**Slow sites hurt learning:**
- Students lose focus waiting for pages
- Mobile users (on school Wi-Fi) suffer most
- Frustration reduces engagement

**Goals:**
- Page load < 2 seconds
- Interactive in < 1 second
- Smooth animations (60 FPS)

---

## Quick Check (15 minutes)

### Run Lighthouse

**Chrome DevTools:**
1. Open DevTools (F12)
2. Click "Lighthouse" tab
3. Select "Performance" only
4. Click "Analyze page load"

**Target Scores:**
- ✅ **90-100**: Excellent
- ⚠️ **50-89**: Needs improvement
- 🔴 **0-49**: Poor

### Key Metrics

**Core Web Vitals:**
- **LCP** (Largest Contentful Paint): < 2.5s ✅
- **FID** (First Input Delay): < 100ms ✅
- **CLS** (Cumulative Layout Shift): < 0.1 ✅

---

## Comprehensive Audit (2 hours)

### Part 1: Automated Testing (30 min)

#### A. Lighthouse (Desktop & Mobile)

Run on all major pages:
- [ ] Home page
- [ ] Game list page
- [ ] 3-5 different games
- [ ] Settings page

**Desktop:**
```bash
lighthouse https://kvenno.app --view --only-categories=performance
```

**Mobile:**
```bash
lighthouse https://kvenno.app --preset=mobile --view
```

#### B. WebPageTest

Use [WebPageTest.org](https://www.webpagetest.org/):
- [ ] Test from Iceland location (or nearest)
- [ ] Test on 3G connection
- [ ] Test on mobile device
- [ ] Check waterfall chart

#### C. Bundle Analysis

**Check bundle size:**
```bash
# For Vite projects
pnpm vite-bundle-visualizer

# Or check build output
pnpm build
ls -lh dist/*.html
```

**Target:**
- HTML files < 250KB ✅
- Total assets < 500KB ✅

### Part 2: Manual Testing (1.5 hours)

#### A. Network Performance (30 min)

**Throttle your connection:**
1. DevTools → Network tab
2. Set to "Slow 3G" or "Fast 3G"
3. Reload page
4. Time how long to interactive

**Check:**
- [ ] Page loads in <5s on 3G
- [ ] Critical content visible in <3s
- [ ] Spinners/loading states show immediately
- [ ] No layout shifts while loading

#### B. Runtime Performance (30 min)

**Record performance:**
1. DevTools → Performance tab
2. Click Record
3. Interact with game for 30 seconds
4. Stop recording
5. Analyze:

**Check for:**
- [ ] No long tasks (>50ms)
- [ ] Smooth animations (60 FPS)
- [ ] Quick response to clicks (<100ms)
- [ ] No memory leaks (run longer, check memory)

**Test specific scenarios:**
- [ ] Start game
- [ ] Answer questions
- [ ] Change settings
- [ ] Switch languages
- [ ] Complete full game session

#### C. Asset Optimization (30 min)

**Images:**
- [ ] All images optimized (compressed)
- [ ] Using modern formats (WebP)
- [ ] Appropriate sizes (not oversized)
- [ ] Lazy loading for below-fold images

**Fonts:**
- [ ] Using system fonts OR
- [ ] Fonts preloaded
- [ ] Font-display: swap
- [ ] WOFF2 format

**CSS:**
- [ ] Critical CSS inlined
- [ ] Unused CSS removed
- [ ] Minified in production

**JavaScript:**
- [ ] Code splitting (if applicable)
- [ ] Tree shaking enabled
- [ ] Minified in production
- [ ] No unused dependencies

---

## Core Web Vitals Deep Dive

### 1. LCP (Largest Contentful Paint) < 2.5s

**What it measures:** Time until largest content element is visible

**Common issues:**
- Large images not optimized
- Render-blocking resources
- Slow server response

**How to fix:**
```html
<!-- Preload critical images -->
<link rel="preload" as="image" href="hero-image.webp">

<!-- Use responsive images -->
<img
  src="game-thumb.webp"
  srcset="game-thumb-small.webp 400w, game-thumb-large.webp 800w"
  sizes="(max-width: 600px) 400px, 800px"
  alt="Game thumbnail"
>
```

### 2. FID (First Input Delay) < 100ms

**What it measures:** Time from first interaction to browser response

**Common issues:**
- Heavy JavaScript execution
- Long tasks blocking main thread
- Too much client-side rendering

**How to fix:**
```typescript
// Break up long tasks
async function processLargeData(data) {
  for (let i = 0; i < data.length; i++) {
    processItem(data[i]);

    // Yield to browser every 50 items
    if (i % 50 === 0) {
      await new Promise(resolve => setTimeout(resolve, 0));
    }
  }
}
```

### 3. CLS (Cumulative Layout Shift) < 0.1

**What it measures:** How much content shifts during load

**Common issues:**
- Images without dimensions
- Dynamic content insertion
- Web fonts causing layout shift

**How to fix:**
```html
<!-- Always specify dimensions -->
<img src="game.png" width="400" height="300" alt="Game">

<!-- Reserve space for dynamic content -->
<div style="min-height: 200px">
  {dynamicContent}
</div>

<!-- Prevent font layout shift -->
<style>
  body {
    font-family: system-ui, sans-serif;
    font-display: swap;
  }
</style>
```

---

## Optimization Checklist

### Level 1: Quick Wins (30 min)

- [ ] **Compress images**
  ```bash
  # Using imagemin
  npx imagemin-cli images/*.png --out-dir=images/optimized
  ```

- [ ] **Enable compression** (Gzip/Brotli)
  ```nginx
  # In nginx config
  gzip on;
  gzip_types text/plain text/css application/json application/javascript;
  ```

- [ ] **Add caching headers**
  ```nginx
  # Cache static assets for 1 year
  location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }
  ```

- [ ] **Minify assets**
  - Already done by Vite ✅
  - Verify in build output

### Level 2: Moderate Wins (1-2 hours)

- [ ] **Convert images to WebP**
  ```bash
  # Convert PNG to WebP
  for file in *.png; do
    cwebp -q 85 "$file" -o "${file%.png}.webp"
  done
  ```

- [ ] **Lazy load images**
  ```html
  <img src="game.png" loading="lazy" alt="Game">
  ```

- [ ] **Code splitting**
  ```typescript
  // Dynamic imports
  const HeavyComponent = lazy(() => import('./HeavyComponent'));
  ```

- [ ] **Remove unused dependencies**
  ```bash
  pnpm depcheck
  # Remove packages listed as unused
  ```

- [ ] **Reduce bundle size**
  ```typescript
  // Use tree-shakeable imports
  import { specific } from 'library';
  // Not: import * as lib from 'library';
  ```

### Level 3: Advanced (2-4 hours)

- [ ] **Implement CDN**
  - Use Cloudflare or similar
  - Serve static assets from CDN

- [ ] **Server-side rendering** (if needed)
  - Consider Next.js or similar
  - Generate static HTML

- [ ] **Service worker caching**
  - Cache game assets
  - Offline support

- [ ] **Resource hints**
  ```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="dns-prefetch" href="https://analytics.google.com">
  ```

---

## Testing Scenarios

### Scenario 1: Student on School Wi-Fi

**Setup:**
- Throttle to "Fast 3G"
- Disable cache
- Test on mobile device

**Test:**
- Load home page
- Navigate to game
- Play through one game
- Switch to another game

**Success criteria:**
- Pages load in <5 seconds
- Games playable without lag
- No broken assets

### Scenario 2: Low-End Device

**Setup:**
- Use CPU throttling (6x slowdown)
- Limited memory

**Test:**
- Run multiple games in tabs
- Check for slowdowns
- Monitor memory usage

**Success criteria:**
- Games still responsive
- No crashes or freezes
- Acceptable FPS (>30)

### Scenario 3: Poor Connection

**Setup:**
- Throttle to "Slow 3G"
- Add latency (500ms)

**Test:**
- Try to load a game
- Check loading indicators
- Test offline behavior

**Success criteria:**
- Loading states clear
- Doesn't appear frozen
- Graceful degradation

---

## Performance Budget

Set limits and track them:

```javascript
// performance-budget.json
{
  "html": {
    "max": "250kb"
  },
  "javascript": {
    "max": "200kb"
  },
  "css": {
    "max": "50kb"
  },
  "images": {
    "max": "500kb total"
  },
  "fonts": {
    "max": "100kb"
  }
}
```

**Track in CI:**
```yaml
# .github/workflows/performance.yml
- name: Check bundle size
  run: |
    SIZE=$(ls -l dist/*.html | awk '{total += $5} END {print total}')
    if [ $SIZE -gt 250000 ]; then
      echo "Bundle too large: $SIZE bytes"
      exit 1
    fi
```

---

## Monitoring

### One-Time Audits
- Lighthouse (quarterly)
- WebPageTest (quarterly)
- Bundle analysis (monthly)

### Continuous Monitoring
- [ ] Set up [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [ ] Monitor Core Web Vitals in production
- [ ] Track performance in analytics

**Free tools:**
- [Google PageSpeed Insights](https://pagespeed.web.dev/)
- [WebPageTest](https://www.webpagetest.org/)
- Search Console (Core Web Vitals report)

---

## Common Issues & Fixes

### Issue: Large bundle size

**Diagnosis:**
```bash
pnpm vite-bundle-visualizer
```

**Fixes:**
- Remove unused dependencies
- Use tree-shakeable imports
- Code splitting for large features
- Lazy load heavy components

### Issue: Slow image loading

**Diagnosis:** Lighthouse flags large images

**Fixes:**
- Compress images (use ImageOptim, Squoosh)
- Convert to WebP
- Use responsive images
- Implement lazy loading

### Issue: Blocking resources

**Diagnosis:** Lighthouse shows render-blocking resources

**Fixes:**
- Inline critical CSS
- Defer non-critical JavaScript
- Preload critical resources

### Issue: Poor FPS during animations

**Diagnosis:** Performance profiler shows dropped frames

**Fixes:**
```css
/* Use transform/opacity for animations */
.animated {
  /* ❌ Bad - triggers layout */
  animation: move 1s ease;
}
@keyframes move {
  from { left: 0; }
  to { left: 100px; }
}

/* ✅ Good - GPU accelerated */
.animated {
  animation: move 1s ease;
}
@keyframes move {
  from { transform: translateX(0); }
  to { transform: translateX(100px); }
}
```

---

## Iceland-Specific Considerations

**School Network Testing:**
- Test during school hours (congestion)
- Test from multiple Icelandic ISPs
- Consider rural areas (slower connections)

**Device Testing:**
- School-provided devices (often older)
- Student phones (varied quality)
- Tablets used in classroom

---

## Status Update

After completing checklist:

```markdown
# Performance Audit - [Date]

## Lighthouse Scores
- Desktop: [X/100]
- Mobile: [X/100]

## Core Web Vitals
- LCP: [X]s (target: <2.5s)
- FID: [X]ms (target: <100ms)
- CLS: [X] (target: <0.1)

## Bundle Sizes
- HTML: [X]KB / 250KB budget
- Total: [X]KB / 500KB budget

## Issues Found
1. [Issue] - Priority: High/Medium/Low
   - Impact: [Description]
   - Fix: [How to fix]
   - Status: Fixed/Pending

## Improvements Made
- [Improvement 1]
- [Improvement 2]

## Next Steps
- [ ] Fix high-priority issues
- [ ] Retest after fixes
- [ ] Next audit: [date]
```

---

## Resources

- [Web.dev Performance](https://web.dev/performance/)
- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Can I Use](https://caniuse.com/) - Browser support

---

**Last Audit**: [Date]
**Next Audit**: [Date + 3 months]
**Current Score**: [X/100]
**Budget Status**: ✅ Under / ⚠️ Near / 🔴 Over
