from django.conf import settings
from django.db import models


class CommentQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(is_approved=True)

    def top_level(self):
        return self.filter(parent__isnull=True)


class Comment(models.Model):
    post = models.ForeignKey(
        'posts.Post', on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'Comment by {self.author} on {self.post}'
