# Network Troubleshooting Guide

How to work a "can't connect" ticket from the command line, layer by layer. Every section shows the command, what healthy output looks like, and how to read the failure. Built while studying for Network+ and tested in my AD homelab.

**Golden rule: troubleshoot bottom-up.** Don't blame DNS when the cable's unplugged. Fix the lowest failing layer first.

---

## Step 0 — `ipconfig` (Windows) / `ip addr` (Linux): do I even have an address?

```
C:\> ipconfig
Ethernet adapter LAB:
   IPv4 Address. . . . . . . . . . . : 192.168.56.20
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.56.10
```

What to read:
- **169.254.x.x (APIPA)** → DHCP failed. The machine gave *itself* an address because no DHCP server answered. Check: is the DHCP server up? Is the client on the right VLAN/network?
- **0.0.0.0** → adapter disabled or driver issue.
- **Correct IP but wrong gateway/DNS** → DHCP scope misconfigured, or a static entry someone forgot about.

Useful variants:
```
ipconfig /all      # full detail: MAC, DHCP server, DNS servers, lease times
ipconfig /release  # drop the DHCP lease
ipconfig /renew    # request a fresh one
ipconfig /flushdns # clear stale DNS cache (fixes "site moved servers" issues)
```

---

## Step 1 — `ping`: is the path alive?

Start close, move outward. Stop at the first failure — that's your layer.

```
C:\> ping 192.168.56.10        # 1. default gateway
C:\> ping 8.8.8.8              # 2. internet IP (bypasses DNS)
C:\> ping www.google.com       # 3. internet by name (tests DNS too)
```

Reading the results:

| Gateway ping | 8.8.8.8 ping | Name ping | Meaning |
|---|---|---|---|
| ✅ | ✅ | ✅ | Path is healthy — problem is the app, not the network |
| ❌ | — | — | Local problem: cable/Wi-Fi, switch port, NIC, or wrong IP config |
| ✅ | ❌ | — | Gateway OK but no internet: ISP/modem/router WAN issue |
| ✅ | ✅ | ❌ | **DNS problem**: can route, can't resolve. Check DNS servers (`ipconfig /all`), try `nslookup` |

> Note: some hosts block ICMP. A failed ping with a *working* TCP connection means the firewall drops ping — not an outage. Always confirm with a port test before declaring something down.

---

## Step 2 — `tracert` / `traceroute`: where does the path die?

```
C:\> tracert 8.8.8.8
  1     1 ms    192.168.56.10      <- your gateway
  2    10 ms    10.0.0.1           <- ISP edge
  3    12 ms    72.14.0.1          <- transit
  4    14 ms    8.8.8.8            <- destination
```

- Hops that answer, then `* * * Request timed out` from some hop onward → the break is **between the last answering hop and the first silent one**.
- Timeouts in the *middle* that recover later → a router deprioritizing ICMP, usually harmless.
- Everything times out after hop 1 → same as "gateway OK, no internet" above.

---

## Step 3 — `nslookup`: interrogate DNS directly

```
C:\> nslookup fileserver01
Server:  dc01.lab.local
Address:  192.168.56.10

Name:    fileserver01.lab.local
Address:  192.168.56.30
```

- **"Non-existent domain"** → the record doesn't exist (typo? machine renamed?).
- **"DNS request timed out"** → the DNS *server* isn't answering. Check: can you ping the DNS IP? Is the DNS service running?
- **Wrong IP returned** → stale record or wrong DNS server (client pointed at ISP DNS instead of internal DNS — classic domain-join killer).

Force a specific server to isolate the problem:
```
nslookup fileserver01 192.168.56.10   # ask THIS server directly
```

---

## Step 4 — `netstat`: what's actually listening / connected?

```
C:\> netstat -ano | findstr LISTENING
  TCP    0.0.0.0:3389     0.0.0.0:0     LISTENING   1234
```

- Port **not** in LISTENING → the service isn't running (or crashed). Start there, not at the firewall.
- `netstat -ano` + Task Manager (PID column) → which process owns the port.
- On the client side, `ESTABLISHED` vs `SYN_SENT`: stuck in `SYN_SENT` = SYN going out, nothing coming back → remote host or firewall dropping it.

---

## Putting it together: three real tickets

**Ticket A — "Internet is down for the whole office"**
`ipconfig` fine → gateway pings ✅ → 8.8.8.8 pings ❌ → `tracert` dies at hop 2 (ISP edge). Verdict: ISP/modem issue, not our LAN. Call the ISP, don't reboot the core switch for an hour.

**Ticket B — "Can't open the file share, but web works"**
Gateway ✅, 8.8.8.8 ✅, `nslookup fileserver01` → "non-existent domain". Verdict: DNS. Client was pointed at 8.8.8.8 instead of the DC. Fix DNS → share opens.

**Ticket C — "RDP to the server times out"**
Ping to server ✅ (host is up) → `Test-NetConnection server01 -Port 3389` ❌ → on the server, `netstat -ano | findstr 3389` shows nothing LISTENING. Verdict: Remote Desktop service not running on the server — not a network problem at all.

---

## Quick-reference card

```
ipconfig /all /release /renew /flushdns   # address & DHCP & DNS cache
ping <gateway> → <8.8.8.8> → <name>       # bottom-up path test
tracert <target>                           # find the dying hop
nslookup <name> [server]                   # DNS interrogation
netstat -ano                               # listening ports & connections
arp -a                                     # IP-to-MAC table (duplicate IP hunts)
```
