from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return self.username

    @property
    def post_count(self) -> int:
        return self.posts.filter(status='published').count()

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip() or self.username
