from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0016_memberregistration_start_year_end_year_blood_group"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="memberregistration",
            name="batch",
        ),
        migrations.RemoveField(
            model_name="memberregistration",
            name="current_year",
        ),
    ]
