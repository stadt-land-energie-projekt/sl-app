# Generated by Django 4.2.10 on 2025-06-30 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("explorer", "0013_rename_potentialareawindstp2018vreg_potentialareawindstp2018eg"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="PotentialareaWindSTP2027VR",
            new_name="PotentialareaWindSTP2024VR",
        ),
        migrations.DeleteModel(
            name="PotentialareaWindSTP2027Repowering",
        ),
        migrations.DeleteModel(
            name="PotentialareaWindSTP2027SearchAreaForestArea",
        ),
        migrations.DeleteModel(
            name="PotentialareaWindSTP2027SearchAreaOpenArea",
        ),
    ]
