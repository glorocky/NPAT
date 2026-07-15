"""
=========================================================
NPAT - Shoonya Client
=========================================================
Broker Interface

Responsibilities
----------------
- Selenium OAuth Login
- Session Management
- Live Quotes
- Option Chain
- WebSocket

Author:
Rocky Chopra

Version:
1.0.0
=========================================================
"""

import json
import time
import hashlib
import requests
import pyotp

from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import SHOONYA
from vendor.shoonya.api_helper import NorenApiPy


class ShoonyaClient:

    def __init__(self):

        self.api = NorenApiPy()

        self.connected = False

        self.access_token = None

        self.user_token = None

        self.auth_code = None

        self.driver = None

    # -----------------------------------------------------

    def _create_driver(self):

        options = webdriver.ChromeOptions()

        options.add_argument("--headless=new")

        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--no-sandbox")

        options.add_argument("--window-size=1920,1080")

        options.set_capability(
            "goog:loggingPrefs",
            {"performance": "ALL"}
        )

        return webdriver.Chrome(options=options)

    # -----------------------------------------------------

    def _scan_network_for_code(self):

        logs = self.driver.get_log("performance")

        for entry in logs:

            try:

                message = json.loads(
                    entry["message"]
                )["message"]

                if message.get("method") != "Network.requestWillBeSent":
                    continue

                url = (
                    message.get("params", {})
                    .get("request", {})
                    .get("url", "")
                )

                if "code=" not in url:
                    continue

                parsed = urlparse(url)

                code = parse_qs(
                    parsed.query
                ).get("code", [None])[0]

                if code:
                    return code

            except Exception:
                continue

        return None

    # -----------------------------------------------------

    @staticmethod
    def _fast_fill(element, value):

        element.click()

        time.sleep(0.1)

        element.clear()

        element.send_keys(value)

        time.sleep(0.1)

    # -----------------------------------------------------

    def is_connected(self):

        return self.connected
    
        # -----------------------------------------------------

    def login(self):

        client_id = (
            f"{SHOONYA.user_id}_U"
            if not SHOONYA.user_id.endswith("_U")
            else SHOONYA.user_id
        )

        raw_user = SHOONYA.user_id.replace("_U", "")

        login_url = (
            "https://trade.shoonya.com/OAuthlogin/"
            f"investor-entry-level/login?api_key={client_id}"
            f"&route_to={raw_user}"
        )

        self.driver = self._create_driver()

        wait = WebDriverWait(self.driver, 30)

        try:

            self.driver.get(login_url)

            print("Opened:", self.driver.current_url)

            wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "input[type='password']")
                )
            )

            time.sleep(1)

            inputs = [
                x
                for x in self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "input:not([type='hidden']):not([type='checkbox'])"
                )
                if x.is_displayed()
            ]

            self._fast_fill(inputs[0], raw_user)

            self._fast_fill(inputs[1], SHOONYA.password)

            otp = pyotp.TOTP(
                SHOONYA.totp_secret
            ).now()

            self._fast_fill(inputs[2], otp)

            wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[normalize-space()='LOGIN']"
                    )
                )
            ).click()

            print("Waiting for OAuth Code...")

            start = time.time()
            
            otp_value = otp

            while True:

                self.auth_code = self._scan_network_for_code()

                if self.auth_code:
                    
                    print(f"✓ OAuth Code Captured : {self.auth_code}")
                    
                    break

                if time.time() - start > 60:
                   new_otp = pyotp.TOTP(
            SHOONYA.totp_secret
        ).now()

        if new_otp != otp_value:

            print("Refreshing expired OTP...")

            self._fast_fill(
                inputs[2],
                new_otp
            )

            wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[normalize-space()='LOGIN']"
                    )
                )
            ).click()

            otp_value = new_otp

            start = time.time()

            continue

        raise Exception(
            "Unable to capture OAuth Code."
        )

            time.sleep(0.5)

        finally:
            

            try:
                
                print("Final Browser URL:", self.driver.current_url)
                
                self.driver.quit()
                
            except:
                pass

        checksum = hashlib.sha256(

            (
                client_id
                + SHOONYA.api_key
                + self.auth_code
            ).encode()

        ).hexdigest()

        payload = {

            "uid": client_id,

            "code": self.auth_code,

            "checksum": checksum

        }

        response = requests.post(

            "https://api.shoonya.com/NorenWClientAPI/GenAcsTok",

             data={"jData": json.dumps(payload)}

        )

        token_data = response.json()

        if token_data.get("stat") != "Ok":

            raise Exception(

                token_data.get(
                    "emsg",
                    "Authentication Failed"
                )

            )

        self.access_token = token_data["access_token"]

        self.user_token = token_data["susertoken"]

        self.api.set_session(

            raw_user,

            SHOONYA.password,

            self.user_token,

            self.access_token

        )

        self.connected = True

        print("Shoonya Login Successful")

        return True
    
        # -----------------------------------------------------

    def logout(self):

        if not self.connected:
            return

        try:
            self.api.logout()
        except Exception:
            pass

        self.connected = False
        self.access_token = None
        self.user_token = None

    # -----------------------------------------------------

    def health_check(self):

        if not self.connected:
            return False

        try:
            result = self.api.get_limits()

            if result and result.get("stat") == "Ok":
                return True

        except Exception:
            return False

        return False

    # -----------------------------------------------------

    def search_symbol(self, exchange, symbol):

        return self.api.searchscrip(
            exchange=exchange,
            searchtext=symbol
        )

    # -----------------------------------------------------

    def get_quote(self, exchange, token):

        return self.api.get_quotes(
            exchange=exchange,
            token=token
        )

    # -----------------------------------------------------

    def get_option_chain(
        self,
        exchange,
        tradingsymbol,
        strikeprice,
        count=5
    ):

        return self.api.get_option_chain(
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            strikeprice=strikeprice,
            count=count
        )

    # -----------------------------------------------------

    def get_positions(self):

        return self.api.get_positions()

    # -----------------------------------------------------

    def get_orders(self):

        return self.api.get_order_book()

    # -----------------------------------------------------

    def place_order(self, **kwargs):

        return self.api.place_order(**kwargs)