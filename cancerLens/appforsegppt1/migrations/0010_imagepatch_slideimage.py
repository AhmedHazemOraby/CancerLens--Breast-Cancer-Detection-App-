# Generated by Django 2.2.28 on 2024-04-21 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appforsegppt1', '0009_auto_20240421_0243'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlideImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='A descriptive title for the slide.', max_length=255)),
                ('image', models.ImageField(help_text='The slide image file.', null=True, upload_to='slide_images/')),
                ('slide_number', models.CharField(blank=True, help_text='An optional identifier or number associated with the slide.', max_length=50)),
                ('description', models.TextField(blank=True, help_text='A detailed description of the slide, including any relevant clinical or contextual information.')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, help_text='The date and time the slide was uploaded.')),
            ],
        ),
        migrations.CreateModel(
            name='ImagePatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_path', models.CharField(max_length=255)),
                ('has_tumor', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('slide_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patches', to='appforsegppt1.SlideImage')),
            ],
        ),
    ]
