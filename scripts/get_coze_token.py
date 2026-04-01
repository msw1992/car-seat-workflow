#!/usr/bin/env python3
"""
获取 Coze API Token 的脚本

Token 格式：dmpl + Base64(client_id:client_secret)

注意：这里不需要调用 OAuth 端点，直接生成 Token！
"""

import os
import sys
import base64


def generate_token(client_id: str, client_secret: str) -> str:
    """
    生成 SDK 使用的 Token
    
    Token 格式：dmpl + Base64(client_id:client_secret)
    """
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    token = f"dmpl{encoded}"
    return token


def main():
    print("=" * 60)
    print("Coze API Token 生成脚本")
    print("=" * 60)
    
    # 获取环境变量
    client_id = os.getenv("COZE_CLIENT_ID", "").strip()
    client_secret = os.getenv("COZE_CLIENT_SECRET", "").strip()
    
    if not client_id or not client_secret:
        print("❌ 错误：缺少环境变量")
        print()
        print("请设置以下环境变量：")
        print("  COZE_CLIENT_ID=你的ClientID")
        print("  COZE_CLIENT_SECRET=你的ClientSecret")
        sys.exit(1)
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: ✅")
    print()
    
    # 生成 Token
    print("正在生成 Token...")
    token = generate_token(client_id, client_secret)
    
    print()
    print(f"✅ Token 生成成功！")
    print(f"   Token: {token}")
    
    # 保存 Token
    token_file = "/tmp/coze_token.txt"
    with open(token_file, "w") as f:
        f.write(token)
    print(f"   Token 已保存到: {token_file}")


if __name__ == "__main__":
    main()
