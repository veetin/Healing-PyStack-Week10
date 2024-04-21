# Generated by Django 5.0.4 on 2024-04-20 22:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('medicos', '0003_datasabertas'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='consulta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('A', 'Agendada'), ('F', 'Finalizada'), ('C', 'Cancelada'), ('I', 'Iniciada')], default='A', max_length=1)),
                ('link', models.URLField(blank=True, null=True)),
                ('data_aberta', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='medicos.datasabertas')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
