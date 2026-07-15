"""
=========================================================
NPAT - Groww Login
=========================================================

Purpose:
    Authenticate with Groww using API Key + TOTP.

Returns:
    Access Token

Author : NPAT
Version : Sprint 1.0
=========================================================
"""

import os

import pyotp
from dotenv import load_dotenv
from growwapi.groww.client import GrowwAPI


load_dotenv()


class GrowwLogin:

    def __init__(self):

        self.api_key = os.getenv("GROWW_API_KEY")
        self.totp_secret = os.getenv("GROWW_TOTP_SECRET")

        if not self.api_key:
            raise ValueError("GROWW_API_KEY not found in .env")

        if not self.totp_secret:
            raise ValueError("GROWW_TOTP_SECRET not found in .env")

    def get_access_token(self):

        current_totp = pyotp.TOTP(
            self.totp_secret
        ).now()

        print(f"Generated TOTP : {current_totp}")

        access_token = GrowwAPI.get_access_token(

            api_key=self.api_key,

            totp=current_totp

        )

        print("✅ Groww Login Successful")

        return access_token