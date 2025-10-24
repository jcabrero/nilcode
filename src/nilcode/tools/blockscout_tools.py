"""
Blockscout-compatible tools for on-chain analysis.

These tools attempt real network calls to fetch balances; if unavailable,
they return a clear offline/failed message. Supports ENS resolution.
"""

from typing import Optional
from langchain.tools import tool
import os
import re
import requests


def _is_ens(name: str) -> bool:
    return "." in name and not name.lower().startswith("0x")


def _resolve_ens(name: str) -> Optional[str]:
    """
    Resolve an ENS name to an address using a public API.
    """
    try:
        url = f"https://api.ensideas.com/ens/resolve/{name}"
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return None
        data = resp.json()
        addr = (data or {}).get("address")
        if isinstance(addr, str) and addr.lower().startswith("0x"):
            return addr
    except Exception:
        return None
    return None


def _fetch_balance_eth(address: str) -> Optional[float]:

    try:
        # Blockscout public mainnet endpoint
        url = (
            "https://blockscout.com/eth/mainnet/api?module=account&action=balance"
            f"&address={address}"
        )
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            j = r.json()
            wei = j.get("result")
            if isinstance(wei, str) and re.fullmatch(r"\d+", wei):
                return int(wei) / 1e18
    except Exception:
        return None
    return None


@tool
def get_address_balance(address_or_ens: str, network: str = "ethereum") -> str:
    """
    Get the ETH balance for an address or ENS name on a given network.

    Args:
        address_or_ens: A hex address or ENS name, e.g., 'vitalik.eth'
        network: Network name, default 'ethereum'

    Returns:
        A human-readable balance string or an analysis note if unknown.
    """
    target_raw = (address_or_ens or "").strip()
    target = target_raw.lower()
    if not target:
        return "❌ Invalid address or ENS name"

    address = None
    resolved = None
    if _is_ens(target):
        resolved = _resolve_ens(target)
        address = resolved
    else:
        address = target_raw

    if not address or not address.lower().startswith("0x"):
        return f"❌ Could not resolve '{address_or_ens}' to an address"

    bal = _fetch_balance_eth(address)
    if bal is None:
        suffix = " (offline/fetch failed)"
        if resolved:
            return f"ℹ️ Balance for {target_raw} ({address}) on {network}: <unknown>{suffix}"
        return f"ℹ️ Balance for {address} on {network}: <unknown>{suffix}"

    # Format with up to 6 decimals, strip trailing zeros
    bal_str = (f"{bal:.6f}").rstrip("0").rstrip(".")
    if resolved:
        return f"✅ Balance for {target_raw} ({address}) on {network}: {bal_str} ETH"
    return f"✅ Balance for {address} on {network}: {bal_str} ETH"


# Exported tool list
blockscout_tools = [
    get_address_balance,
]
