import base64
import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.config import config
from core.db import get_db_session
from oauth.authentication import create_jwt_token, decode_token, get_user_id
from oauth.models import UserOAuthToken
from oauth.schemas import UserOAuthTokenBaseSchema

log = logging.getLogger("uvicorn")

app = FastAPI()


# OAuth Flow
# Step 1. Initiate login
@app.get("/login")
def login_with_xero():
    user_id = UserOAuthToken.create()
    auth_url = f"{config.authorization_url}?response_type=code&client_id={config.client_id}&redirect_uri={config.redirect_url}&scope={config.scopes}&state={user_id}"
    return RedirectResponse(auth_url)


# Step 2. Get callback from xero, after user provides consent
@app.get("/callback")
def callback_from_xero(code: str, state: str):
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(
            bytes(config.client_id + ":" + config.client_secret, "utf-8")
        ).decode("utf-8")
    }
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.redirect_url,
    }

    # Step 3. Exchange code
    with httpx.Client() as client:
        response = client.post(config.token_url, headers=headers, data=token_data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Token exchange failed"
            )

        tokens = response.json()
        log.info("Token details from callback", tokens)

        # Step 4. Save access and refresh tokens
        UserOAuthToken.save_tokens(user_id=state, tokens=tokens)

        # Step 5. Generate our app's jwt token and send it to client
        access_token = create_jwt_token({"uid": state}, token_type="access")
        refresh_token = create_jwt_token({"uid": state}, token_type="refresh")
        return {
            "message": "Authorization successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


# Step 5. Check full list of tenants that we can access
@app.get("/check-tenants")
def fetch_tenants_list(
    user_id: UUID = Depends(get_user_id), session: Session = Depends(get_db_session)
):
    user_token = (
        session.query(UserOAuthToken).filter(UserOAuthToken.id == user_id).first()
    )

    # Step 6. Generate new token from xero, if previous token is expired
    if user_token.expires_at < datetime.utcnow():
        log.info("Previous token for this user has already been expired------------")
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": user_token.refresh_token,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
        }

        with httpx.Client() as client:
            response = client.post(config.token_url, data=token_data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail="Token refresh failed"
                )

            tokens = response.json()
            UserOAuthToken.save_tokens(user_token.id, tokens)
            access_token = tokens["access_token"]

    else:
        log.info("Using the same previous token-----------")
        access_token = user_token.access_token

    # Step 7. Use new access token to fetch from xero api
    with httpx.Client() as client:
        response = client.get(
            config.connection_url,
            headers={
                "Authorization": "Bearer " + access_token,
                "Content-Type": "application/json",
            },
        )
        tenants = response.json()
    log.info("Tenants from xero", tenants)

    for tenant in tenants:
        json_dict = tenant
    return json_dict["tenantId"]


@app.post("/invoices")
def fetch_invoices(
    tenant_id: Annotated[str, Body(embed=True)],
    user_id: UUID = Depends(get_user_id),
    session: Session = Depends(get_db_session),
):
    user_token = (
        session.query(UserOAuthToken).filter(UserOAuthToken.id == user_id).first()
    )

    if user_token.expires_at < datetime.utcnow():
        log.info("Previous token for this user has already been expired------------")
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": user_token.refresh_token,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
        }

        with httpx.Client() as client:
            response = client.post(config.token_url, data=token_data)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail="Token refresh failed"
                )

            tokens = response.json()
            UserOAuthToken.save_tokens(user_token.id, tokens)
            access_token = tokens["access_token"]

    else:
        log.info("Using the same previous token-----------")
        access_token = user_token.access_token

    with httpx.Client() as client:
        response = client.get(
            config.invoice_url,
            headers={
                "Authorization": "Bearer " + access_token,
                "Xero-tenant-id": tenant_id,
                "Content-Type": "application/json",
            },
        )
        invoices = response.json()
    log.info("Invoices from xero------", invoices)


@app.get("/me", response_model=UserOAuthTokenBaseSchema)
def current_user(
    user_id: UUID = Depends(get_user_id), session: Session = Depends(get_db_session)
):
    user = session.query(UserOAuthToken).filter(UserOAuthToken.id == user_id).first()
    if not user:
        return HTTPException(status_code=400, detail="User not found")
    return user


@app.post("/refresh")
def refresh_token(
    refresh_token: Annotated[str, Body(embed=True)],
    session: Session = Depends(get_db_session),
):
    payload, _ = decode_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=400,
            detail="Could not validate refresh token",
        )
    user = session.query(UserOAuthToken).filter_by(id=payload["uid"]).first()
    if not user:
        raise HTTPException(detail="User not found", status_code=400)
    return {"access_token": create_jwt_token({"uid": str(user.id)})}

