# Global Cargo Rates Update (14-02-2026)

## Summary
Successfully updated Global Courier Cargo calculator with new rates from "Global Cargo Rates  Reupdated (14-02-2026).xlsx" file.

## Changes Made

### 1. Rate Matrix Updated (18 Zones)
- **Previous:** 9 zones (basic structure)
- **Updated:** 18 zones with corrected rates

**Zone Codes:**
- **North:** AMB (Ambala), JAI (Jaipur), DEL (Gurgaon)
- **West:** AMD (Ahmedabad), PNQ (Pune), BOM (Mumbai), IDR (Indore)
- **Central:** NAG (Nagpur)
- **South:** BLR (Bangalore), HYD (Hyderabad), MAA (Chennai), CJB (Coimbatore)
- **East:** BBI (Bhubaneswar), LOK (Lucknow), PAT (Patna)
- **NE:** NJP (Siliguri), CCU (Kolkata), GAU (Guwahati)

### 2. Corrected Rate Values
Key corrections made:
- DEL→DEL: 13.0 → **10.0** ✓
- BLR→BLR: 14.0 → **10.0** ✓
- MAA→MAA: 13.0 → **10.0** ✓
- All other rates verified against Excel file

### 3. State-to-Zone Mapping Added
Created `STATE_TO_GLOBAL_CARGO_ZONE` mapping for automatic zone detection:
```python
{
    "chandigarh": "AMB",
    "himachal pradesh": "AMB",
    "jammu & kashmir": "AMB",
    "punjab": "AMB",
    "haryana": "AMB",
    "uttarakhand": "AMB",
    "rajasthan": "JAI",
    "delhi": "DEL",
    "gujaral": "AMD",
    "goa": "PNQ",
    # ... (52 total state mappings)
}
```

### 4. Two-Level Zone Resolution
Updated `resolve_regions()` method now:
1. First checks if `global_cargo_region` is already set in PincodeRecord
2. Falls back to state-based lookup using `STATE_TO_GLOBAL_CARGO_ZONE`
3. Returns empty string only if both fail

## Testing Results

### Rate Verification ✓
```
Test 1: DEL → BOM (Delhi → Mumbai)
  Rate: ₹15.0/kg ✓
  Expected: ₹15.0/kg ✓

Test 2: DEL → BLR (Delhi → Bangalore)
  Rate: ₹14.0/kg ✓
  Expected: ₹14.0/kg ✓

Test 3: BOM → DEL (Mumbai → Delhi)
  Rate: ₹13.0/kg ✓
  Expected: ₹13.0/kg ✓

Test 4: BLR → BLR (Bangalore → Bangalore)
  Rate: ₹10.0/kg ✓
  Expected: ₹10.0/kg ✓
```

### Volumetric Weight Tests ✓
- Divisor: 4000 (equivalent to 7kg per CFT)
- 5kg actual + 100×50×50cm → 62.5kg volumetric ✓
- Chargeable weight correctly uses max(actual, volumetric) ✓

### Surcharge Tests ✓
- Minimum weight: 20kg enforced ✓
- Minimum docket: ₹450 applied ✓
- ODA charge: ₹600 (when applicable) ✓
- Fuel surcharge: 10% on base ✓
- GST: 18% on total ✓

## Files Modified
- `forms/calculator/freight_calculator.py`
  - Updated `ZONE_RATES` matrix with 18×18 grid
  - Added `STATE_TO_GLOBAL_CARGO_ZONE` mapping
  - Updated `resolve_regions()` method
  - Updated `ZONE_MAPPING` for 18 zones

## Testing Files Created (for QA)
- `test_global_cargo_updated.py` - Comprehensive test suite
- `extract_global_cargo_rates.py` - Data extraction script

## Deployment
- **Commit:** 7dbfaf5d
- **Branch:** master
- **Status:** Pushed to GitHub → Railway auto-deployment in progress

## Backward Compatibility
- ✅ Existing Bigship, Safexpress, BluedartSurface, ShreeAnjani logic unchanged
- ✅ Global Cargo API contract remains the same
- ✅ All surcharge logic preserved

## Rate Card Details
### Minimum Chargeable Weight
- **20 kg** (all shipments rounded up to 20kg)

### Volumetric Calculation
- **1 CFT = 7 kg**
- Formula: `(L × B × H cm) / 4000`
- Divisor 4000 already accounts for CFT-to-kg conversion

### Surcharges (VAS)
- **Physical POD:** ₹300/POD (optional service)
- **ODA Charge:** ₹600 (when applicable)
- **Fuel Surcharge:** 10% on base freight + ODA + insurance
- **GST:** 18% on total before GST

### Minimum Docket
- **₹450** minimum base freight

## Excel File Reference
**File:** Global Cargo Rates  Reupdated (14-02-2026).xlsx
**Sheets:**
1. ZONE (18 zones with 4 columns)
2. RATE (19×19 rate matrix in ₹/kg)
3. VAS (Surcharges and additional charges)

## Next Steps (If Needed)
1. Monitor production deployment completion
2. Test quote calculations in production UI
3. Compare sample quotes against Excel baseline
4. Document any zone updates needed
5. Archive old rate card for reference

## Notes
- All 18 zones are now fully integrated
- Intra-zone rates (same origin/destination) are consistently the lowest (₹10)
- Rates properly reflect distance and logistics complexity
- Same logic as Bigship: zone detection → rate lookup → surcharges → GST
