from django.test import TestCase
from django.urls import reverse

from apps.users.models import User
from apps.posts.models import Post
from .models import Comment


def make_user(username, password='pass'):
    return User.objects.create_user(username=username, password=password)


def make_post(author, title='Test Post', status=Post.Status.PUBLISHED):
    return Post.objects.create(author=author, title=title, content='Content.', status=status)


def make_comment(post, author, content='A comment', parent=None):
    return Comment.objects.create(post=post, author=author, content=content, parent=parent)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = make_user('author')
        self.post = make_post(self.user)

    def test_str(self):
        c = make_comment(self.post, self.user)
        self.assertIn('author', str(c))

    def test_is_approved_by_default(self):
        c = make_comment(self.post, self.user)
        self.assertTrue(c.is_approved)

    def test_approved_queryset(self):
        c = make_comment(self.post, self.user)
        self.assertIn(c, Comment.objects.approved())

    def test_top_level_excludes_replies(self):
        parent = make_comment(self.post, self.user, 'Parent')
        reply = make_comment(self.post, self.user, 'Reply', parent=parent)
        top = Comment.objects.top_level()
        self.assertIn(parent, top)
        self.assertNotIn(reply, top)


# ── Add comment ───────────────────────────────────────────────────────────────

class AddCommentTests(TestCase):
    def setUp(self):
        self.author = make_user('author')
        self.commenter = make_user('commenter')
        self.post = make_post(self.author)

    def _url(self):
        return reverse('comments:add', kwargs={'slug': self.post.slug})

    def test_requires_login(self):
        r = self.client.post(self._url(), {'content': 'Hello'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_add_comment_creates_record(self):
        self.client.login(username='commenter', password='pass')
        self.client.post(self._url(), {'content': 'Nice post!'})
        self.assertEqual(Comment.objects.count(), 1)
        c = Comment.objects.first()
        self.assertEqual(c.content, 'Nice post!')
        self.assertEqual(c.author, self.commenter)
        self.assertIsNone(c.parent)

    def test_whitespace_only_content_is_ignored(self):
        self.client.login(username='commenter', password='pass')
        self.client.post(self._url(), {'content': '   '})
        self.assertEqual(Comment.objects.count(), 0)

    def test_empty_content_is_ignored(self):
        self.client.login(username='commenter', password='pass')
        self.client.post(self._url(), {'content': ''})
        self.assertEqual(Comment.objects.count(), 0)

    def test_add_comment_redirects_to_post_detail(self):
        self.client.login(username='commenter', password='pass')
        r = self.client.post(self._url(), {'content': 'Hi'})
        self.assertRedirects(r, reverse('posts:detail', kwargs={'slug': self.post.slug}))

    def test_add_comment_to_draft_is_404(self):
        draft = make_post(self.author, 'Draft Post', status=Post.Status.DRAFT)
        self.client.login(username='commenter', password='pass')
        r = self.client.post(
            reverse('comments:add', kwargs={'slug': draft.slug}),
            {'content': 'Hi'},
        )
        self.assertEqual(r.status_code, 404)

    def test_add_reply_sets_parent(self):
        parent = make_comment(self.post, self.author, 'Parent comment')
        self.client.login(username='commenter', password='pass')
        self.client.post(self._url(), {'content': 'Reply!', 'parent_id': parent.pk})
        reply = Comment.objects.get(content='Reply!')
        self.assertEqual(reply.parent, parent)

    def test_invalid_parent_id_is_404(self):
        self.client.login(username='commenter', password='pass')
        r = self.client.post(self._url(), {'content': 'Hi', 'parent_id': 99999})
        self.assertEqual(r.status_code, 404)


# ── Delete comment ────────────────────────────────────────────────────────────

class DeleteCommentTests(TestCase):
    def setUp(self):
        self.author = make_user('author')
        self.commenter = make_user('commenter')
        self.other = make_user('other')
        self.staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.post = make_post(self.author)

    def _url(self, pk):
        return reverse('comments:delete', kwargs={'pk': pk})

    def test_requires_login(self):
        c = make_comment(self.post, self.commenter)
        r = self.client.post(self._url(c.pk))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Comment.objects.filter(pk=c.pk).exists())

    def test_owner_can_delete_own_comment(self):
        c = make_comment(self.post, self.commenter)
        self.client.login(username='commenter', password='pass')
        self.client.post(self._url(c.pk))
        self.assertFalse(Comment.objects.filter(pk=c.pk).exists())

    def test_non_owner_cannot_delete_others_comment(self):
        c = make_comment(self.post, self.commenter)
        self.client.login(username='other', password='pass')
        self.client.post(self._url(c.pk))
        self.assertTrue(Comment.objects.filter(pk=c.pk).exists())

    def test_staff_can_delete_any_comment(self):
        c = make_comment(self.post, self.commenter)
        self.client.login(username='staff', password='pass')
        self.client.post(self._url(c.pk))
        self.assertFalse(Comment.objects.filter(pk=c.pk).exists())

    def test_delete_nonexistent_comment_is_404(self):
        self.client.login(username='commenter', password='pass')
        r = self.client.post(self._url(99999))
        self.assertEqual(r.status_code, 404)

    def test_delete_redirects_to_post_detail(self):
        c = make_comment(self.post, self.commenter)
        self.client.login(username='commenter', password='pass')
        r = self.client.post(self._url(c.pk))
        self.assertRedirects(r, reverse('posts:detail', kwargs={'slug': self.post.slug}))
