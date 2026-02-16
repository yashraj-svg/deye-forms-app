from __future__ import annotations

import csv
import glob
import math
import os
import pathlib
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, Any, List, Optional

from .config import DEFAULT_SETTINGS, Settings
from .data_loader import PincodeDB, PincodeRecord, load_pincode_master



@dataclass
class ShipmentItem:
    weight_kg: float
    length_cm: float
    breadth_cm: float
    height_cm: float

@dataclass
class QuoteInput:
    from_pincode: str
    to_pincode: str
    items: List[ShipmentItem]
    reverse_pickup: bool = False
    insured_value: Optional[float] = None
    days_in_transit_storage: int = 0
    gst_mode: str = "12pct"
    sds: bool = False  # Special Delivery Service (Safexpress specific, per MOU)
    # Bigship service type options (CFT, LTL, MPS)
    bigship_service_type: str = "LTL"  # Default to LTL if not specified
    bigship_cft: bool = False  # CFT - Cool Food Transport
    bigship_ltl: bool = False  # LTL - Less Than Truckload
    bigship_mps: bool = False  # MPS - Mega Parcel Service
    # Optional: for backward compatibility, you can add these fields and ignore them


@dataclass
class QuoteResult:
    partner_name: str
    deliverable: bool
    reason: Optional[str] = None
    from_zone: Optional[str] = None
    to_zone: Optional[str] = None
    chargeable_weight_kg: float = 0.0
    base_freight: float = 0.0
    surcharges: Dict[str, float] = field(default_factory=dict)
    total_before_gst: float = 0.0
    gst_amount: float = 0.0
    total_after_gst: float = 0.0
    # Rate details for display
    rate_per_kg: float = 0.0
    volumetric_weight_kg: float = 0.0
    actual_weight_kg: float = 0.0
    rate_details: Dict[str, Any] = field(default_factory=dict)


# -----------------------------
# Utilities
# -----------------------------


def _volumetric(weight_divisor: float, l: float, b: float, h: float) -> float:
    return (l * b * h) / weight_divisor

def total_chargeable_weight(items: List[ShipmentItem], volumetric_divisor: float, min_weight: float = 0.0) -> float:
    return max(min_weight, sum(max(item.weight_kg, _volumetric(volumetric_divisor, item.length_cm, item.breadth_cm, item.height_cm)) for item in items))


def _round_money(x: float) -> float:
    return round(float(x), 2)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


@lru_cache(maxsize=None)
def _pin_coords(pin: str) -> Optional[tuple[float, float]]:
    try:
        import pgeocode
    except ImportError:
        print("Install: pip install pgeocode")
        return None
    except Exception:
        return None
    try:
        nomi = pgeocode.Nominatim("in")
        rec = nomi.query_postal_code(str(pin))
        lat = getattr(rec, "latitude", None)
        lon = getattr(rec, "longitude", None)
        if lat is None or lon is None:
            return None
        if isinstance(lat, float) and isinstance(lon, float):
            if math.isnan(lat) or math.isnan(lon):
                return None
        return float(lat), float(lon)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _bluedart_hub_pins(base_dir: str) -> List[str]:
    pattern = os.path.join(
        base_dir,
        "Pickup & Drop Partner Charges",
        "Rahul Delhivery",
        "*.csv",
    )
    matches = glob.glob(pattern)
    if not matches:
        return []
    hubs: List[str] = []
    try:
        with open(matches[0], newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pin = str(row.get("Pin") or "").strip()
                if pin and pin not in hubs:
                    hubs.append(pin)
    except Exception:
        return []
    return hubs


def _nearest_hub_distance_km(pin: str, base_dir: str) -> Optional[float]:
    to_coord = _pin_coords(pin)
    if not to_coord:
        return None
    hub_pins = _bluedart_hub_pins(base_dir)
    if not hub_pins:
        return None
    min_d: Optional[float] = None
    for hub in hub_pins:
        if hub == pin:
            return 0.0
        coord = _pin_coords(hub)
        if not coord:
            continue
        d = _haversine_km(to_coord[0], to_coord[1], coord[0], coord[1])
        if min_d is None or d < min_d:
            min_d = d
    return min_d


def _build_edl_bands() -> List[tuple[float, float, float]]:
    start_charge = 550.0
    end_charge = 6960.0
    steps = 9  # 50km slices from 50->500
    increment = (end_charge - start_charge) / steps
    bands: List[tuple[float, float, float]] = []
    low, high = 20.0, 50.0
    for i in range(steps + 1):
        charge = start_charge + increment * i
        bands.append((low, high, _round_money(charge)))
        low, high = high, high + 50.0
    return bands


_EDL_BANDS = _build_edl_bands()


# -----------------------------
# Base Carrier
# -----------------------------

class BaseCarrier:
    name = "Base"

    def __init__(self, settings: Settings, base_dir: Optional[str] = None):
        self.settings = settings
        self.base_dir = base_dir or str(pathlib.Path(__file__).resolve().parents[2])

    def resolve_regions(self, from_pin: PincodeRecord, to_pin: PincodeRecord) -> Dict[str, str]:
        return {}

    def chargeable_weight(self, inp: QuoteInput, volumetric_divisor: float = 4000.0, min_weight: float = 0.0) -> float:
        return total_chargeable_weight(inp.items, volumetric_divisor, min_weight)

    def base_rate_per_kg(self, from_zone: str, to_zone: str, cw: float) -> float:
        return 0.0

    def calc_surcharges(self, base_freight: float, inp: QuoteInput, from_pin: PincodeRecord, to_pin: PincodeRecord, pins: Optional[PincodeDB] = None) -> Dict[str, float]:
        return {}

    def apply_gst(self, subtotal: float, gst_mode: Optional[str] = None) -> float:
        mode = (gst_mode or getattr(self.settings, "gst_mode", "12pct") or "12pct").lower()
        rate = 0.05 if mode == "5pct" else getattr(self.settings, "gst_percent", 0.18)
        return subtotal * rate

    def get_fuel_surcharge_percent(self, partner: str) -> float:
        if partner.startswith("Bluedart"):
            return 0.30
        if partner.startswith("Safexpress"):
            return 0.10
        return getattr(self.settings, "fuel_surcharge_global_cargo", 0.10)

    def calculate_quote(self, inp: QuoteInput, pins: PincodeDB) -> QuoteResult:
        from_pin = pins.get(inp.from_pincode) or PincodeRecord(pincode=inp.from_pincode)
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)

        regions = self.resolve_regions(from_pin, to_pin)
        from_zone = regions.get("from")
        to_zone = regions.get("to")

        cw = self.chargeable_weight(inp)
        rate = self.base_rate_per_kg(from_zone or "", to_zone or "", cw)
        base_freight = _round_money(rate * cw)
        sur = self.calc_surcharges(base_freight, inp, from_pin, to_pin, pins)
        total_before_gst = _round_money(base_freight + sum(sur.values()))
        gst = _round_money(self.apply_gst(total_before_gst, getattr(inp, "gst_mode", None)))
        total_after_gst = _round_money(total_before_gst + gst)
        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=from_zone,
            to_zone=to_zone,
            chargeable_weight_kg=round(cw, 3),
            base_freight=base_freight,
            surcharges=sur,
            total_before_gst=total_before_gst,
            gst_amount=gst,
            total_after_gst=total_after_gst,
        )


