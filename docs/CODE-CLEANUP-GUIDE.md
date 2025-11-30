# Code Cleanup & Quality Audit Guide

Comprehensive guide for performing code cleanup, establishing workflows, and improving code quality across Kvenno.app repositories.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Code Quality & Standards](#phase-1-code-quality--standards)
4. [Phase 2: Development Workflows](#phase-2-development-workflows)
5. [Phase 3: Debugging Infrastructure](#phase-3-debugging-infrastructure)
6. [Phase 4: Project Organization](#phase-4-project-organization)
5. [Phase 5: Testing & Validation](#phase-5-testing--validation)
6. [Phase 6: Documentation Updates](#phase-6-documentation-updates)
7. [Technology-Specific Guidelines](#technology-specific-guidelines)
8. [Quality Checklist](#quality-checklist)

---

## Overview

### Purpose

This guide establishes consistent code quality, development workflows, and debugging infrastructure across all Kvenno.app repositories.

### Goals

- ✅ Consistent code style and quality
- ✅ Automated quality checks and CI/CD
- ✅ Professional development workflows
- ✅ Comprehensive debugging tools
- ✅ Well-organized project structure
- ✅ Complete and accurate documentation
- ✅ Testing infrastructure
- ✅ Easy developer onboarding

### Timeline

- **Small repository** (<10k lines): 2-3 hours
- **Medium repository** (10k-50k lines): 3-4 hours
- **Large repository** (>50k lines): 4-6 hours

---

## Prerequisites

### Required Tools

```bash
# Node.js (v18+)
node --version

# Package manager (npm, pnpm, or yarn)
pnpm --version  # or npm --version

# Git
git --version
```

### Before Starting

1. **Backup current state:**
   ```bash
   git checkout -b backup/pre-cleanup
   git push origin backup/pre-cleanup
   ```

2. **Create cleanup branch:**
   ```bash
   git checkout -b cleanup/code-quality-audit
   ```

3. **Create tracking document:**
   ```bash
   touch CLEANUP-PLAN.md
   ```

---

## Phase 1: Code Quality & Standards

### 1.1 ESLint Configuration

#### Install ESLint (if not present)

```bash
pnpm add -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser
# For React projects
pnpm add -D eslint-plugin-react-hooks
```

#### Create `.eslintrc.js`

**For TypeScript + React:**
```javascript
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended', // If React
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint'],
  rules: {
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'prefer-const': 'warn',
    'no-var': 'error',
  },
  ignorePatterns: ['dist', 'build', 'node_modules', '*.config.js'],
};
```

**For Node.js:**
```javascript
module.exports = {
  root: true,
  env: {
    node: true,
    es2021: true,
  },
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    '@typescript-eslint/no-explicit-any': 'warn',
    'no-console': 'off', // Allow console in Node.js
  },
};
```

#### Run and Fix

```bash
# Check for issues
pnpm eslint .

# Auto-fix what can be fixed
pnpm eslint . --fix
```

### 1.2 Prettier Configuration

#### Install Prettier

```bash
pnpm add -D prettier
```

#### Create `.prettierrc`

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

#### Create `.prettierignore`

```
# Dependencies
node_modules
pnpm-lock.yaml
package-lock.json
yarn.lock

# Build outputs
dist
build
out
.next
*.html

# Logs
*.log

# Config
.git
.github
```

#### Format Code

```bash
# Check formatting
pnpm prettier --check "**/*.{ts,tsx,js,jsx,json,md}"

# Format all files
pnpm prettier --write "**/*.{ts,tsx,js,jsx,json,md}"
```

### 1.3 TypeScript Configuration

#### Review `tsconfig.json`

Ensure strict mode is enabled (or work towards it):

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

#### Fix Type Errors

```bash
# Check types
pnpm tsc --noEmit

# Or if you have a type-check script
pnpm type-check
```

### 1.4 Remove Unused Code

**Find unused dependencies:**
```bash
# Install depcheck
pnpm add -D depcheck

# Run analysis
pnpm depcheck
```

**Remove unused imports:**
- Use ESLint's `no-unused-vars` rule
- Use IDE's "organize imports" feature
- Manually review and remove dead code

**Clean up comments:**
- Remove commented-out code
- Remove TODO comments for completed tasks
- Update outdated comments

### 1.5 Update package.json Scripts

Add quality scripts:

```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx,.js,.jsx",
    "lint:fix": "eslint . --ext .ts,.tsx,.js,.jsx --fix",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,md}\"",
    "format:check": "prettier --check \"**/*.{ts,tsx,js,jsx,json,md}\"",
    "type-check": "tsc --noEmit",
    "check-all": "pnpm type-check && pnpm lint && pnpm format:check",
    "validate": "pnpm install && pnpm check-all && pnpm build"
  }
}
```

### 1.6 Commit Phase 1

```bash
git add .eslintrc.js .prettierrc .prettierignore package.json tsconfig.json
git commit -m "chore: Set up code quality tools (ESLint, Prettier, TypeScript)"
git push origin cleanup/code-quality-audit
```

---

## Phase 2: Development Workflows

### 2.1 Development Scripts

Ensure package.json has all essential scripts:

```json
{
  "scripts": {
    "dev": "...",           // Start development server
    "build": "...",         // Production build
    "start": "...",         // Start production server (if applicable)
    "test": "...",          // Run tests
    "test:watch": "...",    // Run tests in watch mode
    "clean": "...",         // Clean build artifacts
    "validate": "pnpm install && pnpm check-all && pnpm build"
  }
}
```

### 2.2 Git Hooks (Optional but Recommended)

#### Install Husky

```bash
pnpm add -D husky lint-staged
pnpm exec husky init
```

#### Configure Pre-commit Hook

`.husky/pre-commit`:
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

pnpm lint-staged
```

#### Configure lint-staged

`package.json`:
```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md}": [
      "prettier --write"
    ]
  }
}
```

### 2.3 GitHub Actions CI/CD

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  quality:
    name: Code Quality
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Type check
        run: pnpm type-check

      - name: Lint
        run: pnpm lint

      - name: Format check
        run: pnpm format:check

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: quality

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build
        run: pnpm build

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: dist/
```

### 2.4 Create DEVELOPMENT.md

Create comprehensive development guide covering:

1. **Quick Start**
   - Prerequisites
   - Installation
   - Running development server

2. **Available Scripts**
   - Document all package.json scripts
   - Usage examples

3. **Development Workflow**
   - Branch strategy
   - Commit message format
   - Code review process

4. **Code Quality**
   - ESLint usage
   - Prettier usage
   - TypeScript guidelines

5. **Common Tasks**
   - Adding dependencies
   - Creating new features
   - Updating documentation

6. **Troubleshooting**
   - Common issues and solutions

### 2.5 Commit Phase 2

```bash
git add .github/ .husky/ package.json DEVELOPMENT.md
git commit -m "chore: Set up development workflows and CI/CD"
git push
```

---

## Phase 3: Debugging Infrastructure

### 3.1 VSCode Configuration

Create `.vscode/` directory with:

#### `launch.json` - Debug configurations

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Chrome",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}",
      "sourceMaps": true
    },
    {
      "name": "Debug Node",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/src/index.ts",
      "preLaunchTask": "tsc: build - tsconfig.json",
      "outFiles": ["${workspaceFolder}/dist/**/*.js"]
    }
  ]
}
```

#### `settings.json` - Workspace settings

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "files.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/.git": true
  }
}
```

#### `extensions.json` - Recommended extensions

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "usernamehw.errorlens"
  ]
}
```

### 3.2 Error Handling

**For React projects:**

Create error boundary component:

```typescript
// src/components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}
```

**For Node.js projects:**

Set up global error handlers:

```typescript
// src/utils/errorHandler.ts
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Application specific logging, throwing an error, or other logic
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});
```

### 3.3 Source Maps

Ensure source maps are enabled:

**Vite:**
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    sourcemap: true,
  },
});
```

