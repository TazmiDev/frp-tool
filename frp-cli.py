#!/usr/bin/env python3
import os
import sys
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import shutil
import signal
import time
from typing import Optional

# Configuration file paths
CONFIG_DIR = Path.home() / ".frp"
CONFIG_FILE = CONFIG_DIR / "config.json"
SAVED_CONF_DIR = CONFIG_DIR / "configs"

# Initialize configuration
def init_config():
    CONFIG_DIR.mkdir(exist_ok=True)
    SAVED_CONF_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "server_addr": "127.0.0.1",
                "server_port": 7000,
                "token": "your_token"
            }, f)

# Read configuration (with token masking)
def get_config(hide_token=True):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    if hide_token and "token" in config:
        config["token"] = "******"
    return config

# Update configuration
def update_config(key, value):
    config = get_config(hide_token=False)
    if key == "server":
        addr, port = value.split(":")
        config["server_addr"] = addr
        config["server_port"] = int(port)
    else:
        config[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def generate_temp_config(protocol: str, local_port: int, remote_port: Optional[int] = None):
    config = get_config(hide_token=False)
    base_config = f"""serverAddr = "{config['server_addr']}"
serverPort = {config['server_port']}
auth.token = "{config['token']}"

[[proxies]]
name = "temp_{local_port}_{remote_port or 'auto'}"
type = "{protocol}"
localPort = {local_port}
"""
    
    if protocol in ["http", "https"]:
        base_config += "customDomains = [\"example.com\"]\n"
        if remote_port:
            base_config += f"remotePort = {remote_port}\n"
    elif remote_port:
        base_config += f"remotePort = {remote_port}\n"
    
    return base_config

def save_config(name: str, protocol: str, local_port: int, remote_port: Optional[int] = None):
    config = get_config(hide_token=False)
    conf_content = f"""serverAddr = "{config['server_addr']}"
serverPort = {config['server_port']}"
auth.token = "{config['token']}"

[[proxies]]
name = "{name}"
type = "{protocol}"
localPort = {local_port}
"""
    if remote_port:
        conf_content += f"remotePort = {remote_port}\n"
    if protocol in ["http", "https"]:
        conf_content += 'customDomains = ["example.com"]\n'

    conf_path = SAVED_CONF_DIR / f"{name}.toml"
    with open(conf_path, "w") as f:
        f.write(conf_content)
    print(f"Configuration saved to {conf_path}")

# Enhanced FRP run function
def run_frp(config_content=None, config_file=None):
    # Modify this part of the code
    frp_dir = Path(__file__).parent / "frpinit"
    frpc = frp_dir / "frpc.exe"
    
    # Enhanced path checking
    if not frp_dir.exists():
        print(f"Error: FRP directory does not exist {frp_dir}")
        sys.exit(1)
    
    if not frpc.exists():
        print(f"Error: FRP client not found, please ensure the following file exists: {frpc}")
        sys.exit(1)

    process = None
    tmp_path = None

    def cleanup():
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    def signal_handler(sig, frame):
        print("\nTerminating process...")
        if process:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], shell=True)
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as tmp:
            if config_content:
                tmp.write(config_content)
                tmp_path = tmp.name
            elif config_file:
                shutil.copy(config_file, tmp.name)
                tmp_path = tmp.name

        process = subprocess.Popen([str(frpc), "-c", tmp_path])
        process.wait()
    finally:
        cleanup()

# New configuration display function
def show_config():
    config = get_config()
    print("Current configuration:")
    print(f"Server address: {config['server_addr']}:{config['server_port']}")
    print(f"Auth token: {config['token']}")
    
    print("\nSaved configurations:")
    for conf_file in SAVED_CONF_DIR.glob("*.toml"):
        print(f"- {conf_file.stem}")

