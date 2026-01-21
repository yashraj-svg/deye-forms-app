from django.test import TestCase
from .calculator import QuoteInput, get_all_partner_quotes
from .calculator.freight_calculator import BaseCarrier, BluedartSurface, Safexpress, DEFAULT_SETTINGS
from .calculator.config import Settings


class FreightCalculatorTests(TestCase):
	def test_basic_quote_pipeline(self):
		inp = QuoteInput(
			from_pincode="110001",
			to_pincode="400001",
			weight_kg=25.0,
			length_cm=50.0,
			breadth_cm=40.0,
			height_cm=30.0,
			reverse_pickup=False,
			insured_value=10000.0,
		)
		results = get_all_partner_quotes(inp)
		self.assertGreaterEqual(len(results), 4)
		# Ensure totals are computed
		for r in results:
			if r.deliverable:
				self.assertGreater(r.total_after_gst, 0.0)

	def test_bluedart_surface_divisor_rounding_and_min_weight(self):
		carrier = BluedartSurface(DEFAULT_SETTINGS)
		inp = QuoteInput(
			from_pincode="110001",
			to_pincode="400001",
			weight_kg=5.0,
			length_cm=50.0,
			breadth_cm=40.0,
			height_cm=30.0,
		)
		cw = carrier.chargeable_weight(inp)
		self.assertAlmostEqual(cw, 22.5, places=1)

	def test_bluedart_surface_min_weight_floor(self):
		carrier = BluedartSurface(DEFAULT_SETTINGS)
		inp = QuoteInput(
			from_pincode="110001",
			to_pincode="400001",
			weight_kg=8.0,
			length_cm=10.0,
			breadth_cm=10.0,
			height_cm=10.0,
		)
		cw = carrier.chargeable_weight(inp)
		self.assertEqual(cw, 10.0)

	def test_safexpress_min_weight_applied(self):
		carrier = Safexpress(DEFAULT_SETTINGS)
		inp = QuoteInput(
			from_pincode="110001",
			to_pincode="400001",
			weight_kg=5.0,
			length_cm=50.0,
			breadth_cm=40.0,
			height_cm=30.0,
		)
		cw = carrier.chargeable_weight(inp)
		self.assertEqual(cw, 20.0)

	def test_dynamic_fuel_surcharge_percent_bluedart(self):
		base = BaseCarrier(DEFAULT_SETTINGS)
		pct = base.get_fuel_surcharge_percent("Bluedart (Surface)")
		self.assertEqual(pct, 0.30)

	def test_gst_mode_5pct_applied(self):
		settings = Settings(gst_mode="5pct")
		base = BaseCarrier(settings)
		self.assertEqual(base.apply_gst(100.0), 5.0)
