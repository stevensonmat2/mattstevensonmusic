from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import Post


FEED_PAGE_SIZE = 5


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
    return render(request, 'pages/about.html')


def interactive(request):
    return render(request, 'pages/interactive.html')
