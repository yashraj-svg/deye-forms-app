"""
Test script to verify rate details display in calculator
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

def test_rate_display():
    """Test that rate details are populated correctly"""
    
    # Test case: 411045 (Pune) to 226021 (Lucknow)
    input_data = QuoteInput(
        from_pincode="411045",
        to_pincode="226021",
        weight_kg=10.0,
        length_cm=0,
        breadth_cm=0,
        height_cm=0,
    )
    
    results = get_all_partner_quotes(input_data)
    
    print("=" * 80)
    print("Rate Details Display Test")
    print("=" * 80)
    print(f"\nShipment: {input_data.from_pincode} → {input_data.to_pincode}")
    print(f"Weight: {input_data.weight_kg}kg\n")
    
    for r in results:
        print(f"\n{r.partner_name}")
        print("-" * 60)
        print(f"  From Zone: {r.from_zone}")
        print(f"  To Zone: {r.to_zone}")
        print(f"  Base Freight: ₹{r.base_freight:.2f}")
        print(f"  Total: ₹{r.total_after_gst:.2f}")
        
        # Display rate details
        if r.rate_per_kg > 0:
            print(f"\n  RATE DETAILS:")
            print(f"    Rate per kg: ₹{r.rate_per_kg:.2f}/kg")
            print(f"    Actual Weight: {r.actual_weight_kg:.2f}kg")
            print(f"    Volumetric Weight: {r.volumetric_weight_kg:.2f}kg")
            print(f"    Chargeable Weight: {r.chargeable_weight_kg:.2f}kg")
            
            if r.rate_details:
                print(f"    Additional Info:")
                for key, value in r.rate_details.items():
                    print(f"      - {key}: {value}")
        else:
            print("  ⚠ Rate details not available")
    
    print("\n" + "=" * 80)
    
    # Verify all partners have rate details
    partners_without_details = [r.partner_name for r in results if r.rate_per_kg == 0]
    
    if partners_without_details:
        print(f"❌ Missing rate details for: {', '.join(partners_without_details)}")
        return False
    else:
        print("✓ All partners have rate details populated")
        return True

if __name__ == "__main__":
    success = test_rate_display()
    sys.exit(0 if success else 1)
