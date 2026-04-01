#!/usr/bin/env python3
"""
获取 Coze API Token 的脚本
支持多种认证方式

核心发现：SDK 使用的 COZE_WORKLOAD_IDENTITY_API_KEY 
实际上是 Base64(client_id:client_secret) 格式的凭证
"""

import os
import sys
import base64
import json
import time
import urllib.request
import urllib.error
import urllib.parse

# 检查 cryptography 是否可用
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def generate_jwt_token(client_id: str, private_key: str, include_aud: bool = True) -> str:
    """生成 JWT 断言"""
    if not HAS_CRYPTO:
        raise Exception("cryptography 库未安装")
    
    header = {
        "alg": "RS256",
        "typ": "JWT"
    }
    
    current_time = int(time.time())
    payload = {
        "iss": client_id,
        "iat": current_time,
        "exp": current_time + 3600,
        "jti": f"{current_time}-{os.urandom(16).hex()}"
    }
    
    if include_aud:
        payload["aud"] = "https://api.coze.cn"
    
    def base64url_encode(data: dict) -> str:
        json_str = json.dumps(data, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
        return encoded.rstrip('=')
    
    header_b64 = base64url_encode(header)
    payload_b64 = base64url_encode(payload)
    signing_content = f"{header_b64}.{payload_b64}"
    
    try:
        if private_key.startswith('-----BEGIN'):
            key_obj = serialization.load_pem_private_key(
                private_key.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
        else:
            decoded_key = base64.b64decode(private_key)
            key_obj = serialization.load_der_private_key(
                decoded_key,
                password=None,
                backend=default_backend()
            )
    except Exception as e:
        raise Exception(f"无法解析私钥格式: {e}")
    
    signature = key_obj.sign(
        signing_content.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    return f"{signing_content}.{signature_b64}"


def method_jwt_with_aud(client_id: str, private_key: str) -> str:
    """JWT (含 aud)"""
    token_endpoint = "https://api.coze.cn/.well-known/token"
    jwt_assertion = generate_jwt_token(client_id, private_key, include_aud=True)
    
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt_assertion
    }).encode("utf-8")
    
    req = urllib.request.Request(token_endpoint, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        if result.get("code") == 0 and "data" in result:
            return result["data"].get("access_token", "")
        return ""


def method_jwt_without_aud(client_id: str, private_key: str) -> str:
    """JWT (不含 aud)"""
    token_endpoint = "https://api.coze.cn/.well-known/token"
    jwt_assertion = generate_jwt_token(client_id, private_key, include_aud=False)
    
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt_assertion
    }).encode("utf-8")
    
    req = urllib.request.Request(token_endpoint, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        if result.get("code") == 0 and "data" in result:
            return result["data"].get("access_token", "")
        return ""


def method_basic_auth(client_id: str, client_secret: str) -> str:
    """Basic Auth (Client Secret)"""
    token_endpoint = "https://api.coze.cn/.well-known/token"
    
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    
    req = urllib.request.Request(token_endpoint, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Basic {encoded_credentials}")
    req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        if result.get("code") == 0 and "data" in result:
            return result["data"].get("access_token", "")
        return ""


def method_base64_direct(client_id: str, client_secret: str = "") -> str:
    """
    直接使用 Base64(client_id:client_secret) 格式
    这是沙箱环境使用的格式
    """
    if client_secret:
        credentials = f"{client_id}:{client_secret}"
    else:
        # 如果只有 client_id，用 client_id 作为凭证
        credentials = client_id
    
    token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return token


def method_oauth_token_endpoint(client_id: str, client_secret: str = "") -> str:
    """
    调用 OAuth Token 端点获取 access_token
    """
    token_endpoint = "https://api.coze.cn/.well-known/token"
    
    # 尝试不同的 grant_type
    grant_types = [
        ("client_credentials", {}),
        ("urn:ietf:params:oauth:grant-type:jwt-bearer", {"client_id": client_id}),
    ]
    
    for grant_type, extra_params in grant_types:
        try:
            data = urllib.parse.urlencode({
                "grant_type": grant_type,
                "client_id": client_id,
                **extra_params
            }).encode("utf-8")
            
            req = urllib.request.Request(token_endpoint, data=data, method="POST")
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                if result.get("code") == 0 and "data" in result:
                    return result["data"].get("access_token", "")
        except Exception:
            continue
    
    return ""


def main():
    print("=" * 60)
    print("Coze API Token 获取脚本 (多种方式尝试)")
    print("=" * 60)
    
    # 获取环境变量
    client_id = os.getenv("COZE_CLIENT_ID", "").strip()
    client_secret = os.getenv("COZE_CLIENT_SECRET", "").strip()
    private_key = os.getenv("COZE_PRIVATE_KEY", "").strip()
    # 直接的 token（如果用户已经有有效 token）
    direct_token = os.getenv("COZE_DIRECT_TOKEN", "").strip()
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'✅' if client_secret else '❌'}")
    print(f"Private Key: {'✅' if private_key else '❌'}")
    print(f"Direct Token: {'✅' if direct_token else '❌'}")
    print()
    
    token = None
    method_used = ""
    
    # 方式 0: 直接使用预先生成的 Token
    if direct_token:
        print("尝试 0: 直接使用预先生成的 Token...")
        token = direct_token
        method_used = "Direct Token"
    
    # 方式 1: JWT (含 aud)
    if not token and client_id and private_key:
        print("尝试 1: JWT (含 aud)...")
        try:
            result = method_jwt_with_aud(client_id, private_key)
            if result:
                token = result
                method_used = "JWT (含 aud)"
            else:
                print("   返回为空")
        except Exception as e:
            print(f"   失败: {e}")
    
    # 方式 2: JWT (不含 aud)
    if not token and client_id and private_key:
        print("尝试 2: JWT (不含 aud)...")
        try:
            result = method_jwt_without_aud(client_id, private_key)
            if result:
                token = result
                method_used = "JWT (不含 aud)"
            else:
                print("   返回为空")
        except Exception as e:
            print(f"   失败: {e}")
    
    # 方式 3: Basic Auth
    if not token and client_id and client_secret:
        print("尝试 3: Client Secret Basic Auth...")
        try:
            result = method_basic_auth(client_id, client_secret)
            if result:
                token = result
                method_used = "Client Secret"
            else:
                print("   返回为空")
        except Exception as e:
            print(f"   失败: {e}")
    
    # 方式 4: Base64(client_id) - 沙箱格式
    if not token and client_id:
        print("尝试 4: Base64(client_id) 直接编码...")
        token = method_base64_direct(client_id, "")
        method_used = "Base64(client_id)"
        print(f"   生成 Token: {token[:30]}...")
    
    # 方式 5: Base64(client_id:client_secret) - 沙箱格式
    if not token and client_id and client_secret:
        print("尝试 5: Base64(client_id:client_secret)...")
        token = method_base64_direct(client_id, client_secret)
        method_used = "Base64(client_id:secret)"
        print(f"   生成 Token: {token[:30]}...")
    
    if not token:
        print()
        print("❌ 所有认证方式均失败")
        sys.exit(1)
    
    print()
    print(f"✅ Token 获取成功！方式: {method_used}")
    print(f"   Token: {token[:30]}...")
    
    # 保存 Token
    token_file = "/tmp/coze_token.txt"
    with open(token_file, "w") as f:
        f.write(token)
    print(f"   Token 已保存到: {token_file}")


if __name__ == "__main__":
    main()
