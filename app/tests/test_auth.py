from app.auth import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    password = "secure123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_wrong_password_fails():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)

def test_jwt_token_roundtrip():
    data = {"parent_id": 1, "email": "test@test.com"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded["parent_id"] == 1
    assert decoded["email"] == "test@test.com"

def test_invalid_token_returns_none():
    assert decode_access_token("invalid.token.here") is None