# -----------------------------
# Global Courier Cargo / Rahul
# -----------------------------

class GlobalCourierCargo(BaseCarrier):
    name = "Global Courier Cargo"
    
    # State-to-Zone mapping
    STATE_TO_GLOBAL_CARGO_ZONE = {
        "chandigarh": "AMB",
        "himachal pradesh": "AMB",
        "jammu & kashmir": "AMB",
        "jammu and kashmir": "AMB",
        "punjab": "AMB",
        "haryana": "AMB",
        "uttarakhand": "AMB",
        "uttar pradesh": "AMB",  # Some UP areas
        "up": "AMB",
        "rajasthan": "JAI",
        "delhi": "DEL",
        "ncr": "DEL",
        "agra": "DEL",
        "aligarh": "DEL",
        "moradabad": "DEL",
        "dadra & nagar haveli": "AMD",
        "dadra and nagar haveli": "AMD",
        "daman & diu": "AMD",
        "daman and diu": "AMD",
        "gujarat": "AMD",
        "goa": "PNQ",
        "maharashtra": "BOM",  # For Nashik/Mumbai suburbs
        "karnataka": "BLR",
        "andhra pradesh": "HYD",
        "telangana": "HYD",
        "tamil nadu": "MAA",
        "puducherry": "MAA",
        "kerala": "CJB",
        "odisha": "BBI",
        "west bengal": "CCU",
        "jharkhand": "CCU",
        "bihar": "PAT",
        "siligrim": "NJP",
        "sikkim": "NJP",
        # Special case mappings for specific cities/zones
        "pune": "PNQ",
        "mumbai": "BOM",
        "nagpur": "NAG",
        "indore": "IDR",
        "coimbatore": "CJB",
        "lucknow": "LOK",
        "patna": "PAT",
        "hyderabad": "HYD",
        "bangalore": "BLR",
    }
    
    # Zone definitions from updated rate card (18 zones)
    ZONE_MAPPING = {
        "AMB": "Ambala",      # Chandigarh, Himachal Pradesh, J&K, Punjab, UP West, Uttarakhand
        "JAI": "Jaipur",      # Rajasthan
        "DEL": "Gurgaon",     # Delhi, NCR, Haryana, Agra, Aligarh, Moradabad
        "AMD": "Ahmedabad",   # Dadra & Nagar Haveli, Daman & Diu, Gujarat
        "PNQ": "Pune",        # Pune, ROM, Goa
        "BOM": "Mumbai",      # Mumbai, Mumbai Suburbs, Nashik
        "NAG": "Nagpur",      # Vidarbha
        "IDR": "Indore",      # Madhya Pradesh, Chattishgarh
        "BLR": "Bangalore",   # Karnataka
        "HYD": "Hyderabad",   # Andhra Pradesh, Telangana
        "MAA": "Chennai",     # Andaman & Nicobar, Puducherry, Tamil Nadu
        "CJB": "Coimbatore",  # TN (Coimbatore), Kerala
        "BBI": "Bhubaneswar", # Odisha
        "LOK": "Lucknow",     # Uttar Pradesh East
        "PAT": "Patna",       # Bihar
        "NJP": "Siliguri",    # Siliguri, Sikkim
        "CCU": "Kolkata",     # West Bengal, Jharkhand
        "GAU": "Guwahati",    # North East
    }
    
    # Rate matrix: ZONE_RATES[from_zone][to_zone] = rate per kg (UPDATED 14-02-2026)
    ZONE_RATES = {
        "AMB": {"AMB": 12.0, "JAI": 13.0, "DEL": 12.0, "AMD": 14.0, "PNQ": 14.0, "BOM": 14.0, "NAG": 13.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 17.0, "LOK": 14.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
        "JAI": {"AMB": 13.0, "JAI": 10.0, "DEL": 12.0, "AMD": 12.0, "PNQ": 14.0, "BOM": 13.0, "NAG": 13.0, "IDR": 14.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 18.0, "NJP": 36.0, "CCU": 16.0, "GAU": 18.0},
        "DEL": {"AMB": 12.0, "JAI": 12.0, "DEL": 10.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 13.0, "IDR": 14.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 16.0, "LOK": 12.0, "PAT": 16.0, "NJP": 34.0, "CCU": 16.0, "GAU": 17.0},
        "AMD": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 10.0, "PNQ": 13.0, "BOM": 12.0, "NAG": 12.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 13.0, "BBI": 16.0, "LOK": 13.0, "PAT": 18.0, "NJP": 34.0, "CCU": 16.0, "GAU": 16.0},
        "PNQ": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 12.0, "IDR": 13.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 15.0, "BBI": 16.0, "LOK": 14.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
        "BOM": {"AMB": 13.0, "JAI": 14.0, "DEL": 13.0, "AMD": 12.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 10.0, "IDR": 13.0, "BLR": 13.0, "HYD": 13.0, "MAA": 14.0, "CJB": 14.0, "BBI": 16.0, "LOK": 13.0, "PAT": 18.0, "NJP": 35.0, "CCU": 17.0, "GAU": 17.0},
        "NAG": {"AMB": 12.0, "JAI": 12.0, "DEL": 13.0, "AMD": 12.0, "PNQ": 10.0, "BOM": 10.0, "NAG": 10.0, "IDR": 12.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 16.0},
        "IDR": {"AMB": 12.0, "JAI": 13.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 14.0, "BOM": 13.0, "NAG": 12.0, "IDR": 10.0, "BLR": 13.0, "HYD": 13.0, "MAA": 13.0, "CJB": 14.0, "BBI": 15.0, "LOK": 14.0, "PAT": 16.0, "NJP": 35.0, "CCU": 17.0, "GAU": 16.0},
        "BLR": {"AMB": 14.0, "JAI": 14.0, "DEL": 15.0, "AMD": 13.0, "PNQ": 13.0, "BOM": 13.0, "NAG": 13.0, "IDR": 14.0, "BLR": 10.0, "HYD": 13.0, "MAA": 13.0, "CJB": 13.0, "BBI": 14.0, "LOK": 15.0, "PAT": 18.0, "NJP": 32.0, "CCU": 17.0, "GAU": 17.0},
        "HYD": {"AMB": 14.0, "JAI": 14.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 13.0, "BOM": 12.0, "NAG": 12.0, "IDR": 12.0, "BLR": 14.0, "HYD": 10.0, "MAA": 12.0, "CJB": 12.0, "BBI": 16.0, "LOK": 15.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 16.0},
        "MAA": {"AMB": 14.0, "JAI": 14.0, "DEL": 13.0, "AMD": 13.0, "PNQ": 12.0, "BOM": 12.0, "NAG": 12.0, "IDR": 13.0, "BLR": 12.0, "HYD": 13.0, "MAA": 10.0, "CJB": 12.0, "BBI": 14.0, "LOK": 15.0, "PAT": 16.0, "NJP": 32.0, "CCU": 15.0, "GAU": 16.0},
        "CJB": {"AMB": 15.0, "JAI": 15.0, "DEL": 16.0, "AMD": 16.0, "PNQ": 17.0, "BOM": 17.0, "NAG": 16.0, "IDR": 15.0, "BLR": 14.0, "HYD": 14.0, "MAA": 13.0, "CJB": 10.0, "BBI": 16.0, "LOK": 13.0, "PAT": 16.0, "NJP": 32.0, "CCU": 16.0, "GAU": 17.0},
        "BBI": {"AMB": 13.0, "JAI": 13.0, "DEL": 13.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 15.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 10.0, "LOK": 13.0, "PAT": 15.0, "NJP": 35.0, "CCU": 15.0, "GAU": 15.0},
        "LOK": {"AMB": 12.0, "JAI": 13.0, "DEL": 12.0, "AMD": 14.0, "PNQ": 15.0, "BOM": 15.0, "NAG": 14.0, "IDR": 13.0, "BLR": 14.0, "HYD": 14.0, "MAA": 14.0, "CJB": 14.0, "BBI": 13.0, "LOK": 13.0, "PAT": 16.0, "NJP": 36.0, "CCU": 16.0, "GAU": 17.0},
        "PAT": {"AMB": 17.0, "JAI": 17.0, "DEL": 15.0, "AMD": 15.0, "PNQ": 16.0, "BOM": 15.0, "NAG": 14.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 15.0, "LOK": 13.0, "PAT": 15.0, "NJP": 36.0, "CCU": 13.0, "GAU": 14.0},
        "NJP": {"AMB": 35.0, "JAI": 35.0, "DEL": 36.0, "AMD": 36.0, "PNQ": 36.0, "BOM": 36.0, "NAG": 30.0, "IDR": 30.0, "BLR": 35.0, "HYD": 35.0, "MAA": 35.0, "CJB": 35.0, "BBI": 35.0, "LOK": 30.0, "PAT": 35.0, "NJP": 25.0, "CCU": 30.0, "GAU": 30.0},
        "CCU": {"AMB": 18.0, "JAI": 17.0, "DEL": 16.0, "AMD": 17.0, "PNQ": 16.0, "BOM": 16.0, "NAG": 15.0, "IDR": 14.0, "BLR": 15.0, "HYD": 15.0, "MAA": 15.0, "CJB": 15.0, "BBI": 12.0, "LOK": 15.0, "PAT": 14.0, "NJP": 20.0, "CCU": 12.0, "GAU": 13.0},
        "GAU": {"AMB": 15.0, "JAI": 16.0, "DEL": 17.0, "AMD": 17.0, "PNQ": 17.0, "BOM": 16.0, "NAG": 15.0, "IDR": 16.0, "BLR": 17.0, "HYD": 17.0, "MAA": 17.0, "CJB": 17.0, "BBI": 18.0, "LOK": 18.0, "PAT": 17.0, "NJP": 17.0, "CCU": 12.0, "GAU": 16.0},
    }

    def resolve_regions(self, from_pin: PincodeRecord, to_pin: PincodeRecord) -> Dict[str, str]:
        """Resolve origin and destination to Global Cargo zones.
        
        First check if global_cargo_region is already set in PincodeRecord.
        If not, try to map using state or city lookup.
        """
        from_zone = from_pin.global_cargo_region or ""
        to_zone = to_pin.global_cargo_region or ""
        
        # If global_cargo_region not set, try to map by state
        if not from_zone and from_pin.state:
            from_zone = self.STATE_TO_GLOBAL_CARGO_ZONE.get(from_pin.state.lower().strip(), "")
        
        if not to_zone and to_pin.state:
            to_zone = self.STATE_TO_GLOBAL_CARGO_ZONE.get(to_pin.state.lower().strip(), "")
        
        return {
            "from": from_zone,
            "to": to_zone,
        }

    def chargeable_weight(self, inp: QuoteInput) -> float:
        # Volumetric: 1 cubic feet = 7 kg, so L*B*H(cm) / 4000  cubic feet * 7
        return total_chargeable_weight(inp.items, 4000.0, 20.0)

    def base_rate_per_kg(self, from_zone: str, to_zone: str, cw: float) -> float:
        # Get rate from matrix
        if from_zone in self.ZONE_RATES and to_zone in self.ZONE_RATES[from_zone]:
            return self.ZONE_RATES[from_zone][to_zone]
        # Default fallback
        return 13.0

    def calc_surcharges(self, base_freight: float, inp: QuoteInput, from_pin: PincodeRecord, to_pin: PincodeRecord, pins: Optional[PincodeDB] = None) -> Dict[str, float]:
        s: Dict[str, float] = {}
        # ODA flat 600 when ODA is True; 0 when False
        if to_pin.is_oda:
            s["oda"] = 600.0
        # Insurance (FOV charge)
        if inp.insured_value and inp.insured_value > 0:
            rate = 0.002 if self.settings.default_risk_type == "carrier" else 0.001
            s["insurance"] = max(inp.insured_value * rate, 100.0)
        # Fuel surcharge: 10% on (base_freight + oda + insurance)
        subtotal_for_fuel = base_freight + s.get("oda", 0) + s.get("insurance", 0)
        s["fuel_surcharge"] = self.get_fuel_surcharge_percent(self.name) * subtotal_for_fuel
        # Reverse pickup flat example
        if inp.reverse_pickup:
            s["reverse_pickup"] = 150.0
        # Demurrage after 3 days
        if inp.days_in_transit_storage > 3:
            days = inp.days_in_transit_storage - 3
            s["demurrage"] = 2.0 * self.chargeable_weight(inp) * days
        return {k: _round_money(v) for k, v in s.items()}

    def calculate_quote(self, inp: QuoteInput, pins: PincodeDB) -> QuoteResult:
        from_pin = pins.get(inp.from_pincode) or PincodeRecord(pincode=inp.from_pincode)
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)

        regions = self.resolve_regions(from_pin, to_pin)
        from_zone = regions.get("from")
        to_zone = regions.get("to")

        # If Rahul CSV marks destination as not deliverable (ODA blank), short-circuit.
        if to_pin.deliverable is False:
            return QuoteResult(
                partner_name=self.name,
                deliverable=False,
                reason="Not deliverable for destination pincode",
                from_zone=from_zone,
                to_zone=to_zone,
            )

        cw = self.chargeable_weight(inp)
        
        # Standard zone rate calculation for both ODA and SFC
        rate = self.base_rate_per_kg(from_zone or "", to_zone or "", cw)
        minimum_base = 450.0
        base_freight = _round_money(max(rate * cw, minimum_base))
        
        # Surcharges: ODA ₹600 (when ODA=True), Insurance, Fuel 10%, Reverse Pickup ₹150, Demurrage
        sur = self.calc_surcharges(base_freight, inp, from_pin, to_pin)
        
        # GST calculation: 18% on (base + surcharges)
        subtotal_for_gst = _round_money(base_freight + sum(sur.values()))
        gst = _round_money(self.apply_gst(subtotal_for_gst))
        total_before_gst = subtotal_for_gst
        total_after_gst = _round_money(total_before_gst + gst)

        # Calculate volumetric weight for display (sum of all items)
        vol_wt = sum(_volumetric(4000.0, item.length_cm, item.breadth_cm, item.height_cm) for item in inp.items)
        actual_wt = sum(item.weight_kg for item in inp.items)

        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=from_zone,
            to_zone=to_zone,
            chargeable_weight_kg=round(cw, 3),
            base_freight=base_freight,
            surcharges=sur,
            total_before_gst=total_before_gst,
            gst_amount=gst,
            total_after_gst=total_after_gst,
            rate_per_kg=rate,
            volumetric_weight_kg=round(vol_wt, 3),
            actual_weight_kg=actual_wt,
            rate_details={
                "zone_code": to_zone,
                "from_zone": from_zone,
                "to_zone": to_zone,
                "rate_per_kg": rate,
                "volumetric_divisor": 4000,
                "minimum_weight": 20.0,
                "minimum_base_charge": 450.0,
            }
        )


