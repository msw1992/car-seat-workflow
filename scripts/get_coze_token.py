#!/usr/bin/env python3
"""
获取 Coze API Token 的脚本
支持多种认证方式：
1. Private Key JWT - 服务类应用（应用ID + 私钥）
2. Client Secret Basic Auth - Web 后端应用

使用方法：
  python scripts/get_coze_token.py
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
    """
    生成 JWT 断言用于私钥认证
    
    Args:
        client_id: 应用 ID
        private_key: RSA 私钥内容
        include_aud: 是否包含 aud 字段
    """
    if not HAS_CRYPTO:
        raise Exception("cryptography 库未安装")
    
    # JWT Header
    header = {
        "alg": "RS256",
        "typ": "JWT"
    }
    
    # JWT Payload - Claims
    current_time = int(time.time())
    payload = {
        "iss": client_id,
        "iat": current_time,
        "exp": current_time + 3600,
        "jti": f"{current_time}-{os.urandom(16).hex()}"
    }
    
    # 尝试添加 aud 字段
    if include_aud:
        payload["aud"] = "https://api.coze.cn"
    
    # Base64url 编码
    def base64url_encode(data: dict) -> str:
        json_str = json.dumps(data, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
        return encoded.rstrip('=')
    
    header_b64 = base64url_encode(header)
    payload_b64 = base64url_encode(payload)
    
    signing_content = f"{header_b64}.{payload_b64}"
    
    # 加载私钥
    try:
        if private_key.startswith('-----BEGIN'):
            key_obj = serialization.load_pem_private_key(
                private_key.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
        elif private_key.startswith('-----BEGIN RSA'):
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
    
    # 签名
    signature = key_obj.sign(
        signing_content.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    return f"{signing_content}.{signature_b64}"


def try_jwt_auth(client_id: str, private_key: str, include_aud: bool, 
                 client_assertion_type: str = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer") -> str:
    """
    尝试 JWT 认证
    """
    token_endpoint = "https://api.coze.cn/.well-known/token"
    
    jwt_assertion = generate_jwt_token(client_id, private_key, include_aud)
    
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_assertion_type": client_assertion_type,
        "client_assertion": jwt_assertion
    }).encode("utf-8")
    
    req = urllib.request.Request(
        token_endpoint,
        data=data,
        method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        
        if result.get("code") == 0 and "data" in result:
            token = result["data"].get("access_token")
            if token:
                return token
        
        raise Exception(f"获取 Token 失败: {result}")


def try_basic_auth(client_id: str, client_secret: str) -> str:
    """
    尝试 Basic Auth (Client Secret)
    """
    token_endpoint = "https://api.coze.cn/.well-known/token"
    
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    
    req = urllib.request.Request(
        token_endpoint,
        data=data,
        method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Basic {encoded_credentials}")
    req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        
        if result.get("code") == 0 and "data" in result:
            token = result["data"].get("access_token")
            if token:
                return token
        
        raise Exception(f"获取 Token 失败: {result}")


def main():
    print("=" * 60)
    print("Coze API Token 获取脚本")
    print("=" * 60)
    
    # 获取环境变量
    client_id = os.getenv("COZE_CLIENT_ID", "").strip()
    client_secret = os.getenv("COZE_CLIENT_SECRET", "").strip()
    private_key = os.getenv("COZE_PRIVATE_KEY", "").strip()
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'✅' if client_secret else '❌'}")
    print(f"Private Key: {'✅' if private_key else '❌'}")
    print()
    
    token = None
    method_used = ""
    
    # 方法1: 私钥 JWT (包含 aud)
    if client_id and private_key:
        print("尝试 1: JWT (含 aud 字段)...")
        try:
            token = try_jwt_auth(client_id, private_key, include_aud=True)
            method_used = "JWT (含 aud)"
        except Exception as e:
            print(f"   失败: {e}")
    
    # 方法2: 私钥 JWT (不包含 aud)
    if not token and client_id and private_key:
        print("尝试 2: JWT (不含 aud 字段)...")
        try:
            token = try_jwt_auth(client_id, private_key, include_aud=False)
            method_used = "JWT (不含 aud)"
        except Exception as e:
            print(f"   失败: {e}")
    
    # 方法3: Client Secret Basic Auth
    if not token and client_id and client_secret:
        print("尝试 3: Client Secret Basic Auth...")
        try:
            token = try_basic_auth(client_id, client_secret)
            method_used = "Client Secret"
        except Exception as e:
            print(f"   失败: {e}")
    
    if not token:
        print()
        print("❌ 所有认证方式均失败")
        print()
        print("请检查：")
        print("1. Client ID 是否正确（应该是以 dmpl 开头的字符串）")
        print("2. Private Key 是否与应用匹配")
        print("3. 应用是否已启用")
        sys.exit(1)
    
    print()
    print(f"✅ Token 获取成功！方式: {method_used}")
    print(f"   Token: {token[:20]}...{token[-10:]}")
    
    # 保存 Token
    token_file = "/tmp/coze_token.txt"
    with open(token_file, "w") as f:
        f.write(token)
    print(f"   Token 已保存到: {token_file}")


if __name__ == "__main__":
    main()
