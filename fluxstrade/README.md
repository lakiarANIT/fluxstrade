# Fluxstrade

Fluxstrade is a small full-stack monorepo for Deriv OAuth2 login with PKCE. The Flask backend owns the OAuth flow and stores the Deriv access token in a server-side filesystem session. The Next.js frontend only talks to the backend and displays Demo and Real account balances.

## Stack

- Backend: Flask, Flask-CORS, Flask-Session, python-dotenv
- Frontend: Next.js 14 App Router, TypeScript, Tailwind CSS
- Runtime: Docker Compose with hot reload

## Setup

1. Copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Fill in:

   - `DERIV_CLIENT_ID`
   - `DERIV_APP_ID`
   - `FLASK_SECRET_KEY`
   - `DERIV_REDIRECT_URI`

3. In the Deriv app settings, register this callback URL exactly:

   ```text
   http://localhost:5000/api/callback
   ```

4. Start both services:

   ```bash
   docker compose up --build
   ```

5. Open:

   ```text
   http://localhost:3000
   ```

## Routes

- `GET /api/login`: starts Deriv OAuth2 login with PKCE
- `GET /api/callback`: validates state, exchanges authorization code, stores token in the backend session, redirects to frontend
- `GET /api/me`: returns authenticated user state and grouped accounts
- `GET /api/accounts`: returns grouped Demo and Real accounts with balances
- `POST /api/logout`: clears the server session

## Notes

- The Deriv access token is never sent to the browser.
- CORS is configured for `http://localhost:3000` and supports credentials.
- Account balances are read from Deriv's Options accounts REST endpoint:
  `GET https://api.derivws.com/trading/v1/options/accounts`.
