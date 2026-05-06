from urllib.parse import urlencode

from flask import Flask, jsonify, redirect, request, session
from flask_cors import CORS
from flask_session import Session

from config import Config
from deriv import DerivAPIError, exchange_code_for_token, fetch_accounts, group_accounts
from pkce import generate_code_challenge, generate_code_verifier, generate_state


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    Session(app)
    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.get("/api/login")
    def login():
        if not app.config["DERIV_CLIENT_ID"]:
            return api_error("DERIV_CLIENT_ID is not configured.", 500)

        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        state = generate_state()

        session.clear()
        session["oauth_state"] = state
        session["code_verifier"] = code_verifier

        params = {
            "response_type": "code",
            "client_id": app.config["DERIV_CLIENT_ID"],
            "redirect_uri": app.config["DERIV_REDIRECT_URI"],
            "scope": app.config["DERIV_OAUTH_SCOPE"],
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return redirect(f"{app.config['DERIV_AUTH_URL']}?{urlencode(params)}")

    @app.get("/api/callback")
    def callback():
        error = request.args.get("error")
        if error:
            return redirect_frontend_error(request.args.get("error_description") or error)

        code = request.args.get("code")
        returned_state = request.args.get("state")
        expected_state = session.get("oauth_state")
        code_verifier = session.get("code_verifier")

        if not code:
            return redirect_frontend_error("Missing authorization code.")
        if not returned_state or returned_state != expected_state:
            session.clear()
            return redirect_frontend_error("Invalid OAuth state. Please try signing in again.")
        if not code_verifier:
            session.clear()
            return redirect_frontend_error("Missing PKCE verifier. Please try signing in again.")

        try:
            token_data = exchange_code_for_token(code, code_verifier)
        except DerivAPIError as exc:
            session.clear()
            return redirect_frontend_error(exc.message)

        session.pop("oauth_state", None)
        session.pop("code_verifier", None)
        session["access_token"] = token_data["access_token"]
        session["token_type"] = token_data.get("token_type", "Bearer")
        session["expires_in"] = token_data.get("expires_in")
        session.modified = True

        return redirect(f"{app.config['FRONTEND_URL']}/auth/callback?success=1")

    @app.get("/api/me")
    def me():
        access_token = session.get("access_token")
        if not access_token:
            return jsonify({"authenticated": False, "user": None, "accounts": {"demo": [], "real": []}}), 401

        try:
            accounts = fetch_accounts(access_token)
        except DerivAPIError as exc:
            return handle_deriv_error(exc)

        grouped = group_accounts(accounts)
        return jsonify(
            {
                "authenticated": True,
                "user": {
                    "displayName": infer_display_name(accounts),
                    "accountCount": len(accounts),
                },
                "accounts": grouped,
            }
        )

    @app.get("/api/accounts")
    def accounts():
        access_token = session.get("access_token")
        if not access_token:
            return api_error("Not authenticated.", 401)

        try:
            accounts = fetch_accounts(access_token)
        except DerivAPIError as exc:
            return handle_deriv_error(exc)

        return jsonify({"accounts": group_accounts(accounts)})

    @app.post("/api/logout")
    def logout():
        session.clear()
        return jsonify({"ok": True})

    @app.errorhandler(404)
    def not_found(_):
        return api_error("Route not found.", 404)

    @app.errorhandler(500)
    def server_error(_):
        return api_error("Unexpected server error.", 500)

    def redirect_frontend_error(message: str):
        return redirect(f"{app.config['FRONTEND_URL']}/auth/callback?{urlencode({'error': message})}")

    return app


def infer_display_name(accounts):
    first_real = next((account for account in accounts if account["kind"] == "real"), None)
    first_account = first_real or (accounts[0] if accounts else None)
    if not first_account:
        return "Deriv trader"
    return f"Deriv trader {first_account['accountId']}"


def handle_deriv_error(exc: DerivAPIError):
    if exc.status_code in (401, 403):
        session.clear()
    return api_error(exc.message, exc.status_code, exc.details)


def api_error(message: str, status_code: int = 400, details=None):
    payload = {"error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code


app = create_app()
