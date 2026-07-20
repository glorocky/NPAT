import requests

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}

# Initialize cookies
session.get(
    "https://www.nseindia.com/option-chain",
    headers=headers,
    timeout=10,
)

# Get expiry list
contract = session.get(
    "https://www.nseindia.com/api/option-chain-contract-info?symbol=NIFTY",
    headers=headers,
    timeout=10,
)

contract.raise_for_status()

expiry = contract.json()["expiryDates"][0]

print("Expiry:", expiry)

# Fetch option chain v3
url = (
    f"https://www.nseindia.com/api/option-chain-v3"
    f"?type=Indices&symbol=NIFTY&expiry={expiry}"
)

print(url)

r = session.get(
    url,
    headers=headers,
    timeout=10,
)

print("Status:", r.status_code)

print(r.text[:1000])