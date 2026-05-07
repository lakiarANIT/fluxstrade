# Fluxstrade Deployment

Deploy the backend first, then the frontend. The main login flow uses a client-provided Deriv API token, so production only needs a backend URL, a frontend URL, and a Deriv app ID for API calls.

## 1. Deploy Backend To Render

Create a new Render Web Service from this repository.

- Root Directory: `fluxstrade/backend`
- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

Set these Render environment variables:

```env
FLASK_ENV=production
FLASK_SECRET_KEY=whdhfhjsjjdy7ehjfjjjfjjjdkkskks
SESSION_FILE_DIR=/tmp/fluxstrade_sessions
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=true

FRONTEND_URL=https://your-vercel-app.vercel.app
CORS_ORIGINS=https://your-vercel-app.vercel.app

DERIV_APP_ID=your_deriv_app_id
DERIV_AUTH_URL=https://auth.deriv.com/oauth2/auth
DERIV_TOKEN_URL=https://auth.deriv.com/oauth2/token
DERIV_API_BASE_URL=https://api.derivws.com
```

After Render deploys, test:

```text
https://your-render-service.onrender.com/api/health
```

## 2. Configure Deriv

Create or choose a Deriv app ID and set it as `DERIV_APP_ID`. Clients create API tokens in their own Deriv account settings, choose the scopes they want to allow, and paste the token into Fluxstrade.

## 3. Deploy Frontend To Vercel

Create a new Vercel project from this repository.

- Root Directory: `fluxstrade/frontend`
- Framework Preset: `Next.js`
- Build Command: leave default, or use `npm run build`
- Install Command: leave default, or use `npm install`

Set this Vercel environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
```

Deploy, then copy your Vercel production URL.

## 4. Final Link-Up

Go back to Render and update:

```env
FRONTEND_URL=https://your-vercel-app.vercel.app
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

Redeploy the Render backend after changing these values.

## 5. Test Production Login

Open your Vercel app and paste a Deriv API token.

Expected flow:

1. Vercel frontend posts the token to Render `/api/token-login`.
2. Render validates the token by fetching Deriv accounts.
3. Render stores the token in its server-side session.
4. The frontend shows Demo and Real balances.
