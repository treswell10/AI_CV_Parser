import getpass
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_password():
    print("\n=== Password Hashing Test ===")
    password = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("❌ Passwords do not match.")
        return False

    hashed = get_password_hash(password)
    print(f"✅ Passwords match.\nHashed: {hashed}")

    check = getpass.getpass("Re-enter password to verify against hash: ")
    if verify_password(check, hashed):
        print("✅ Verification successful.")
    else:
        print("❌ Verification failed.")
        return False

    # Wrong password must fail
    if not verify_password(check + "x", hashed):
        print("✅ Wrong password correctly rejected.")
    else:
        print("❌ Wrong password was accepted!")
        return False

    return True


def test_token():
    print("\n=== JWT Token Test ===")
    username = input("Enter username for token: ").strip() or "testuser"

    # 1. Create token with default expiry
    token = create_access_token({"sub": username})
    print(f"✅ Token created:\n{token}")

    # 2. Decode and check payload
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        print(f"❌ Token decode failed: {e}")
        return False

    if payload.get("sub") == username:
        print(f"✅ Subject matches: {payload['sub']}")
    else:
        print(f"❌ Subject mismatch: {payload.get('sub')}")
        return False

    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    print(f"✅ Expires at (UTC): {exp:%Y-%m-%d %H:%M:%S}")

    # 3. Custom expiry
    short_token = create_access_token({"sub": username}, timedelta(minutes=1))
    short_payload = jwt.decode(short_token, SECRET_KEY, algorithms=[ALGORITHM])
    short_exp = datetime.fromtimestamp(short_payload["exp"], tz=timezone.utc)
    print(f"✅ Custom 1-min token expires at (UTC): {short_exp:%Y-%m-%d %H:%M:%S}")

    # 4. Expired token must be rejected
    expired_token = create_access_token({"sub": username}, timedelta(seconds=-1))
    try:
        jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])
        print("❌ Expired token was accepted!")
        return False
    except JWTError:
        print("✅ Expired token correctly rejected.")

    # 5. Wrong secret must be rejected
    try:
        jwt.decode(token, "WRONG_KEY", algorithms=[ALGORITHM])
        print("❌ Token accepted with wrong key!")
        return False
    except JWTError:
        print("✅ Wrong secret key correctly rejected.")

    return True


def main():
    pw_ok = test_password()
    token_ok = test_token()

    print("\n=== Summary ===")
    print(f"Password tests: {'✅ PASSED' if pw_ok else '❌ FAILED'}")
    print(f"Token tests:    {'✅ PASSED' if token_ok else '❌ FAILED'}")


if __name__ == "__main__":
    main()