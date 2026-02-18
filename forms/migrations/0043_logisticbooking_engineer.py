from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0042_logisticbooking'),
    ]

    operations = [
        migrations.AddField(
            model_name='logisticbooking',
            name='engineer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logistic_bookings', to='auth.user'),
        ),
    ]
