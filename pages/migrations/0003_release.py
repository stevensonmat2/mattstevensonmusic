from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_alter_post_body'),
    ]

    operations = [
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='releases/')),
                ('link', models.URLField(blank=True)),
                ('text', models.TextField(help_text='Use the rich text editor to describe the release.')),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('sort_order', '-pk'),
            },
        ),
    ]