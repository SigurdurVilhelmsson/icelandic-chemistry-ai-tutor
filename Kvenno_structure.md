# KVENNO.APP - Unified Site Structure

This document defines the complete structure, design system, and navigation patterns for kvenno.app. **Copy this file to every repo** to give Claude Code the full context when working on individual projects.

## 1. Site Structure & URL Routing

```
kvenno.app/
├── /                           (Landing page - repo: kvenno-landing)
│
├── /1-ar/                      (1st year hub - repo: kvenno-1ar-hub)
│   ├── /1-ar/ai-tutor/         (AI Chemistry Tutor - repo: ai-tutor-app)
│   ├── /1-ar/games/            (Chemistry Games 1st yr - repo: chemistry-games-1ar)
│   └── /1-ar/[future-tools]/   (Future expansion)
│
├── /2-ar/                      (2nd year hub - repo: kvenno-2ar-hub)
│   ├── /2-ar/lab-reports/      (Lab Reports App - repo: lab-reports-app)
│   ├── /2-ar/ai-tutor/         (AI Chemistry Tutor - repo: ai-tutor-app)
│   ├── /2-ar/games/            (Chemistry Games 2nd yr - repo: chemistry-games-2ar)
│   └── /2-ar/[future-tools]/   (Future expansion)
│
├── /3-ar/                      (3rd year hub - repo: kvenno-3ar-hub)
│   ├── /3-ar/lab-reports/      (Lab Reports App - repo: lab-reports-app)
│   ├── /3-ar/ai-tutor/         (AI Chemistry Tutor - repo: ai-tutor-app)
│   ├── /3-ar/games/            (Chemistry Games 3rd yr - repo: chemistry-games-3ar)
│   └── /3-ar/[future-tools]/   (Future expansion)
│
├── /val/                       (Elective courses hub - repo: kvenno-val-hub)
│   └── /val/[tools]/           (Elective tools TBD)
│
└── /f-bekkir/                  (Social sciences track - repo: kvenno-fbekkir-hub)
    └── /f-bekkir/[tools]/      (Social sciences tools TBD)
```

### Shared vs Year-Specific Apps

**Shared Across Years** (same repo, deployed to multiple paths):
- AI Chemistry Tutor (`ai-tutor-app`) - Used in 1st, 2nd, and 3rd year
- Lab Reports (`lab-reports-app`) - Used in 2nd and 3rd year

**Year-Specific** (separate repos):
- Chemistry Games - Different content/difficulty per year:
  - `chemistry-games-1ar` → /1-ar/games/
  - `chemistry-games-2ar` → /2-ar/games/
  - `chemistry-games-3ar` → /3-ar/games/

**Future Tools**:
- Can be either shared or year-specific depending on content
- Document in this file which approach is used for each new tool

## 2. Design System

### Brand Colors
- **Primary Orange**: `#f36b22` (Kvennaskólinn í Reykjavík brand color)
- **Background**: White or light gray (`#f5f5f5` for sections)
- **Text**: Dark gray/black (`#333333` for body text)
- **Accent/Links**: Consider darker shade of orange or complementary color

### Typography
- **Headings**: Sans-serif, bold
- **Body**: Sans-serif, regular weight
- **Specific fonts**: TBD - currently using system defaults

### Button/Tile Styling
All navigation buttons and tool tiles should use:
- Border: 2px solid #f36b22 (or filled background #f36b22 with white text)
- Border radius: 8px
- Padding: 16px 24px
- Hover state: Slightly darker shade or shadow effect
- Font size: 16-18px for buttons

### Layout Patterns
- **Maximum content width**: 1200px, centered
- **Spacing**: Consistent 16px or 24px grid
- **Responsive**: Mobile-first, stack tiles vertically on small screens

## 3. Header Component

Every page on kvenno.app must include a consistent header with:

```
┌─────────────────────────────────────────────┐
│ [Logo/Site Name]              [Admin] [Info] │
└─────────────────────────────────────────────┘
```

### Header Requirements:
- **Site name/logo**: "Kvenno Efnafræði" or similar, links to `/`
- **Right-aligned buttons**: 
  - "Admin" (for teacher access)
  - "Info" (for help/about)
- **Background**: White with bottom border or subtle shadow
- **Height**: ~60px
- **Sticky**: Consider making header sticky on scroll

### Header Code Template:
```jsx
// Add to every app
<header className="site-header">
  <div className="header-content">
    <a href="/" className="site-logo">Kvenno Efnafræði</a>
    <div className="header-actions">
      <button className="header-btn">Admin</button>
      <button className="header-btn">Info</button>
    </div>
  </div>
</header>
```

## 4. Navigation & Breadcrumbs

### Breadcrumb Pattern
Every sub-page must show its location in the hierarchy:

```
Heim > 1. ár > Lab Reports
```

- Always start with "Heim" (Home) linking to `/`
- Show current section (e.g., "1. ár")
- Show current app name (not linked)
- Style: Small text, gray, with > or / separators

### Back Navigation
Each app should also include a clear "Til baka" (Back) button that goes to its parent hub.

## 5. Landing Page (/)

