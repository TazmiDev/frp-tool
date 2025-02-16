# FRP Command Line Tool

A Python command line tool to simplify FRP client operations, supporting quick port forwarding and configuration management.

## Installation

### Prerequisites
- Python 3.8+
- [frpc tool](https://github.com/fatedier/frp/releases), we support the frp tool author!

### Quick Installation
```powershell
./install.ps1
```

## User Guide

### Quick Start
1. Initialize configuration
```bash
frp --set server=frp.example.com:7000 --set token=your_token
```

2. Start HTTP forwarding
```bash
frp --http 8080
```

3. View current configuration (sensitive information is automatically hidden)
```bash
frp --config
```

### Command Description
| Option       | Description                          | Example                     |
|--------------|--------------------------------------|-----------------------------|
| --tcp        | TCP port forwarding (LOCAL:REMOTE)   | --tcp 8000:9999             |
| --udp        | UDP port forwarding                  | --udp 5353:53               |
| --http       | HTTP forwarding                      | --http 8080                 |
| --https      | HTTPS forwarding                     | --https 8443                |
| --set        | Set configuration parameters         | --set server=1.1.1.1:7000   |
| --config     | Show current configuration           | --config                    |
| --save       | Save configuration preset            | --save 3306:3307 --conf mysql|
| run          | run --conf file                      | run mysql                   |

### Typical Scenarios
#### TCP Forwarding
```bash
frp --tcp 3306:13306
```

## Notes

1. Before first use:
    - Download the frpc binary files `frpc.exe`  for your platform
    - Place them in the following path `./frpinit`

2. Windows systems may require:
    - Running as administrator
    - Allowing firewall communication

3. Uninstall the tool:
```powershell
.\uninstall.ps1
```
## Implementation Principles

- Dynamically generate TOML configuration files
- Automatically manage the lifecycle of temporary files
- Safely terminate child processes using process signals
- Persistent configuration storage

```
> 📌 Tip: It is recommended to use with the latest frps v0.61.1 version for the best compatibility.
```