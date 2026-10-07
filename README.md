# Networking Labs

Hands-on networking study labs built for CompTIA Network+ prep: a working subnet calculator, a subnetting cheat sheet I actually use, and a command-line troubleshooting guide written from real lab scenarios.

## Contents

| File | What it is |
|---|---|
| `subnet_calculator.py` | Working IPv4 subnet calculator (stdlib only). Feed it `192.168.1.77/24` and get network, broadcast, first/last usable, host count, masks, and wildcard — with correct /31 (RFC 3021) and /32 handling. |
| `SUBNETTING.md` | Practical subnetting cheat sheet: /24–/30 table, the "interesting octet" method, and 3 worked examples. |
| `troubleshooting-guide.md` | Layered "can't connect" workflow using `ipconfig`, `ping`, `tracert`, `nslookup`, and `netstat` — with example outputs, a results matrix, and 3 real ticket scenarios. |

## Skills demonstrated

- IPv4 subnetting (CIDR, VLSM, block-size math)
- DNS/DHCP fundamentals and failure modes
- Bottom-up troubleshooting methodology (physical → network → transport → application)
- Python stdlib (`ipaddress`, `argparse`) for network tooling

## What I learned

- Subnetting stopped being memorization once I learned the block-size method — it's just arithmetic.
- Most "network is down" tickets are DNS, DHCP, or layer-1. The `ping gateway → ping 8.8.8.8 → ping by name` sequence isolates the layer in 30 seconds.
- Writing the calculator forced me to handle the edge cases (/31, /32) that exam questions love.

## How to run

```bash
# Subnet calculator (Python 3, no dependencies)
python3 subnet_calculator.py 192.168.1.77/24
python3 subnet_calculator.py 10.0.0.5 --mask 255.255.255.0
python3 subnet_calculator.py 172.16.0.5/31 --binary
```

Example output:

```
Input:           192.168.1.77/24
Network:         192.168.1.0/24
Broadcast:       192.168.1.255
First usable:    192.168.1.1
Last usable:     192.168.1.254
Usable hosts:    254
Subnet mask:     255.255.255.0
Wildcard mask:   0.0.0.255
Total addresses: 256
```

The cheat sheet and troubleshooting guide are Markdown — read them right here on GitHub.
