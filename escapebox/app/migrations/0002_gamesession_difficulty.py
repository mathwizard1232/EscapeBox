# Generated by Django 5.1.1 on 2024-09-23 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="gamesession",
            name="difficulty",
            field=models.IntegerField(default=0),
        ),
    ]
