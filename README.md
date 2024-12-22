# FastAPI OAuth Integration with Xero

This project demonstrates the implementation of an OAuth 2.0 authentication flow in a FastAPI application, integrated with Xero’s API. The application allows users to authenticate with Xero, fetch tenants, and retrieve invoices using OAuth access tokens. Additionally, the app generates and validates custom JWT tokens for authentication within the app.

## Features

- **OAuth Flow with Xero**: Authenticate users with Xero and obtain access and refresh tokens.
- **JWT Authentication**: Secure access to your endpoints with custom JWT tokens.
- **Token Refresh**: Automatically refresh expired Xero tokens using refresh tokens.
- **Get Xero Tenants**: Fetch a list of tenants associated with the authenticated user.
- **Fetch Xero Invoices**: Retrieve invoices from a specific tenant.
- **User Profile**: Get the authenticated user's OAuth token details.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
  - [Login with Xero](#1-login-with-xero)
  - [Callback from Xero](#2-callback-from-xero)
  - [Check Tenants](#3-check-tenants)
  - [Fetch Invoices](#4-fetch-invoices)
  - [Current User](#5-current-user)
  - [Refresh Token](#6-refresh-token)
- [Code Explanation](#code-explanation)
- [License](#license)

## Installation

Follow these steps to set up the project locally:

### Step 1: Clone the Repository

Clone the repository to your local machine.

```bash
git clone https://github.com/your-username/fastapi-xero-oauth.git
cd fastapi-xero-oauth
```

### Step 2: Set Up Configuration

Create a `.env` file (or modify `config.py`) to set your configuration variables. These variables are used for interacting with Xero’s API.

```env
CLIENT_ID=<your_client_id>
CLIENT_SECRET=<your_client_secret>
REDIRECT_URL=<your_redirect_url>
AUTHORIZATION_URL=<xero_authorization_url>
TOKEN_URL=<xero_token_url>
CONNECTION_URL=<xero_connection_url>
INVOICE_URL=<xero_invoice_url>
SCOPES=<requested_scopes>
```

### Step 3: Set Up Database

Ensure that the database connection is properly configured in `core/db.py` to interact with your database.

```python
# Example database setup using SQLAlchemy
DATABASE_URL = "sqlite:///./test.db"  # Example with SQLite, adjust for your database
```

### Step 4: Run the Application

Run the FastAPI application locally through docker compose:

```bash
docker-compose build
docker-compose up
```

This will start the application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Endpoints

### 1. Login with Xero

- **Endpoint**: `/login-with-xero`
- **Method**: GET
- **Description**: Initiates the login process by redirecting the user to Xero’s authorization page where they can consent to the required permissions.
- **Response**: Redirects the user to Xero’s OAuth authorization URL.

### 2. Callback from Xero

- **Endpoint**: `/callback`
- **Method**: GET
- **Description**: Handles the OAuth callback after user authorization, exchanges the authorization code for tokens, and generates custom JWT access and refresh tokens.
- **Query Parameters**:
  - `code`: The authorization code returned by Xero.
  - `state`: The user ID that was passed during the login initiation.
- **Response**: JSON with `access_token` and `refresh_token` (JWT tokens for application use).

### 3. Check Tenants

- **Endpoint**: `/check-tenants`
- **Method**: GET
- **Description**: Fetches the list of tenants associated with the authenticated user. Requires a valid JWT access token.
- **Headers**:
  - `Authorization`: Bearer `<access_token>`
- **Response**: A tenant ID of the authenticated user.

### 4. Fetch Invoices

- **Endpoint**: `/invoices`
- **Method**: POST
- **Description**: Fetches invoices from a specific tenant. Requires the `tenant_id` in the request body and a valid JWT access token.
- **Request Body**:
  - `tenant_id`: The ID of the Xero tenant.
- **Headers**:
  - `Authorization`: Bearer `<access_token>`
- **Response**: A list of invoices from the specified tenant.

### 5. Current User

- **Endpoint**: `/me`
- **Method**: GET
- **Description**: Retrieves the OAuth token details of the authenticated user.
- **Headers**:
  - `Authorization`: Bearer `<access_token>`
- **Response**: The user’s OAuth token details in the `UserOAuthTokenBaseSchema` format.

### 6. Refresh Token

- **Endpoint**: `/refresh`
- **Method**: POST
- **Description**: Refreshes the access token using a valid refresh token. This will return a new access token.
- **Request Body**:
  - `refresh_token`: The JWT refresh token.
- **Response**: A new JWT access token.

## Code Explanation

### OAuth Flow

1. **Login with Xero**: The user is redirected to Xero's authorization page to grant access to your application.
2. **Callback**: After the user grants access, Xero redirects back with an authorization code. The code is exchanged for access and refresh tokens.
3. **Token Storage**: The access and refresh tokens are stored in the database for future use.
4. **JWT Token Generation**: The server generates custom JWT tokens to authenticate users within the app, which are returned to the client.
5. **Token Refresh**: When the access token expires, the refresh token is used to obtain a new access token from the backend.
6. **Xero Token Refresh**: If access token from Xero has expired, backend automatically connects with Xero api and generates a new access token using previous refresh token.

### Key Components

- `create_jwt_token`: Generates a JWT token using the user ID and a specified token type (access or refresh).
- `decode_token`: Decodes and validates a JWT token to extract the user information.
- `get_user_id`: A FastAPI dependency that extracts the user ID from the JWT token in the request header.
- `UserOAuthToken.save_tokens`: Stores the access and refresh tokens in the database.
- `httpx.Client()`: Used to make HTTP requests to Xero’s API endpoints to fetch tenants and invoices.

### Error Handling

- If the Xero token is expired, the app will automatically attempt to refresh it using the refresh token.
- Proper error responses are sent for issues like invalid tokens or failed requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
