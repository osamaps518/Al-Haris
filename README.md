# Al-Haris Backend

Parental control API for monitoring and filtering children's internet access. Built with FastAPI, PostgreSQL, and UT1 blocklists.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT with email verification (Resend)
- **Content Filtering:** UT1 blacklists (adult, gambling, violence, games, chat)
- **Screenshots:** ScreenshotOne API (skipped for explicit content)
- **Deployment:** Railway

## Live API

- **Base URL:** `https://al-haris-production.up.railway.app`
- **Interactive Docs:** `https://al-haris-production.up.railway.app/docs`

## API Reference

### Authentication

| Endpoint       | Method | Description               |
| -------------- | ------ | ------------------------- |
| `/auth/signup` | POST   | Create parent account     |
| `/auth/login`  | POST   | Request verification code |
| `/auth/verify` | POST   | Verify code, receive JWT  |

**POST /auth/signup**

```json
// Request
{ "email": "parent@example.com", "password": "secret123", "name": "Ahmed" }

// Response
{ "message": "Account created. Verification code sent." }
```

**POST /auth/login**

```json
// Request
{ "email": "parent@example.com", "password": "secret123" }

// Response
{ "message": "Verification code sent" }
```

**POST /auth/verify**

```json
// Request
{ "email": "parent@example.com", "code": "123456" }

// Response
{ "access_token": "eyJhbG...", "token_type": "bearer" }
```

**GET /auth/me** _(Requires Auth)_

```json
// Response
{ "name": "Ahmed" }
```

### Parent Endpoints (Requires Bearer Token)

| Endpoint                   | Method | Description               |
| -------------------------- | ------ | ------------------------- |
| `/parent/children`         | GET    | List all children         |
| `/parent/child`            | POST   | Add a child               |
| `/parent/settings`         | GET    | Get blocking settings     |
| `/parent/categories`       | PUT    | Update blocked categories |
| `/parent/block-url`        | POST   | Block specific URL        |
| `/parent/reports`          | GET    | Get all reports           |
| `/parent/child/{child_id}` | DELETE | Delete a child            |
| `/parent/unblock-url`      | DELETE | Unblock a URL             |
| `/parent/app-status`       | GET    | Get filtering status      |
| `/parent/app-status`       | PUT    | Enable/disable filtering  |

## Endpoint Details

**GET /parent/children**

```json
// Response
{
  "children": [
    {
      "id": 1,
      "name": "Yusuf",
      "device_name": "Samsung A52",
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

**POST /parent/child**

```json
// Request
{ "name": "Yusuf", "device_name": "Samsung A52" }

// Response
{ "message": "Child added", "child_id": 1 }
```

**GET /parent/settings**

```json
// Response
{
  "enabled_categories": ["adult", "gambling"],
  "blocked_urls": ["reddit.com"],
  "available_categories": ["adult", "gambling", "violence", "games", "chat"]
}
```

**PUT /parent/categories**

```json
// Request
{ "categories": ["adult", "gambling", "violence"] }

// Response
{ "message": "Categories updated", "enabled_categories": ["adult", "gambling", "violence"] }
```

**POST /parent/block-url**

```json
// Request
{ "url": "reddit.com" }

// Response
{ "message": "URL blocked" }
```

**GET /parent/reports**

```json
// Response
{
  "reports": [
    {
      "id": 1,
      "website_url": "https://bet365.com",
      "screenshot_url": "https://api.screenshotone.com/take?...",
      "timestamp": "2025-01-15T14:22:00",
      "child_name": "Yusuf"
    }
  ]
}
```

**DELETE /parent/child/{child_id}**

```json
// Response
{ "message": "Child deleted" }

// Error (404)
{ "detail": "Child not found" }
```

**DELETE /parent/unblock-url**

```json
// Request
{ "url": "reddit.com" }

// Response
{ "message": "URL unblocked" }

// Error (404)
{ "detail": "URL not found in blocklist" }
```

**GET /parent/app-status**

```json
// Response
{ "filtering_enabled": true }
```

**PUT /parent/app-status**

```json
// Request
{ "enabled": false }

