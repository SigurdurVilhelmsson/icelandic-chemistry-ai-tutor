# Azure AD Implementation Guide

Step-by-step guide for implementing Azure AD authentication in the Icelandic Chemistry AI Tutor.

## Prerequisites

Before starting:
- [ ] Access to Azure Portal with app registration permissions
- [ ] Node.js and npm installed
- [ ] Existing AI Tutor codebase cloned
- [ ] Understanding of React and TypeScript

## Part 1: Azure Portal Setup

### Step 1: Create App Registration

1. **Log in to Azure Portal**:
   - Go to https://portal.azure.com
   - Sign in with administrator account

2. **Navigate to App Registrations**:
   - Search for "Azure Active Directory" or "Microsoft Entra ID"
   - Click "App registrations" in left sidebar
   - Click "+ New registration"

3. **Configure the registration**:
   ```
   Name: Kvenno Chemistry AI Tutor
   Supported account types: Single tenant (Kvennaskólinn organization only)
   Redirect URI:
     - Platform: Single-page application (SPA)
     - URI: https://kvenno.app/1-ar/ai-tutor/
   ```

4. **Click "Register"**

### Step 2: Note Your Credentials

After registration, you'll see:

- **Application (client) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Directory (tenant) ID**: `yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy`

**Save these values** - you'll need them for environment variables.

### Step 3: Add Additional Redirect URIs

Since the app is deployed to three paths, add redirect URIs for all:

1. Go to "Authentication" in left sidebar
2. Under "Single-page application", click "+ Add URI"
3. Add these redirect URIs:
   ```
   https://kvenno.app/1-ar/ai-tutor/
   https://kvenno.app/2-ar/ai-tutor/
   https://kvenno.app/3-ar/ai-tutor/
   http://localhost:5173/ (for development)
   ```
4. Click "Save"

### Step 4: Configure Token Settings

1. Still in "Authentication":
   - ✅ Access tokens (used for implicit flows)
   - ✅ ID tokens (used for implicit and hybrid flows)

2. Click "Save"

### Step 5: API Permissions (Optional)

The basic setup doesn't require additional permissions, but if you need user profile info:

1. Go to "API permissions"
2. Default permission is already there: `User.Read`
3. If needed, add additional permissions and grant admin consent

## Part 2: Install MSAL Packages

```bash
cd frontend

# Install MSAL libraries
npm install @azure/msal-browser @azure/msal-react

# Install types (if not auto-installed)
npm install --save-dev @types/node
```

## Part 3: Configure Environment Variables

1. **Create `.env` file** in `frontend/`:
   ```bash
   # Azure AD Configuration
   VITE_AZURE_CLIENT_ID=your-client-id-from-step-2
   VITE_AZURE_TENANT_ID=your-tenant-id-from-step-2

   # API endpoint (if needed)
   VITE_API_ENDPOINT=http://localhost:8000

   # Base path (for multi-path deployment)
   VITE_BASE_PATH=/
   ```

2. **Update `.env.example`**:
   ```bash
   # Copy .env to .env.example but use placeholder values
   VITE_AZURE_CLIENT_ID=your-azure-client-id-here
   VITE_AZURE_TENANT_ID=your-azure-tenant-id-here
   VITE_API_ENDPOINT=http://localhost:8000
   VITE_BASE_PATH=/
   ```

3. **Verify `.gitignore` includes `.env`**:
   ```
   # .gitignore
   .env
   .env.local
   ```

## Part 4: Create MSAL Configuration

Create `frontend/src/config/authConfig.ts`:

```typescript
import { Configuration, RedirectRequest } from '@azure/msal-browser';

/**
 * MSAL Configuration
 * See: https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-browser
 */

// Azure AD credentials from environment variables
export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID || '',
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID || ''}`,
    redirectUri: window.location.origin + (import.meta.env.VITE_BASE_PATH || '/'),
  },
  cache: {
    cacheLocation: 'sessionStorage', // "sessionStorage" or "localStorage"
    storeAuthStateInCookie: false, // Set to true for IE11/Edge
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return;

        switch (level) {
          case 0: // Error
            console.error(message);
            break;
          case 1: // Warning
            console.warn(message);
            break;
          case 2: // Info
            console.info(message);
            break;
          case 3: // Verbose
            console.debug(message);
            break;
        }
      },
    },
  },
};

/**
 * Scopes for login request
 * "User.Read" allows the app to read the user's profile
 */
export const loginRequest: RedirectRequest = {
  scopes: ['User.Read'],
};

/**
 * Validate configuration
 */
if (!msalConfig.auth.clientId || !import.meta.env.VITE_AZURE_TENANT_ID) {
  console.error(
    'Azure AD configuration missing! Please set VITE_AZURE_CLIENT_ID and VITE_AZURE_TENANT_ID in .env file'
  );
}
```

## Part 5: Create Authentication Context

Create `frontend/src/contexts/AuthContext.tsx`:

```typescript
import React, { createContext, useContext, ReactNode } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { AccountInfo } from '@azure/msal-browser';

interface AuthContextType {
  isAuthenticated: boolean;
  account: AccountInfo | null;
  login: () => void;
  logout: () => void;
  isTeacher: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const account = accounts[0] || null;

  // Check if user is a teacher (based on email)
  // TODO: Move to centralized configuration or backend
  const TEACHER_EMAILS = [
    'teacher1@kvenno.is',
    'teacher2@kvenno.is',
    // Add more teacher emails here
  ];

  const isTeacher = account ? TEACHER_EMAILS.includes(account.username) : false;

