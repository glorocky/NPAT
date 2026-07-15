from data.shoonya_client import ShoonyaClient

print("=" * 60)
print("NPAT Phase 3A Test")
print("=" * 60)

client = ShoonyaClient()

try:

    if client.login():

        print("\n✅ LOGIN SUCCESS")

        print("Connected :", client.is_connected())

        print("Health :", client.health_check())

    else:

        print("\n❌ LOGIN FAILED")

finally:

    client.logout()

    print("\nLogged Out")