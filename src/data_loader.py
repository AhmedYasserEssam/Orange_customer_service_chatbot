"""Data loading utilities for customer profiles and internet catalog."""

import os
import csv
from typing import List, Dict, Any

from src.config import CUSTOMER_DATA_PATH, INTERNET_DATA_PATH

_customer_data = None
_internet_catalog = None


def load_customer_data() -> List[Dict]:
    """Load customer data from CSV."""
    global _customer_data
    if _customer_data is None:
        try:
            _customer_data = []
            if os.path.exists(CUSTOMER_DATA_PATH):
                with open(CUSTOMER_DATA_PATH, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    _customer_data = list(reader)
            print(f"Loaded {len(_customer_data)} customer records")
        except Exception as e:
            print(f"Error loading customer data: {e}")
            _customer_data = []
    return _customer_data


def load_internet_catalog() -> List[Dict[str, Any]]:
    """Load mobile internet bundles catalog from CSV for programmatic filtering.

    Returns only Mobile internet rows with numeric quotas and a bundle name.
    """
    global _internet_catalog
    if _internet_catalog is not None:
        return _internet_catalog

    _internet_catalog = []
    try:
        if not os.path.exists(INTERNET_DATA_PATH):
            return _internet_catalog

        with open(INTERNET_DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("Internet Bundle") or row.get("internet bundle") or "").strip()
                quota_raw = (row.get("Inclusive Volume(MBS)") or row.get("inclusive volume(mbs)") or "").strip()
                price_raw = (row.get("Price(EGP)") or row.get("price(egp)") or "").strip()
                family = (row.get("Internet Bundle Type") or row.get("internet bundle type") or "").strip()
                dial = (row.get("To subscribe call") or row.get("to subscribe call") or "").strip()
                itype = (row.get("Internet type") or row.get("internet type") or "").strip()

                if not name or not quota_raw or not quota_raw.isdigit():
                    continue
                quota_mb = int(quota_raw)
                if itype and itype.lower() != "mobile internet":
                    continue
                try:
                    price_val = float(price_raw) if price_raw else None
                except ValueError:
                    price_val = None

                _internet_catalog.append({
                    "name": name,
                    "quota_mb": quota_mb,
                    "price_egp": price_val,
                    "family": family,
                    "dial": dial,
                })
    except Exception as e:
        print(f"Error loading internet catalog: {e}")
        _internet_catalog = []
    return _internet_catalog
