import pyotp

from config import GROWW
from growwapi.groww.client import GrowwAPI


if not GROWW.api_key:
    raise RuntimeError("GROWW_API_KEY is missing from .env")

if not GROWW.totp_secret:
    raise RuntimeError("GROWW_TOTP_SECRET is missing from .env")


# Generate the current 6-digit TOTP
totp = pyotp.TOTP(GROWW.totp_secret).now()

print("TOTP generated successfully:", bool(totp))

# Request a fresh Groww access token
response = GrowwAPI.get_access_token(
    api_key=GROWW.api_key,
    totp=totp,
)

print("Groww authentication request completed.")
print("Response type:", type(response).__name__)

if isinstance(response, str):
    if not response.strip():
        raise RuntimeError(
            "Groww returned an empty access token."
        )

    print("Access token received successfully: True")
    print("Access token length:", len(response))

elif isinstance(response, dict):
    print("Response keys:", list(response.keys()))

else:
    raise RuntimeError(
        "Unexpected Groww authentication response type: "
        f"{type(response).__name__}"
    )