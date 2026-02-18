from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0043_logisticbooking_engineer'),
    ]

    operations = [
        migrations.AddField(
            model_name='logisticbooking',
            name='object_variant',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
