"""Outcome metric standardizer and apples-to-apples normalization engine.

Converts diverse reported units (kWh, MMBtu, lbs CO2, Series A $, etc.)
into standardized canonical metrics and computes normalized return-on-grant ratios.
"""

import re
from typing import Dict, Any, Optional, Tuple


class MetricNormalizer:
    """Standardizes reported metrics into canonical units and computes efficiency benchmarks."""

    # Unit conversion factors to canonical units
    # Canonical GHG: Metric Tons CO2e (MT_CO2e)
    # Canonical Electricity: MWh
    # Canonical Thermal: MMBtu
    # Canonical Power: MW
    # Canonical Currency: USD
    # Canonical Labor: Direct FTE Jobs

    @staticmethod
    def normalize_ghg(value: float, raw_unit: str) -> Tuple[float, str]:
        """Convert various GHG/carbon units to Metric Tons CO2e."""
        u = (raw_unit or "").lower().strip()
        if "lb" in u or "pound" in u:
            # 1 metric ton = 2204.62 lbs
            return value / 2204.62, "MT_CO2e_yr"
        elif "kg" in u or "kilogram" in u:
            # 1 metric ton = 1000 kg
            return value / 1000.0, "MT_CO2e_yr"
        elif "short ton" in u or "us ton" in u or "ton" in u and "metric" not in u and "mt" not in u:
            # 1 short ton = 0.907185 metric tons
            return value * 0.907185, "MT_CO2e_yr"
        elif "kt" in u or "thousand mt" in u:
            return value * 1000.0, "MT_CO2e_yr"
        elif "mmt" in u or "million mt" in u:
            return value * 1_000_000.0, "MT_CO2e_yr"
        return value, "MT_CO2e_yr"

    @staticmethod
    def normalize_energy(value: float, raw_unit: str) -> Tuple[float, str]:
        """Convert electricity or energy units to canonical MWh."""
        u = (raw_unit or "").lower().strip()
        if "kwh" in u:
            return value / 1000.0, "MWh_yr"
        elif "gwh" in u:
            return value * 1000.0, "MWh_yr"
        elif "twh" in u:
            return value * 1_000_000.0, "MWh_yr"
        elif "therm" in u:
            # 1 therm = 0.0293001 MWh
            return value * 0.0293001, "MWh_yr"
        elif "mmbtu" in u:
            # 1 MMBtu = 0.293071 MWh
            return value * 0.293071, "MWh_yr"
        elif "btu" in u:
            return value / 3_412_142.0, "MWh_yr"
        return value, "MWh_yr"

    @staticmethod
    def normalize_currency(value: float, raw_unit: str = "USD") -> Tuple[float, str]:
        """Normalize currency values to USD."""
        return float(value), "USD"

    @staticmethod
    def parse_numeric_with_unit(raw_str: str) -> Tuple[Optional[float], Optional[str]]:
        """Extract numeric value and unit suffix from string like '$14.2M' or '3,500 MT/yr'."""
        if not raw_str:
            return None, None
        
        cleaned = raw_str.strip().replace(",", "")
        
        # Check for currency symbols
        is_currency = "$" in cleaned
        cleaned_no_curr = cleaned.replace("$", "").strip()

        # Match multiplier patterns
        m = re.search(r"([\d\.]+)\s*([a-zA-Z/%_\-]+)?", cleaned_no_curr)
        if not m:
            return None, None
        
        val_str = m.group(1)
        suffix = (m.group(2) or "").lower()

        try:
            val = float(val_str)
        except ValueError:
            return None, None

        if "b" in suffix or "billion" in raw_str.lower():
            val *= 1_000_000_000
        elif "m" in suffix or "million" in raw_str.lower():
            val *= 1_000_000
        elif "k" in suffix or "thousand" in raw_str.lower():
            val *= 1_000

        unit = "USD" if is_currency else suffix
        return val, unit

    @staticmethod
    def compute_benchmarks(
        total_awarded: float,
        leveraged_capital: float,
        annual_ghg_mt: float,
        jobs: float,
        patents: int,
        products: int,
        startups: int,
        awards_count: int,
        trl_advancements: list[float] = None
    ) -> Dict[str, float]:
        """Calculate standardized apples-to-apples efficiency metrics per dollar of public funding.
        
        Returns:
            - leverage_ratio: Private $ leveraged per $1 grant awarded
            - ghg_abatement_per_10k_usd: Metric tons CO2e avoided annually per $10,000 awarded
            - jobs_per_million_usd: Direct FTE clean energy jobs per $1,000,000 awarded
            - ip_and_product_velocity: Total IP (patents) + commercial products per $1,000,000 awarded
            - commercialization_rate_pct: Percentage of projects commercialized
            - avg_trl_gain: Mean TRL levels advanced
        """
        awarded_safe = max(total_awarded, 1.0)
        
        leverage_ratio = round(leveraged_capital / awarded_safe, 2)
        ghg_per_10k = round((annual_ghg_mt / awarded_safe) * 10000.0, 3)
        jobs_per_m = round((jobs / awarded_safe) * 1_000_000.0, 2)
        ip_velocity = round(((patents + products) / awarded_safe) * 1_000_000.0, 2)
        
        comm_rate = 0.0
        if awards_count > 0:
            comm_rate = round(min(((products + startups) / awards_count) * 100.0, 100.0), 1)

        avg_trl = 0.0
        if trl_advancements:
            avg_trl = round(sum(trl_advancements) / len(trl_advancements), 1)

        return {
            "leverage_ratio": leverage_ratio,
            "ghg_abatement_per_10k_usd": ghg_per_10k,
            "jobs_per_million_usd": jobs_per_m,
            "ip_and_product_velocity": ip_velocity,
            "commercialization_rate_pct": comm_rate,
            "avg_trl_gain": avg_trl,
        }