# -----------------------------
# Shree Anjani Courier (simplified)
# -----------------------------

class ShreeAnjaniCourier(BaseCarrier):
    name = "Shree Anjani Courier"

    # Example slab structure; replace with real slabs from PDF
    # key: destination band, value: list of (upto_kg, per_kg_rate)
    DEST_SLABS: Dict[str, List[tuple]] = {
        "Local": [(5, 20.0), (20, 15.0), (float("inf"), 12.0)],
        "Gujarat": [(5, 25.0), (20, 18.0), (float("inf"), 15.0)],
        "Rest of India": [(5, 30.0), (20, 22.0), (float("inf"), 18.0)],
    }

    def resolve_regions(self, from_pin: PincodeRecord, to_pin: PincodeRecord) -> Dict[str, str]:
        # Heuristic: band by state
        band = "Gujarat" if (to_pin.state or "").lower() == "gujarat" else "Rest of India"
        if (from_pin.city or "").lower() == (to_pin.city or "").lower():
            band = "Local"
        return {"from": from_pin.state or "", "to": band}

    def chargeable_weight(self, inp: QuoteInput) -> float:
        return total_chargeable_weight(inp.items, 5000.0)

    def base_rate_per_kg(self, from_zone: str, to_zone: str, cw: float) -> float:
        slabs = self.DEST_SLABS.get(to_zone or "Rest of India", [])
        for upto, rate in slabs:
            if cw <= upto:
                return rate
        return slabs[-1][1] if slabs else 20.0

    def calc_surcharges(self, base_freight: float, inp: QuoteInput, from_pin: PincodeRecord, to_pin: PincodeRecord, pins: Optional[PincodeDB] = None) -> Dict[str, float]:
        s: Dict[str, float] = {}
        # Parcel valuation 2% of invoice
        if inp.insured_value and inp.insured_value > 0:
            s["valuation"] = 0.02 * inp.insured_value
        # Parcel & cover charges example
        s["waybill"] = 30.0
        # Fuel 15% on total bill later — we'll handle by recomputing
        # Here we just return base items; fuel computed in finalize
        return {k: _round_money(v) for k, v in s.items()}

    def calculate_quote(self, inp: QuoteInput, pins: PincodeDB) -> QuoteResult:
        # override to apply fuel on total bill amount
        from_pin = pins.get(inp.from_pincode) or PincodeRecord(pincode=inp.from_pincode)
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)

        regions = self.resolve_regions(from_pin, to_pin)
        cw = self.chargeable_weight(inp)
        rate = self.base_rate_per_kg(regions.get("from", ""), regions.get("to", "Rest of India"), cw)

        result = super().calculate_quote(inp, pins)
        if not result.deliverable:
            return result
        # Remove previously computed GST since we need to add fuel first
        subtotal_wo_gst = result.total_before_gst
        fuel = _round_money(self.settings.fuel_surcharge_anjani * subtotal_wo_gst)
        result.surcharges["fuel_surcharge"] = fuel
        new_subtotal = _round_money(subtotal_wo_gst + fuel)
        gst = _round_money(self.apply_gst(new_subtotal, getattr(inp, "gst_mode", None)))
        result.total_before_gst = new_subtotal
        result.gst_amount = gst
        result.total_after_gst = _round_money(new_subtotal + gst)

        # Add rate details
        vol_wt = sum(_volumetric(5000.0, item.length_cm, item.breadth_cm, item.height_cm) for item in inp.items)
        actual_wt = sum(item.weight_kg for item in inp.items)
        result.rate_per_kg = rate
        result.volumetric_weight_kg = round(vol_wt, 3)
        result.actual_weight_kg = actual_wt
        result.rate_details = {
            "destination_band": regions.get("to", "Rest of India"),
            "volumetric_divisor": 5000,
        }

        return result


