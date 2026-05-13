from django.test import TestCase, Client
from django.urls import reverse

from apps.users.models import User
from .models import Category, Post, Tag


def make_user(username='author', password='testpass'):
    return User.objects.create_user(username=username, password=password)


def make_post(author, title='Test Post', status=Post.Status.PUBLISHED, **kwargs):
    return Post.objects.create(author=author, title=title, content='Some content.', status=status, **kwargs)


# ── Model ─────────────────────────────────────────────────────────────────────

class PostModelTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.post = make_post(self.user)

    def test_slug_auto_generated(self):
        self.assertEqual(self.post.slug, 'test-post')

    def test_excerpt_auto_generated_from_content(self):
        self.assertTrue(len(self.post.excerpt) > 0)

    def test_excerpt_truncated_at_300(self):
        long = Post.objects.create(
            author=self.user, title='Long', content='x' * 400, status=Post.Status.PUBLISHED
        )
        self.assertLessEqual(len(long.excerpt), 300)

    def test_reading_time_minimum_1(self):
        self.assertGreaterEqual(self.post.reading_time, 1)

    def test_str(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_like_count_zero(self):
        self.assertEqual(self.post.like_count, 0)

    def test_comment_count_zero(self):
        self.assertEqual(self.post.comment_count, 0)

    def test_is_liked_by_returns_false_for_other_user(self):
        other = make_user('other')
        self.assertFalse(self.post.is_liked_by(other))


class PostQuerySetTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.published = make_post(self.user, 'Published')
        self.draft = make_post(self.user, 'Draft', status=Post.Status.DRAFT)
        self.featured = make_post(self.user, 'Featured', is_featured=True)

    def test_published_excludes_drafts(self):
        qs = Post.objects.published()
        self.assertIn(self.published, qs)
        self.assertNotIn(self.draft, qs)

    def test_featured_returns_only_is_featured(self):
        qs = Post.objects.featured()
        self.assertIn(self.featured, qs)
        self.assertNotIn(self.published, qs)

    def test_with_counts_annotates_likes_and_comments(self):
        post = Post.objects.with_counts().get(pk=self.published.pk)
        self.assertEqual(post.likes_total, 0)
        self.assertEqual(post.comments_total, 0)

    def test_by_author_filters_correctly(self):
        other = make_user('other')
        other_post = make_post(other, 'Other')
        qs = Post.objects.by_author(self.user)
        self.assertNotIn(other_post, qs)

    def test_recent_orders_newest_first(self):
        # featured was created last
        qs = list(Post.objects.published().recent())
        self.assertEqual(qs[0], self.featured)


class CategoryModelTests(TestCase):
    def test_slug_auto_generated(self):
        cat = Category.objects.create(name='Tech News')
        self.assertEqual(cat.slug, 'tech-news')

    def test_str(self):
        cat = Category.objects.create(name='Sports')
        self.assertEqual(str(cat), 'Sports')


# ── Views ─────────────────────────────────────────────────────────────────────

class HomeViewTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_home_ok(self):
        r = self.client.get(reverse('posts:home'))
        self.assertEqual(r.status_code, 200)

    def test_home_shows_published_posts(self):
        p = make_post(self.user, 'Visible Post')
        r = self.client.get(reverse('posts:home'))
        self.assertContains(r, 'Visible Post')

    def test_home_hides_drafts(self):
        make_post(self.user, 'Hidden Draft', status=Post.Status.DRAFT)
        r = self.client.get(reverse('posts:home'))
        self.assertNotContains(r, 'Hidden Draft')


class BlogViewTests(TestCase):
    def test_blog_ok(self):
        r = self.client.get(reverse('posts:blog'))
        self.assertEqual(r.status_code, 200)

    def test_search_returns_matching(self):
        user = make_user()
        make_post(user, 'Django Tips')
        r = self.client.get(reverse('posts:blog'), {'search': 'Django'})
        self.assertContains(r, 'Django Tips')

    def test_search_excludes_drafts(self):
        user = make_user()
        make_post(user, 'Secret Draft', status=Post.Status.DRAFT)
        r = self.client.get(reverse('posts:blog'), {'search': 'Secret'})
        self.assertNotContains(r, 'Secret Draft')


class PostDetailViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.post = make_post(self.user)
        self.draft = make_post(self.user, 'My Draft', status=Post.Status.DRAFT)

    def test_detail_published_ok(self):
        r = self.client.get(reverse('posts:detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(r.status_code, 200)

    def test_detail_draft_is_404(self):
        r = self.client.get(reverse('posts:detail', kwargs={'slug': self.draft.slug}))
        self.assertEqual(r.status_code, 404)

    def test_detail_nonexistent_slug_is_404(self):
        r = self.client.get(reverse('posts:detail', kwargs={'slug': 'no-such-post'}))
        self.assertEqual(r.status_code, 404)

    def test_detail_increments_views(self):
        before = self.post.views_count
        self.client.get(reverse('posts:detail', kwargs={'slug': self.post.slug}))
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, before + 1)


class PostCreateViewTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_create_redirects_anonymous(self):
        r = self.client.get(reverse('posts:create'))
        self.assertRedirects(r, '/users/login/?next=/post/new/')

    def test_create_get_ok(self):
        self.client.login(username='author', password='testpass')
        r = self.client.get(reverse('posts:create'))
        self.assertEqual(r.status_code, 200)

    def test_create_post_saves(self):
        self.client.login(username='author', password='testpass')
        self.client.post(reverse('posts:create'), {
            'title': 'Brand New',
            'content': 'Content here',
            'status': Post.Status.PUBLISHED,
        })
        self.assertTrue(Post.objects.filter(title='Brand New').exists())

    def test_create_post_sets_author_to_logged_in_user(self):
        self.client.login(username='author', password='testpass')
        self.client.post(reverse('posts:create'), {
            'title': 'Authored Post',
            'content': 'Content',
            'status': Post.Status.DRAFT,
        })
        post = Post.objects.get(title='Authored Post')
        self.assertEqual(post.author, self.user)

    def test_create_invalid_title_shows_form_errors(self):
        self.client.login(username='author', password='testpass')
        r = self.client.post(reverse('posts:create'), {
            'title': 'ab',  # too short
            'content': 'Content',
            'status': Post.Status.DRAFT,
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Post.objects.filter(title='ab').exists())


class PostEditViewTests(TestCase):
    def setUp(self):
        self.author = make_user('author')
        self.other = make_user('other')
        self.post = make_post(self.author)

    def test_edit_redirects_anonymous(self):
        r = self.client.get(reverse('posts:edit', kwargs={'slug': self.post.slug}))
        self.assertRedirects(r, f'/users/login/?next=/post/{self.post.slug}/edit/')

    def test_edit_get_ok_for_author(self):
        self.client.login(username='author', password='testpass')
        r = self.client.get(reverse('posts:edit', kwargs={'slug': self.post.slug}))
        self.assertEqual(r.status_code, 200)

    def test_edit_by_non_author_is_404(self):
        self.client.login(username='other', password='testpass')
        r = self.client.get(reverse('posts:edit', kwargs={'slug': self.post.slug}))
        self.assertEqual(r.status_code, 404)

    def test_edit_post_updates_title(self):
        self.client.login(username='author', password='testpass')
        self.client.post(reverse('posts:edit', kwargs={'slug': self.post.slug}), {
            'title': 'Updated Title',
            'content': 'Updated content',
            'status': Post.Status.PUBLISHED,
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_edit_post_by_non_author_does_not_update(self):
        self.client.login(username='other', password='testpass')
        self.client.post(reverse('posts:edit', kwargs={'slug': self.post.slug}), {
            'title': 'Hijacked',
            'content': 'x',
            'status': Post.Status.PUBLISHED,
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Test Post')


class PostDeleteViewTests(TestCase):
    def setUp(self):
        self.author = make_user('author')
        self.other = make_user('other')
        self.post = make_post(self.author)

    def test_delete_redirects_anonymous(self):
        r = self.client.post(reverse('posts:delete', kwargs={'slug': self.post.slug}))
        self.assertRedirects(r, f'/users/login/?next=/post/{self.post.slug}/delete/')
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_get_shows_confirm_page(self):
        self.client.login(username='author', password='testpass')
        r = self.client.get(reverse('posts:delete', kwargs={'slug': self.post.slug}))
        self.assertEqual(r.status_code, 200)

    def test_delete_post_removes_it(self):
        self.client.login(username='author', password='testpass')
        self.client.post(reverse('posts:delete', kwargs={'slug': self.post.slug}))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_by_non_author_is_404(self):
        self.client.login(username='other', password='testpass')
        r = self.client.post(reverse('posts:delete', kwargs={'slug': self.post.slug}))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())


class CategoryViewTests(TestCase):
    def setUp(self):
        user = make_user()
        self.cat = Category.objects.create(name='Science')
        make_post(user, 'Science Post', category=self.cat)

    def test_category_view_ok(self):
        r = self.client.get(reverse('posts:category', kwargs={'slug': self.cat.slug}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Science Post')

    def test_category_unknown_slug_is_404(self):
        r = self.client.get(reverse('posts:category', kwargs={'slug': 'nope'}))
        self.assertEqual(r.status_code, 404)


class SearchViewTests(TestCase):
    def setUp(self):
        user = make_user()
        make_post(user, 'Python Tips')
        make_post(user, 'Hidden Draft', status=Post.Status.DRAFT)

    def test_search_ok(self):
        r = self.client.get(reverse('posts:search'), {'search': 'Python'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Python Tips')

    def test_search_no_results_for_draft(self):
        r = self.client.get(reverse('posts:search'), {'search': 'Hidden'})
        self.assertNotContains(r, 'Hidden Draft')

    def test_search_empty_query(self):
        r = self.client.get(reverse('posts:search'), {'search': ''})
        self.assertEqual(r.status_code, 200)
