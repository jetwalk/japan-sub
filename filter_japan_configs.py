import requests
import base64
import json
import urllib.parse
from datetime import datetime
import os

# 目标文件 URL
SOURCE_URL = "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt"
# 输出文件路径
OUTPUT_FILE = "japan_configs.txt"
OUTPUT_BASE64_FILE = "japan_configs_base64.txt"

def fetch_configs():
    """下载配置文件"""
    try:
        response = requests.get(SOURCE_URL, timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.RequestException as e:
        print(f"Error fetching configs: {e}")
        return []

def is_japan_node(config_line):
    """判断是否为日本节点"""
    protocols = ["vmess://", "vless://", "ss://", "trojan://", "hysteria2://"]
    if not any(config_line.startswith(proto) for proto in protocols):
        return False

    try:
        if config_line.startswith("vmess://"):
            # VMess 配置需要 Base64 解码
            config_data = config_line.replace("vmess://", "")
            config_data = base64.b64decode(config_data).decode("utf-8")
            config = json.loads(config_data)
            remark = config.get("ps", "")
        elif config_line.startswith("hysteria2://"):
            # Hysteria2 配置解析
            parsed = urllib.parse.urlparse(config_line)
            remark = parsed.fragment  # 备注在 URL 的 fragment 部分
        else:
            # VLESS, Shadowsocks, Trojan 配置
            parsed = urllib.parse.urlparse(config_line)
            remark = parsed.fragment

        # 检查备注是否包含日本标识
        japan_keywords = ["JP", "Japan", "japan", "🇯🇵", "日本"]
        return any(keyword in remark for keyword in japan_keywords)
    except Exception as e:
        print(f"Error parsing config: {config_line}, {e}")
        return False

def save_configs(configs):
    """保存筛选出的配置到文件"""
    if not configs:
        print("No Japan configs found.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(configs) + "\n")
    print(f"Saved {len(configs)} Japan configs to {OUTPUT_FILE}")

    configs_content = "\n".join(configs) + "\n"
    base64_content = base64.b64encode(configs_content.encode("utf-8")).decode("utf-8")
    with open(OUTPUT_BASE64_FILE, "w", encoding="utf-8") as f:
        f.write(base64_content)
    print(f"Saved Base64 encoded configs to {OUTPUT_BASE64_FILE}")

def main():
    print(f"Running at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    configs = fetch_configs()
    if not configs:
        print("No configs fetched. Exiting.")
        return

    japan_configs = [line for line in configs if is_japan_node(line)]
    save_configs(japan_configs)

if __name__ == "__main__":
    main()
