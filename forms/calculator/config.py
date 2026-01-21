from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class Settings:
    gst_percent: float = 0.18
    gst_mode: str = "12pct"
    default_risk_type: str = "carrier"  # 'carrier' or 'owner'
    free_demurrage_days: int = 3
    fuel_surcharge_global_cargo: float = 0.10  # 10% on (Base + ODA + surcharges)
    fuel_surcharge_anjani: float = 0.15       # on total bill; verify with PDF
    docket_charge_global_cargo: float = 0.0  # NOT USED - Rs.450 minimum LR applied to final total instead
    enable_debug: bool = True
    # Safexpress example state surcharge percentages (apply on base freight)
    safexpress_state_surcharge: Dict[str, float] = field(default_factory=lambda: {
        "Kerala": 4.0,
        "Jammu & Kashmir": 4.0,
        "Assam": 4.0,
        "Arunachal Pradesh": 12.0,
        "Nagaland": 12.0,
        "Manipur": 12.0,
        "Mizoram": 12.0,
        "Meghalaya": 12.0,
        "Tripura": 12.0,
        "Sikkim": 12.0,
    })


DEFAULT_SETTINGS = Settings()
