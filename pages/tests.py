from django.test import TestCase

from .models import SilentMovie, Song


class InteractivePageTests(TestCase):
    def test_interactive_page_exposes_active_media_in_order(self):
        inactive_song = Song.objects.create(
            title='Hidden song',
            audio='songs/hidden.mp3',
            is_active=False,
        )
        first_song = Song.objects.create(
            title='First song',
            audio='songs/first.mp3',
            sort_order=1,
            effect_parameters={'filter': {'type': 'lowpass', 'frequency': 800}},
        )
        second_song = Song.objects.create(
            title='Second song',
            audio='songs/second.mp3',
            sort_order=2,
        )
        first_movie = SilentMovie.objects.create(
            title='First movie',
            video='movies/first.mp4',
            sort_order=1,
        )
        SilentMovie.objects.create(
            title='Hidden movie',
            video='movies/hidden.mp4',
            is_active=False,
        )

        response = self.client.get('/interactive/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['songs']), [first_song, second_song])
        self.assertEqual(list(response.context['silent_movies']), [first_movie])
        self.assertNotContains(response, inactive_song.title)
        self.assertContains(response, 'songs/first.mp3')
        self.assertContains(response, 'movies/first.mp4')
        self.assertContains(response, '"frequency": 800')
