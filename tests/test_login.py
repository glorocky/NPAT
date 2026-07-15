from data.login import GrowwLogin


def main():

    login = GrowwLogin()

    token = login.get_access_token()

    print("\nAccess Token")

    print(token[:25] + "...")

    print("\n✅ Login Test Passed")


if __name__ == "__main__":
    main()