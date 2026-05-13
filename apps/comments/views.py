from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from apps.posts.models import Post
from .models import Comment


@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            parent_id = request.POST.get('parent_id')
            parent = get_object_or_404(Comment, id=parent_id) if parent_id else None
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent,
            )
    return redirect('posts:detail', slug=slug)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    slug = comment.post.slug
    if request.user == comment.author or request.user.is_staff:
        comment.delete()
    return redirect('posts:detail', slug=slug)
