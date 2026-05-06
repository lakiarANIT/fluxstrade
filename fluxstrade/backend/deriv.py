from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from flask import current_app


class DerivAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int = 500, details: Any | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def exchange_code_for_token(code: str, code_verifier: str) -> dict[str, Any]:
    config = current_app.config
    payload = {
        "grant_type": "authorization_code",
        "client_id": config["DERIV_CLIENT_ID"],
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": config["DERIV_REDIRECT_URI"],
    }

    try:
        response = requests.post(
            config["DERIV_TOKEN_URL"],
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=config["REQUEST_TIMEOUT"],
        )
    except requests.RequestException as exc:
        raise DerivAPIError("Could not reach Deriv token endpoint.", details=str(exc)) from exc

    data = _parse_json_response(response)
    if not response.ok:
        raise DerivAPIError("Deriv rejected the authorization code.", response.status_code, data)

    access_token = data.get("access_token")
    if not access_token:
        raise DerivAPIError("Deriv token response did not include an access token.", details=data)

    return data


def fetch_accounts(access_token: str) -> list[dict[str, Any]]:
    config = current_app.config
    if not config["DERIV_APP_ID"]:
        raise DerivAPIError("DERIV_APP_ID is not configured.", status_code=500)

    try:
        response = requests.get(
            f"{config['DERIV_API_BASE_URL']}/trading/v1/options/accounts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Deriv-App-ID": config["DERIV_APP_ID"],
                "Accept": "application/json",
            },
            timeout=config["REQUEST_TIMEOUT"],
        )
    except requests.RequestException as exc:
        raise DerivAPIError("Could not reach Deriv accounts endpoint.", details=str(exc)) from exc

    data = _parse_json_response(response)
    if not response.ok:
        raise DerivAPIError("Could not fetch Deriv accounts.", response.status_code, data)

    raw_accounts = data.get("data", data)
    if isinstance(raw_accounts, dict):
        raw_accounts = [raw_accounts]
    if not isinstance(raw_accounts, list):
        raise DerivAPIError("Deriv accounts response had an unexpected shape.", details=data)

    return [_normalize_account(account) for account in raw_accounts if isinstance(account, dict)]


def group_accounts(accounts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    demo = [account for account in accounts if account["kind"] == "demo"]
    real = [account for account in accounts if account["kind"] == "real"]
    return {"demo": demo, "real": real}


def _parse_json_response(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError as exc:
        raise DerivAPIError(
            "Deriv returned a non-JSON response.",
            status_code=response.status_code,
            details=response.text[:500],
        ) from exc


def _normalize_account(account: dict[str, Any]) -> dict[str, Any]:
    account_id = str(
        account.get("account_id")
        or account.get("loginid")
        or account.get("id")
        or account.get("account")
        or "unknown"
    )
    account_type = str(account.get("account_type") or account.get("type") or "").lower()
    kind = _classify_account(account_id, account_type, account)

    return {
        "accountId": account_id,
        "type": account_type or kind,
        "kind": kind,
        "currency": str(account.get("currency") or "").upper() or "N/A",
        "balance": _normalize_balance(account.get("balance")),
        "status": account.get("status"),
        "rawType": account_type,
    }


def _classify_account(account_id: str, account_type: str, account: dict[str, Any]) -> str:
    explicit_demo = account.get("demo_account")
    if explicit_demo is not None:
        return "demo" if bool(explicit_demo) else "real"

    lowered_id = account_id.lower()
    if "demo" in account_type or lowered_id.startswith(("demo", "vrtc", "dot")):
        return "demo"
    return "real"


def _normalize_balance(value: Any) -> str:
    if value is None or value == "":
        return "0.00"
    try:
        return f"{Decimal(str(value)):.2f}"
    except (InvalidOperation, ValueError):
        return str(value)
