# Al-Haris (الحارس)

Al-Haris is a parental control application that enables parents to monitor and manage their children's device usage through content filtering, URL blocking, and activity reporting. The project consists of three components: a FastAPI backend, a parent client for monitoring and configuration, and an Android client that enforces blocking rules on children's devices.

## Backend

The backend handles authentication, content filtering decisions, and data persistence using a server-side approach where blocking logic lives on the server rather than on client devices.


### Design Decisions

**Server-Side Content Filtering**: The backend maintains master blocklists in memory and provides a check endpoint, allowing child devices to query and cache personalized blocklists for local VPN filtering.

**Category-Based Blocking**: Mandatory categories (malware, phishing) are always enforced, while optional categories (adult, gambling, violence, games, chat) are parent-configurable.

**Conditional Screenshot Capture**: Screenshots are captured for blocked site attempts except for adult content, giving parents visibility without storing inappropriate imagery.

**Three-factor Authentication**: All parent authentication requires email verification with a six-digit code before receiving an access token. On child's device, a parent can chose to enter credentials manually or scanning through a specific child's QR code. 

### Technologies and Services

- **FastAPI** provides automatic request validation, built-in OpenAPI documentation, and async capabilities.
- **PostgreSQL** handles persistent data with foreign key relationships and cascade deletes.  
- **UT1 Blacklists** from the University of Toulouse provide domain categorization loaded into memory on startup for fast lookups. 
- **ScreenshotOne** API captures website previews for non-explicit blocked sites 
- **Resend** SMTP handles verification code email delivery. 
- **Railway** hosts production with PostgreSQL, automatic GitHub deployments, and environment management.

### API Structure

Thirteen endpoints organized into: 
- authentication (signup, login, verification)
- parent management (children, categories, blocked URLs, reports)
- child device operations (blocklist retrieval, domain checking)
- QR code Login (generating QR token, logging in using the token)
- activity reporting(get reports for parent, submit reports from child)

### Live API
- Base URL: https://al-haris-production.up.railway.app
- Interactive Docs: https://al-haris-production.up.railway.app/docs


## Parent Client

Parents can add child profiles, configure blocked categories, add specific URLs to block, and review activity reports with screenshots. _Technical details to be added by client team._

## Child Client (Android)

Retrieves personalized blocklists and enforces blocking via local VPN filtering, submitting reports when blocked content is accessed. _Technical details to be added by client team._
