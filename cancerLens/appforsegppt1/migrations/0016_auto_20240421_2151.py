# Generated by Django 2.2.28 on 2024-04-21 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appforsegppt1', '0015_auto_20240421_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercredentials',
            name='password',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='usercredentials',
            name='username',
            field=models.CharField(max_length=500),
        ),
    ]
