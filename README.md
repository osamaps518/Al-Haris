# Al-Haris Backend API

Parental control application backend built with FastAPI, PostgreSQL, and Docker.

## Features

- Parent authentication with email verification (JWT-based)
- Child device management(receiving/saving reports and reviewing access urls)
- Website blocking by category (adult, gambling, violence, games, chat)
- Custom URL blocking
- Activity reports with server-side screenshots
- UT1 blacklist integration for content filtering

## Live API

**Base URL**: `https://your-app.up.railway.app`

**API Documentation**: `https://your-app.up.railway.app/docs`

## Quick Start

### Option 1: Use Deployed API (Recommended)

No setup needed. Use the endpoints directly:

```bash
# Health check
curl https://your-app.up.railway.app/health

# Signup
curl -X POST https://your-app.up.railway.app/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "parent@example.com", "password": "secret", "name": "Parent"}'
```

### Option 2: Run Locally with Docker

1. **Pull the image**:

   ```bash
   docker pull yourusername/alharis-api:latest
   ```

2. **Create `.env` file**:

   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   RESEND_API_KEY=your-resend-key
   RESEND_API_URL=https://api.resend.com/emails
   FROM_EMAIL=onboarding@resend.dev
   SCREENSHOT_API_KEY=your-screenshotone-key
   ```

3. **Run with Docker Compose**:

   ```bash
   docker-compose up -d
   ```

   Or standalone (provide your own PostgreSQL):

   ```bash
   docker run -p 8000:8000 --env-file .env yourusername/alharis-api:latest
   ```

4. **Access**: `http://localhost:8000/docs`

### Option 3: Build from Source

```bash
git clone https://github.com/yourusername/alharis-backend.git
cd alharis-backend
cp .env.example .env  # Edit with your values
docker-compose up --build
```

## API Endpoints

### Authentication

| Method | Endpoint       | Description                |
| ------ | -------------- | -------------------------- |
| POST   | `/auth/signup` | Create parent account      |
| POST   | `/auth/login`  | Request verification code  |
| POST   | `/auth/verify` | Verify code, get JWT token |

### Parent Management

| Method | Endpoint             | Description               |
| ------ | -------------------- | ------------------------- |
| GET    | `/parent/children`   | List all children         |
| POST   | `/parent/child`      | Add a child               |
| GET    | `/parent/settings`   | Get blocking settings     |
| PUT    | `/parent/categories` | Update blocked categories |
| POST   | `/parent/block-url`  | Block specific URL        |
| GET    | `/parent/reports`    | View activity reports     |

### Child Device

| Method | Endpoint                | Description              |
| ------ | ----------------------- | ------------------------ |
| GET    | `/child/{id}/blocklist` | Get blocklist for device |
| POST   | `/child/report`         | Submit activity report   |

## Environment Variables

| Variable                      | Description                  | Required |
| ----------------------------- | ---------------------------- | -------- |
| `DATABASE_URL`                | PostgreSQL connection string | Yes      |
| `SECRET_KEY`                  | JWT signing key              | Yes      |
| `ALGORITHM`                   | JWT algorithm (HS256)        | Yes      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry                 | Yes      |
| `RESEND_API_KEY`              | Resend.com API key           | Yes      |
| `RESEND_API_URL`              | Resend API endpoint          | Yes      |
| `FROM_EMAIL`                  | Sender email address         | Yes      |
| `SCREENSHOT_API_KEY`          | ScreenshotOne API key        | Yes      |

## Blocked Categories

- `adult` - Adult content (auto-includes sexual education)
- `gambling` - Gambling sites
- `violence` - Violent/aggressive content
- `games` - Gaming sites
- `chat` - Chat platforms

**Always enabled**: `malware` (includes phishing)

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Auth**: JWT with email verification
- **Email**: Resend SMTP
- **Screenshots**: ScreenshotOne API
- **Blocklists**: UT1 Blacklists

## Project Structure

```
app/
├── main.py          # FastAPI app, startup
├── auth.py          # JWT, password hashing
├── database.py      # SQLAlchemy setup
├── queries.py       # Database queries
├── blocklists.py    # UT1 blocklist loading
├── screenshots.py   # Screenshot capture
└── routers/
    ├── auth.py      # Auth endpoints
    ├── blocking.py  # Blocking endpoints
    ├── children.py  # Child management
    └── reports.py   # Report endpoints
```
