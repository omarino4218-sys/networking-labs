# Subnetting Cheat Sheet

The quick-reference I made while studying for Network+. Memorize the /24–/30 table and the "interesting octet" method and you can subnet any question in under a minute.

## The table (/24 – /30)

| CIDR | Mask | Block size | Usable hosts | Typical use |
|---|---|---|---|---|
| /24 | 255.255.255.0 | 256 | 254 | Default LAN, small office |
| /25 | 255.255.255.128 | 128 | 126 | Splitting one /24 in half |
| /26 | 255.255.255.192 | 64 | 62 | Department VLAN |
| /27 | 255.255.255.224 | 32 | 30 | Small team / lab bench |
| /28 | 255.255.255.240 | 16 | 14 | Point-of-sale cluster, DMZ slice |
| /29 | 255.255.255.248 | 8 | 6 | Router-to-router links (older style) |
| /30 | 255.255.255.252 | 4 | 2 | Point-to-point WAN link |
| /31 | 255.255.255.254 | 2 | 2 | Modern point-to-point (RFC 3021, no broadcast) |
| /32 | 255.255.255.255 | 1 | 1 | Single host route / loopback |

**Memory trick:** block size = 256 − (mask's last octet). Usable hosts = block size − 2 (network + broadcast), except /31 and /32.

## The method: find the "interesting octet"

1. Look at the mask octet that isn't 255 or 0 — that's the interesting octet.
2. Block size = 256 − that octet.
3. Subnets start at multiples of the block size: 0, 64, 128, 192...
4. Network = the multiple at/below your IP. Broadcast = (next multiple − 1). Usable = everything between.

## Worked examples

### Example 1 — Which subnet is `192.168.10.77/27` in?

- Mask `/27` = 255.255.255.**224** → interesting octet is the 4th, block size = 256 − 224 = **32**
- Subnets: .0, .32, .64, .96, ...
- 77 falls between .64 and .96 → **Network: 192.168.10.64/27**
- Broadcast: 192.168.10.95 · Usable: 192.168.10.65 – 192.168.10.94 (30 hosts)

### Example 2 — Carve `10.0.0.0/24` into 4 equal subnets

- Need 4 subnets → borrow 2 bits (`2² = 4`) → new prefix **/26**
- Block size = 64. Subnets:
  - 10.0.0.0/26 (usable .1 – .62, broadcast .63)
  - 10.0.0.64/26 (usable .65 – .126, broadcast .127)
  - 10.0.0.128/26 (usable .129 – .190, broadcast .191)
  - 10.0.0.192/26 (usable .193 – .254, broadcast .255)

### Example 3 — How many /29s fit in a /24, and what's the 5th one?

- /24 → /29 borrows 5 bits → `2⁵` = **32 subnets**, block size 8
- 5th subnet (counting from 0): start at 4 × 8 = 32 → **192.168.x.32/29**
- Broadcast: .39 · Usable: .33 – .38 (6 hosts)

## Common exam traps

- **"How many hosts?"** vs **"how many usable hosts?"** — subtract 2 for network/broadcast (unless /31).
- **First usable is usually the gateway** — `.1` of the subnet in most SOHO/enterprise designs.
- **/31 has no broadcast** and both addresses are usable (RFC 3021).
- **Classful defaults** (/8, /16, /24) only matter for the *starting* mask — the math is the same.
- **VLSM**: always carve the *largest* subnet first, or you'll fragment the space.
