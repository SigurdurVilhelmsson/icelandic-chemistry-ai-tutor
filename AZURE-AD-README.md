# Azure AD Authentication - Overview

This document provides an overview of Azure AD authentication implementation for the Icelandic Chemistry AI Tutor app on kvenno.app.

## What is Azure AD?

**Azure AD (Microsoft Entra ID)** is Microsoft's cloud-based identity and access management service. Through the **Menntaský project**, all Icelandic secondary schools and universities have Azure AD integration, allowing students and teachers to authenticate using their school accounts.

## Why Azure AD for Kvenno.app?

1. **Seamless Integration**: Students and teachers already have @kvenno.is accounts
2. **No Password Management**: No need to create separate accounts or remember passwords
3. **Secure**: Industry-standard OAuth 2.0 and OpenID Connect protocols
4. **Single Sign-On**: Users stay logged in across kvenno.app tools
5. **Role-Based Access**: Distinguish between teachers and students

## Authentication Flow

```
1. User visits /1-ar/ai-tutor/ (or /2-ar/ or /3-ar/)
2. App checks if user is authenticated
3. If not → Redirect to Microsoft login page
4. User logs in with @kvenno.is account
5. Microsoft redirects back to app with authentication token
6. App verifies token and grants access
7. User sees AI Tutor interface
```

## Who Can Access?

**Authenticated Users**:
- ✅ Students with @kvenno.is accounts
- ✅ Teachers with @kvenno.is accounts

**Access Levels**:
- **Students**: Full access to AI Tutor chat interface
- **Teachers**: Full access + future admin features (planned)

## Implementation Overview

The AI Tutor uses **client-side authentication** with Microsoft Authentication Library (MSAL):

- **@azure/msal-browser**: Core authentication library
- **@azure/msal-react**: React hooks and components
- **No backend auth server needed**: Authentication handled entirely client-side
- **Automatic token refresh**: MSAL handles token lifecycle

## Key Features

1. **Protected Routes**: Only authenticated users can access the chat interface
2. **Automatic Redirects**: Unauthenticated users redirected to Microsoft login
3. **Token Management**: MSAL securely stores and refreshes tokens
4. **Logout**: Clear logout functionality that revokes tokens
5. **Role Detection**: Identifies teachers vs. students (for future features)

## Multi-Path Deployment

The AI Tutor is deployed to three paths:
- `/1-ar/ai-tutor/`
- `/2-ar/ai-tutor/`
- `/3-ar/ai-tutor/`

Each deployment requires:
1. **Separate build** with appropriate `VITE_BASE_PATH`
2. **Registered redirect URI** in Azure AD portal for each path
3. **Same Azure AD app registration** (shared across all paths)

## Environment Variables Required

```bash
# .env file
VITE_AZURE_CLIENT_ID=your-client-id-here
VITE_AZURE_TENANT_ID=your-tenant-id-here
```

These values are obtained from the Azure AD app registration in the Azure Portal.

## Security Considerations

⚠️ **Important**:

1. **Client-side role checks are for UX only**
   - Never trust client-side authorization for critical operations
   - Server-side validation required for sensitive actions (future enhancement)

2. **Credentials in .env files**
   - Never commit `.env` files to git
   - Use `.env.example` for documentation
   - Store secrets securely

3. **Token handling**
   - MSAL handles secure token storage
   - Tokens stored in browser sessionStorage or localStorage
   - Automatic refresh before expiration
   - Logout clears all tokens

4. **Multi-factor authentication**
   - Can be enforced at Azure AD level
   - Recommended for teacher accounts
   - Configured in Azure Portal, not in app code

## Documentation Structure

This project includes four Azure AD documentation files:

1. **AZURE-AD-README.md** (this file) - Overview and concepts
2. **AZURE-AD-IMPLEMENTATION-GUIDE.md** - Step-by-step implementation instructions
3. **AZURE-AD-CHECKLIST.md** - Implementation progress tracker
4. **AZURE-AD-QUICK-REFERENCE.md** - Quick lookups while coding

## Getting Started

**For Developers**:
1. Read this overview (AZURE-AD-README.md)
2. Follow the step-by-step guide (AZURE-AD-IMPLEMENTATION-GUIDE.md)
3. Use the checklist to track progress (AZURE-AD-CHECKLIST.md)
4. Reference the quick guide while coding (AZURE-AD-QUICK-REFERENCE.md)

**For Deployment**:
- Ensure Azure AD app registration is configured correctly
- Add redirect URIs for all deployment paths
- Set environment variables on build server
- Test authentication at each deployed path

## Current Status

**Implementation Status**: ⏳ Planned

The AI Tutor currently does not have Azure AD authentication implemented. This documentation provides the roadmap for adding authentication to protect the app and enable teacher-specific features.

## Next Steps

1. Create Azure AD app registration in Azure Portal
2. Install MSAL packages (`@azure/msal-browser`, `@azure/msal-react`)
3. Configure MSAL provider in React app
4. Add authentication context and hooks
5. Protect routes with authentication requirements
6. Test authentication flow at all deployment paths
7. Implement role-based access control for teachers

## Support

For questions or issues:
- Azure AD setup: Contact IT support at Kvennaskólinn
- Implementation questions: See AZURE-AD-IMPLEMENTATION-GUIDE.md
- Azure Portal access: Contact project administrator

---

**Last Updated**: 2025-11-22
**Maintainer**: Sigurdur Vilhelmsson, Kvennaskólinn í Reykjavík