// Response
{ "message": "App status updated", "filtering_enabled": false }
```

### Child Device Endpoints (No Auth Required)

| Endpoint                      | Method | Description                    |
| ----------------------------- | ------ | ------------------------------ |
| `/child/{child_id}/blocklist` | GET    | Get blocking config for device |
| `/child/{child_id}/check`     | GET    | Check if domain is blocked     |
| `/child/report`               | POST   | Submit blocked access report   |

**GET /child/{child_id}/blocklist**

```json
// Response
{
  "enabled_categories": ["adult", "gambling"],
  "blocked_urls": ["reddit.com"]
}
```

**GET /child/{child_id}/check?domain=example.com**

```json
// Response
{ "blocked": true, "reason": "adult" }

// Or if allowed
{ "blocked": false, "reason": null }
```

**POST /child/report**

```json
// Request
{ "child_id": 1, "website_url": "https://bet365.com" }

// Response
{
  "message": "Report submitted",
  "report_id": 1,
  "screenshot_captured": true,
  "blocked_reason": "gambling"
}
```

Note: Screenshots are **not captured** for explicit content. For other categories (gambling, violence, etc.), screenshots are captured. Frontend can apply blur if needed.

**GET /child/{child_id}/blocklist** (now includes filtering status)

```json
// Response (filtering ON)
{
  "enabled_categories": ["adult", "gambling"],
  "blocked_urls": ["reddit.com"],
  "filtering_enabled": true
}

// Response (filtering OFF - VPN should disconnect)
{
  "enabled_categories": [],
  "blocked_urls": [],
  "filtering_enabled": false
}
```

## QR Code Authentication

### Endpoints

| Endpoint                  | Method | Description                       |
| ------------------------- | ------ | --------------------------------- |
| `/auth/generate-qr-token` | POST   | Generate QR token for child login |
| `/auth/login-qr`          | POST   | Child login with scanned QR       |

**POST /auth/generate-qr-token** _(Requires Auth)_

```json
// Request
{ "child_id": 1 }

// Response
{
  "token": "xJ9kL2mN4pQ6rS8tU0vW1xY3zA5bC7dE9fG1hI3jK5lM7nO9pQ1rS3tU5vW7xY9z",
  "child_name": "Yusuf",
  "expires_at": "2025-01-20T14:35:00.000Z"
}
```

**POST /auth/login-qr** _(No Auth Required)_

```json
// Request
{ "token": "xJ9kL2mN4pQ6rS8tU0vW1xY3zA5bC7dE9fG1hI3jK5lM7nO9pQ1rS3tU5vW7xY9z" }

// Response
{
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "child_id": 1
}

// Error (401)
{ "detail": "Invalid or expired QR token" }
{ "detail": "QR token already used" }
{ "detail": "QR token expired" }
```

## Content Categories

| Category   | Description                   | Screenshot |
| ---------- | ----------------------------- | ---------- |
| `malware`  | Always blocked (security)     | Yes        |
| `adult`    | Pornography, explicit content | **No**     |
| `gambling` | Betting, casino sites         | Yes        |
| `violence` | Aggressive/dangerous content  | Yes        |
| `games`    | Gaming sites                  | Yes        |
| `chat`     | Chat/messaging platforms      | Yes        |

## Local Development

**Prerequisites:** Docker, Python 3.11+

```bash
# Clone
git clone https://github.com/your-username/al-haris-backend.git
cd al-haris-backend

# Environment variables
cp .env.example .env
# Fill in values (see below)

# Start PostgreSQL
docker-compose up -d db

# Install dependencies
pip install -r requirements.txt

# Initialize database
psql $DATABASE_URL -f db/schema.sql

# Run server
uvicorn app.main:app --reload
```

## Environment Variables

```
DATABASE_URL=postgresql://user:pass@localhost:5432/alharis
SECRET_KEY=your-jwt-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
RESEND_API_KEY=re_xxxxx
RESEND_API_URL=https://api.resend.com/emails
FROM_EMAIL=onboarding@resend.dev
SCREENSHOT_API_KEY=xxxxx
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Parent App  │────▶│   Backend   │◀────│ Child App   │
│   (React)   │     │  (FastAPI)  │     │  (Android)  │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │ PostgreSQL  │
                    └─────────────┘


```
