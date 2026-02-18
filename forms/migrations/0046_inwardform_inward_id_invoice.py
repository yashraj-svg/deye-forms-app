from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0045_logisticbooking_status_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='inwardform',
            name='inward_id',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='inwardform',
            name='invoice_number',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
