# Ralph Implementation Plan

## Overview
Ralph is a PM assistant tool with Jira integration, email authentication, bot protection, and voice chat capabilities.

## Features (Priority Order)

### 1. Email Authentication with Magic Link [COMPLETED] ✓
**Priority:** HIGHEST
**Status:** ✅ Completed
**Description:** Users can log in using email-based magic links (passwordless auth)
**Dependencies:** None
**Estimated Complexity:** Medium

**Implementation:**
- [x] Set up authentication system (Better Auth with magic link plugin)
- [x] Create email sending service integration (Resend)
- [x] Build login UI component (/login page)
- [x] Implement magic link generation and validation
- [x] Add session management (Better Auth sessions)
- [x] Create protected route middleware (dashboard checks auth)

**Implementation Details:**
- **Auth Library:** Better Auth v1.3.27 with magic link plugin
- **Email Service:** Resend for sending magic link emails
- **Database:** SQLite with Prisma ORM
- **Pages Created:**
  - `/login` - Email input form for magic link
  - `/dashboard` - Protected page showing user info
  - `/` - Updated home page with navigation
- **API Routes:** `/api/auth/[...all]` - Handles all auth requests
- **Files Created:**
  - `src/lib/auth.ts` - Server-side auth configuration
  - `src/lib/auth-client.ts` - Client-side auth utilities
  - `src/lib/prisma.ts` - Prisma client singleton
  - `src/app/login/page.tsx` - Login page
  - `src/app/dashboard/page.tsx` - Protected dashboard
  - `src/app/dashboard/sign-out-button.tsx` - Sign out component
  - `src/app/api/auth/[...all]/route.ts` - Auth API handler
  - `prisma/schema.prisma` - Database schema with User, Session, Account, Verification models

---

### 2. Jira Integration [NEXT]
**Priority:** HIGH
**Status:** Not Started
**Description:** Integration with Jira API for ticket management
**Dependencies:** Authentication system
**Estimated Complexity:** High

**Implementation:**
- [ ] Set up Jira API client
- [ ] Create Jira OAuth flow or API token management
- [ ] Build UI for Jira connection/configuration
- [ ] Implement ticket fetching and display
- [ ] Add error handling and rate limiting

---

### 3. Jira Ticket Creation Assistant
**Priority:** HIGH
**Status:** Not Started
**Description:** Helps PMs create new Jira tickets with intelligent suggestions
**Dependencies:** Jira Integration, Authentication
**Estimated Complexity:** High

**Implementation:**
- [ ] Design ticket creation form UI
- [ ] Implement AI/template-based suggestions for ticket fields
- [ ] Add project and issue type selection
- [ ] Create ticket preview functionality
- [ ] Implement ticket submission to Jira

---

### 4. Bot Detection with Captcha
**Priority:** MEDIUM
**Status:** Not Started
**Description:** Captcha integration to prevent bot access
**Dependencies:** Authentication system
**Estimated Complexity:** Low

**Implementation:**
- [ ] Choose captcha provider (hCaptcha, reCAPTCHA, or Cloudflare Turnstile)
- [ ] Integrate captcha on login page
- [ ] Add server-side verification
- [ ] Handle captcha failures gracefully

---

### 5. Voice Chat for PMs
**Priority:** MEDIUM
**Status:** Not Started
**Description:** Voice chat capability because PMs love to talk
**Dependencies:** Authentication system
**Estimated Complexity:** High

**Implementation:**
- [ ] Choose voice communication solution (WebRTC, Twilio, etc.)
- [ ] Implement voice call UI
- [ ] Add voice recording/transcription if needed
- [ ] Set up real-time communication infrastructure
- [ ] Add call quality indicators

---

## Current Status
- **Last Updated:** 2025-10-12 (Updated after completing authentication)
- **Current Focus:** Jira Integration (next priority)
- **Completed Features:** 1/5 (20%)
- **In Progress:** None
- **Recently Completed:** Email Authentication with Magic Link ✓

## Technical Stack
- **Framework:** Next.js 15.5.4 with React 19.1.0
- **Styling:** Tailwind CSS 4
- **Type Safety:** TypeScript 5
- **Linting:** Biome 2.2.0
- **Database:** SQLite with Prisma 6.17.1
- **Authentication:** Better Auth 1.3.27
- **Email Service:** Resend 6.1.2
- **Deployment:** TBD

## Notes
- Start with authentication as it's foundational for all other features
- Jira integration and ticket creation are core features and should be prioritized
- Voice chat and captcha can be implemented later as enhancements
