# Generated by Django 4.2 on 2023-10-27 21:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escrow_app', '0005_remove_userprofile_first_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('Transaction_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('transaction_duration', models.CharField(choices=[('1-3 Days', '1-3 Days'), ('3-5 Days', '3-5 Days'), ('7-14 Days', '7-14 Days')], max_length=200)),
                ('buyer_id', models.CharField(max_length=100)),
                ('seller_id', models.CharField(max_length=100)),
                ('product_list', models.TextField()),
                ('product_total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('transaction_total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('buyer_approval', models.BooleanField(blank=True, default=False, null=True)),
                ('seller_approval', models.BooleanField(blank=True, default=False, null=True)),
                ('Transaction_status', models.CharField(choices=[('Open', 'Open'), ('Pending', 'Pending'), ('Completed', 'Completed')], default='Open', max_length=200)),
                ('rejection_note', models.CharField(blank=True, max_length=250, null=True)),
                ('Actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_actor', to=settings.AUTH_USER_MODEL)),
                ('Initiator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_initiator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('Order_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ref', models.CharField(blank=True, max_length=200, null=True)),
                ('amount', models.PositiveIntegerField(blank=True, null=True)),
                ('order_status', models.CharField(choices=[('Payment Received', 'Payment Received'), ('Payment Completed', 'Payment Completed'), ('Order Canceled', 'Order Canceled')], max_length=200)),
                ('Transaction_details', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='escrow_app.transaction')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
