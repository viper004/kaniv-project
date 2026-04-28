from django.db import migrations, models


def populate_member_years(apps, schema_editor):
    MemberRegistration = apps.get_model("members", "memberRegistration")

    for member in MemberRegistration.objects.all():
        batch = (getattr(member, "batch", "") or "").strip()
        start_year = ""
        end_year = ""

        if "-" in batch:
            parts = [part.strip() for part in batch.split("-", 1)]
            if len(parts) == 2:
                start_year, end_year = parts

        member.start_year = start_year
        member.end_year = end_year
        if not member.blood_group:
            member.blood_group = "O+"
        member.save(update_fields=["start_year", "end_year", "blood_group"])


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0015_alter_memberregistration_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberregistration",
            name="start_year",
            field=models.CharField(default="", max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="memberregistration",
            name="end_year",
            field=models.CharField(default="", max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="memberregistration",
            name="blood_group",
            field=models.CharField(
                choices=[
                    ("A+", "A+"),
                    ("A-", "A-"),
                    ("B+", "B+"),
                    ("B-", "B-"),
                    ("AB+", "AB+"),
                    ("AB-", "AB-"),
                    ("O+", "O+"),
                    ("O-", "O-"),
                ],
                default="O+",
                max_length=3,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(populate_member_years, migrations.RunPython.noop),
    ]
