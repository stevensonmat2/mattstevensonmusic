import bleach
import markdown
import re
from django.db import models
from django.urls import reverse
from django.templatetags.static import static
from django.utils import timezone
from django.utils.text import slugify
from filer.fields.image import FilerImageField


ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    'h1', 'h2', 'h3', 'h4', 'p', 'br', 'hr', 'img', 'pre', 'code',
    'blockquote', 'strong', 'em', 'u', 's', 'ul', 'ol', 'li', 'figure',
    'figcaption', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'span',
}
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    'a': {'href', 'title', 'rel', 'target'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    '*': {'class', 'style'},
}


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            is_published=True,
            published_at__lte=timezone.now(),
        )


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    legacy_top_image = models.ImageField(upload_to='posts/top-images/', blank=True)
    top_image = FilerImageField(null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    body = models.TextField(
        help_text='Use the rich text editor to format the post body and add links or images.',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ('-published_at', '-pk')

    def __str__(self):
        return self.title

    @property
    def top_image_url(self):
        if self.top_image and self.top_image.file:
            return self.top_image.url
        if self.legacy_top_image and self.legacy_top_image.storage.exists(self.legacy_top_image.name):
            return self.legacy_top_image.url
        return static('images/timeWas_cover_BTMFDR_2003x2003.png')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def body_html(self):
        if re.search(r'<[a-z][^>]*>', self.body, re.IGNORECASE):
            rendered = self.body
        else:
            rendered = markdown.markdown(
                self.body,
                extensions=['extra', 'nl2br', 'sane_lists'],
            )
        return bleach.clean(
            rendered,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols={'http', 'https', 'mailto'},
        )

    def get_absolute_url(self):
        return reverse('pages:home') + f'#post-{self.pk}'


class Release(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    release_date = models.DateField(default=timezone.now)
    legacy_image = models.ImageField(upload_to='releases/', blank=True)
    image = FilerImageField(null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    link = models.URLField(blank=True)
    text = models.TextField(
        help_text='Use the rich text editor to describe the release.',
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('sort_order', '-pk')

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image and self.image.file:
            return self.image.url
        if self.legacy_image and self.legacy_image.storage.exists(self.legacy_image.name):
            return self.legacy_image.url
        return static('images/timeWas_cover_BTMFDR_2003x2003.png')

    @property
    def text_html(self):
        if re.search(r'<[a-z][^>]*>', self.text, re.IGNORECASE):
            rendered = self.text
        else:
            rendered = markdown.markdown(
                self.text,
                extensions=['extra', 'nl2br', 'sane_lists'],
            )
        return bleach.clean(
            rendered,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols={'http', 'https', 'mailto'},
        )
