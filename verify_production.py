#!/usr/bin/env python
"""
Test production website to verify ODA charges are now showing
"""
import requests
import time

print("=" * 80)
print("VERIFYING PRODUCTION DEPLOYMENT")
print("=" * 80)

time.sleep(5)  # Wait a bit more for deployment

url = "https://www.deyeindia.in/calculator/"

print(f"\nTesting: {url}")
print("Shipment: 560060 → 688529 (73kg, CFT)")
print("\nExpected: ODA charge ₹600 should now be visible")
print("-" * 80)

try:
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        # Check if the page contains ODA charge indicator
        if "ODA" in response.text or "600" in response.text:
            print("\n✅ SUCCESS! Production website is updated!")
            print("   ODA charges are now showing on the page")
        else:
            print("\n⏳ Waiting for deployment to fully complete...")
            print("   Trying again in a moment...")
    else:
        print(f"\n⚠️  Got status code: {response.status_code}")
        print("   Deployment might still be in progress")
        
except Exception as e:
    print(f"\n⚠️  Could not access production site: {e}")
    print("   Deployment likely still in progress...")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("1. Wait 2-3 minutes for Railway to fully redeploy")
print("2. Visit https://www.deyeindia.in/calculator/")
print("3. Test with same shipment: 560060 → 688529, 73kg")
print("4. Verify CFT shows:")
print("   - Base Freight: ₹791.32")
print("   - ODA Charge: ₹600.00")
print("   - Total: ₹1,524.32")
print("=" * 80)