The root landing page contains:
1. **Header** (as defined above)
2. **Intro section**: Brief welcome text about Kvennaskólinn chemistry tools
3. **Main navigation tiles**: Four large buttons/cards:
   - **1. ár** → `/1-ar/`
   - **2. ár** → `/2-ar/`
   - **3. ár** → `/3-ar/`
   - **Val** → `/val/`

### Landing Page Layout:
```
┌─────────────────────────────────┐
│          Header                  │
├─────────────────────────────────┤
│                                  │
│  Welcome to Kvenno Chemistry     │
│  [Intro paragraph]               │
│                                  │
│  ┌──────────┐  ┌──────────┐    │
│  │  1. ár   │  │  2. ár   │    │
│  └──────────┘  └──────────┘    │
│                                  │
│  ┌──────────┐  ┌──────────┐    │
│  │  3. ár   │  │   Val    │    │
│  └──────────┘  └──────────┘    │
│                                  │
└─────────────────────────────────┘
```

## 6. Year/Section Hub Pages

Each hub page (1.ár, 2.ár, 3.ár, Val) has:
1. **Header** (consistent)
2. **Breadcrumbs**: `Heim > [Section Name]`
3. **Section title**: e.g., "1. árs verkfæri"
4. **Tool tiles**: Grid of available apps/tools
5. **Future expansion space**: Placeholder tiles for upcoming tools

### Tool Tile Structure:
Each tool tile should display:
- Icon or image (optional)
- Tool name (e.g., "Lab Reports")
- Brief description (1-2 sentences)
- Click → Navigate to tool

## 7. Individual App Pages

Each app (Lab Reports, AI Tutor, etc.) must include:

1. **Header** (consistent across site)
2. **Breadcrumbs**: `Heim > [Section] > [App Name]`
3. **App-specific content**
4. **Footer with navigation**: Link back to hub and home

### App Deployment:
- Each app is a separate React build
- Deployed to its designated path (e.g., `/1-ar/lab-reports/`)
- Uses `basename` in React Router if needed
- Must handle its own routing within its path

## 8. This App's Details

> **NOTE**: Update this section for each repo

- **Repo Name**: `icelandic-chemistry-ai-tutor` (also known as `ai-tutor-app`)
- **Deployed To**:
  - `/1-ar/ai-tutor/` (1st year chemistry)
  - `/2-ar/ai-tutor/` (2nd year chemistry)
  - `/3-ar/ai-tutor/` (3rd year chemistry)
- **Purpose**: RAG-based AI teaching assistant that answers chemistry questions in Icelandic with citations from curriculum-aligned content. Provides 24/7 personalized learning support using Claude Sonnet 4 and OpenAI embeddings with ChromaDB vector search.
- **Current Status**: Active Development - MVP Phase (November 2025)
- **Technology**: React + TypeScript frontend, Python FastAPI backend, LangChain RAG pipeline
- **Funding**: RANNÍS Sprotasjóður 2025-2026 (3.6M ISK grant)

## 9. Deployment Notes

### Server Setup (nginx)
- All apps served from `/var/www/kvenno.app/`
- nginx configuration handles routing to correct directories
- Each React app built with `npm run build`
- Build outputs copied to appropriate subdirectories

### Build Commands:
```bash
npm run build
# Then copy build/* to /var/www/kvenno.app/[app-path]/
```

### Environment Variables:
Each app may need:
- `PUBLIC_URL` or `basename` for correct routing
- API endpoints if calling backend services
- Authentication tokens

## 10. Development Workflow with Claude Code

When working on any repo with Claude Code:

1. **Always start with**: "Read KVENNO-STRUCTURE.md first"
2. **Reference design system**: Use #f36b22, consistent button styles
3. **Include header**: Copy header component into your app
4. **Test navigation**: Make sure links work correctly
5. **Breadcrumbs**: Add appropriate breadcrumb trail
6. **Responsive**: Test on mobile sizes

### Updating This File:
When you make design decisions or structural changes:
1. Update KVENNO-STRUCTURE.md in one repo
2. Copy the updated file to all other repos
3. Ask Claude Code in each repo: "Review KVENNO-STRUCTURE.md and update this app to match current standards"

## 11. Icelandic Language

All user-facing text must be in Icelandic:
- "Heim" not "Home"
- "Til baka" not "Back"
- "Verkfæri" not "Tools"
- Consistent terminology across all apps

## 12. Authentication & Access Control

Some apps require teacher authentication:
- Lab Reports app: Teacher grading interface
- Future admin features

**Consistent login approach**:
- School Google account SSO (preferred)
- Backend handles authentication
- JWT tokens for session management
- Clear visual indication of login status

---

## Quick Reference

**Primary Color**: #f36b22  
**Max Width**: 1200px  
**Header Height**: ~60px  
**Button Radius**: 8px  

**Key Links**:
- Home: `/`
- 1st Year: `/1-ar/`
- 2nd Year: `/2-ar/`
- 3rd Year: `/3-ar/`
- Electives: `/val/`

---

*Last updated: 2024-11-20*  
*Maintainer: Siggi, Kvennaskólinn í Reykjavík*
