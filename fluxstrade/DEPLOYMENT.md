# Fluxstrade Deployment

Deploy the backend first, then the frontend. Deriv will not accept localhost redirect URLs for production apps, so the OAuth callback must use your deployed backend URL.

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

DERIV_CLIENT_ID=your_deriv_oauth_app_id
DERIV_APP_ID=your_deriv_oauth_app_id
DERIV_REDIRECT_URI=https://your-render-service.onrender.com/api/callback
DERIV_AUTH_URL=https://auth.deriv.com/oauth2/auth
DERIV_TOKEN_URL=https://auth.deriv.com/oauth2/token
DERIV_API_BASE_URL=https://api.derivws.com
DERIV_OAUTH_SCOPE=trade account_manage
```

After Render deploys, test:

```text
https://your-render-service.onrender.com/api/health
```

## 2. Configure Deriv

In the Deriv developer dashboard, register or update your OAuth app.

Use this Redirect URL exactly:

```text
https://your-render-service.onrender.com/api/callback
```

Enable these scopes:

```text
trade
account_manage
```

The app/application ID from Deriv is used as both:

```env
DERIV_CLIENT_ID=your_deriv_oauth_app_id
DERIV_APP_ID=your_deriv_oauth_app_id
```

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

Open your Vercel app and click Login with Deriv.

Expected flow:

1. Vercel frontend sends you to Render `/api/login`.
2. Render sends you to Deriv OAuth.
3. Deriv redirects back to Render `/api/callback`.
4. Render stores the token in its server-side session.
5. Render redirects you to the Vercel frontend.
6. The frontend calls Render `/api/me` and shows Demo and Real balances.
