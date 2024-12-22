from pydantic_settings import BaseSettings


class Config(BaseSettings):
    database_url: str

    # xero client id and client secret
    client_id: str
    client_secret: str
    authorization_url: str
    redirect_url: str
    connection_url: str
    token_url: str
    scopes: str
    state: str
    invoice_url: str

    # expiry for access token and refresh token
    access_token_expiry_minutes: int = 30  # 30 minutes
    refresh_token_expiry_minutes: int = 1440  # 24 hours

    secret_key: str
    refresh_secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"


config = Config()