# -----------------------------
# Safexpress and Bluedart (placeholders)
# -----------------------------

class Safexpress(BaseCarrier):
    name = "Safexpress"
    ZONE_RATE_A_TO_E: Dict[str, float] = {"A": 6.0, "B": 8.0, "C": 10.0, "D": 12.0, "E": 15.0}

    # Safexpress weight slabs: if weight falls in a slab, round to next 10kg
    # Example: 52kg stays 52kg, 124kg -> 130kg, 1-10kg -> 10kg, 11-20kg -> 20kg, etc.
    WEIGHT_SLABS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 200, 250, 300, 500, 1000]

    ORIGIN_REGION_BY_STATE = {
        # North One: Delhi, Uttar Pradesh, Haryana, Rajasthan
        "delhi": "NORTH_ONE",
        "uttar pradesh": "NORTH_ONE",
        "haryana": "NORTH_ONE",
        "rajasthan": "NORTH_ONE",
        # North Two: Chandigarh, Punjab, Himachal Pradesh, Uttarakhand, Jammu & Kashmir
        "chandigarh": "NORTH_TWO",
        "punjab": "NORTH_TWO",
        "himachal pradesh": "NORTH_TWO",
        "uttarakhand": "NORTH_TWO",
        "jammu and kashmir": "NORTH_TWO",
        "ladakh": "NORTH_TWO",
        # East: West Bengal, Odisha, Bihar, Jharkhand, Chhattisgarh
        "west bengal": "EAST",
        "odisha": "EAST",
        "orissa": "EAST",
        "bihar": "EAST",
        "jharkhand": "EAST",
        "chhattisgarh": "EAST",
        # North East
        "assam": "NORTH_EAST",
        "meghalaya": "NORTH_EAST",
        "tripura": "NORTH_EAST",
        "arunachal pradesh": "NORTH_EAST",
        "mizoram": "NORTH_EAST",
        "manipur": "NORTH_EAST",
        "nagaland": "NORTH_EAST",
        "sikkim": "NORTH_EAST",
        # West One: Gujarat, Daman & Diu, Dadra & Nagar Haveli
        "gujarat": "WEST_ONE",
        "gujaratstate": "WEST_ONE",
        "daman and diu": "WEST_ONE",
        "dadra and nagar haveli": "WEST_ONE",
        # West Two: Maharashtra, Goa
        "maharashtra": "WEST_TWO",
        "goa": "WEST_TWO",
        # South One: Andhra Pradesh, Telangana, Karnataka, Tamil Nadu
        "andhra pradesh": "SOUTH_ONE",
        "telangana": "SOUTH_ONE",
        "karnataka": "SOUTH_ONE",
        "tamil nadu": "SOUTH_ONE",
        # South Two: Kerala, Puducherry
        "kerala": "SOUTH_TWO",
        "puducherry": "SOUTH_TWO",
        "pondicherry": "SOUTH_TWO",
        # Central: Madhya Pradesh
        "madhya pradesh": "CENTRAL",
    }

    # Annexure 2 matrix origin_region -> dest_region -> band A-E
    ZONE_MATRIX: Dict[str, Dict[str, str]] = {
        "NORTH_ONE": {
            "NORTH_ONE": "A",
            "NORTH_TWO": "A",
            "EAST": "D",
            "NORTH_EAST": "E",
            "WEST_ONE": "B",
            "WEST_TWO": "C",
            "SOUTH_ONE": "C",
            "SOUTH_TWO": "D",
            "CENTRAL": "B",
        },
        "NORTH_TWO": {
            "NORTH_ONE": "A",
            "NORTH_TWO": "A",
            "EAST": "D",
            "NORTH_EAST": "E",
            "WEST_ONE": "C",
            "WEST_TWO": "C",
            "SOUTH_ONE": "D",
            "SOUTH_TWO": "D",
            "CENTRAL": "B",
        },
        "EAST": {
            "NORTH_ONE": "C",
            "NORTH_TWO": "D",
            "EAST": "A",
            "NORTH_EAST": "B",
            "WEST_ONE": "C",
            "WEST_TWO": "D",
            "SOUTH_ONE": "C",
            "SOUTH_TWO": "D",
            "CENTRAL": "B",
        },
        "NORTH_EAST": {
            "NORTH_ONE": "C",
            "NORTH_TWO": "D",
            "EAST": "B",
            "NORTH_EAST": "A",
            "WEST_ONE": "D",
            "WEST_TWO": "D",
            "SOUTH_ONE": "D",
            "SOUTH_TWO": "E",
            "CENTRAL": "C",
        },
        "WEST_ONE": {
            "NORTH_ONE": "B",
            "NORTH_TWO": "C",
            "EAST": "D",
            "NORTH_EAST": "E",
            "WEST_ONE": "A",
            "WEST_TWO": "A",
            "SOUTH_ONE": "C",
            "SOUTH_TWO": "D",
            "CENTRAL": "B",
        },
        "WEST_TWO": {
            "NORTH_ONE": "C",
            "NORTH_TWO": "D",
            "EAST": "D",
            "NORTH_EAST": "E",
            "WEST_ONE": "A",
            "WEST_TWO": "A",
            "SOUTH_ONE": "B",
            "SOUTH_TWO": "D",
            "CENTRAL": "B",
        },
        "SOUTH_ONE": {
            "NORTH_ONE": "C",
            "NORTH_TWO": "D",
            "EAST": "D",
            "NORTH_EAST": "E",
            "WEST_ONE": "C",
            "WEST_TWO": "B",
            "SOUTH_ONE": "A",
            "SOUTH_TWO": "A",
            "CENTRAL": "B",
        },
        "SOUTH_TWO": {
            "NORTH_ONE": "D",
            "NORTH_TWO": "D",
            "EAST": "D",
            "NORTH_EAST": "E",
            "WEST_ONE": "C",
            "WEST_TWO": "C",
            "SOUTH_ONE": "A",
            "SOUTH_TWO": "A",
            "CENTRAL": "B",
        },
        "CENTRAL": {
            "NORTH_ONE": "B",
            "NORTH_TWO": "C",
            "EAST": "D",
            "NORTH_EAST": "E",
            "WEST_ONE": "A",
            "WEST_TWO": "B",
            "SOUTH_ONE": "B",
            "SOUTH_TWO": "D",
            "CENTRAL": "A",
        },
    }

    MIN_FREIGHT_BY_ZONE = {"A": 500.0, "B": 500.0, "C": 600.0, "D": 600.0, "E": 700.0}

    UCC_CITIES = {"ahmedabad", "bengaluru", "bangalore", "chennai", "delhi", "new delhi", "hyderabad", "kolkata", "mumbai", "pune", "vasai", "vasaivirar"}

    # State surcharges per MOU: ₹4/kg for Kerala/Assam/J&K, ₹12/kg for NE states
    STATE_SURCHARGE_PER_KG = {
        # Safexpress MoU Annexure 1: State Surcharges
        # ₹4/kg for Kerala, Assam, J&K - lowercase keys for case-insensitive matching
        "kerala": 4.0,
        "assam": 4.0,
        "jammu and kashmir": 4.0,
        "j&k": 4.0,
        # ₹12/kg for NE states (Arunachal Pradesh, Mizoram, Tripura, Manipur, Meghalaya, Nagaland)
        "arunachal pradesh": 12.0,
        "mizoram": 12.0,
        "tripura": 12.0,
        "manipur": 12.0,
        "meghalaya": 12.0,
        "nagaland": 12.0,
    }

    def _region_for_state(self, state: str) -> str:
        key = (state or "").strip().lower()
        return self.ORIGIN_REGION_BY_STATE.get(key, "CENTRAL")

    def resolve_regions(self, from_pin: PincodeRecord, to_pin: PincodeRecord) -> Dict[str, str]:
        from_region = self._region_for_state(from_pin.state or "")
        to_region = self._region_for_state(to_pin.state or "")
        band = self.ZONE_MATRIX.get(from_region, {}).get(to_region, "C")
        return {"from": from_region, "to": band}

    def chargeable_weight(self, inp: QuoteInput) -> float:
        # Safexpress MoU: 1 cubic foot = 6 kg -> divisor 4000 in cm³
        # Minimum chargeable weight: 20 kg per MOU
        # NO WEIGHT SLAB ROUNDING - use actual weight directly
        return total_chargeable_weight(inp.items, 4000.0, 20.0)

    def base_rate_per_kg(self, from_zone: str, to_zone: str, cw: float, reverse_pickup: bool = False) -> float:
        band = to_zone or "C"
        rate = self.ZONE_RATE_A_TO_E.get(band, 10.0)
        # Removed extra 2 Rs for reverse pickup as per new requirement
        return rate

    def _min_freight(self, band: str) -> float:
        return self.MIN_FREIGHT_BY_ZONE.get(band, 600.0)

    def calc_surcharges(self, base_freight: float, inp: QuoteInput, from_pin: PincodeRecord, to_pin: PincodeRecord, pins: Optional[PincodeDB] = None) -> Dict[str, float]:
        s: Dict[str, float] = {"waybill": 150.0}
        
        # Value Surcharge: ₹100 for each ₹50,000 slab or part thereof per MOU
        # If insured_value is provided, calculate based on slabs. Otherwise default to ₹100
        if inp.insured_value and inp.insured_value > 0:
            import math
            value_slabs = math.ceil(inp.insured_value / 50000.0)
            s["value_surcharge"] = 100.0 * value_slabs
        else:
            s["value_surcharge"] = 100.0
        
        # UCC cities surcharge: ₹100 per MOU for Delhi, Mumbai, Pune, etc.
        if (to_pin.city or "").strip().lower() in self.UCC_CITIES:
            s["ucc"] = 100.0
        
        # SafExtension: Rs 1500/waybill OR Rs 3/kg, whichever is higher (per MOU)
        # Treat as ODA charge from whitelist
        safex_is_oda = to_pin.safexpress_is_oda
        if safex_is_oda is None:
            safex_is_oda = True  # not in whitelist => treat as ODA
        if safex_is_oda:
            cw = self.chargeable_weight(inp)
            s["safe_extension"] = max(1500.0, 3.0 * cw)
        
        # SDS Charge (Special Delivery Service): Rs 1500/waybill OR Rs 5/kg, whichever is higher (per MOU)
        # Only charge if SDS flag is set
        if inp.sds:
            cw = self.chargeable_weight(inp)
            s["sds"] = max(1500.0, 5.0 * cw)
        
        # State per-kg surcharge per MOU
        state_key = (to_pin.state or "").strip().lower()
        perkg = self.STATE_SURCHARGE_PER_KG.get(state_key)
        if perkg:
            s["state_surcharge"] = _round_money(perkg * self.chargeable_weight(inp))
        
        # NOTE: Fuel surcharge is calculated in calculate_quote() AFTER OSC is determined
        return {k: _round_money(v) for k, v in s.items()}

    def calculate_quote(self, inp: QuoteInput, pins: PincodeDB) -> QuoteResult:
        from_pin = pins.get(inp.from_pincode) or PincodeRecord(pincode=inp.from_pincode)
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)

        regions = self.resolve_regions(from_pin, to_pin)
        band = regions.get("to") or "C"

        cw = self.chargeable_weight(inp)
        rate = self.base_rate_per_kg(regions.get("from", ""), band, cw, reverse_pickup=inp.reverse_pickup)
        vol_wt = sum(_volumetric(4000.0, item.length_cm, item.breadth_cm, item.height_cm) for item in inp.items)
        actual_wt = sum(item.weight_kg for item in inp.items)
        
        # Safexpress: Calculate base freight WITHOUT minimum first
        base_freight = _round_money(rate * cw)
        
        # Get surcharges (initially without fuel and OSC)
        sur = self.calc_surcharges(base_freight, inp, from_pin, to_pin)
        
        # Apply minimum freight adjustment: minimum applies to (base_freight + waybill) only
        min_lr_charge = 500.0
        base_plus_waybill = base_freight + sur.get("waybill", 0)
        osc_amount = max(0.0, min_lr_charge - base_plus_waybill)
        if osc_amount > 0:
            sur["osc"] = _round_money(osc_amount)
        
        # Now calculate fuel: 10% on (base + waybill + value + ucc + oda + reverse + osc)
        # NOTE: fuel is NOT applied to fuel itself
        subtotal_for_fuel = base_freight + sum({k: v for k, v in sur.items() if k != "fuel_surcharge"}.values())
        sur["fuel_surcharge"] = _round_money(self.get_fuel_surcharge_percent(self.name) * subtotal_for_fuel)
        
        # Final total
        total_before_gst = _round_money(base_freight + sum(sur.values()))
        gst = _round_money(self.apply_gst(total_before_gst))
        total_after_gst = _round_money(total_before_gst + gst)
        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=regions.get("from"),
            to_zone=band,
            chargeable_weight_kg=round(cw, 3),
            base_freight=base_freight,
            surcharges=sur,
            total_before_gst=total_before_gst,
            gst_amount=gst,
            total_after_gst=total_after_gst,
            rate_per_kg=rate,
            volumetric_weight_kg=round(vol_wt, 3),
            actual_weight_kg=actual_wt,
            rate_details={
                "from_region": regions.get("from", ""),
                "to_band": band,
                "volumetric_divisor": 4720,
            },
        )