**Webpack:**
```javascript
// webpack.config.js
module.exports = {
  devtool: 'source-map',
};
```

**TypeScript:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "sourceMap": true
  }
}
```

### 3.4 Create DEBUGGING.md

Create comprehensive debugging guide covering:

1. **Quick Start**
2. **VSCode Debugging**
3. **Browser DevTools**
4. **Common Scenarios**
5. **Performance Debugging**
6. **Tips & Tricks**

### 3.5 Commit Phase 3

```bash
git add .vscode/ src/components/ErrorBoundary.tsx DEBUGGING.md
git commit -m "feat: Set up debugging infrastructure and tools"
git push
```

---

## Phase 4: Project Organization

### 4.1 File Structure Review

Ensure consistent organization:

```
project/
├── src/                    # Source code
│   ├── components/        # Reusable components
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript types
│   ├── hooks/             # Custom hooks (React)
│   ├── services/          # API services
│   └── index.ts           # Entry point
├── tests/                 # Tests
├── docs/                  # Documentation
├── public/                # Static assets
├── dist/                  # Build output
└── config/                # Configuration files
```

### 4.2 File Naming Conventions

Establish and enforce conventions:

- **Components**: PascalCase (`UserProfile.tsx`)
- **Utilities**: camelCase (`formatDate.ts`)
- **Constants**: UPPER_SNAKE_CASE (`API_ENDPOINTS.ts`)
- **Types**: PascalCase (`User.types.ts`)
- **Tests**: Same as source + `.test.ts` (`formatDate.test.ts`)

### 4.3 Import Organization

Use consistent import order:

```typescript
// 1. External dependencies
import { useState } from 'react';
import axios from 'axios';

