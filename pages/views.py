import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .forms import ContactForm
from .models import Article, Post, Release


FEED_PAGE_SIZE = 5
CONTACT_RATE_LIMIT = 5
CONTACT_RATE_WINDOW = 60 * 60
logger = logging.getLogger(__name__)


def _feed_slice(offset, query='', tag_slug=''):
    posts = Post.objects.published()
    if query:
        posts = posts.filter(title__icontains=query) | posts.filter(body__icontains=query)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    posts = list(posts.distinct().prefetch_related('tags')[offset:offset + FEED_PAGE_SIZE + 1])
    has_more = len(posts) > FEED_PAGE_SIZE
    return posts[:FEED_PAGE_SIZE], has_more


def home(request):
    query = request.GET.get('q', '').strip()
    tag_slug = request.GET.get('tag', '').strip()
    posts, has_more = _feed_slice(0, query, tag_slug)
    return render(request, 'pages/home.html', {
        'posts': posts,
        'has_more': has_more,
        'next_offset': FEED_PAGE_SIZE,
        'search_query': query,
        'tag_slug': tag_slug,
    })


def post_feed(request):
    try:
        offset = max(int(request.GET.get('offset', 0)), 0)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'offset must be a non-negative integer.'}, status=400)

    query = request.GET.get('q', '').strip()
    tag_slug = request.GET.get('tag', '').strip()
    posts, has_more = _feed_slice(offset, query, tag_slug)
    return JsonResponse({
        'html': render_to_string('pages/_post_list.html', {'posts': posts}, request=request),
        'has_more': has_more,
        'next_offset': offset + len(posts),
    })


def about(request):
    return render(request, 'pages/about.html', {
        'article': Article.objects.filter(slug='bio').first(),
    })


def discography(request):
    return render(request, 'pages/discography.html', {
        'releases': Release.objects.all(),
    })


def interactive(request):
    return render(request, 'pages/interactive.html')


def contact(request):
    if request.method == 'POST':
        rate_key = f'contact-rate:{request.META.get("REMOTE_ADDR", "unknown")}'
        if cache.add(rate_key, 1, CONTACT_RATE_WINDOW):
            attempts = 1
        else:
            try:
                attempts = cache.incr(rate_key)
            except ValueError:
                cache.add(rate_key, 1, CONTACT_RATE_WINDOW)
                attempts = 1
        if attempts > CONTACT_RATE_LIMIT:
            return render(request, 'pages/contact.html', {
                'form': ContactForm(request.POST),
                'rate_limited': True,
            }, status=429)

        form = ContactForm(request.POST)
        if form.is_valid():
            recipient = getattr(settings, 'CONTACT_EMAIL', '')
            if not recipient:
                logger.error('CONTACT_EMAIL is not configured; contact form submission rejected.')
                return render(request, 'pages/contact.html', {
                    'form': form,
                    'send_error': True,
                }, status=503)

            try:
                message = EmailMessage(
                    subject='Website contact message',
                    body=(
                        f"Email: {form.cleaned_data['email']}\n\n"
                        f"{form.cleaned_data['message']}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient],
                    reply_to=[form.cleaned_data['email']],
                )
                sent_count = message.send(fail_silently=False)
                if sent_count != 1:
                    raise RuntimeError(f'Email backend reported {sent_count} messages sent.')
                logger.info(
                    'Contact form email accepted by backend=%s host=%s port=%s from=%s to=%s',
                    settings.EMAIL_BACKEND,
                    settings.EMAIL_HOST,
                    settings.EMAIL_PORT,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient,
                )
            except Exception:
                logger.exception('Contact form email delivery failed.')
                return render(request, 'pages/contact.html', {
                    'form': form,
                    'send_error': True,
                }, status=503)
            return render(request, 'pages/contact_success.html')
    else:
        form = ContactForm(initial={'form_started': int(time.time())})

    return render(request, 'pages/contact.html', {'form': form})
