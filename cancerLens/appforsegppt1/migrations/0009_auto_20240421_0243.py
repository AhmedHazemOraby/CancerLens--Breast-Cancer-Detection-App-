# Generated by Django 2.2.28 on 2024-04-20 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appforsegppt1', '0008_add_hande_table_add_tumormask_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_hande_table',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='add_ihc_table',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='add_tumormask_table',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='add_wsi_table',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='usercredentials',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
