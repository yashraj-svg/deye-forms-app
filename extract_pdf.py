#!/usr/bin/env python
"""Extract text from MoU PDF."""
import pdfplumber

pdf_path = 'Deye Inverter Technology Pvt Ltd-Distribution+MoU-3.pdf'

print("="*80)
print("EXTRACTING SAFEXPRESS COMMERCIAL TERMS FROM PDF")
print("="*80)

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    # Extract first 10 pages
    for i, page in enumerate(pdf.pages[:10]):
        text = page.extract_text()
        print(f"\n--- PAGE {i+1} ---\n")
        print(text)
        if i >= 8:  # Get enough pages to find Safexpress section
            break
