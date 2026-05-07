# Fluxstrade

Fluxstrade is a small full-stack monorepo for viewing Deriv Demo and Real account balances. Clients paste a Deriv API token into the Next.js frontend, and the Flask backend validates it with Deriv before storing it in a server-side filesystem session.

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

   - `DERIV_APP_ID`
   - `FLASK_SECRET_KEY`

3. Start both services:

   ```bash
   docker compose up --build
   ```

4. Open:

   ```text
   http://localhost:3000
   ```

5. Paste a Deriv API token in the app UI with enough scope to read account information.

## Routes

- `POST /api/token-login`: validates a pasted Deriv API token, stores it in the backend session, and returns grouped accounts
- `GET /api/me`: returns authenticated user state and grouped accounts
- `GET /api/accounts`: returns grouped Demo and Real accounts with balances
- `POST /api/logout`: clears the server session

## Notes

- The pasted Deriv token is sent to the backend once during connection and is not returned to the browser.
- Do not put client/user API tokens in `.env`. `DERIV_CLIENT_ID` is only for the optional OAuth redirect fallback.
- Only use tokens you are authorised to use. Tokens with Trade, Payments, or Admin scopes can control sensitive account actions.
- CORS is configured for `http://localhost:3000` and supports credentials.
- Account balances are read from Deriv's Options accounts REST endpoint:
  `GET https://api.derivws.com/trading/v1/options/accounts`.