HELP_TEXT = {
    "en": """Usage: frp [OPTIONS]
Options:
  --tcp LOCAL[:REMOTE]    TCP port forwarding
  --udp LOCAL[:REMOTE]    UDP port forwarding
  --http(s) LOCAL[:REMOTE] HTTP/HTTPS forwarding
  --set KEY=VALUE         Set config (server=IP:PORT, token=XXX)
  --save LOCAL[:REMOTE] --conf NAME  Save configuration
  --config                Show current configuration
  run CONFIG_NAME         Run saved configuration
  --help [LANG]           Show help (supported: zh-CN, ru)
""",

    "zh-CN": """用法: frp [选项]
选项:
  --tcp 本地[:远程]       TCP端口映射
  --udp 本地[:远程]       UDP端口映射
  --http(s) 本地[:远程]   HTTP/HTTPS映射
  --set 键=值            设置配置项 (server=IP:端口, token=XXX)
  --save 本地[:远程] --conf 名称 保存配置
  --config               显示当前配置
  run 配置名称           运行已保存的配置
  --help [语言]          显示帮助 (支持zh-CN, ru)
""",

    "ru": """Использование: frp [ОПЦИИ]
Опции:
  --tcp ЛОКАЛЬНЫЙ[:УДАЛЕННЫЙ] TCP проброс
  --udp ЛОКАЛЬНЫЙ[:УДАЛЕННЫЙ] UDP проброс 
  --http(s) ЛОКАЛЬНЫЙ[:УДАЛЕННЫЙ] HTTP/HTTPS проброс
  --set КЛЮЧ=ЗНАЧЕНИЕ     Настройки (server=IP:PORT, token=XXX)
  --save ЛОКАЛЬ[:УДАЛЕН] --conf ИМЯ Сохранить конфиг
  --config               Показать текущие настройки
  run ИМЯ_КОНФИГА        Запустить сохраненную конфигурацию
  --help [ЯЗЫК]          Справка (поддерживается zh-CN, ru)
"""
}

def parse_port(port_str: str, default_remote=None):
    if ":" in port_str:
        local, remote = port_str.split(":", 1)
        return int(local), int(remote)
    return int(port_str), default_remote

def main():
    init_config()
    parser = argparse.ArgumentParser(add_help=False)
    
    # Use subcommand parser
    subparsers = parser.add_subparsers(dest='command', title='subcommands')
    
    # Run command parser
    run_parser = subparsers.add_parser('run', help='Run saved configuration')
    run_parser.add_argument('config_name', help='Configuration name to run')
    
    # Common parameters
    parser.add_argument("--tcp", nargs='?')
    parser.add_argument("--udp", nargs='?')
    parser.add_argument("--http", nargs='?')
    parser.add_argument("--https", nargs='?')
    parser.add_argument("--set", nargs=1)
    parser.add_argument("--save", nargs='?')
    parser.add_argument("--conf", nargs=1)
    parser.add_argument("--config", action='store_true')
    parser.add_argument("--help", nargs="*")
    
    args = parser.parse_args()
    
    if args.config:
        show_config()
        return
    
    if args.help is not None:
        lang = args.help[0] if args.help else "en"
        print(HELP_TEXT.get(lang, HELP_TEXT["en"]))
        return
    
    if args.set:
        key, value = args.set[0].split("=", 1)
        update_config(key, value)
        print(f"Configuration updated: {key} = {value}")
        return
    
    if args.save and args.conf:
        protocol = "tcp"
        if ":" in args.save:
            local, remote = parse_port(args.save)
        else:
            local = args.save
            remote = None
        save_config(args.conf[0], protocol, local, remote)
        return
    
    # Handle run command
    if args.command == 'run':
        conf_file = SAVED_CONF_DIR / f"{args.config_name}.toml"
        if not conf_file.exists():
            print(f"Error: Configuration {args.config_name} does not exist")
            return
        run_frp(config_file=conf_file)
        return
    
    # Handle protocol parameters
    protocol_map = {
        '--tcp': 'tcp',
        '--udp': 'udp', 
        '--http': 'http',
        '--https': 'https'
    }
    
    for arg in protocol_map:
        port_str = getattr(args, arg[2:])
        if port_str:
            protocol = protocol_map[arg]
            local, remote = parse_port(port_str, None if protocol in ['http', 'https'] else 0)
            config_content = generate_temp_config(protocol, local, remote)
            run_frp(config_content=config_content)
            return

    # Show help if no parameters
    print(HELP_TEXT["en"])

if __name__ == "__main__":
    main()