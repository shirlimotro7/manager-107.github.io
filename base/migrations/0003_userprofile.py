# Generated by Django 3.0.4 on 2020-03-13 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0002_auto_20200313_1914'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movil', models.CharField(choices=[('yes', 'yes'), ('no', 'no')], max_length=3)),
                ('category', models.CharField(choices=[('Pilot', 'Pilot'), ('Navigator', 'Navigator')], max_length=9)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
