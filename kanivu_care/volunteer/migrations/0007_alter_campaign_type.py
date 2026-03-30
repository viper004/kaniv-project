from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("volunteer", "0006_campaignenrollment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="type",
            field=models.CharField(
                choices=[
                    ("Health", "Health & Medical"),
                    ("Social", "Social Service"),
                    ("Environment", "Environmental"),
                    ("Education", "Educational"),
                    ("Fundraising", "Fundraising"),
                    ("Awareness", "Awareness"),
                    ("Event", "Event-Based"),
                    ("Skill", "Skill-Based"),
                ],
                max_length=50,
            ),
        ),
    ]
