from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("volunteer", "0010_remove_volunteer_period_remove_volunteer_year_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="volunteer",
            name="was_student",
            field=models.BooleanField(default=False),
        ),
    ]
