# Azure AD Quick Reference

Quick lookups for common Azure AD authentication tasks while coding.

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [MSAL Configuration](#msal-configuration)
3. [React Hooks](#react-hooks)
4. [Common Patterns](#common-patterns)
5. [TypeScript Types](#typescript-types)
6. [Troubleshooting](#troubleshooting)

---

## Environment Variables

### Required Variables

```bash
# .env
VITE_AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VITE_AZURE_TENANT_ID=yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy

# Optional
VITE_BASE_PATH=/1-ar/ai-tutor/
VITE_API_ENDPOINT=http://localhost:8000
```

### Accessing in Code

```typescript
// Vite uses import.meta.env
const clientId = import.meta.env.VITE_AZURE_CLIENT_ID;
const tenantId = import.meta.env.VITE_AZURE_TENANT_ID;
```

---

## MSAL Configuration

### Basic Config

```typescript
import { Configuration } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID}`,
    redirectUri: window.location.origin + (import.meta.env.VITE_BASE_PATH || '/'),
  },
  cache: {
    cacheLocation: 'sessionStorage', // or 'localStorage'
    storeAuthStateInCookie: false,
  },
};
```

### Login Request Scopes

```typescript
import { RedirectRequest } from '@azure/msal-browser';

export const loginRequest: RedirectRequest = {
  scopes: ['User.Read'], // Minimum scope for basic profile
};

// For additional scopes:
export const apiLoginRequest: RedirectRequest = {
  scopes: ['User.Read', 'email', 'profile'],
};
```

---

## React Hooks

### `useMsal()` Hook

Get MSAL instance and accounts:

```typescript
import { useMsal } from '@azure/msal-react';

function MyComponent() {
  const { instance, accounts, inProgress } = useMsal();

  // instance: MSAL PublicClientApplication
  // accounts: Array of AccountInfo objects
  // inProgress: "login" | "logout" | "none" | "acquireToken"

  const account = accounts[0]; // Get first account
}
```

### `useIsAuthenticated()` Hook

Check authentication status:

```typescript
import { useIsAuthenticated } from '@azure/msal-react';

function MyComponent() {
  const isAuthenticated = useIsAuthenticated();

  if (isAuthenticated) {
    return <div>Logged in!</div>;
  }
  return <div>Not logged in</div>;
}
```

### `useAccount()` Hook

Get specific account info:

```typescript
import { useAccount } from '@azure/msal-react';

function MyComponent() {
  const account = useAccount();

  if (account) {
    console.log(account.name); // User's name
    console.log(account.username); // Email address
    console.log(account.localAccountId); // Unique ID
  }
}
```

### Custom `useAuth()` Hook (Our Implementation)

```typescript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { isAuthenticated, account, login, logout, isTeacher } = useAuth();

  return (
    <div>
      {isAuthenticated ? (
        <>
          <p>Welcome, {account?.name}!</p>
          {isTeacher && <p>You are a teacher</p>}
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <button onClick={login}>Login</button>
      )}
    </div>
  );
}
```

---

## Common Patterns

### Login (Redirect)

```typescript
import { useMsal } from '@azure/msal-react';
import { loginRequest } from '../config/authConfig';

function LoginButton() {
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginRedirect(loginRequest);
  };

  return <button onClick={handleLogin}>Skrá inn</button>;
}
```

### Logout (Redirect)

```typescript
import { useMsal } from '@azure/msal-react';

function LogoutButton() {
  const { instance } = useMsal();

  const handleLogout = () => {
    instance.logoutRedirect({
      postLogoutRedirectUri: window.location.origin,
    });
  };

  return <button onClick={handleLogout}>Útskrá</button>;
}
```

### Protected Component

```typescript
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';

function MyPage() {
  return (
    <>
      <AuthenticatedTemplate>
        <div>This shows only when logged in</div>
      </AuthenticatedTemplate>

      <UnauthenticatedTemplate>
        <div>This shows only when logged out</div>
      </UnauthenticatedTemplate>
    </>
  );
}
```

### Acquire Token (for API calls)

```typescript
import { useMsal } from '@azure/msal-react';

async function callAPI() {
  const { instance, accounts } = useMsal();

  const request = {
    scopes: ['User.Read'],
    account: accounts[0],
  };

  try {
    const response = await instance.acquireTokenSilent(request);
    const accessToken = response.accessToken;

    // Use token in API call
    const apiResponse = await fetch('/api/endpoint', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    return apiResponse.json();
  } catch (error) {
    // If silent acquisition fails, try interactive
    const response = await instance.acquireTokenRedirect(request);
  }
}
```

### Check Role (Teacher vs Student)

```typescript
import { useAuth } from '../contexts/AuthContext';

function TeacherFeature() {
  const { isTeacher } = useAuth();

  if (!isTeacher) {
    return <div>Aðeins kennarar hafa aðgang</div>;
  }

  return <div>Teacher-only content here</div>;
}
```

---

## TypeScript Types

### AccountInfo

```typescript
import { AccountInfo } from '@azure/msal-browser';

interface AccountInfo {
  homeAccountId: string;
  environment: string;
  tenantId: string;
  username: string; // Email address
  localAccountId: string;
  name?: string; // Display name
  idTokenClaims?: object;
}
```

### AuthenticationResult

```typescript
import { AuthenticationResult } from '@azure/msal-browser';

interface AuthenticationResult {
  authority: string;
  uniqueId: string;
  tenantId: string;
  scopes: string[];
  account: AccountInfo;
  idToken: string;
  accessToken: string;
  expiresOn: Date;
  tokenType: string;
}
```

### Custom Auth Context Type

```typescript
// From our AuthContext
interface AuthContextType {
  isAuthenticated: boolean;
  account: AccountInfo | null;
  login: () => void;
  logout: () => void;
  isTeacher: boolean;
}
```

---

## Troubleshooting

### Error: "AADSTS50011: The reply URL specified in the request does not match"

**Cause**: Redirect URI not registered in Azure AD

**Solution**:
1. Go to Azure Portal → App registrations → Your app
2. Click "Authentication"
3. Add the exact URL to "Single-page application" redirect URIs
4. Click "Save"

### Error: "Failed to acquire token silently"

**Cause**: Token expired or user needs to re-authenticate

**Solution**:
```typescript
try {
  const response = await instance.acquireTokenSilent(request);
} catch (error) {
  // Fallback to interactive login
  await instance.acquireTokenRedirect(request);
}
```

### Error: "Cannot read property of undefined" in useAuth

**Cause**: Component not wrapped in AuthProvider

**Solution**:
```typescript
// In App.tsx or main.tsx
<AuthProvider>
  <YourComponent />
</AuthProvider>
```

### User not staying logged in after page refresh

**Cause**: Wrong cache location

**Solution**:
```typescript
// In authConfig.ts
cache: {
  cacheLocation: 'localStorage', // Change from 'sessionStorage'
}
```

### Redirect happening but user not authenticated

**Cause**: MSAL instance not handling redirect

**Solution**:
```typescript
// In main.tsx
const msalInstance = new PublicClientApplication(msalConfig);

// Handle redirect promise
await msalInstance.handleRedirectPromise();

// Then render app
ReactDOM.createRoot(...)
```

---

## Useful Links

- **MSAL React Docs**: https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react
- **MSAL Browser Docs**: https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-browser
- **Azure AD Portal**: https://portal.azure.com
- **MSAL Samples**: https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/samples

---

## Code Snippets

### Full Auth Provider Template

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

const TEACHER_EMAILS = ['teacher@kvenno.is'];

export function AuthProvider({ children }: { children: ReactNode }) {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const account = accounts[0] || null;
  const isTeacher = account ? TEACHER_EMAILS.includes(account.username) : false;

  const login = () => instance.loginRedirect({ scopes: ['User.Read'] });
  const logout = () => instance.logoutRedirect({ postLogoutRedirectUri: '/' });

  return (
    <AuthContext.Provider value={{ isAuthenticated, account, login, logout, isTeacher }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

### Full App.tsx Template

```typescript
import React from 'react';
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import { AuthProvider } from './contexts/AuthContext';
import { LoginPage } from './components/LoginPage';
import { ChatInterface } from './components/ChatInterface';

function App() {
  return (
    <AuthProvider>
      <AuthenticatedTemplate>
        <ChatInterface />
      </AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <LoginPage />
      </UnauthenticatedTemplate>
    </AuthProvider>
  );
}

export default App;
```

---

**Last Updated**: 2025-11-22
**Maintainer**: Sigurdur Vilhelmsson, Kvennaskólinn í Reykjavík
