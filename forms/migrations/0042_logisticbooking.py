from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0041_dailytravelsummary'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogisticBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer_name', models.CharField(max_length=255)),
                ('contact_details', models.CharField(max_length=255)),
                ('pickup_pincode', models.CharField(max_length=10)),
                ('pickup_state', models.CharField(blank=True, max_length=100)),
                ('pickup_district', models.CharField(blank=True, max_length=100)),
                ('pickup_city', models.CharField(blank=True, max_length=100)),
                ('pickup_address', models.TextField(blank=True)),
                ('delivery_name', models.CharField(max_length=255)),
                ('delivery_contact', models.CharField(max_length=255)),
                ('delivery_pincode', models.CharField(max_length=10)),
                ('delivery_state', models.CharField(blank=True, max_length=100)),
                ('delivery_district', models.CharField(blank=True, max_length=100)),
                ('delivery_city', models.CharField(blank=True, max_length=100)),
                ('delivery_address', models.TextField(blank=True)),
                ('object_type', models.CharField(choices=[('Inverter', 'Inverter'), ('PCB', 'PCB'), ('Battery', 'Battery')], max_length=20)),
                ('object_capacity', models.CharField(blank=True, max_length=100)),
                ('object_serial_number', models.CharField(blank=True, max_length=100)),
                ('object_quantity', models.PositiveIntegerField(default=1)),
                ('courier_partner', models.CharField(max_length=100)),
                ('shipment_weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('awb_number', models.CharField(blank=True, max_length=100)),
                ('invoice_number', models.CharField(max_length=100)),
                ('batch_id', models.CharField(db_index=True, max_length=36)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
