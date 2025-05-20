# AuthVault Minimal Demo

A minimal implementation of a two-factor authentication system using RSA encryption and TOTP.

## Requirements

- Python 3.6+
- Flask
- PyOTP
- PyCryptodome

## Installation

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the server:
   ```
   python app.py
   ```

2. The server will print a TOTP secret for the test user. Use this secret to set up an authenticator app like Google Authenticator or Authy.

3. Open your browser and go to `http://localhost:5000`

4. Login with:
   - Username: `testuser`
   - Password: `password123`

5. Enter the TOTP code from your authenticator app when prompted.

## Authentication Flow

1. User enters username and password
2. Password is encrypted with RSA before transmission
3. Server verifies username and decrypted password
4. If successful, user is prompted for TOTP code
5. After verifying TOTP, access is granted

## Security Notes

This is a minimal demonstration and lacks many security features required for production use:
- Passwords are stored in plaintext in memory
- New RSA keys are generated each server restart
- No protection against brute force attacks
- No session expiration
- Limited error handling