# Azure AD Implementation Checklist

Use this checklist to track your progress implementing Azure AD authentication for the AI Tutor app.

## Phase 1: Azure Portal Setup

- [ ] **Access Azure Portal**
  - [ ] Obtain administrator access to Azure Portal
  - [ ] Can navigate to "App registrations"

- [ ] **Create App Registration**
  - [ ] Created new app registration named "Kvenno Chemistry AI Tutor"
  - [ ] Selected "Single tenant" account type
  - [ ] Added initial redirect URI for SPA

- [ ] **Document Credentials**
  - [ ] Copied Application (client) ID
  - [ ] Copied Directory (tenant) ID
  - [ ] Saved credentials securely (NOT in git)

- [ ] **Configure Redirect URIs**
  - [ ] Added `https://kvenno.app/1-ar/ai-tutor/`
  - [ ] Added `https://kvenno.app/2-ar/ai-tutor/`
  - [ ] Added `https://kvenno.app/3-ar/ai-tutor/`
  - [ ] Added `http://localhost:5173/` (for development)

- [ ] **Configure Token Settings**
  - [ ] Enabled "Access tokens"
  - [ ] Enabled "ID tokens"
  - [ ] Saved authentication settings

- [ ] **Set API Permissions**
  - [ ] Verified `User.Read` permission exists
  - [ ] (Optional) Added additional permissions if needed
  - [ ] (Optional) Granted admin consent

## Phase 2: Install Dependencies

- [ ] **Navigate to frontend directory**
  ```bash
  cd frontend
  ```

- [ ] **Install MSAL packages**
  - [ ] Installed `@azure/msal-browser`
  - [ ] Installed `@azure/msal-react`
  - [ ] Verified packages in `package.json`

- [ ] **Verify TypeScript types**
  - [ ] Types auto-installed or manually added

## Phase 3: Environment Configuration

- [ ] **Create `.env` file**
  - [ ] Created `frontend/.env`
  - [ ] Added `VITE_AZURE_CLIENT_ID`
  - [ ] Added `VITE_AZURE_TENANT_ID`
  - [ ] Verified values match Azure Portal

- [ ] **Update `.env.example`**
  - [ ] Created/updated `frontend/.env.example`
  - [ ] Used placeholder values (not real credentials)
  - [ ] Documented all required variables

- [ ] **Verify `.gitignore`**
  - [ ] Confirmed `.env` is in `.gitignore`
  - [ ] Confirmed `.env` is NOT committed to git
  - [ ] Double-checked no credentials in git history

## Phase 4: Create MSAL Configuration

- [ ] **Create auth config file**
  - [ ] Created `frontend/src/config/authConfig.ts`
  - [ ] Configured `msalConfig` with client ID and tenant ID
  - [ ] Set `redirectUri` to use `VITE_BASE_PATH`
  - [ ] Configured cache location (sessionStorage or localStorage)
  - [ ] Added logger options for debugging

- [ ] **Define login request scopes**
  - [ ] Created `loginRequest` with `User.Read` scope
  - [ ] Exported configuration for use in app

- [ ] **Add validation**
  - [ ] Added checks for missing environment variables
  - [ ] Added console warnings for configuration issues

## Phase 5: Create Authentication Context

- [ ] **Create AuthContext file**
  - [ ] Created `frontend/src/contexts/AuthContext.tsx`
  - [ ] Defined `AuthContextType` interface
  - [ ] Created `AuthProvider` component
  - [ ] Created `useAuth` hook

- [ ] **Implement authentication methods**
  - [ ] Implemented `login()` function (redirect)
  - [ ] Implemented `logout()` function (redirect)
  - [ ] Exposed `isAuthenticated` state
  - [ ] Exposed `account` information

- [ ] **Add role detection**
  - [ ] Defined `TEACHER_EMAILS` array
  - [ ] Implemented `isTeacher` logic
  - [ ] Exported `isTeacher` in context

## Phase 6: Update Main Entry Point

- [ ] **Update `main.tsx`**
  - [ ] Imported MSAL components
  - [ ] Created `PublicClientApplication` instance
  - [ ] Wrapped app with `MsalProvider`
  - [ ] Verified app still runs

## Phase 7: Update App Component

- [ ] **Update `App.tsx`**
  - [ ] Imported `AuthenticatedTemplate` and `UnauthenticatedTemplate`
  - [ ] Wrapped app with `AuthProvider`
  - [ ] Added authenticated view (existing chat interface)
  - [ ] Added unauthenticated view (login page)
  - [ ] Tested conditional rendering

## Phase 8: Create Login Page

