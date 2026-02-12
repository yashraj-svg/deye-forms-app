#!/usr/bin/env python3
"""
Bigship Calculator - Support for CFT, LTL, MPS service types
Franchise partner rates - effective 1st Jan 2026

NOTE: This calculator queries the PincodeData model for ODA status.
All India pincodes are serviceable for Bigship. ODA charges apply only for ODA pincodes.
"""

from pathlib import Path
from typing import Dict, Optional, List
from forms.calculator.data_loader import PincodeRecord, PincodeDB
from forms.calculator.freight_calculator import (
    BaseCarrier, QuoteInput, QuoteResult, ShipmentItem, Settings, _round_money
)


class BigshipPincodeDB:
    """
    Query Bigship ODA pincodes from Django database.
    All India pincodes are serviceable for Bigship.
    """
    
    def __init__(self):
        print("[Bigship] Initializing with database-backed pincode lookup...")
        self._db_available = self._check_database()
    
    def _check_database(self) -> bool:
        """Check if Django database is available"""
        try:
            from django.apps import apps
            if not apps.ready:
                print("[Bigship] Django not ready, database unavailable")
                return False
            from forms.models import PincodeData
            # Try a simple query to verify database connection
            count = PincodeData.objects.filter(bigship_is_oda=True).count()
            print(f"[Bigship] Database available, found {count} ODA pincodes")
            return True
        except Exception as e:
            print(f"[Bigship] Database unavailable: {e}")
            return False
    
    def is_serviceable(self, pincode: str) -> bool:
        """
        Check if pincode is serviceable by Bigship.
        ALL India pincodes are serviceable.
        """
        # Bigship services all India pincodes
        return True
    
    def is_oda(self, pincode: str) -> bool:
        """Check if pincode is ODA (Out of Delivery Area) from database"""
        if not self._db_available:
            return False  # Default to non-ODA if database is unavailable
        
        try:
            from forms.models import PincodeData
            record = PincodeData.objects.filter(
                pincode=str(pincode).strip(),
                bigship_is_oda=True
            ).exists()
            return record
        except Exception as e:
            print(f"[Bigship] Error querying ODA status for {pincode}: {e}")
            return False
    
    def get_details(self, pincode: str) -> Optional[dict]:
        """Get pincode details from database"""
        if not self._db_available:
            return None
        
        try:
            from forms.models import PincodeData
            rec = PincodeData.objects.get(pincode=str(pincode).strip())
            return {
                "city": rec.city,
                "state": rec.state,
                "is_oda": rec.bigship_is_oda
            }
        except Exception:
            return None


