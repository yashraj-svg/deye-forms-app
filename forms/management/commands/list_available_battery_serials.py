from django.core.management.base import BaseCommand
from forms.models import InwardForm, OutwardForm
from django.db.models import Count

class Command(BaseCommand):
    help = 'List available battery serials (inwarded but not outwarded) and debug battery_id values.'

    def handle(self, *args, **options):
        inward_battery_ids = list(InwardForm.objects.values_list('battery_id', flat=True))
        outward_battery_ids = list(OutwardForm.objects.values_list('battery_id', flat=True))
        self.stdout.write(self.style.WARNING(f'All InwardForm battery_id values: {inward_battery_ids}'))
        self.stdout.write(self.style.WARNING(f'All OutwardForm battery_id values: {outward_battery_ids}'))

        inward_counts = InwardForm.objects.values('battery_id').annotate(count_inward=Count('id'))
        outward_counts = OutwardForm.objects.values('battery_id').annotate(count_outward=Count('id'))
        outward_map = {row['battery_id']: row['count_outward'] for row in outward_counts}
        available_serials = []
        for row in inward_counts:
            serial = row['battery_id']
            if not serial:
                continue
            inward = row['count_inward']
            outward = outward_map.get(serial, 0)
            if inward > outward:
                available_serials.append(serial)
        self.stdout.write(self.style.SUCCESS(f'Available battery serials for outward: {available_serials}'))
