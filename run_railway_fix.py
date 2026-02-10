#!/usr/bin/env python3
"""
🚂 RAILWAY FIX - One-Click Solution
Run this from your computer (no Railway shell needed!)
Works with Railway CLI
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and show output"""
    print(f"\n{'='*70}")
    print(f"🔄 {description}...")
    print(f"{'='*70}")
    print(f"Running: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ ERROR: Command failed!")
        return False
    return True


def main():
    print("\n" + "="*70)
    print("🚂 RAILWAY DATABASE FIX - ONE CLICK SOLUTION")
    print("="*70)
    
    # Step 1: Check Railway CLI
    print("\n📋 STEP 1: Checking Railway CLI...")
    result = subprocess.run("cmd /c railway --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Railway CLI not installed!")
        print("\nInstall from: https://docs.railway.app/guides/cli")
        return
    print(f"✅ Railway CLI found: {result.stdout.strip()}")
    
    # Step 2: Check if logged in
    print("\n🔑 STEP 2: Checking Railway login...")
    result = subprocess.run("cmd /c railway whoami", shell=True, capture_output=True, text=True)
    if result.returncode != 0 or "not authenticated" in result.stdout.lower():
        print("❌ Not logged into Railway!")
        print("\nLogin with:")
        print("   cmd /c railway login")
        print("\nThen come back and run this script again")
        return
    print(f"✅ Logged in as: {result.stdout.strip()}")
    
    # Step 3: Connect to project
    print("\n🔗 STEP 3: Connecting to Railway project...")
    print("   (Railway will auto-detect from .env or ask you to select)")
    
    # Step 4: Run the fix command
    print("\n🗑️  STEP 4: Deleting old stock and reloading correct data...")
    print("   This will:")
    print("   ✓ Delete 1,069 wrong items")
    print("   ✓ Load 1,976 correct items from Excel")
    print("   ✓ Verify 259,406 PCS total")
    
    # The magic command
    fix_command = 'cmd /c railway run python fix_railway_now.py'
    
    result = subprocess.run(fix_command, shell=True)
    
    if result.returncode == 0:
        print("\n" + "="*70)
        print("✅ SUCCESS - DATABASE FIX COMPLETE!")
        print("="*70)
        print("\n📝 WHAT TO DO NOW:")
        print("   1. Go to: https://railway.app/")
        print("   2. Find your app in the dashboard")
        print("   3. Click RESTART button")
        print("   4. Wait 30 seconds")
        print("   5. Visit: https://deycindia.in/stock/received/")
        print("   6. Should show: 259,406 PCS (not 7.5 million!)")
        print("\n✨ Done!")
    else:
        print("\n" + "="*70)
        print("❌ FIX FAILED - See errors above")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
