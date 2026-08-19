(() => {
    const feed = document.querySelector('[data-feed-url]');
    if (!feed) return;

    const posts = feed.querySelector('[data-feed-posts]');
    const status = feed.querySelector('[data-feed-status]');
    const sentinel = feed.querySelector('[data-feed-sentinel]');
    let loading = false;
    const filters = new URLSearchParams();
    if (feed.dataset.searchQuery) filters.set('q', feed.dataset.searchQuery);
    if (feed.dataset.tagSlug) filters.set('tag', feed.dataset.tagSlug);

    const loadMore = async () => {
        if (loading || feed.dataset.hasMore !== 'true') return;

        loading = true;
        feed.setAttribute('aria-busy', 'true');
        status.textContent = 'Loading more posts...';

        try {
            filters.set('offset', feed.dataset.nextOffset);
            const response = await fetch(`${feed.dataset.feedUrl}?${filters}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });
            if (!response.ok) throw new Error(`Feed request failed: ${response.status}`);

            const data = await response.json();
            posts.insertAdjacentHTML('beforeend', data.html);
            feed.dataset.nextOffset = data.next_offset;
            feed.dataset.hasMore = data.has_more ? 'true' : 'false';
            status.textContent = data.has_more ? '' : 'You have reached the end.';
        } catch (error) {
            status.textContent = 'Posts could not be loaded. Please try again.';
        } finally {
            loading = false;
            feed.setAttribute('aria-busy', 'false');
        }
    };

    const observer = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) loadMore();
    }, { rootMargin: '500px 0px' });

    observer.observe(sentinel);
})();
