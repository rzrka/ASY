# Generated by Django 3.0.8 on 2020-08-30 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20200805_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telework',
            name='delivery_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время сдачи на проверку'),
        ),
    ]
