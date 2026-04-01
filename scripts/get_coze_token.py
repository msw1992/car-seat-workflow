#!/usr/bin/env python3
"""
获取 Coze API Token 的脚本
支持两种认证方式：
1. Client ID + Client Secret (Basic Auth) - Web 后端应用
2. Private Key JWT 断言 - 服务类应用

使用方法：
  # 方式一：Client ID + Client Secret
  export COZE_CLIENT_ID=your_client_id
  export COZE_CLIENT_SECRET=your_client_secret
  python scripts/get_coze_token.py
  
  # 方式二：Private Key JWT
  export COZE_PRIVATE_KEY=your_private_key_content
  python scripts/get_coze_token.py
"""

import os
import sys
import base64
import json
import time
import hashlib
import hmac
import urllib.request
import urllib.error
import urllib.parse

# 检查 cryptography 是否可用
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
    from cryptography.exceptions import InvalidSignature
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def get_token_with_client_secret(client_id: str, client_secret: str) -> str:
    """
    使用 Client ID + Client Secret 获取 Token (Basic Auth)
    适用于 Web 后端应用
    """
    token_endpoint = os.getenv(
        "COZE_WORKLOAD_IDENTITY_TOKEN_ENDPOINT",
        "https://api.coze.cn/.well-known/token"
    )
    
    # 构造 Basic Auth 凭证
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    
    # 构造请求
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    
    req = urllib.request.Request(
        token_endpoint,
        data=data,
        method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Basic {encoded_credentials}")
    req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
    
    return _do_token_request(req)


def generate_jwt_token(client_id: str, private_key: str) -> str:
    """
    生成 JWT 断言用于私钥认证
    
    Args:
        client_id: OAuth 应用的 Client ID
        private_key: RSA 私钥内容
        
    Returns:
        JWT 断言字符串
    """
    if not HAS_CRYPTO:
        raise Exception("cryptography 库未安装，请使用 pip install cryptography")
    
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
        "exp": current_time + 3600,  # 1小时后过期
        "jti": f"{current_time}-{os.urandom(16).hex()}"
    }
    
    # Base64url 编码
    def base64url_encode(data: dict) -> str:
        json_str = json.dumps(data, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
        return encoded.rstrip('=')
    
    header_b64 = base64url_encode(header)
    payload_b64 = base64url_encode(payload)
    
    # 签名内容
    signing_content = f"{header_b64}.{payload_b64}"
    
    # 使用私钥签名
    try:
        # 尝试加载 PEM 格式私钥
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
            # 尝试 base64 解码后加载
            decoded_key = base64.b64decode(private_key)
            key_obj = serialization.load_der_private_key(
                decoded_key,
                password=None,
                backend=default_backend()
            )
    except Exception as e:
        raise Exception(f"无法解析私钥格式: {e}")
    
    # 使用 RS256 签名
    signature = key_obj.sign(
        signing_content.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    signature_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    return f"{signing_content}.{signature_b64}"


def get_token_with_private_key(client_id: str, private_key: str) -> str:
    """
    使用 Private Key JWT 断言获取 Token
    适用于服务类应用
    """
    if not HAS_CRYPTO:
        raise Exception("cryptography 库未安装，请使用 pip install cryptography")
    
    token_endpoint = os.getenv(
        "COZE_WORKLOAD_IDENTITY_TOKEN_ENDPOINT",
        "https://api.coze.cn/.well-known/token"
    )
    
    # 生成 JWT 断言
    jwt_assertion = generate_jwt_token(client_id, private_key)
    
    # 构造请求
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt_assertion
    }).encode("utf-8")
    
    req = urllib.request.Request(
        token_endpoint,
        data=data,
        method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("X-Client-Sdk", "coze-coding-dev-sdk-python/0.5.0")
    
    return _do_token_request(req)


def _do_token_request(req: urllib.request.Request) -> str:
    """执行 Token 请求"""
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            if result.get("code") == 0 and "data" in result:
                token = result["data"].get("access_token")
                if token:
                    return token
                    
            raise Exception(f"获取 Token 失败: {result}")
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get("msg", error_body)
        except:
            error_msg = error_body
        raise Exception(f"HTTP 错误 {e.code}: {error_msg}")
    except Exception as e:
        raise Exception(f"获取 Token 失败: {str(e)}")


def main():
    print("=" * 60)
    print("Coze API Token 获取脚本")
    print("=" * 60)
    
    # 检查是否安装了 cryptography
    if not HAS_CRYPTO:
        print("⚠️  提示: cryptography 库未安装")
        print("   如果使用私钥认证，请先安装: pip install cryptography")
        print()
    
    # 获取环境变量
    client_id = os.getenv("COZE_CLIENT_ID", "").strip()
    client_secret = os.getenv("COZE_CLIENT_SECRET", "").strip()
    private_key = os.getenv("COZE_PRIVATE_KEY", "").strip()
    
    token = None
    auth_method = ""
    
    # 优先使用私钥认证
    if client_id and private_key:
        print("🔐 检测到私钥配置，使用 JWT 断言认证...")
        print(f"   Client ID: {client_id[:12]}...{client_id[-4:] if len(client_id) > 16 else ''}")
        try:
            token = get_token_with_private_key(client_id, private_key)
            auth_method = "Private Key JWT"
        except Exception as e:
            print(f"❌ 私钥认证失败: {e}")
            if not client_secret:
                sys.exit(1)
            print("   降级尝试 Client Secret 认证...")
    
    # 降级使用 Client Secret
    if not token and client_id and client_secret:
        print("🔐 检测到 Client Secret 配置，使用 Basic Auth...")
        print(f"   Client ID: {client_id[:12]}...{client_id[-4:] if len(client_id) > 16 else ''}")
        token = get_token_with_client_secret(client_id, client_secret)
        auth_method = "Client Secret"
    
    if not token:
        print("❌ 错误：未找到有效的认证凭证")
        print("")
        print("请设置以下环境变量之一：")
        print("")
        print("方式一：Client ID + Client Secret (Web 后端应用)")
        print("  export COZE_CLIENT_ID=your_client_id")
        print("  export COZE_CLIENT_SECRET=your_client_secret")
        print("")
        print("方式二：Client ID + Private Key (服务类应用)")
        print("  export COZE_CLIENT_ID=your_client_id")
        print("  export COZE_PRIVATE_KEY=\"$(cat private_key.pem)\"")
        print("")
        print("详细说明请参考: docs/COZE_OAUTH_CONFIG_GUIDE.md")
        sys.exit(1)
    
    print()
    print(f"✅ Token 获取成功！认证方式: {auth_method}")
    print(f"   Token: {token[:20]}...{token[-10:]}")
    
    # 写入临时文件供后续使用
    token_file = os.getenv("COZE_TOKEN_FILE", "/tmp/coze_token.txt")
    with open(token_file, "w") as f:
        f.write(token)
    print(f"   Token 已保存到: {token_file}")
    
    # 同时输出供 GitHub Actions 使用
    print()
    print(f"::add-mask::token")
    print(f"::set-output name=token::{token}")


if __name__ == "__main__":
    main()
