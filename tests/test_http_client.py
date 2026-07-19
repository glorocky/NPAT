from data.utils.http_client import HttpClient

client = HttpClient()

response = client.get("https://httpbin.org/get")

print(response.status_code)

print(response.json())

client.close()