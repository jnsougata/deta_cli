import hmac
import hashlib


def singature(
    access_token: str,
    http_method: str,
    uri: str,
    timestamp: str,
    content_type: str,
    raw_body: str,
):
    deta_sign_version = "v0"
    token_id, token_secret = access_token.split("_")
    string_to_sign = f"{http_method.upper()}\n{uri}\n{timestamp}\n{content_type}\n{raw_body}\n"
    signature = hmac.new(token_secret.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest()
    return f"{deta_sign_version}={token_id}:{signature}"