class Bigship(BaseCarrier):
    """Bigship courier calculator - CFT, LTL, MPS service types)"""
    
    name = "Bigship"
    
    # Service types
    SERVICE_TYPES = {
        "CFT": "CFT - Courier Freight Transport (Light Weight)",
        "LTL": "LTL - Less Than Truckload (Heavy Shipments)",
        "MPS": "MPS - Metro Parcel Service (Non-ODA Only)"
    }
    
    # Franchise Partner Rates - CFT (Cool Food Transport)
    # Weight slabs in kg, Rate per kg
    CFT_RATES = {
        # Weight range: (min, max): rate_per_kg
        "slab_1": {"range": (0, 5), "rate": 80.0, "min_charge": 400},
        "slab_2": {"range": (5, 10), "rate": 70.0, "min_charge": 500},
        "slab_3": {"range": (10, 25), "rate": 60.0, "min_charge": 800},
        "slab_4": {"range": (25, 50), "rate": 50.0, "min_charge": 1500},
        "slab_5": {"range": (50, 100), "rate": 40.0, "min_charge": 2500},
        "slab_6": {"range": (100, 250), "rate": 35.0, "min_charge": 4000},
    }
    
    # Franchise Partner Rates - LTL (Less Than Truckload)
    LTL_RATES = {
        "slab_1": {"range": (0, 5), "rate": 50.0, "min_charge": 250},
        "slab_2": {"range": (5, 10), "rate": 45.0, "min_charge": 350},
        "slab_3": {"range": (10, 25), "rate": 40.0, "min_charge": 600},
        "slab_4": {"range": (25, 50), "rate": 35.0, "min_charge": 1000},
        "slab_5": {"range": (50, 100), "rate": 30.0, "min_charge": 2000},
        "slab_6": {"range": (100, 250), "rate": 25.0, "min_charge": 3000},
    }
    
    # Franchise Partner Rates - MPS (Mega Parcel Service)
    MPS_RATES = {
        "slab_1": {"range": (0, 5), "rate": 60.0, "min_charge": 300},
        "slab_2": {"range": (5, 10), "rate": 55.0, "min_charge": 400},
        "slab_3": {"range": (10, 25), "rate": 50.0, "min_charge": 700},
        "slab_4": {"range": (25, 50), "rate": 45.0, "min_charge": 1200},
        "slab_5": {"range": (50, 100), "rate": 35.0, "min_charge": 2200},
        "slab_6": {"range": (100, 250), "rate": 30.0, "min_charge": 3500},
    }
    
    # Surcharges (as % of base freight)
    FUEL_SURCHARGE_PCT = 0.12  # 12% fuel surcharge
    GST_RATE = 0.18  # 18% GST
    
    # ODA charges - minimum 600 per user requirement
    ODA_CHARGE = 600.0  # Flat ODA charge minimum
    
    def __init__(self, settings: Settings, base_dir: Optional[str] = None):
        super().__init__(settings, base_dir)
        
        print(f"[Bigship] ==================== INITIALIZATION DEBUG ====================")
        print(f"[Bigship] Initializing Bigship calculator with database-backed ODA lookup")
        
        # Initialize database-backed pincode DB (no file required)
        self.bigship_pins = BigshipPincodeDB()
        
        print(f"[Bigship] =============================================================")
    
    def resolve_regions(self, from_pin: PincodeRecord, to_pin: PincodeRecord) -> Dict[str, str]:
        """For Bigship, we don't use zones - just check serviceability"""
        return {
            "from": to_pin.state or "Unknown",
            "to": to_pin.city or "Unknown"
        }
    
    def get_rate_table(self, service_type: str) -> Dict:
        """Get rate table for the selected service type"""
        if service_type == "CFT":
            return self.CFT_RATES
        elif service_type == "LTL":
            return self.LTL_RATES
        elif service_type == "MPS":
            return self.MPS_RATES
        else:
            return self.LTL_RATES  # Default to LTL
    
    def get_rate_for_weight(self, weight: float, service_type: str) -> tuple:
        """Get rate per kg and minimum charge for given weight and service"""
        rates = self.get_rate_table(service_type)
        
        for slab_key, slab_info in rates.items():
            min_w, max_w = slab_info["range"]
            if min_w <= weight < max_w:
                return slab_info["rate"], slab_info["min_charge"]
        
        # If weight exceeds all slabs, use highest slab
        last_slab = list(rates.values())[-1]
        return last_slab["rate"], last_slab["min_charge"]
    
    def calculate_base_freight(self, weight: float, service_type: str) -> float:
        """Calculate base freight charge"""
        rate, min_charge = self.get_rate_for_weight(weight, service_type)
        freight = weight * rate
        return max(freight, min_charge)
    
    def calculate_quote(self, inp: QuoteInput, pins: PincodeDB) -> QuoteResult:
        """Calculate freight quote for Bigship"""
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)
        
        # Get service type from input (CFT, LTL, or MPS)
        service_type = getattr(inp, 'bigship_service_type', 'LTL')
        
        # All India pincodes are serviceable for Bigship (no serviceability check needed)
        
        # Calculate chargeable weight
        cw = self.chargeable_weight(inp, volumetric_divisor=5000.0, min_weight=5.0)
        
        # Calculate base freight
        base_freight = self.calculate_base_freight(cw, service_type)
        
        # Calculate surcharges
        surcharges: Dict[str, float] = {}
        
        # Check for ODA (only for LTL and CFT, NOT for MPS)
        # MPS service does not include ODA locations and does not charge ODA
        # ODA minimum charge: 600 as per user requirement
        if service_type in ['LTL', 'CFT'] and self.bigship_pins.is_oda(inp.to_pincode):
            surcharges["oda"] = self.ODA_CHARGE
        
        # Fuel surcharge
        fuel_charge = base_freight * self.FUEL_SURCHARGE_PCT
        surcharges["fuel_surcharge"] = _round_money(fuel_charge)
        
        # Calculate totals
        total_before_gst = base_freight + sum(surcharges.values())
        gst_amount = total_before_gst * self.GST_RATE
        total_after_gst = total_before_gst + gst_amount
        
        # Get destination details
        regions = self.resolve_regions(to_pin, to_pin)
        
        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=regions.get("from"),
            to_zone=regions.get("to"),
            chargeable_weight_kg=cw,
            base_freight=_round_money(base_freight),
            surcharges={k: _round_money(v) for k, v in surcharges.items()},
            total_before_gst=_round_money(total_before_gst),
            gst_amount=_round_money(gst_amount),
            total_after_gst=_round_money(total_after_gst),
            rate_per_kg=self.get_rate_for_weight(cw, service_type)[0],
            actual_weight_kg=sum(item.weight_kg for item in inp.items),
            rate_details={
                "service_type": service_type,
                "is_oda": self.bigship_pins.is_oda(inp.to_pincode),
                "destination_state": to_pin.state,
                "destination_city": to_pin.city,
            }
        )
