# Generated by Django 4.0.4 on 2022-05-05 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languageschool', '0013_rename_word_word_word_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='personal_pronoun_1',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='personal_pronoun_2',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='personal_pronoun_3',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='personal_pronoun_4',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='personal_pronoun_5',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='personal_pronoun_6',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]