// 2. Internal absolute imports
import { Button } from '@/components/Button';
import { formatDate } from '@/utils/formatDate';

// 3. Relative imports
import { localHelper } from './helpers';

// 4. Types
import type { User } from '@/types';

// 5. Styles (if applicable)
import './styles.css';
```

### 4.4 Update .gitignore

Ensure comprehensive .gitignore:

```
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
build/
dist/
out/
.next/

# Misc
.DS_Store
*.log
.env
.env.local
.env.production

# Editor
.vscode/
.idea/
*.swp
*.swo

# OS
Thumbs.db
```

### 4.5 Commit Phase 4

```bash
git add .
git commit -m "refactor: Reorganize project structure and conventions"
git push
```

---

## Phase 5: Testing & Validation

### 5.1 Set Up Testing Framework

**For React:**
```bash
pnpm add -D vitest @testing-library/react @testing-library/jest-dom
```

**For Node:**
```bash
pnpm add -D vitest
```

### 5.2 Create Test Configuration

**vitest.config.ts:**
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom', // or 'node'
    setupFiles: './tests/setup.ts',
  },
});
```

### 5.3 Add Example Tests

```typescript
// src/utils/formatDate.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate } from './formatDate';

describe('formatDate', () => {
  it('formats date correctly', () => {
    const date = new Date('2025-01-15');
    expect(formatDate(date)).toBe('2025-01-15');
  });
});
```

### 5.4 Update Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest --coverage"
  }
}
```

### 5.5 Create Validation Script

Add comprehensive validation:

```json
{
  "scripts": {
    "validate": "pnpm install && pnpm type-check && pnpm lint && pnpm test && pnpm build"
  }
}
```

### 5.6 Commit Phase 5

```bash
git add tests/ vitest.config.ts package.json
git commit -m "test: Set up testing infrastructure"
git push
```

---

## Phase 6: Documentation Updates

### 6.1 Update README.md

Ensure README includes:

1. **Project Title & Description**
2. **Badges** (build status, version, license)
3. **Features**
4. **Quick Start**
5. **Installation**
6. **Usage Examples**
7. **Available Scripts**
8. **Project Structure**
9. **Contributing Guidelines**
10. **License**

### 6.2 Create/Update Additional Docs

- **CONTRIBUTING.md** - How to contribute
- **CHANGELOG.md** - Version history
- **LICENSE** - License information
- **CODE_OF_CONDUCT.md** - Code of conduct (if public)

### 6.3 Document Dependencies

Add comments explaining major dependencies:

```json
{
  "dependencies": {
    "react": "^18.2.0",     // UI library
    "axios": "^1.6.0",      // HTTP client
    "zod": "^3.22.0"        // Schema validation
  }
}
```

### 6.4 Add Inline Documentation

Ensure functions have JSDoc comments:

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

### 6.5 Commit Phase 6

```bash
git add README.md CONTRIBUTING.md CHANGELOG.md docs/
git commit -m "docs: Update all documentation"
git push
```

---

## Technology-Specific Guidelines

### React Projects

- ✅ Use function components with hooks
- ✅ Implement ErrorBoundary
- ✅ Use TypeScript for props
- ✅ Organize by feature, not file type
- ✅ Use React DevTools for debugging

### Node.js Projects

- ✅ Use ES modules (`"type": "module"`)
- ✅ Implement global error handlers
- ✅ Use environment variables properly
- ✅ Add health check endpoints
- ✅ Use proper logging (winston, pino)

### Next.js Projects

- ✅ Use App Router if possible
- ✅ Implement proper SEO
- ✅ Optimize images with next/image
- ✅ Use Server Components where applicable
- ✅ Configure proper caching

### Vue.js Projects

- ✅ Use Composition API
- ✅ Implement proper TypeScript support
- ✅ Use Vue DevTools
- ✅ Follow official style guide
- ✅ Organize by feature

---

## Quality Checklist

### Code Quality
- [ ] ESLint configured and passing
- [ ] Prettier configured and code formatted
- [ ] TypeScript strict mode enabled (or working towards it)
- [ ] No unused dependencies
- [ ] No dead code
- [ ] No TODO comments for completed items

### Development Workflows
- [ ] All essential scripts present
- [ ] Git hooks configured (optional)
- [ ] CI/CD pipeline set up
- [ ] DEVELOPMENT.md guide created
- [ ] VSCode workspace configured

### Debugging
- [ ] VSCode debugging configurations
- [ ] Error boundaries implemented (React)
- [ ] Source maps enabled
- [ ] DEBUGGING.md guide created
- [ ] Error handling in place

### Project Organization
- [ ] Consistent file structure
- [ ] File naming conventions followed
- [ ] Import organization consistent
- [ ] .gitignore comprehensive and up-to-date

### Testing
- [ ] Testing framework set up
- [ ] Example tests created
- [ ] Test scripts in package.json
- [ ] Coverage reporting configured

### Documentation
- [ ] README.md comprehensive and current
- [ ] DEVELOPMENT.md created
- [ ] DEBUGGING.md created
- [ ] CONTRIBUTING.md present (if needed)
- [ ] Inline JSDoc comments added
- [ ] All scripts documented

### Final Validation
- [ ] `pnpm validate` passes
- [ ] CI/CD pipeline passes
- [ ] All documentation reviewed
- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] Code properly formatted

---

## Completion

### Create Pull Request

```bash
# Ensure all changes are committed
git status

