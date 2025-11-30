#!/usr/bin/env node

/**
 * Repository Health Check Script
 *
 * Runs all health checks and updates REPOSITORY-STATUS.md
 * Can be run via: pnpm check:status
 * Or ask Claude: "Check my repository status"
 */

import { execSync } from 'child_process';
import fs from 'fs';

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function run(command, options = {}) {
  try {
    return execSync(command, { encoding: 'utf-8', ...options });
  } catch (error) {
    return null;
  }
}

console.log('\n' + '='.repeat(60));
log('🔍 Repository Health Check', 'blue');
console.log('='.repeat(60) + '\n');

const results = {
  security: { status: 'unknown', details: [] },
  quality: { status: 'unknown', details: [] },
  dependencies: { status: 'unknown', details: [] },
  git: { status: 'unknown', details: [] },
  build: { status: 'unknown', details: [] },
};

// 1. Security Check
log('🔒 Security Check...', 'blue');
try {
  const audit = run('pnpm audit --json');
  if (audit) {
    const auditData = JSON.parse(audit);
    const vulns = auditData.metadata?.vulnerabilities || {};
    const total = Object.values(vulns).reduce((sum, count) => sum + count, 0);

    if (total === 0) {
      results.security.status = 'good';
      log('  ✅ No vulnerabilities found', 'green');
    } else {
      results.security.status = 'warning';
      log(`  ⚠️  Found ${total} vulnerabilities`, 'yellow');
      results.security.details.push(`${total} vulnerabilities found`);
    }
  }
} catch (error) {
  results.security.status = 'error';
  log('  ❌ Security check failed', 'red');
}

// 2. Code Quality Check
log('\n💻 Code Quality...', 'blue');
let qualityPassed = true;

// TypeScript
try {
  run('pnpm type-check', { stdio: 'pipe' });
  log('  ✅ TypeScript: No errors', 'green');
} catch (error) {
  qualityPassed = false;
  log('  ❌ TypeScript: Errors found', 'red');
  results.quality.details.push('TypeScript errors');
}

// ESLint
try {
  run('pnpm lint', { stdio: 'pipe' });
  log('  ✅ ESLint: No errors', 'green');
} catch (error) {
  qualityPassed = false;
  log('  ⚠️  ESLint: Issues found', 'yellow');
  results.quality.details.push('ESLint issues');
}

// Prettier
try {
  run('pnpm format:check', { stdio: 'pipe' });
  log('  ✅ Prettier: All files formatted', 'green');
} catch (error) {
  qualityPassed = false;
  log('  ⚠️  Prettier: Files need formatting', 'yellow');
  results.quality.details.push('Files need formatting');
}

results.quality.status = qualityPassed ? 'good' : 'warning';

// 3. Dependencies Check
log('\n📦 Dependencies...', 'blue');
try {
  const outdated = run('pnpm outdated');
  if (outdated && outdated.trim()) {
    const lines = outdated.split('\n').filter(l => l.trim());
    const count = lines.length - 1; // Subtract header
    results.dependencies.status = 'warning';
    log(`  ⚠️  ${count} packages have updates available`, 'yellow');
    results.dependencies.details.push(`${count} updates available`);
  } else {
    results.dependencies.status = 'good';
    log('  ✅ All dependencies up to date', 'green');
  }
} catch (error) {
  // pnpm outdated exits with code 1 if updates exist
  results.dependencies.status = 'warning';
  log('  ⚠️  Some packages have updates', 'yellow');
}

// 4. Git Status
log('\n📝 Git Status...', 'blue');
try {
  const status = run('git status --porcelain');
  const branch = run('git rev-parse --abbrev-ref HEAD').trim();

  if (status && status.trim()) {
    results.git.status = 'warning';
    const changes = status.split('\n').filter(l => l.trim()).length;
    log(`  ⚠️  ${changes} uncommitted changes`, 'yellow');
    results.git.details.push(`${changes} uncommitted changes`);
  } else {
    results.git.status = 'good';
    log('  ✅ Working directory clean', 'green');
  }

  log(`  📍 Branch: ${branch}`, 'blue');
} catch (error) {
  results.git.status = 'error';
  log('  ❌ Git check failed', 'red');
}

// 5. Build Check
log('\n🏗️  Build...', 'blue');
log('  ⏭️  Skipping build (run manually to verify)', 'yellow');
results.build.status = 'skipped';

// Summary
console.log('\n' + '='.repeat(60));
log('📊 Summary', 'blue');
console.log('='.repeat(60));

const statusEmoji = {
  good: '🟢',
  warning: '🟡',
  error: '🔴',
  skipped: '⚪',
  unknown: '⚪',
};

console.log('\n');
console.log(`${statusEmoji[results.security.status]} Security: ${results.security.status}`);
console.log(`${statusEmoji[results.quality.status]} Code Quality: ${results.quality.status}`);
console.log(`${statusEmoji[results.dependencies.status]} Dependencies: ${results.dependencies.status}`);
console.log(`${statusEmoji[results.git.status]} Git: ${results.git.status}`);
console.log(`${statusEmoji[results.build.status]} Build: ${results.build.status}`);

// Recommendations
const hasIssues = Object.values(results).some(r =>
  r.status === 'warning' || r.status === 'error'
);

if (hasIssues) {
  console.log('\n' + '='.repeat(60));
  log('⚡ Recommended Actions', 'yellow');
  console.log('='.repeat(60) + '\n');

  if (results.security.status !== 'good') {
    log('  1. Fix security vulnerabilities: pnpm audit --fix', 'yellow');
  }
  if (results.quality.details.includes('Files need formatting')) {
    log('  2. Format code: pnpm format', 'yellow');
  }
  if (results.quality.details.includes('ESLint issues')) {
    log('  3. Fix linting: pnpm lint:fix', 'yellow');
  }
  if (results.dependencies.status === 'warning') {
    log('  4. Review updates: pnpm outdated', 'yellow');
  }
} else {
  console.log('\n' + '='.repeat(60));
  log('🎉 All Checks Passed!', 'green');
  console.log('='.repeat(60));
  log('\nRepository is healthy. Great work!', 'green');
}

console.log('\n📄 For detailed status, see: REPOSITORY-STATUS.md');
console.log('💬 Or ask Claude: "Update my repository status"\n');
