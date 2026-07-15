from .NorenApi import NorenApi
from threading import Timer
import pandas as pd
import time
import concurrent.futures
import requests
import pyotp

api = None

class Order:
    def __init__(self, buy_or_sell:str = None, product_type:str = None,
                 exchange: str = None, tradingsymbol:str =None, 
                 price_type: str = None, quantity: int = None, 
                 price: float = None, trigger_price:float = None, discloseqty: int = 0,
                 retention:str = 'DAY', remarks: str = "tag",
                 order_id:str = None):
        self.buy_or_sell = buy_or_sell
        self.product_type = product_type
        self.exchange = exchange
        self.tradingsymbol = tradingsymbol
        self.quantity = quantity
        self.discloseqty = discloseqty
        self.price_type = price_type
        self.price = price
        self.trigger_price = trigger_price
        self.retention = retention
        self.remarks = remarks
        self.order_id = None

def get_time(time_string):
    data = time.strptime(time_string, '%d-%m-%Y %H:%M:%S')
    return time.mktime(data)

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        # Set base host to the standard endpoints
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
        global api
        api = self

    def login(self, userid, password, twoFA, api_secret, vendor_code, app_key, is_raw_otp=True):
        try:
            # 1. Let the official parent SDK handle the authentication sequence natively
            login_ret = NorenApi.login(
                self, 
                userid=userid, 
                password=password, 
                twoFA=twoFA, 
                vendor_code=vendor_code, 
                api_secret=api_secret, 
                imei="abc1234"
            )
            
            # 2. Extract and print the response status details safely
            if login_ret and login_ret.get('stat') == 'Ok':
                print("âœ“ Successfully authenticated with Shoonya API Gateway via Native Pipeline.")
                return login_ret
            else:
                emsg = login_ret.get('emsg') if login_ret else "No response from gateway"
                print(f"Stage 1 Auth Failed: {emsg}")
                return None

        except Exception as e:
            print(f"Exception encountered during native login sequence: {str(e)}")
            return None
            
            session = requests.Session()
            login_url = "https://api.shoonya.com/NorenWClientTP/QuickConnect.html"
            response = session.post(login_url, json=login_payload)
            
            if response.status_code != 200:
                print(f"Stage 1 Auth Failed. HTTP Status: {response.status_code}")
                return None
                
            res_data = response.json()
            auth_code = res_data.get("authCode")
            
            if not auth_code:
                print(f"Failed to retrieve Auth Code. Response data: {res_data}")
                return None

            # 3. Exchange Auth Code for the production Access Token
            token_payload = {
                "uid": userid,
                "authCode": auth_code,
                "apiKey": app_key,
                "secretKey": api_secret
            }
            
            token_url = "https://trade.shoonya.com/NorenWClientAPI/GenAcsTok"
            token_response = session.post(token_url, json=token_payload)
            token_data = token_response.json()
            
            access_token = token_data.get("accessToken")
            if not access_token:
                print(f"Failed to generate Access Token: {token_data}")
                return None
                
            # 4. Bind session references internally so parent SDK methods execute normally
            self._userid = userid
            self._token = access_token
            self._set_session(userid, access_token)
            
            print("Successfully authenticated via 2026 OAuth Pipeline.")
            return token_data

        except Exception as e:
            print(f"Exception encountered during custom login sequence: {str(e)}")
            return None

    def place_basket(self, orders):
        resp_err = 0
        resp_ok  = 0
        result   = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.placeOrder, order): order for order in orders}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    result.append(future.result())
                    resp_ok = resp_ok + 1
                except Exception as exc:
                    print(f"Order failed: {exc}")
                    resp_err = resp_err + 1
        return result
                
    def placeOrder(self, order: Order):
        ret = NorenApi.place_order(self, buy_or_sell=order.buy_or_sell, product_type=order.product_type,
                                   exchange=order.exchange, tradingsymbol=order.tradingsymbol, 
                                   quantity=order.quantity, discloseqty=order.discloseqty, price_type=order.price_type, 
                                   price=order.price, trigger_price=order.trigger_price,
                                   retention=order.retention, remarks=order.remarks)
        return ret

class NorenApiPy(NorenApi):

    def __init__(self):
        super().__init__(
            host="https://api.shoonya.com/NorenWClientAPI/",
            websocket="wss://api.shoonya.com/NorenWSAPI/"
        )

        global api
        api = self

    def placeOrder(self, order: Order):

        return self.place_order(
            buy_or_sell=order.buy_or_sell,
            product_type=order.product_type,
            exchange=order.exchange,
            tradingsymbol=order.tradingsymbol,
            quantity=order.quantity,
            discloseqty=order.discloseqty,
            price_type=order.price_type,
            price=order.price,
            trigger_price=order.trigger_price,
            retention=order.retention,
            remarks=order.remarks
        )

    def place_basket(self, orders):

        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

            futures = [
                executor.submit(self.placeOrder, order)
                for order in orders
            ]

            for future in concurrent.futures.as_completed(futures):
                result.append(future.result())

        return result
    