# Push final changes
git push origin cleanup/code-quality-audit

# Create PR via GitHub CLI or web interface
gh pr create --title "Code Quality Audit & Cleanup" --body "Comprehensive code cleanup following Kvenno.app standards"
```

### Update CLEANUP-PLAN.md

Mark all phases as complete:

```markdown
# Code Cleanup Plan

## Status: COMPLETED ✅

### Phase 1: Code Quality & Standards ✅
- [x] ESLint configured
- [x] Prettier configured
- [x] TypeScript strict mode
- [x] Unused code removed
- [x] Scripts updated

### Phase 2: Development Workflows ✅
- [x] Development scripts
- [x] Git hooks
- [x] CI/CD pipeline
- [x] DEVELOPMENT.md

### Phase 3: Debugging Infrastructure ✅
- [x] VSCode configurations
- [x] Error handling
- [x] Source maps
- [x] DEBUGGING.md

### Phase 4: Project Organization ✅
- [x] File structure
- [x] Naming conventions
- [x] Import organization
- [x] .gitignore updated

### Phase 5: Testing & Validation ✅
- [x] Testing framework
- [x] Example tests
- [x] Validation script

### Phase 6: Documentation ✅
- [x] README.md updated
- [x] Additional docs created
- [x] Dependencies documented
- [x] Inline documentation
```

---

## Post-Cleanup

### Merge to Main

After PR review and approval:

```bash
git checkout main
git pull origin main
git merge cleanup/code-quality-audit
git push origin main
```

### Delete Cleanup Branch

```bash
git branch -d cleanup/code-quality-audit
git push origin --delete cleanup/code-quality-audit
```

### Team Communication

Notify team of changes:
- New scripts available
- CI/CD requirements
- Git hooks (if added)
- Documentation updates

---

## Maintenance

### Regular Cleanup

Schedule regular cleanups:
- **Monthly**: Review dependencies, update docs
- **Quarterly**: Full audit using this guide
- **Annually**: Major refactoring if needed

### Keep Tools Updated

```bash
# Update dependencies
pnpm update --latest

# Check for security vulnerabilities
pnpm audit

# Update Node.js to LTS
nvm install --lts
```

---

## Resources

- [ESLint Documentation](https://eslint.org/)
- [Prettier Documentation](https://prettier.io/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vitest Documentation](https://vitest.dev/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Last Updated:** 2025-11-29
**Version:** 1.0.0
**Maintained by:** Kvenno.app Development Team
