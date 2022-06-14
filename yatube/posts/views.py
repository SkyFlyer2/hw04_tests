from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect, render, get_object_or_404
from .forms import PostForm
from .models import Post, Group, User
from .utils import page_list


def index(request):
    """Главная страница."""

    post_list = Post.objects.select_related('author', 'group')
    page_obj = page_list(post_list, request)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    """вывод записей одной из групп. """

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    page_obj = page_list(posts, request)
    return render(request, 'posts/group_list.html', {'group': group,
                                                     'page_obj': page_obj})


def profile(request, username):
    """вывод списка всех записей пользователя. """

    user = get_object_or_404(User, username=username)
    # Здесь код запроса к модели и создание словаря контекста
    post_list = user.posts.select_related('author')
    page_obj = page_list(post_list, request)
    return render(request, 'posts/profile.html', {
        'author': user,
        'page_obj': page_obj
    })


def post_detail(request, post_id):
    """подробная информация о записи. """

    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/post_detail.html', {
        'post_detail': post
    })


@login_required
def post_create(request):
    """добавление новой записи в базу. """

    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """редактирование записи. """

    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(
        request, 'posts/create_post.html', {
            'form': form,
            'is_edit': True,
            'post_id': post_id
        })
