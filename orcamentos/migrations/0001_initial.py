# Generated by Django 4.2.11 on 2024-04-10 21:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('despesas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orcamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data_inicio', models.DateField(db_index=True)),
                ('data_fim', models.DateField(db_index=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='despesas.categoria')),
                ('conta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='despesas.conta')),
            ],
            options={
                'verbose_name_plural': 'Orçamentos',
            },
        ),
    ]
