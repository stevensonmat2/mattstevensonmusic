import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_release_artist'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='release_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]