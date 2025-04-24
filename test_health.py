import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取 API_KEY
API_KEY = os.getenv("API_KEY")

# 基础 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查端点"""
    # 设置请求头
    headers = {
        "X-API-Key": API_KEY
    }

    # 发送请求
    response = requests.get(f"{BASE_URL}/health", headers=headers)

    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 验证响应
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "ok" and data.get("api_key_status") == "valid":
            print("✅ 健康检查测试通过!")
            return True

    print("❌ 健康检查测试失败!")
    return False

def test_health_check_invalid_key():
    """测试使用无效 API_KEY 的健康检查端点"""
    # 设置请求头
    headers = {
        "X-API-Key": "invalid-key"
    }

    # 发送请求
    response = requests.get(f"{BASE_URL}/health", headers=headers)

    # 打印响应
    print(f"无效密钥测试 - 状态码: {response.status_code}")

    # 验证响应
    if response.status_code == 403:
        print("✅ 无效 API_KEY 测试通过!")
        return True

    print("❌ 无效 API_KEY 测试失败!")
    return False

if __name__ == "__main__":
    print("=== 测试健康检查端点 ===")
    print(f"使用 API_KEY: {API_KEY}")

    # 运行测试
    test_health_check()
    print()
    test_health_check_invalid_key()
