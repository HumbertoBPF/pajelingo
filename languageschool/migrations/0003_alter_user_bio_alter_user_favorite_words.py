# Generated by Django 4.2.1 on 2023-05-22 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0002_user_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='favorite_words',
            field=models.ManyToManyField(blank=True, to='languageschool.word'),
        ),
    ]