  const login = () => {
    instance.loginRedirect({
      scopes: ['User.Read'],
    });
  };

  const logout = () => {
    instance.logoutRedirect({
      postLogoutRedirectUri: window.location.origin + (import.meta.env.VITE_BASE_PATH || '/'),
    });
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        account,
        login,
        logout,
        isTeacher,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

## Part 6: Update Main App

Update `frontend/src/main.tsx`:

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from './config/authConfig';
import App from './App';
import './index.css';

// Create MSAL instance
const msalInstance = new PublicClientApplication(msalConfig);

// Initialize MSAL
await msalInstance.initialize();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MsalProvider instance={msalInstance}>
      <App />
    </MsalProvider>
  </React.StrictMode>
);
```

## Part 7: Wrap App with Auth Provider

Update `frontend/src/App.tsx`:

```typescript
import React from 'react';
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import { ChatProvider } from './contexts/ChatContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ChatInterface } from './components/ChatInterface';
import { SiteHeader } from './components/SiteHeader';
import { Breadcrumbs } from './components/Breadcrumbs';
import { LoginPage } from './components/LoginPage';
import { detectYearFromPath } from './utils/navigation';

function AppContent() {
  const { isAuthenticated } = useAuth();
  const currentYear = detectYearFromPath();

  return (
    <>
      <AuthenticatedTemplate>
        <div className="flex flex-col h-screen overflow-hidden">
          <SiteHeader />
          <Breadcrumbs year={currentYear} appName="AI Kennsluaðili" />
          <div className="flex-1 overflow-hidden">
            <ChatInterface currentYear={currentYear} />
          </div>
        </div>
      </AuthenticatedTemplate>

      <UnauthenticatedTemplate>
        <LoginPage />
      </UnauthenticatedTemplate>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <AppContent />
      </ChatProvider>
    </AuthProvider>
  );
}

export default App;
```

## Part 8: Create Login Page Component

Create `frontend/src/components/LoginPage.tsx`:

```typescript
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { SiteHeader } from './SiteHeader';

export function LoginPage() {
  const { login } = useAuth();

  return (
    <div className="flex flex-col h-screen">
      <SiteHeader />

      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full mx-4 bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold mb-4 text-center" style={{ color: '#f36b22' }}>
            AI Kennsluaðili - Efnafræði
          </h1>

          <p className="text-gray-600 mb-6 text-center">
            Skráðu þig inn með Kvennó aðgangi til að nota AI kennsluaðilann.
          </p>

          <button
            onClick={login}
            className="w-full py-3 px-6 rounded-lg font-medium text-white transition-all hover:opacity-90"
            style={{ backgroundColor: '#f36b22' }}
          >
            Skrá inn með Microsoft
          </button>

          <p className="text-sm text-gray-500 mt-4 text-center">
            Notaðu @kvenno.is netfangið þitt til að skrá þig inn
          </p>
        </div>
      </div>
    </div>
  );
}
```

## Part 9: Update SiteHeader with Logout

Update `frontend/src/components/SiteHeader.tsx` to include logout functionality:

```typescript
import { useAuth } from '../contexts/AuthContext';

export function SiteHeader() {
  const { isAuthenticated, account, logout } = useAuth();

  // ... existing code ...

  // Add logout button for authenticated users
  {isAuthenticated && (
    <button
      onClick={logout}
      className="header-btn px-4 py-2 rounded-lg font-medium transition-all hover:bg-gray-50"
      style={{
        border: '2px solid #f36b22',
        color: '#f36b22'
      }}
    >
      Útskrá ({account?.name})
    </button>
  )}
```

## Part 10: Test Authentication

### Local Testing

1. **Start dev server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Visit** `http://localhost:5173`

3. **Expected behavior**:
   - Should show login page
   - Click "Skrá inn með Microsoft"
   - Redirects to Microsoft login
   - After login, redirects back to app
   - Should show chat interface

### Production Testing

After deploying to each path, test:

1. Visit `https://kvenno.app/1-ar/ai-tutor/`
   - Should redirect to Microsoft login
   - After login, should return to `/1-ar/ai-tutor/`

2. Repeat for `/2-ar/ai-tutor/` and `/3-ar/ai-tutor/`

3. Test logout functionality

## Part 11: Deploy

Use the multi-path deployment script:

```bash
# Set environment variables for production
export VITE_AZURE_CLIENT_ID=your-production-client-id
export VITE_AZURE_TENANT_ID=your-production-tenant-id

# Run deployment script
./scripts/deploy-all-paths.sh
```

## Troubleshooting

### "AADSTS50011: The reply URL does not match"

**Solution**: Add the exact redirect URI to Azure AD app registration

### "User not authenticated after redirect"

**Solution**:
- Check browser console for errors
- Verify client ID and tenant ID are correct
- Clear browser cache and cookies

### "Cannot read property 'login' of undefined"

**Solution**: Ensure AuthProvider wraps your components

### Tokens not persisting

**Solution**: Check `cacheLocation` in msalConfig (use "localStorage" instead of "sessionStorage")

## Next Steps

- [ ] Implement teacher-only features
- [ ] Add server-side token validation for API calls
- [ ] Set up monitoring for authentication failures
- [ ] Add session timeout warnings
- [ ] Implement refresh token rotation

## Resources

- [MSAL React Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react)
- [Azure AD Documentation](https://docs.microsoft.com/en-us/azure/active-directory/)
- [MSAL Browser Samples](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/samples/msal-browser-samples)

---

**Last Updated**: 2025-11-22
**Maintainer**: Sigurdur Vilhelmsson, Kvennaskólinn í Reykjavík
