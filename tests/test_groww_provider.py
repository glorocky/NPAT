from providers.groww_provider import GrowwProvider

provider = GrowwProvider("dummy_token")

print(provider.provider_info())

info = provider.provider_info()

assert info["provider"] == "Groww"
assert info["class"] == "GrowwProvider"

print("✅ GrowwProvider initialization test passed")
