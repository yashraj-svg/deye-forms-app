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
    """Bigship courier calculator - CFT, LTL, MPS service types"""
    
    name = "Bigship"
    
    # Service types
    SERVICE_TYPES = {
        "CFT": "CFT - Courier Freight Transport (Light Weight)",
        "LTL": "LTL - Less Than Truckload (Heavy Shipments)",
        "MPS": "MPS - Metro Parcel Service (Non-ODA Only)"
    }
    
    # ============ ZONE MAPPING FOR CFT (9 ZONES) ============
    # Map states to Bigship CFT zones
    STATE_TO_ZONE = {
        # North One (N1)
        "Delhi": "N1", "DL": "N1",
        "Uttar Pradesh": "N1", "UP": "N1",
        "Haryana": "N1",
        "Rajasthan": "N1",
        # North Two (N2)
        "Chandigarh": "N2",
        "Punjab": "N2",
        "Himachal Pradesh": "N2", "HP": "N2",
        "Uttarakhand": "N2",
        "Jammu & Kashmir": "N2", "J&K": "N2",
        "Ladakh": "N2",
        # East (E)
        "West Bengal": "E", "WB": "E",
        "Odisha": "E",
        "Bihar": "E",
        "Jharkhand": "E",
        # North East (NE)
        "Assam": "NE",
        "Meghalaya": "NE",
        "Tripura": "NE",
        "Manipur": "NE",
        "Mizoram": "NE",
        "Nagaland": "NE",
        "Arunachal Pradesh": "NE",
        "Sikkim": "NE",
        # West One (W1)
        "Gujarat": "W1",
        "Dadra and Nagar Haveli": "W1",
        # West Two (W2)
        "Maharashtra": "W2",
        # South One (S1)
        "Karnataka": "S1",
        "Telangana": "S1",
        # South Two (S2)
        "Andhra Pradesh": "S2",
        "Tamil Nadu": "S2",
        # Central
        "Madhya Pradesh": "Central",
        "Chhattisgarh": "Central",
        "Goa": "Central",
        "Kerala": "Central",
    }
    
    # ============ ZONE MAPPING FOR LTL (16 ZONES) ============
    # Map states to Bigship LTL zones (more granular than CFT)
    STATE_TO_LTL_ZONE = {
        # N1: Delhi, Chandigarh, parts of Haryana, UP, Rajasthan
        "Delhi": "N1", "DL": "N1", "Chandigarh": "N1",
        "Haryana": "N3",  # Haryana can be N1 or N3, using N3 as default
        
        # N2: Himachal Pradesh, Uttarakhand, Punjab
        "Himachal Pradesh": "N2", "HP": "N2",
        "Uttarakhand": "N2",
        "Punjab": "N2",
        
        # N3: Haryana, Rajasthan, Uttar Pradesh (broader coverage)
        "Rajasthan": "N3",
        "Uttar Pradesh": "N3", "UP": "N3",
        
        # N4: J&K, Himachal, Uttarakhand (northern states)
        "Jammu & Kashmir": "N4", "J&K": "N4",
        
        # C1: Central (Madhya Pradesh focus)
        "Madhya Pradesh": "C1",
        
        # C2: Chhattisgarh, Madhya Pradesh
        "Chhattisgarh": "C2",
        
        # W1: Maharashtra (major cities), Gujarat
        "Maharashtra": "W1",
        
        # W2: Gujarat, Goa, other western states
        "Gujarat": "W2",
        "Goa": "W2",
        "Dadra and Nagar Haveli": "W2",
        "Daman and Diu": "W2",
        
        # S1: Karnataka, parts of South
        "Karnataka": "S1",
        
        # S2: Andhra Pradesh, Karnataka, Telangana
        "Andhra Pradesh": "S2",
        "Telangana": "S2",
        
        # S3: Tamil Nadu
        "Tamil Nadu": "S3",
        
        # S4: Kerala
        "Kerala": "S4",
        
        # E1: West Bengal, parts of Bihar
        "West Bengal": "E1", "WB": "E1",
        
        # E2: Bihar, Odisha, Jharkhand, West Bengal
        "Bihar": "E2",
        "Odisha": "E2",
        "Jharkhand": "E2",
        
        # NE1: Assam
        "Assam": "NE1",
        
        # NE2: Other Northeast states
        "Arunachal Pradesh": "NE2",
        "Manipur": "NE2",
        "Meghalaya": "NE2",
        "Mizoram": "NE2",
        "Nagaland": "NE2",
        "Sikkim": "NE2",
        "Tripura": "NE2",
    }
    
    # ============ ZONE MAPPING FOR MPS (10 ZONES) ============
    # Map states to Bigship MPS zones (simplest zone structure)
    STATE_TO_MPS_ZONE = {
        # N1: Delhi NCR region
        "Delhi": "N1", "DL": "N1",
        "Haryana": "N1",
        "Chandigarh": "N1",
        
        # N2: North region (UP, Rajasthan, Punjab)
        "Uttar Pradesh": "N2", "UP": "N2",
        "Rajasthan": "N2",
        "Punjab": "N2",
        "Dehradun": "N2",
        "Uttarakhand": "N2",
        
        # C: Central India
        "Madhya Pradesh": "C", "MP": "C",
        "Chhattisgarh": "C",
        
        # W1: Mumbai
        "Maharashtra": "W1",
        
        # W2: Gujarat and Western states
        "Gujarat": "W2",
        "Goa": "W2",
        "Daman and Diu": "W2",
        "Dadra and Nagar Haveli": "W2",
        
        # S1: Chennai, Bangalore South
        "Tamil Nadu": "S1", "TN": "S1",
        "Karnataka": "S1",
        
        # S2: Andhra, Telangana, South region
        "Andhra Pradesh": "S2", "AP": "S2",
        "Telangana": "S2",
        "Pondicherry": "S2",
        
        # E1: Kolkata
        "West Bengal": "E1", "WB": "E1",
        
        # E2: Eastern region
        "Bihar": "E2",
        "Jharkhand": "E2",
        "Odisha": "E2",
        
        # SPL: Special zones (Northeast, Himalayan, South Special)
        "Assam": "SPL",
        "Arunachal Pradesh": "SPL",
        "Manipur": "SPL",
        "Meghalaya": "SPL",
        "Mizoram": "SPL",
        "Nagaland": "SPL",
        "Sikkim": "SPL",
        "Tripura": "SPL",
        "Himachal Pradesh": "SPL", "HP": "SPL",
        "Jammu & Kashmir": "SPL", "J&K": "SPL",
        "Ladakh": "SPL",
        "Kerala": "SPL",
    }
    # ============ CFT RATES MATRIX (Rs per kg) ============
    # Zone-to-Zone rate matrix
    CFT_RATES_MATRIX = {
        "N1": {"N1": 9.02, "N2": 9.77, "E": 13.75, "NE": 24.27, "W1": 10.31, "W2": 12.88, "S1": 15.35, "S2": 16.63, "Central": 11.19},
        "N2": {"N1": 9.94, "N2": 9.25, "E": 15.48, "NE": 32.75, "W1": 11.92, "W2": 13.31, "S1": 15.64, "S2": 17.94, "Central": 11.97},
        "E": {"N1": 11.91, "N2": 12.76, "E": 10.71, "NE": 26.09, "W1": 12.18, "W2": 12.17, "S1": 13.05, "S2": 16.43, "Central": 11.32},
        "NE": {"N1": 26.26, "N2": 29.26, "E": 21.53, "NE": 22.76, "W1": 27.26, "W2": 28.43, "S1": 27.26, "S2": 28.59, "Central": 26.26},
        "W1": {"N1": 11.06, "N2": 13.43, "E": 16.00, "NE": 33.75, "W1": 7.95, "W2": 10.46, "S1": 14.44, "S2": 15.87, "Central": 11.43},
        "W2": {"N1": 12.62, "N2": 13.95, "E": 14.83, "NE": 29.60, "W1": 9.38, "W2": 8.81, "S1": 11.86, "S2": 14.05, "Central": 11.19},
        "S1": {"N1": 14.56, "N2": 16.29, "E": 14.42, "NE": 30.85, "W1": 12.01, "W2": 11.25, "S1": 10.71, "S2": 10.84, "Central": 12.92},
        "S2": {"N1": 16.93, "N2": 20.11, "E": 15.52, "NE": 33.42, "W1": 11.91, "W2": 10.58, "S1": 10.48, "S2": 8.57, "Central": 11.86},
        "Central": {"N1": 11.25, "N2": 12.58, "E": 14.52, "NE": 31.80, "W1": 9.91, "W2": 10.73, "S1": 13.25, "S2": 15.82, "Central": 11.25},
    }
    
    # ============ CFT ADDITIONAL CHARGES ============
    CFT_LR_CHARGE = 25.0
    CFT_PICKUP_CHARGE_PER_KG = 1.0  # Rs 1/kg or Rs 75, whichever is higher
    CFT_PICKUP_CHARGE_MIN = 75.0
    CFT_PICKUP_WEIGHT_THRESHOLD = 20.0  # Only charge if weight > 20kg
    CFT_OWNER_RISK = 33.0
    CFT_ODA_CHARGE = 600.0
    CFT_MIN_BASE_FREIGHT = 350.0  # Minimum base freight
    CFT_GREEN_TAX_RATE = 0.01  # 1% when delivering to Delhi
    CFT_VOLUMETRIC_DIVISOR = 2700
    
    # ============ LTL RATES MATRIX (Rs per kg) - 16 ZONES ============
    # Zone-to-Zone rate matrix for LTL (Less Than Truckload)
    LTL_RATES_MATRIX = {
        "N1":  {"N1": 7.60, "N2": 8.50, "N3": 8.96, "N4": 9.21, "C1": 11.23, "C2": 11.36, "W1": 11.87, "W2": 11.33, "S1": 17.46, "S2": 17.46, "S3": 18.27, "S4": 24.32, "E1": 15.49, "E2": 15.66, "NE1": 19.99, "NE2": 24.61},
        "N2":  {"N1": 8.61, "N2": 9.78, "N3": 9.10, "N4": 11.05, "C1": 12.52, "C2": 14.39, "W1": 16.61, "W2": 17.18, "S1": 18.94, "S2": 18.57, "S3": 19.66, "S4": 24.32, "E1": 15.98, "E2": 16.82, "NE1": 20.01, "NE2": 25.54},
        "N3":  {"N1": 8.20, "N2": 8.71, "N3": 8.26, "N4": 10.25, "C1": 12.91, "C2": 12.64, "W1": 12.46, "W2": 13.35, "S1": 17.59, "S2": 15.57, "S3": 16.25, "S4": 24.32, "E1": 14.72, "E2": 14.90, "NE1": 22.11, "NE2": 25.02},
        "N4":  {"N1": 11.30, "N2": 11.19, "N3": 11.19, "N4": 8.93, "C1": 15.73, "C2": 16.69, "W1": 13.30, "W2": 13.87, "S1": 17.62, "S2": 16.78, "S3": 17.32, "S4": 24.69, "E1": 16.11, "E2": 15.72, "NE1": 21.67, "NE2": 23.93},
        "C1":  {"N1": 12.14, "N2": 12.07, "N3": 12.69, "N4": 13.30, "C1": 11.14, "C2": 12.33, "W1": 10.17, "W2": 10.84, "S1": 14.90, "S2": 14.47, "S3": 17.30, "S4": 19.15, "E1": 14.72, "E2": 14.65, "NE1": 22.55, "NE2": 26.80},
        "C2":  {"N1": 12.91, "N2": 12.64, "N3": 12.77, "N4": 13.04, "C1": 12.53, "C2": 8.43, "W1": 10.70, "W2": 12.31, "S1": 16.86, "S2": 16.34, "S3": 16.33, "S4": 19.22, "E1": 15.05, "E2": 15.09, "NE1": 23.03, "NE2": 26.53},
        "W1":  {"N1": 12.22, "N2": 12.65, "N3": 13.15, "N4": 14.44, "C1": 10.44, "C2": 11.74, "W1": 7.60, "W2": 8.57, "S1": 12.84, "S2": 12.88, "S3": 13.56, "S4": 18.94, "E1": 17.45, "E2": 17.67, "NE1": 20.07, "NE2": 23.22},
        "W2":  {"N1": 12.68, "N2": 12.89, "N3": 13.81, "N4": 17.27, "C1": 11.21, "C2": 15.99, "W1": 9.37, "W2": 10.52, "S1": 17.59, "S2": 17.93, "S3": 18.27, "S4": 18.93, "E1": 18.99, "E2": 17.84, "NE1": 27.21, "NE2": 26.22},
        "S1":  {"N1": 12.48, "N2": 17.10, "N3": 16.92, "N4": 15.44, "C1": 13.08, "C2": 13.56, "W1": 10.54, "W2": 11.54, "S1": 9.52, "S2": 11.04, "S3": 11.18, "S4": 13.49, "E1": 16.25, "E2": 16.25, "NE1": 23.16, "NE2": 23.22},
        "S2":  {"N1": 12.55, "N2": 18.00, "N3": 16.92, "N4": 16.25, "C1": 13.02, "C2": 13.15, "W1": 11.00, "W2": 13.22, "S1": 10.79, "S2": 10.19, "S3": 13.36, "S4": 14.16, "E1": 16.25, "E2": 17.73, "NE1": 23.10, "NE2": 24.47},
        "S3":  {"N1": 13.56, "N2": 17.35, "N3": 17.30, "N4": 17.32, "C1": 13.68, "C2": 13.56, "W1": 11.57, "W2": 12.93, "S1": 11.59, "S2": 10.84, "S3": 9.52, "S4": 13.27, "E1": 22.01, "E2": 21.63, "NE1": 24.25, "NE2": 26.09},
        "S4":  {"N1": 13.56, "N2": 17.21, "N3": 18.00, "N4": 16.65, "C1": 13.28, "C2": 13.18, "W1": 11.56, "W2": 12.48, "S1": 12.81, "S2": 12.20, "S3": 12.58, "S4": 12.47, "E1": 21.36, "E2": 21.16, "NE1": 24.10, "NE2": 24.70},
        "E1":  {"N1": 12.14, "N2": 13.07, "N3": 13.45, "N4": 13.56, "C1": 12.14, "C2": 12.60, "W1": 13.35, "W2": 13.47, "S1": 12.14, "S2": 13.02, "S3": 13.45, "S4": 14.23, "E1": 9.26, "E2": 11.45, "NE1": 14.15, "NE2": 16.81},
        "E2":  {"N1": 13.44, "N2": 13.45, "N3": 13.56, "N4": 14.24, "C1": 12.67, "C2": 13.56, "W1": 13.61, "W2": 13.29, "S1": 14.90, "S2": 13.56, "S3": 16.25, "S4": 17.98, "E1": 11.86, "E2": 9.88, "NE1": 15.97, "NE2": 18.41},
        "NE1": {"N1": 18.51, "N2": 19.26, "N3": 20.09, "N4": 21.39, "C1": 17.67, "C2": 17.67, "W1": 18.33, "W2": 20.09, "S1": 20.09, "S2": 20.09, "S3": 20.09, "S4": 21.33, "E1": 13.40, "E2": 15.44, "NE1": 10.89, "NE2": 12.56},
        "NE2": {"N1": 22.31, "N2": 22.14, "N3": 23.56, "N4": 25.37, "C1": 18.88, "C2": 18.88, "W1": 21.85, "W2": 23.07, "S1": 21.39, "S2": 22.14, "S3": 23.56, "S4": 25.37, "E1": 15.44, "E2": 17.29, "NE1": 11.82, "NE2": 13.78},
    }
    
    # ============ LTL ADDITIONAL CHARGES ============
    LTL_LR_CHARGE = 80.0
    LTL_PICKUP_CHARGE_PER_KG = 1.0  # Rs 1/kg or Rs 75, whichever is higher
    LTL_PICKUP_CHARGE_MIN = 75.0
    LTL_PICKUP_WEIGHT_THRESHOLD = 20.0  # Only charge if weight > 20kg
    LTL_OWNER_RISK = 33.0
    LTL_ODA_CHARGE = 600.0
    LTL_MIN_BASE_FREIGHT = 350.0  # Minimum base freight
    LTL_GREEN_TAX_RATE = 0.01  # 1% when delivering to Delhi
    LTL_MIN_WEIGHT = 25.0
    LTL_VOLUMETRIC_DIVISOR = 4500
    
    # ============ MPS RATES MATRIX (Rs - weight slab based) - 10 ZONES ============
    # Zone-to-Zone rate matrix for MPS with 10kg base + per kg charges
    # Structure: "Zone": {"to_Zone": {"10kg": base_rate, "add_1kg": per_kg_rate}}
    MPS_RATES_MATRIX = {
        "N1": {
            "N1": {"10kg": 153, "add_1kg": 14},
            "N2": {"10kg": 222, "add_1kg": 20},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 263, "add_1kg": 23},
            "W2": {"10kg": 296, "add_1kg": 24},
            "S1": {"10kg": 263, "add_1kg": 23},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 263, "add_1kg": 23},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "N2": {
            "N1": {"10kg": 222, "add_1kg": 20},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 296, "add_1kg": 24},
            "W2": {"10kg": 296, "add_1kg": 24},
            "S1": {"10kg": 296, "add_1kg": 24},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 296, "add_1kg": 24},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "C": {
            "N1": {"10kg": 296, "add_1kg": 24},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 222, "add_1kg": 20},
            "W1": {"10kg": 296, "add_1kg": 24},
            "W2": {"10kg": 296, "add_1kg": 24},
            "S1": {"10kg": 296, "add_1kg": 24},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 296, "add_1kg": 24},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "W1": {
            "N1": {"10kg": 263, "add_1kg": 23},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 153, "add_1kg": 14},
            "W2": {"10kg": 222, "add_1kg": 20},
            "S1": {"10kg": 296, "add_1kg": 24},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 263, "add_1kg": 23},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "W2": {
            "N1": {"10kg": 296, "add_1kg": 24},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 222, "add_1kg": 20},
            "W2": {"10kg": 222, "add_1kg": 20},
            "S1": {"10kg": 296, "add_1kg": 24},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 296, "add_1kg": 24},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "S1": {
            "N1": {"10kg": 263, "add_1kg": 23},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 296, "add_1kg": 24},
            "W2": {"10kg": 296, "add_1kg": 24},
            "S1": {"10kg": 180, "add_1kg": 17},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 263, "add_1kg": 23},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "S2": {
            "N1": {"10kg": 296, "add_1kg": 24},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 296, "add_1kg": 24},
            "W2": {"10kg": 296, "add_1kg": 24},
            "S1": {"10kg": 222, "add_1kg": 20},
            "S2": {"10kg": 222, "add_1kg": 20},
            "E1": {"10kg": 296, "add_1kg": 24},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "E1": {
            "N1": {"10kg": 296, "add_1kg": 24},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 296, "add_1kg": 24},
            "W2": {"10kg": 296, "add_1kg": 24},
            "S1": {"10kg": 296, "add_1kg": 24},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 153, "add_1kg": 14},
            "E2": {"10kg": 222, "add_1kg": 20},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "E2": {
            "N1": {"10kg": 296, "add_1kg": 24},
            "N2": {"10kg": 296, "add_1kg": 24},
            "C": {"10kg": 296, "add_1kg": 24},
            "W1": {"10kg": 296, "add_1kg": 24},
            "W2": {"10kg": 296, "add_1kg": 24},
            "S1": {"10kg": 296, "add_1kg": 24},
            "S2": {"10kg": 296, "add_1kg": 24},
            "E1": {"10kg": 296, "add_1kg": 24},
            "E2": {"10kg": 296, "add_1kg": 24},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
        "SPL": {
            "N1": {"10kg": 376, "add_1kg": 32},
            "N2": {"10kg": 376, "add_1kg": 32},
            "C": {"10kg": 376, "add_1kg": 32},
            "W1": {"10kg": 376, "add_1kg": 32},
            "W2": {"10kg": 376, "add_1kg": 32},
            "S1": {"10kg": 376, "add_1kg": 32},
            "S2": {"10kg": 376, "add_1kg": 32},
            "E1": {"10kg": 376, "add_1kg": 32},
            "E2": {"10kg": 376, "add_1kg": 32},
            "SPL": {"10kg": 376, "add_1kg": 32},
        },
    }
    
    # ============ MPS ADDITIONAL CHARGES ============
    MPS_LR_CHARGE = 25.0  # MPS LR charge is Rs 25 (from actual bills)
    MPS_OWNER_RISK = 0.0  # MPS does NOT charge Owner Risk
    MPS_ODA_CHARGE = 0.0  # MPS does NOT have ODA charges
    MPS_PICKUP_CHARGE = 0.0  # MPS does NOT charge Pickup
    MPS_MIN_BASE_FREIGHT = 0.0  # MPS has NO minimum base freight
    MPS_GREEN_TAX_RATE = 0.01  # 1% when delivering to Delhi
    MPS_VOLUMETRIC_DIVISOR = 5000
    
    # Placeholder rates for CFT (old slab-based) - will be deprecated
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
        """Get zones for from and to pincodes"""
        from_zone = self.get_zone_from_state(from_pin.state)
        to_zone = self.get_zone_from_state(to_pin.state)
        return {
            "from": from_zone,
            "to": to_zone
        }
    
    def get_zone_from_state(self, state: str, service_type: str = "CFT") -> str:
        """Get zone from state name based on service type"""
        if not state:
            if service_type == "LTL":
                return "N1"
            elif service_type == "MPS":
                return "N1"
            else:
                return "Central"
        
        if service_type == "LTL":
            zone_map = self.STATE_TO_LTL_ZONE
            default = "N1"
        elif service_type == "MPS":
            zone_map = self.STATE_TO_MPS_ZONE
            default = "N1"
        else:  # CFT
            zone_map = self.STATE_TO_ZONE
            default = "Central"
        
        # Try exact match
        if state in zone_map:
            return zone_map[state]
        
        # Try case-insensitive match
        for state_key, zone in zone_map.items():
            if state_key.lower() == state.lower():
                return zone
        
        # Default based on service type
        return default
    
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
    
    def get_rate_for_weight(self, weight: float, service_type: str, from_zone: str = None, to_zone: str = None) -> tuple:
        """Get rate per kg for weight and service type"""
        if service_type == "CFT" and from_zone and to_zone:
            # CFT uses zone matrix
            try:
                rate = self.CFT_RATES_MATRIX.get(from_zone, {}).get(to_zone, 10.0)
                return rate, 0  # No minimum for CFT (will be calculated with charges)
            except:
                return 10.0, 0
        
        # LTL and MPS use weight slabs
        rates = self.get_rate_table(service_type)
        
        for slab_key, slab_info in rates.items():
            min_w, max_w = slab_info["range"]
            if min_w <= weight < max_w:
                return slab_info["rate"], slab_info["min_charge"]
        
        # If weight exceeds all slabs, use highest slab
        last_slab = list(rates.values())[-1]
        return last_slab["rate"], last_slab["min_charge"]
    
    def calculate_base_freight(self, weight: float, service_type: str, from_zone: str = None, to_zone: str = None) -> float:
        """Calculate base freight charge"""
        rate, min_charge = self.get_rate_for_weight(weight, service_type, from_zone, to_zone)
        freight = weight * rate
        return max(freight, min_charge) if min_charge else freight
    
    def calculate_cft_quote(self, inp: QuoteInput, pins: PincodeDB, from_zone: str, to_zone: str) -> QuoteResult:
        """Calculate CFT freight quote with zone-based matrix and additional charges"""
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)
        
        # Calculate actual weight and volumetric weight
        actual_weight = sum(item.weight_kg for item in inp.items)
        volumetric_weight = self.chargeable_weight(inp, volumetric_divisor=self.CFT_VOLUMETRIC_DIVISOR, min_weight=0.0)
        
        # Use whichever is higher: actual or volumetric
        chargeable_weight = max(actual_weight, volumetric_weight)
        
        # Get rate from CFT zone matrix (Rs/kg)
        rate = self.CFT_RATES_MATRIX.get(from_zone, {}).get(to_zone, 10.0)
        base_freight = chargeable_weight * rate
        
        # Apply minimum base freight (Rs 350)
        base_freight = max(base_freight, self.CFT_MIN_BASE_FREIGHT)
        
        # Calculate all additional charges
        surcharges: Dict[str, float] = {}
        
        # LR Charge (always)
        surcharges["lr"] = self.CFT_LR_CHARGE
        
        # Pickup Charge - only if weight > 20kg, max(1 Rs/kg, 75 Rs)
        if chargeable_weight > self.CFT_PICKUP_WEIGHT_THRESHOLD:
            pickup = max(chargeable_weight * self.CFT_PICKUP_CHARGE_PER_KG, self.CFT_PICKUP_CHARGE_MIN)
            surcharges["pickup"] = _round_money(pickup)
        
        # Owner Risk (always Rs 33)
        surcharges["owner_risk"] = self.CFT_OWNER_RISK
        
        # Green Tax - only if delivering TO Delhi (1% of base freight)
        if to_pin.state and to_pin.state.lower() == "delhi":
            green_tax = base_freight * self.CFT_GREEN_TAX_RATE
            surcharges["green_tax"] = _round_money(green_tax)
        
        # ODA Charge (if destination is ODA per database)
        if self.bigship_pins.is_oda(inp.to_pincode):
            surcharges["oda"] = self.CFT_ODA_CHARGE
        
        # Calculate totals (GST already included in matrix rates)
        total = base_freight + sum(surcharges.values())
        
        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=from_zone,
            to_zone=to_zone,
            chargeable_weight_kg=chargeable_weight,
            base_freight=_round_money(base_freight),
            surcharges={k: _round_money(v) for k, v in surcharges.items()},
            total_before_gst=_round_money(total),
            gst_amount=0.0,
            total_after_gst=_round_money(total),
            rate_per_kg=rate,
            actual_weight_kg=actual_weight,
            rate_details={
                "service_type": "CFT",
                "from_zone": from_zone,
                "to_zone": to_zone,
                "is_oda": self.bigship_pins.is_oda(inp.to_pincode),
                "destination_state": to_pin.state,
                "destination_city": to_pin.city,
            }
        )
    
    def calculate_ltl_quote(self, inp: QuoteInput, pins: PincodeDB, from_zone: str, to_zone: str) -> QuoteResult:
        """Calculate LTL freight quote with zone-based matrix and additional charges"""
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)
        
        # Calculate actual weight and volumetric weight
        actual_weight = sum(item.weight_kg for item in inp.items)
        volumetric_weight = self.chargeable_weight(inp, volumetric_divisor=self.LTL_VOLUMETRIC_DIVISOR, min_weight=self.LTL_MIN_WEIGHT)
        
        # Use whichever is higher: actual or volumetric
        chargeable_weight = max(actual_weight, volumetric_weight)
        
        # Get rate from LTL zone matrix (Rs/kg)
        rate = self.LTL_RATES_MATRIX.get(from_zone, {}).get(to_zone, 15.0)
        base_freight = chargeable_weight * rate
        
        # Apply minimum base freight (Rs 350)
        base_freight = max(base_freight, self.LTL_MIN_BASE_FREIGHT)
        
        # Calculate all additional charges
        surcharges: Dict[str, float] = {}
        
        # LR Charge (always)
        surcharges["lr"] = self.LTL_LR_CHARGE
        
        # Pickup Charge - only if weight > 20kg, max(1 Rs/kg, 75 Rs)
        if chargeable_weight > self.LTL_PICKUP_WEIGHT_THRESHOLD:
            pickup = max(chargeable_weight * self.LTL_PICKUP_CHARGE_PER_KG, self.LTL_PICKUP_CHARGE_MIN)
            surcharges["pickup"] = _round_money(pickup)
        
        # Owner Risk (always Rs 33)
        surcharges["owner_risk"] = self.LTL_OWNER_RISK
        
        # Green Tax - only if delivering TO Delhi (1% of base freight)
        if to_pin.state and to_pin.state.lower() == "delhi":
            green_tax = base_freight * self.LTL_GREEN_TAX_RATE
            surcharges["green_tax"] = _round_money(green_tax)
        
        # ODA Charge (if destination is ODA per database)
        if self.bigship_pins.is_oda(inp.to_pincode):
            surcharges["oda"] = self.LTL_ODA_CHARGE
        
        # Calculate totals (GST already included in matrix rates)
        total = base_freight + sum(surcharges.values())
        
        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=from_zone,
            to_zone=to_zone,
            chargeable_weight_kg=chargeable_weight,
            base_freight=_round_money(base_freight),
            surcharges={k: _round_money(v) if isinstance(v, float) else v for k, v in surcharges.items()},
            total_before_gst=_round_money(total),
            gst_amount=0.0,
            total_after_gst=_round_money(total),
            rate_per_kg=rate,
            actual_weight_kg=actual_weight,
            rate_details={
                "service_type": "LTL",
                "from_zone": from_zone,
                "to_zone": to_zone,
                "is_oda": self.bigship_pins.is_oda(inp.to_pincode),
                "destination_state": to_pin.state,
                "destination_city": to_pin.city,
            }
        )
    
    def calculate_mps_quote(self, inp: QuoteInput, pins: PincodeDB, from_zone: str, to_zone: str) -> QuoteResult:
        """Calculate MPS freight quote - Only Base (from matrix based on chargeable weight) + LR"""
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)
        
        # Calculate actual weight and volumetric weight
        actual_weight = sum(item.weight_kg for item in inp.items)
        volumetric_weight = self.chargeable_weight(inp, volumetric_divisor=self.MPS_VOLUMETRIC_DIVISOR, min_weight=0.0)
        
        # Use whichever is higher: actual or volumetric
        chargeable_weight = max(actual_weight, volumetric_weight)
        
        # Get rate from matrix for this zone pair
        # The matrix already contains the final rates for MPS
        zone_rates = self.MPS_RATES_MATRIX.get(from_zone, {}).get(to_zone, {"10kg": 296, "add_1kg": 24})
        
        # Calculate base freight based on weight slab structure (from matrix)
        if chargeable_weight <= 10:
            base_freight = zone_rates["10kg"]
        else:
            base_freight = zone_rates["10kg"] + (chargeable_weight - 10) * zone_rates["add_1kg"]
        
        # MPS: NO minimum base freight, NO surcharges except LR
        
        # Calculate surcharges (MPS has ONLY LR charge)
        surcharges: Dict[str, float] = {}
        
        # LR Charge (only charge for MPS)
        surcharges["lr"] = self.MPS_LR_CHARGE
        
        # Green Tax - only if delivering TO Delhi (1% of base freight)
        if to_pin.state and to_pin.state.lower() == "delhi":
            green_tax = base_freight * self.MPS_GREEN_TAX_RATE
            surcharges["green_tax"] = _round_money(green_tax)
        
        # Note: MPS does NOT have Owner Risk, Pickup Charges, or ODA charges
        
        # Calculate totals (GST already included in matrix rates)
        total = base_freight + sum(surcharges.values())
        
        # Calculate average rate per kg for reference
        avg_rate = base_freight / chargeable_weight if chargeable_weight > 0 else zone_rates["10kg"] / 10
        
        return QuoteResult(
            partner_name=self.name,
            deliverable=True,
            from_zone=from_zone,
            to_zone=to_zone,
            chargeable_weight_kg=chargeable_weight,
            base_freight=_round_money(base_freight),
            surcharges={k: _round_money(v) for k, v in surcharges.items()},
            total_before_gst=_round_money(total),
            gst_amount=0.0,
            total_after_gst=_round_money(total),
            rate_per_kg=avg_rate,
            actual_weight_kg=actual_weight,
            rate_details={
                "service_type": "MPS",
                "from_zone": from_zone,
                "to_zone": to_zone,
                "is_oda": False,  # MPS is Non-ODA only
                "destination_state": to_pin.state,
                "destination_city": to_pin.city,
            }
        )
    
    def calculate_quote(self, inp: QuoteInput, pins: PincodeDB) -> QuoteResult:
        """Calculate freight quote for Bigship"""
        to_pin = pins.get(inp.to_pincode) or PincodeRecord(pincode=inp.to_pincode)
        from_pin = pins.get(inp.from_pincode) or PincodeRecord(pincode=inp.from_pincode)
        
        # Get service type from input (CFT, LTL, or MPS)
        service_type = getattr(inp, 'bigship_service_type', 'LTL')
        
        # All India pincodes are serviceable for Bigship (no serviceability check needed)
        
        # ============ CFT (Cold Freight Temperature) ============
        if service_type == "CFT":
            from_zone = self.get_zone_from_state(from_pin.state, "CFT")
            to_zone = self.get_zone_from_state(to_pin.state, "CFT")
            return self.calculate_cft_quote(inp, pins, from_zone, to_zone)
        
        # ============ LTL (Less Than Truckload) ============
        if service_type == "LTL":
            from_zone = self.get_zone_from_state(from_pin.state, "LTL")
            to_zone = self.get_zone_from_state(to_pin.state, "LTL")
            return self.calculate_ltl_quote(inp, pins, from_zone, to_zone)
        
        # ============ MPS (Metro Parcel Service) - Non-ODA Only ============
        # MPS uses zone-based weight slab pricing (10kg base + per kg addon)
        # MPS does not serve ODA locations and does not charge ODA
        if service_type == "MPS":
            from_zone = self.get_zone_from_state(from_pin.state, "MPS")
            to_zone = self.get_zone_from_state(to_pin.state, "MPS")
            return self.calculate_mps_quote(inp, pins, from_zone, to_zone)
        
        # Default to LTL if service type not recognized
        from_zone = self.get_zone_from_state(from_pin.state, "LTL")
        to_zone = self.get_zone_from_state(to_pin.state, "LTL")
        return self.calculate_ltl_quote(inp, pins, from_zone, to_zone)
