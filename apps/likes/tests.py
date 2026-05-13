from django.test import TestCase
from django.urls import reverse

from apps.users.models import User
from apps.posts.models import Post
from .models import Like


def make_user(username, password='pass'):
    return User.objects.create_user(username=username, password=password)


def make_post(author, title='Likeable Post', status=Post.Status.PUBLISHED):
    return Post.objects.create(author=author, title=title, content='Content.', status=status)


class LikeModelTests(TestCase):
    def setUp(self):
        self.user = make_user('u')
        self.post = make_post(self.user)

    def test_str(self):
        like = Like.objects.create(user=self.user, post=self.post)
        self.assertIn('u', str(like))

    def test_unique_together_prevents_double_like(self):
        Like.objects.create(user=self.user, post=self.post)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user, post=self.post)


class ToggleLikeViewTests(TestCase):
    def setUp(self):
        self.user = make_user('liker')
        self.post = make_post(self.user)

    def _url(self, slug=None):
        return reverse('likes:toggle', kwargs={'slug': slug or self.post.slug})

    def test_requires_login(self):
        r = self.client.post(self._url())
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Like.objects.count(), 0)

    def test_get_method_not_allowed(self):
        self.client.login(username='liker', password='pass')
        r = self.client.get(self._url())
        self.assertEqual(r.status_code, 405)

    def test_like_creates_like_returns_json(self):
        self.client.login(username='liker', password='pass')
        r = self.client.post(self._url())
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['count'], 1)
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_removes_like_returns_json(self):
        Like.objects.create(user=self.user, post=self.post)
        self.client.login(username='liker', password='pass')
        r = self.client.post(self._url())
        data = r.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['count'], 0)
        self.assertEqual(Like.objects.count(), 0)

    def test_toggle_twice_ends_up_liked(self):
        self.client.login(username='liker', password='pass')
        self.client.post(self._url())
        self.client.post(self._url())
        self.client.post(self._url())
        data = self.client.post(self._url()).json()
        # 4 toggles: like → unlike → like → unlike
        self.assertFalse(data['liked'])

    def test_like_draft_is_404(self):
        draft = make_post(self.user, 'Draft', status=Post.Status.DRAFT)
        self.client.login(username='liker', password='pass')
        r = self.client.post(self._url(draft.slug))
        self.assertEqual(r.status_code, 404)

    def test_like_nonexistent_post_is_404(self):
        self.client.login(username='liker', password='pass')
        r = self.client.post(self._url('no-such-post'))
        self.assertEqual(r.status_code, 404)

    def test_multiple_users_can_like_same_post(self):
        user2 = make_user('liker2')
        self.client.login(username='liker', password='pass')
        self.client.post(self._url())
        self.client.logout()
        self.client.login(username='liker2', password='pass')
        r = self.client.post(self._url())
        data = r.json()
        self.assertEqual(data['count'], 2)
