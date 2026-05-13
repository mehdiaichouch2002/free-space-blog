from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.comments.forms import CommentForm
from .forms import PostForm
from .models import Category, Post, Tag


def home(request):
    featured = (
        Post.objects.published()
        .featured()
        .select_related('author', 'category')
        .prefetch_related('tags')
    )
    posts = (
        Post.objects.published()
        .with_counts()
        .select_related('author', 'category')
        .prefetch_related('tags')
        .recent()
    )
    return render(request, 'posts/home.html', {'featured': featured, 'posts': posts})


def blog(request):
    search = request.GET.get('search', '').strip()
    posts = (
        Post.objects.published()
        .with_counts()
        .select_related('author', 'category')
        .recent()
    )
    if search:
        posts = posts.filter(Q(title__icontains=search) | Q(content__icontains=search))
    categories = Category.objects.all()
    return render(request, 'posts/blog.html', {
        'posts': posts,
        'categories': categories,
        'search': search,
    })


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category').prefetch_related('tags'),
        slug=slug, status=Post.Status.PUBLISHED,
    )
    # Atomic increment — no race condition
    Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    comments = (
        post.comments
        .filter(is_approved=True, parent__isnull=True)
        .select_related('author')
        .prefetch_related('replies__author')
    )
    is_liked = post.is_liked_by(request.user)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': CommentForm(),
        'is_liked': is_liked,
    })


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = (
        Post.objects.published()
        .filter(category=category)
        .with_counts()
        .select_related('author')
        .recent()
    )
    return render(request, 'posts/category_posts.html', {'category': category, 'posts': posts})


def search(request):
    query = request.GET.get('search', '').strip()
    posts = Post.objects.none()
    if query:
        posts = (
            Post.objects.published()
            .with_counts()
            .select_related('author', 'category')
            .filter(Q(title__icontains=query) | Q(content__icontains=query))
            .recent()
        )
    return render(request, 'posts/search.html', {'posts': posts, 'search': query})


def about(request):
    return render(request, 'posts/about.html')


def services(request):
    return render(request, 'posts/services.html')


def contact(request):
    if request.method == 'POST':
        messages.success(request, 'Message sent! We will get back to you soon.')
        return redirect('posts:contact')
    return render(request, 'posts/contact.html')


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Post created!')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form, 'action': 'Create'})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'form': form, 'action': 'Edit', 'post': post})


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('posts:home')
    return render(request, 'posts/post_confirm_delete.html', {'post': post})