class BluedartSurface(BaseCarrier):
    name = "Bluedart (Surface)"
    ZONE_RATE_1_TO_5: Dict[str, float] = {"1": 8.0, "2": 11.0, "3": 11.0, "4": 14.0, "5": 24.0}

    REGION_BY_STATE = {
        "himachal pradesh": "NORTH",
        "punjab": "NORTH",
        "haryana": "NORTH",
        "uttarakhand": "NORTH",
        "uttar pradesh": "NORTH",
        "rajasthan": "NORTH",
        "delhi": "NORTH",
        "bihar": "EAST",
        "odisha": "EAST",
        "orissa": "EAST",
        "west bengal": "EAST",
        "jharkhand": "EAST",
        "maharashtra": "WEST",
        "madhya pradesh": "WEST",
        "gujarat": "WEST",
        "chhattisgarh": "WEST",
        "goa": "WEST",
        "daman and diu": "WEST",
        "dadra and nagar haveli": "WEST",
        "karnataka": "SOUTH",
        "tamil nadu": "SOUTH",
        "kerala": "SOUTH",
        "andhra pradesh": "SOUTH",
        "telangana": "SOUTH",
        "pondicherry": "SOUTH",
        "puducherry": "SOUTH",
        "nagaland": "NE",
        "mizoram": "NE",
        "manipur": "NE",
        "meghalaya": "NE",
        "tripura": "NE",
        "arunachal pradesh": "NE",
        "jammu and kashmir": "J&K",
        "ladakh": "J&K",
    }

    ZONE_MATRIX = {
        "NORTH": {"NORTH": "1", "EAST": "3", "WEST": "2", "SOUTH": "3", "NE": "5", "J&K": "2"},
        "EAST": {"NORTH": "3", "EAST": "1", "WEST": "3", "SOUTH": "4", "NE": "2", "J&K": "5"},
        "WEST": {"NORTH": "2", "EAST": "3", "WEST": "1", "SOUTH": "2", "NE": "5", "J&K": "5"},
        "SOUTH": {"NORTH": "3", "EAST": "4", "WEST": "2", "SOUTH": "1", "NE": "5", "J&K": "5"},
        "NE": {"NORTH": "5", "EAST": "2", "WEST": "5", "SOUTH": "2", "NE": "1", "J&K": "2"},
        "J&K": {"NORTH": "2", "EAST": "5", "WEST": "5", "SOUTH": "5", "NE": "5", "J&K": "1"},
    }

    RAS_STATES = {"bihar", "jharkhand", "kerala", "jammu and kashmir", "ladakh"}

    def _region(self, pin: PincodeRecord) -> str:
        if pin.bluedart_region:
            return pin.bluedart_region
        key = (pin.state or "").strip().lower()
        return self.REGION_BY_STATE.get(key, "WEST")

    def resolve_regions(self, from_pin: PincodeRecord, to_pin: PincodeRecord) -> Dict[str, str]:
        from_region = self._region(from_pin)
        to_region = self._region(to_pin)
        zone = self.ZONE_MATRIX.get(from_region, {}).get(to_region, "3")
        return {"from": from_region, "to": zone}

    def chargeable_weight(self, inp: QuoteInput) -> float:
        divisor = 2700.0  # 1 Cu Ft = 10 Kg std
        # For each item, round up volumetric to nearest 0.5kg, then sum
        def item_chargeable(item):
            vol_wt_raw = _volumetric(divisor, item.length_cm, item.breadth_cm, item.height_cm)
            vol_wt = math.ceil(vol_wt_raw * 2.0) / 2.0
            return max(item.weight_kg, vol_wt)
        total = sum(item_chargeable(item) for item in inp.items)
        return max(10.0, total)

    def base_rate_per_kg(self, from_zone: str, to_zone: str, cw: float) -> float:
        return self.ZONE_RATE_1_TO_5.get(to_zone or "3", 11.0)

    def calc_surcharges(self, base_freight: float, inp: QuoteInput, from_pin: PincodeRecord, to_pin: PincodeRecord, pins: Optional[PincodeDB] = None) -> Dict[str, float]:
        s: Dict[str, float] = {"docket": 100.0}
        # Fuel surcharge linked to diesel index
        s["fuel_surcharge"] = self.get_fuel_surcharge_percent(self.name) * base_freight
        # Remote area (RAS) states flat per-kg
        if (to_pin.state or "").strip().lower() in self.RAS_STATES:
            s["ras"] = 4.0 * self.chargeable_weight(inp)
        # Extra Distance (EDL) based on nearest hub distance
        edl_distance = _nearest_hub_distance_km(to_pin.pincode, self.base_dir)
        if edl_distance is not None and edl_distance > 20.0:
            s["edl"] = self._edl_charge(edl_distance)
        # ODA/EDL left for future distance logic; treat deliverable flag
        if to_pin.is_oda:
            s["oda"] = max(600.0, 3.0 * self.chargeable_weight(inp))
        return {k: _round_money(v) for k, v in s.items()}

    def _edl_charge(self, distance_km: float) -> float:
        for low, high, charge in _EDL_BANDS:
            if distance_km <= high:
                return charge
        return math.ceil(distance_km) * 14.0

    def calculate_quote(self, inp: QuoteInput, pins: PincodeDB) -> QuoteResult:
        from_pin = pins.get(inp.from_pincode) or PincodeRecord(pincode=inp.from_pincode)
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)

        regions = self.resolve_regions(from_pin, to_pin)
        zone = regions.get("to") or "3"

        cw = self.chargeable_weight(inp)
        rate = self.base_rate_per_kg(regions.get("from", ""), zone, cw)
        # For display, sum volumetric and actual weights for all items
        vol_wt = sum(_volumetric(5000.0, item.length_cm, item.breadth_cm, item.height_cm) for item in inp.items)
        actual_wt = sum(item.weight_kg for item in inp.items)
        base_freight = _round_money(max(rate * cw, 150.0))
        sur = self.calc_surcharges(base_freight, inp, from_pin, to_pin)
        total_before_gst = _round_money(base_freight + sum(sur.values()))
        gst = _round_money(self.apply_gst(total_before_gst))
        total_after_gst = _round_money(total_before_gst + gst)
        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=regions.get("from"),
            to_zone=zone,
            chargeable_weight_kg=round(cw, 3),
            base_freight=base_freight,
            surcharges=sur,
            total_before_gst=total_before_gst,
            gst_amount=gst,
            total_after_gst=total_after_gst,
            rate_per_kg=rate,
            volumetric_weight_kg=round(vol_wt, 3),
            actual_weight_kg=actual_wt,
            rate_details={
                "zone": zone,
                "volumetric_divisor": 5000,
            },
        )


