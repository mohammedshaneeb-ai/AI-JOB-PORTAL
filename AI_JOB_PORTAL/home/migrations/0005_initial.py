# Generated by Django 4.2.4 on 2023-08-11 09:53

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("home", "0004_delete_candidate"),
    ]

    operations = [
        migrations.CreateModel(
            name="Candidate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("place", models.CharField(max_length=100)),
                ("score", models.DecimalField(decimal_places=2, max_digits=5)),
                ("domain", models.CharField(max_length=30)),
                ("resume_link", models.URLField()),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=20)),
                ("age", models.IntegerField()),
                ("experience", models.IntegerField()),
                ("education", models.TextField()),
                ("skills", models.TextField()),
            ],
        ),
    ]