from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0010_article_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_icon', filer.fields.image.FilerImageField(
                    blank=True,
                    help_text='The image shown as the browser tab icon.',
                    null=True,
                    on_delete=models.SET_NULL,
                    related_name='+',
                    to='filer.image',
                )),
            ],
            options={
                'verbose_name': 'site settings',
                'verbose_name_plural': 'site settings',
            },
        ),
    ]