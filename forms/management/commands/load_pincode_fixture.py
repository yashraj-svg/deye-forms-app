import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from forms.models import PincodeData


class Command(BaseCommand):
    help = "Load PincodeData from JSON fixture if table is empty."

    def handle(self, *args, **options):
        if PincodeData.objects.exists():
            self.stdout.write(self.style.SUCCESS("PincodeData already populated."))
            return

        fixture_path = os.path.join("forms", "fixtures", "pincode_data.json")
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR("Fixture not found: forms/fixtures/pincode_data.json"))
            return

        call_command("loaddata", fixture_path)
        self.stdout.write(self.style.SUCCESS("PincodeData loaded from fixture."))
