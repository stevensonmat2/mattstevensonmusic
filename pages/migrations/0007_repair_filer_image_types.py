from django.db import migrations


def repair_image_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    File = apps.get_model('filer', 'File')
    image_content_type = ContentType.objects.get(app_label='filer', model='image')
    File.objects.filter(polymorphic_ctype__isnull=True).update(
        polymorphic_ctype_id=image_content_type.pk,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_filer_images'),
    ]

    operations = [
        migrations.RunPython(repair_image_types, migrations.RunPython.noop),
    ]