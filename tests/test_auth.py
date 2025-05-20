from fastapi import status
import pytest

def test_register_login_logout_and_me(client, make_auth_header):
    # Without token
    resp = client.get("/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # With token
    auth_header = make_auth_header()
    resp = client.get("/auth/me", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK

    # logout
    resp = client.post("/auth/logout", headers=auth_header)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # After logout, /me is forbidden again
    resp = client.get("/auth/me", headers=auth_header)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
