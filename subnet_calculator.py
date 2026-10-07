#!/usr/bin/env python3
"""
Subnet calculator — given an IPv4 address and prefix length, prints the
network address, broadcast address, first/last usable hosts, usable host
count, subnet mask, and wildcard mask.

Stdlib only (ipaddress + argparse). Handles /31 and /32 edge cases the way
real routers do (RFC 3021: /31 = point-to-point, no broadcast).

Usage:
    python subnet_calculator.py 192.168.1.77/24
    python subnet_calculator.py 10.0.0.5 --mask 255.255.255.0
    python subnet_calculator.py 172.16.8.200/21 --binary
"""

import argparse
import ipaddress
import sys


def to_binary_str(ip: ipaddress.IPv4Address) -> str:
    """Dotted-binary representation, e.g. 11000000.10101000.00000001.00000000"""
    return ".".join(f"{int(octet):08b}" for octet in str(ip).split("."))


def calculate(cidr: str, show_binary: bool = False) -> dict:
    # strict=False lets you pass a host address (192.168.1.77/24) instead of
    # requiring the network address — much friendlier for quick checks.
    net = ipaddress.ip_network(cidr, strict=False)

    result = {
        "input": cidr,
        "network": str(net.network_address),
        "broadcast": str(net.broadcast_address),
        "mask": str(net.netmask),
        "wildcard": str(net.hostmask),
        "prefix": net.prefixlen,
        "total_addresses": net.num_addresses,
    }

    if net.prefixlen == 32:
        # Single host route — no usable range, no broadcast
        result["first_usable"] = str(net.network_address)
        result["last_usable"] = str(net.network_address)
        result["usable_hosts"] = 1
        result["note"] = "/32 is a single host route (no network/broadcast)."
    elif net.prefixlen == 31:
        # RFC 3021 point-to-point: both addresses usable, no broadcast
        hosts = list(net.hosts())  # ipaddress handles /31 correctly
        result["first_usable"] = str(hosts[0])
        result["last_usable"] = str(hosts[-1])
        result["usable_hosts"] = 2
        result["note"] = "/31 per RFC 3021: point-to-point link, no broadcast address."
    else:
        hosts = list(net.hosts())
        result["first_usable"] = str(hosts[0])
        result["last_usable"] = str(hosts[-1])
        result["usable_hosts"] = len(hosts)

    if show_binary:
        result["network_binary"] = to_binary_str(net.network_address)
        result["mask_binary"] = to_binary_str(net.netmask)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="IPv4 subnet calculator (stdlib only)."
    )
    parser.add_argument(
        "address",
        help="IP with CIDR, e.g. 192.168.1.77/24",
    )
    parser.add_argument(
        "--mask",
        help="Dotted-decimal mask instead of CIDR, e.g. 255.255.255.0",
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Also show network and mask in binary",
    )
    args = parser.parse_args()

    cidr = args.address
    if args.mask:
        # Convert 192.168.1.77 + 255.255.255.0 -> 192.168.1.77/24
        try:
            base = args.address.split("/")[0]
            prefix = ipaddress.IPv4Network(f"0.0.0.0/{args.mask}").prefixlen
            cidr = f"{base}/{prefix}"
        except ValueError as e:
            print(f"Error: bad mask '{args.mask}': {e}", file=sys.stderr)
            return 2

    try:
        r = calculate(cidr, args.binary)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    print(f"Input:           {r['input']}")
    print(f"Network:         {r['network']}/{r['prefix']}")
    print(f"Broadcast:       {r['broadcast']}")
    print(f"First usable:    {r['first_usable']}")
    print(f"Last usable:     {r['last_usable']}")
    print(f"Usable hosts:    {r['usable_hosts']}")
    print(f"Subnet mask:     {r['mask']}")
    print(f"Wildcard mask:   {r['wildcard']}")
    print(f"Total addresses: {r['total_addresses']}")
    if args.binary:
        print(f"Network (bin):   {r['network_binary']}")
        print(f"Mask (bin):      {r['mask_binary']}")
    if "note" in r:
        print(f"Note: {r['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
