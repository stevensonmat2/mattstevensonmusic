import bleach
import markdown
import re
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


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
    top_image = models.ImageField(upload_to='posts/top-images/', blank=True)
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
