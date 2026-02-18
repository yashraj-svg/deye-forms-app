from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0044_logisticbooking_object_variant'),
    ]

    operations = [
        migrations.AddField(
            model_name='logisticbooking',
            name='pickup_status',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='logisticbooking',
            name='pickup_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='logisticbooking',
            name='delivery_status',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='logisticbooking',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='logisticbooking',
            name='remark',
            field=models.TextField(blank=True),
        ),
    ]
