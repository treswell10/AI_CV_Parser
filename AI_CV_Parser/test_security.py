import getpass
from security import get_password_hash, verify_password


def main():
    password = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("❌ Passwords do not match.")
        return

    hashed = get_password_hash(password)
    print(f"✅ Passwords match.\nHashed: {hashed}")

    check = getpass.getpass("Re-enter password to verify against hash: ")
    if verify_password(check, hashed):
        print("✅ Verification successful.")
    else:
        print("❌ Verification failed.")


if __name__ == "__main__":
    main()