#!/usr/bin/env python3
"""
获取 Coze API Token 的脚本

认证方式：Base64(client_id:client_secret)
Client ID 格式：xxx.app.coze
Client Secret：从 Web 后端应用获取
"""

import os
import sys
import base64
import json
import urllib.request
import urllib.error
import urllib.parse


def get_token_basic_auth(client_id: str, client_secret: str) -> str:
    """
    使用 Client ID + Client Secret 获取 Token
    凭证格式：Base64(client_id:client_secret)
    """
    token_endpoint = "https://api.coze.cn/.well-known/token"
    
    # 构造凭证
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    
    print(f"   Client ID: {client_id}")
    print(f"   Client Secret: {'✅' if client_secret else '❌'}")
    print(f"   Encoded: {encoded_credentials[:40]}...")
    
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
            print(f"   响应: {result}")
            
            if result.get("code") == 0 and "data" in result:
                token = result["data"].get("access_token")
                if token:
                    return token
            
            raise Exception(f"获取 Token 失败: {result}")
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"   HTTP 错误: {e.code}")
        print(f"   响应内容: {error_body}")
        raise Exception(f"HTTP {e.code}: {error_body}")
    except Exception as e:
        print(f"   异常: {e}")
        raise


def main():
    print("=" * 60)
    print("Coze API Token 获取脚本")
    print("=" * 60)
    
    # 获取环境变量
    client_id = os.getenv("COZE_CLIENT_ID", "").strip()
    client_secret = os.getenv("COZE_CLIENT_SECRET", "").strip()
    
    if not client_id or not client_secret:
        print("❌ 错误：缺少环境变量")
        print()
        print("请设置以下环境变量：")
        print("  COZE_CLIENT_ID=19499234802410690483057804554110.app.coze")
        print("  COZE_CLIENT_SECRET=你的客户端密钥")
        sys.exit(1)
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'✅' if client_secret else '❌'}")
    print()
    
    try:
        print("正在获取 Token (Basic Auth)...")
        token = get_token_basic_auth(client_id, client_secret)
        
        print()
        print(f"✅ Token 获取成功！")
        print(f"   Token: {token[:30]}...{token[-10:]}")
        
        # 保存 Token
        token_file = "/tmp/coze_token.txt"
        with open(token_file, "w") as f:
            f.write(token)
        print(f"   Token 已保存到: {token_file}")
        
    except Exception as e:
        print()
        print(f"❌ 获取 Token 失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
