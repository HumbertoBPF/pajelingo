# Generated by Django 4.0.4 on 2023-01-02 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0033_alter_category_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='flag_image',
            field=models.ImageField(blank=True, upload_to='images/%d/%m/%Y'),
        ),
    ]