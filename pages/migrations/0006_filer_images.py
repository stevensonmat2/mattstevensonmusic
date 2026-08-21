import mimetypes
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import migrations, models
from filer.fields.image import FilerImageField


def copy_image_to_filer(Image, old_name):
    if not old_name:
        return None

    try:
        with default_storage.open(old_name, 'rb') as source:
            content = ContentFile(source.read())
    except FileNotFoundError:
        return None

    filename = os.path.basename(old_name)
    image = Image(
        name=filename,
        original_filename=filename,
        mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
        is_public=True,
    )
    image.file.save(filename, content, save=True)
    return image


def migrate_images(apps, schema_editor):
    FilerImage = apps.get_model('filer', 'Image')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Post = apps.get_model('pages', 'Post')
    Release = apps.get_model('pages', 'Release')
    image_cache = {}
    image_content_type = ContentType.objects.get(app_label='filer', model='image')

    for post in Post.objects.exclude(legacy_top_image=''):
        old_name = post.legacy_top_image.name
        if old_name not in image_cache:
            image_cache[old_name] = copy_image_to_filer(FilerImage, old_name)
        if image_cache[old_name]:
            image_cache[old_name].polymorphic_ctype_id = image_content_type.pk
            image_cache[old_name].save(update_fields=('polymorphic_ctype',))
            post.top_image_id = image_cache[old_name].pk
            post.save(update_fields=('top_image',))

    for release in Release.objects.exclude(legacy_image=''):
        old_name = release.legacy_image.name
        if old_name not in image_cache:
            image_cache[old_name] = copy_image_to_filer(FilerImage, old_name)
        if image_cache[old_name]:
            image_cache[old_name].polymorphic_ctype_id = image_content_type.pk
            image_cache[old_name].save(update_fields=('polymorphic_ctype',))
            release.image_id = image_cache[old_name].pk
            release.save(update_fields=('image',))


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0018_alter_file_options'),
        ('pages', '0005_release_release_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='top_image',
            new_name='legacy_top_image',
        ),
        migrations.RenameField(
            model_name='release',
            old_name='image',
            new_name='legacy_image',
        ),
        migrations.AddField(
            model_name='post',
            name='top_image',
            field=FilerImageField(blank=True, null=True, on_delete=models.SET_NULL, related_name='+'),
        ),
        migrations.AddField(
            model_name='release',
            name='image',
            field=FilerImageField(blank=True, null=True, on_delete=models.SET_NULL, related_name='+'),
        ),
        migrations.RunPython(migrate_images, migrations.RunPython.noop),
    ]