- [ ] **Create LoginPage component**
  - [ ] Created `frontend/src/components/LoginPage.tsx`
  - [ ] Designed login UI with Kvenno branding
  - [ ] Added "Skrá inn með Microsoft" button
  - [ ] Connected button to `login()` function
  - [ ] Used correct Icelandic text
  - [ ] Applied design system colors (#f36b22)

- [ ] **Test login page appearance**
  - [ ] Verified layout is centered and responsive
  - [ ] Checked mobile view
  - [ ] Verified branding matches site standards

## Phase 9: Update Site Header

- [ ] **Add logout functionality to SiteHeader**
  - [ ] Imported `useAuth` hook
  - [ ] Added logout button for authenticated users
  - [ ] Displayed user name in header
  - [ ] Tested logout flow

- [ ] **Optional: Add user menu**
  - [ ] Created dropdown menu for user options
  - [ ] Added profile link
  - [ ] Added settings link

## Phase 10: Local Testing

- [ ] **Run development server**
  ```bash
  npm run dev
  ```

- [ ] **Test unauthenticated state**
  - [ ] Visited `http://localhost:5173`
  - [ ] Saw login page (not chat interface)
  - [ ] Verified branding and text

- [ ] **Test authentication flow**
  - [ ] Clicked "Skrá inn með Microsoft"
  - [ ] Redirected to Microsoft login page
  - [ ] Entered test account credentials
  - [ ] Redirected back to app
  - [ ] Saw chat interface (authenticated view)

- [ ] **Test logout**
  - [ ] Clicked logout button
  - [ ] Redirected to login page
  - [ ] Confirmed tokens cleared

- [ ] **Test token persistence**
  - [ ] Logged in
  - [ ] Refreshed page
  - [ ] Still authenticated (didn't need to log in again)

## Phase 11: Production Deployment

- [ ] **Prepare environment variables**
  - [ ] Set `VITE_AZURE_CLIENT_ID` for production
  - [ ] Set `VITE_AZURE_TENANT_ID` for production
  - [ ] Documented where these are stored (build server, CI/CD)

- [ ] **Build for each path**
  - [ ] Built with `VITE_BASE_PATH=/1-ar/ai-tutor/`
  - [ ] Built with `VITE_BASE_PATH=/2-ar/ai-tutor/`
  - [ ] Built with `VITE_BASE_PATH=/3-ar/ai-tutor/`

- [ ] **Deploy to server**
  - [ ] Used `deploy-all-paths.sh` script
  - [ ] Or manually deployed each build to correct path
  - [ ] Verified files copied to correct directories

- [ ] **Set file permissions**
  - [ ] Owned by `www-data:www-data`
  - [ ] Permissions set to `755`

## Phase 12: Production Testing

- [ ] **Test Path 1: /1-ar/ai-tutor/**
  - [ ] Visited `https://kvenno.app/1-ar/ai-tutor/`
  - [ ] Saw login page
  - [ ] Logged in successfully
  - [ ] Redirected to correct path after login
  - [ ] Chat interface loaded
  - [ ] Breadcrumbs show "Heim > 1. ár > AI Kennsluaðili"
  - [ ] Logout works

- [ ] **Test Path 2: /2-ar/ai-tutor/**
  - [ ] Visited `https://kvenno.app/2-ar/ai-tutor/`
  - [ ] Saw login page
  - [ ] Logged in successfully
  - [ ] Redirected to correct path after login
  - [ ] Chat interface loaded
  - [ ] Breadcrumbs show "Heim > 2. ár > AI Kennsluaðili"
  - [ ] Logout works

- [ ] **Test Path 3: /3-ar/ai-tutor/**
  - [ ] Visited `https://kvenno.app/3-ar/ai-tutor/`
  - [ ] Saw login page
  - [ ] Logged in successfully
  - [ ] Redirected to correct path after login
  - [ ] Chat interface loaded
  - [ ] Breadcrumbs show "Heim > 3. ár > AI Kennsluaðili"
  - [ ] Logout works

- [ ] **Cross-browser testing**
  - [ ] Tested in Chrome
  - [ ] Tested in Firefox
  - [ ] Tested in Safari (if applicable)
  - [ ] Tested in Edge

- [ ] **Mobile testing**
  - [ ] Tested on iOS Safari
  - [ ] Tested on Android Chrome
  - [ ] Login flow works on mobile
  - [ ] UI is responsive

## Phase 13: Role-Based Access (Future)

- [ ] **Teacher identification**
  - [ ] Teacher emails configured
  - [ ] Teachers can access teacher features
  - [ ] Students cannot access teacher features

- [ ] **Backend validation**
  - [ ] Server-side role checking implemented
  - [ ] API endpoints validate teacher status
  - [ ] Sensitive operations protected

## Phase 14: Monitoring & Maintenance

- [ ] **Error monitoring**
  - [ ] Authentication errors logged
  - [ ] Failed login attempts tracked
  - [ ] Redirect errors monitored

- [ ] **Token refresh testing**
  - [ ] Verified tokens refresh automatically
  - [ ] No "session expired" errors for active users

- [ ] **Security audit**
  - [ ] No credentials in git
  - [ ] No credentials in client-side code
  - [ ] Tokens stored securely by MSAL
  - [ ] Logout properly clears all tokens

## Phase 15: Documentation

- [ ] **Update project README**
  - [ ] Documented Azure AD requirement
  - [ ] Added setup instructions
  - [ ] Listed environment variables

- [ ] **Update deployment docs**
  - [ ] Documented multi-path deployment with auth
  - [ ] Added redirect URI registration steps
  - [ ] Documented environment variable management

- [ ] **Create troubleshooting guide**
  - [ ] Common authentication errors
  - [ ] Solutions for redirect issues
  - [ ] Token refresh problems

---

## Completion Status

**Overall Progress**: ⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️ 0%

Update this as you complete each phase!

---

**Last Updated**: 2025-11-22
**Maintainer**: Sigurdur Vilhelmsson, Kvennaskólinn í Reykjavík
