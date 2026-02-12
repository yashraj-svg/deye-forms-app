import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deye_config.settings")

from forms.calculator.freight_calculator import QuoteInput, GlobalCourierCargo
from forms.calculator.data_loader import load_pincode_master
from forms.calculator.config import Settings


def main() -> None:
    calc = GlobalCourierCargo(Settings())
    pins = load_pincode_master("/app")

    samples = [
        (110020, 411045, 110.0, 2141.70),
        (560060, 686691, 11.0, 1362.90),
        (493445, 411045, 290.0, 5269.88),
        (560060, 642001, 70.0, 2050.84),
        (411045, 226021, 132.0, 2398.70),
        (560060, 574214, 7.0, 1362.90),
        (852201, 201305, 50.0, 973.50),
        (560060, 571105, 40.0, 674.96),
        (201305, 190019, 35.0, 590.59),
        (132103, 201305, 68.0, 882.64),
        (560060, 688001, 11.0, 1362.90),
        (560060, 630556, 95.0, 2505.14),
    ]

    ok = 0
    for from_pin, to_pin, weight, expected in samples:
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
        total = round(calc.calculate_quote(inp, pins).total_after_gst, 2)
        status = "OK" if abs(total - expected) < 0.01 else "MISMATCH"
        print(f"{from_pin}->{to_pin} {weight}kg total={total} expected={expected} {status}")
        if status == "OK":
            ok += 1

    print(f"Matched {ok}/{len(samples)}")


if __name__ == "__main__":
    main()
