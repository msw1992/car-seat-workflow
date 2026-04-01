#!/usr/bin/env python3
"""
获取 Coze API Token 的脚本
使用 OAuth 2.0 客户端凭证模式获取访问 Token

使用方法：
  python scripts/get_coze_token.py
  
环境变量：
  COZE_CLIENT_ID     - OAuth 应用 Client ID
  COZE_CLIENT_SECRET - OAuth 应用 Client Secret

输出：
  将 Token 写入临时文件或直接设置环境变量
"""

import os
import sys
import base64
import json
import urllib.request
import urllib.error


def get_oauth_token(client_id: str, client_secret: str) -> str:
    """
    使用 OAuth 2.0 客户端凭证模式获取访问 Token
    
    Args:
        client_id: OAuth 应用的 Client ID
        client_secret: OAuth 应用的 Client Secret
        
    Returns:
        访问 Token 字符串
        
    Raises:
        Exception: 获取 Token 失败时抛出异常
    """
    # OAuth Token 端点
    token_endpoint = os.getenv(
        "COZE_WORKLOAD_IDENTITY_TOKEN_ENDPOINT",
        "https://api.coze.cn/.well-known/token"
    )
    
    # 构造 Basic Auth 凭证（Base64(client_id:client_secret)）
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
        raise Exception(f"HTTP 错误 {e.code}: {error_body}")
    except Exception as e:
        raise Exception(f"获取 Token 失败: {str(e)}")


def main():
    # 获取环境变量
    client_id = os.getenv("COZE_CLIENT_ID", "").strip()
    client_secret = os.getenv("COZE_CLIENT_SECRET", "").strip()
    
    if not client_id or not client_secret:
        print("❌ 错误：缺少环境变量 COZE_CLIENT_ID 或 COZE_CLIENT_SECRET")
        print("")
        print("请设置以下环境变量：")
        print("  export COZE_CLIENT_ID=your_client_id")
        print("  export COZE_CLIENT_SECRET=your_client_secret")
        sys.exit(1)
    
    try:
        print(f"正在获取 Coze API Token...")
        print(f"Client ID: {client_id[:8]}...{client_id[-4:]}")
        
        token = get_oauth_token(client_id, client_secret)
        
        print(f"✅ Token 获取成功！")
        print(f"Token: {token[:20]}...{token[-10:]}")
        
        # 输出 Token（供其他脚本使用）
        print(f"\n[TOKEN_OUTPUT] {token}")
        
        # 写入临时文件供后续使用
        token_file = os.getenv("COZE_TOKEN_FILE", "/tmp/coze_token.txt")
        with open(token_file, "w") as f:
            f.write(token)
        print(f"Token 已保存到: {token_file}")
        
        return token
        
    except Exception as e:
        print(f"❌ 获取 Token 失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
