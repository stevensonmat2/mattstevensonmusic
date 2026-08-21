from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_release'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='artist',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]