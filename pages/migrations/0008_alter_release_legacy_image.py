from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_repair_filer_image_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='release',
            name='legacy_image',
            field=models.ImageField(blank=True, upload_to='releases/'),
        ),
    ]