# -----------------------------
# Orchestration
# -----------------------------

def get_all_partner_quotes(inp: QuoteInput, base_dir: Optional[str] = None, settings: Settings = DEFAULT_SETTINGS) -> List[QuoteResult]:
    """
    Load pincode master, run quotes across partners, return sorted by total cost.
    """
    from .bigship_calculator import Bigship  # Import here to avoid circular dependency
    
    if base_dir is None:
        import pathlib
        base_dir = str(pathlib.Path(__file__).resolve().parents[2])

    pins = load_pincode_master(base_dir)
    carriers: List[BaseCarrier] = [
        Safexpress(settings, base_dir=base_dir),
        BluedartSurface(settings, base_dir=base_dir),
        GlobalCourierCargo(settings, base_dir=base_dir),
        ShreeAnjaniCourier(settings, base_dir=base_dir),
        Bigship(settings, base_dir=base_dir),
    ]
    
    # Get quotes from all carriers
    results = []
    for carrier in carriers:
        try:
            quote = carrier.calculate_quote(inp, pins)
            results.append(quote)
        except Exception as e:
            print(f"Error getting quote from {carrier.name}: {e}")
            # Create a not-deliverable result
            results.append(QuoteResult(
                partner_name=carrier.name,
                deliverable=False,
                reason=str(e)
            ))
    
    # Mark not deliverable totals as infinity for sorting purpose
    def sort_key(r: QuoteResult):
        return (0 if r.deliverable else 1, r.total_after_gst or float("inf"))

    return sorted(results, key=sort_key)


