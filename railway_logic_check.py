import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deye_config.settings")

from forms.calculator.freight_calculator import QuoteInput, GlobalCourierCargo
from forms.calculator.data_loader import load_pincode_master
from forms.calculator.config import Settings


def main() -> None:
    calc = GlobalCourierCargo(Settings())
    pins = load_pincode_master("/app")

    samples = [
        (110020, 411045, 110.0),
        (560060, 686691, 11.0),
        (493445, 411045, 290.0),
        (560060, 642001, 70.0),
        (411045, 226021, 132.0),
        (560060, 574214, 7.0),
        (852201, 201305, 50.0),
        (560060, 571105, 40.0),
        (201305, 190019, 35.0),
        (132103, 201305, 68.0),
        (560060, 688001, 11.0),
        (560060, 630556, 95.0),
    ]

    for from_pin, to_pin, weight in samples:
        inp = QuoteInput(
            from_pincode=from_pin,
            to_pincode=to_pin,
            items=[
                type(
                    "Item",
                    (),
                    {
                        "weight_kg": weight,
                        "length_cm": 0,
                        "breadth_cm": 0,
                        "height_cm": 0,
                    },
                )()
            ],
            insured_value=0,
            reverse_pickup=False,
            days_in_transit_storage=0,
        )
        result = calc.calculate_quote(inp, pins)
        from_pin_rec = pins.get(from_pin)
        to_pin_rec = pins.get(to_pin)
        print("-")
        print(f"{from_pin}->{to_pin} {weight}kg")
        print(f"  zones: {result.from_zone} -> {result.to_zone}")
        print(f"  is_oda: {getattr(to_pin_rec, 'is_oda', None)}")
        print(f"  base_rate: {result.rate_per_kg}")
        print(f"  base_freight: {result.base_freight}")
        print(f"  surcharges: {result.surcharges}")
        print(f"  total_before_gst: {result.total_before_gst}")
        print(f"  gst: {result.gst_amount}")
        print(f"  total_after_gst: {result.total_after_gst}")


if __name__ == "__main__":
    main()
