# Generated by Django 5.1.1 on 2024-09-25 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_gamesession_rating_count_gamesession_total_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gamestate",
            name="current_scenario",
            field=models.CharField(default="initial", max_length=100),
        ),
        migrations.AlterField(
            model_name="gamestate",
            name="status",
            field=models.CharField(
                choices=[
                    ("ongoing", "Ongoing"),
                    ("escaped", "Escaped"),
                    ("caught", "Caught"),
                    ("quit", "Quit"),
                    ("quarantined", "Quarantined"),
                    ("disconnected", "Disconnected"),
                ],
                default="ongoing",
                max_length=20,
            ),
        ),
    ]