def print_partner_breakdown(results: List[QuoteResult]) -> None:
    print("| Partner | Base | Docket | FS% | RAS/ODA/EDL | GST | Total |")
    print("|---------|------|--------|-----|------------|-----|-------|")
    for r in results:
        if not r.deliverable:
            continue
        fs_val = r.surcharges.get("fuel_surcharge", 0.0)
        fs_pct = (fs_val / r.base_freight * 100) if r.base_freight else 0.0
        ras_oda_edl = sum(v for k, v in r.surcharges.items() if k in {"ras", "oda", "edl"})
        print(
            f"| {r.partner_name} | Rs{r.base_freight:,.0f} | Rs{r.surcharges.get('docket', 0):,.0f} | {fs_pct:.0f}% | Rs{ras_oda_edl:,.0f} | Rs{r.gst_amount:,.0f} | **Rs{r.total_after_gst:,.0f}** |"
        )


if __name__ == "__main__":
    # Quick manual test example with multiple items
    sample = QuoteInput(
        from_pincode="110001",
        to_pincode="400001",
        items=[
            ShipmentItem(weight_kg=25.0, length_cm=50.0, breadth_cm=40.0, height_cm=30.0),
            ShipmentItem(weight_kg=15.0, length_cm=30.0, breadth_cm=25.0, height_cm=20.0),
        ],
        reverse_pickup=False,
        insured_value=50000.0,
        days_in_transit_storage=0,
        gst_mode="12pct",
    )
    quotes = get_all_partner_quotes(sample)
    import json
    print(json.dumps([q.__dict__ for q in quotes], indent=2))
    print_partner_breakdown(quotes)
