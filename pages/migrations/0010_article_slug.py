from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0009_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='slug',
            field=models.SlugField(default='bio', max_length=220, unique=True),
            preserve_default=False,
        ),
    ]
