import re
import unidecode
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from .models import Post, Category, Comment, Location, Follow
from .forms import PostForm, CommentForm, UserForm


User = get_user_model()


def filter_posts(posts):
    """
    Фильтрует посты, выбирая только опубликованные записи и категории.
    Аннотирует количество комментариев и сортирует результаты по дате публикации.

    :Аргументы:
    - posts: QuerySet объектов Post

    :Возвращает:
    - QuerySet с выбранными полями и фильтрами
    """
    return posts.select_related(
        'category',
        'author',
        'location'
    ).annotate(
        comment_count=Count('comments')
    ).filter(
        Q(is_published=True)
        & Q(category__is_published=True)
    ).order_by("-pub_date")


def paginator_page(list, count, request):
    """
    Создает пагинатор для списка элементов.

    :Аргументы:
    - list: Список элементов для пагинации
    - count: Количество элементов на странице
    - request: Объект запроса, используемый для получения номера страницы

    :Возвращает:
    - Объект Page из пэйджинатора, соответствующий номеру страницы
    """
    paginator = Paginator(list, count)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """
    Представление главной страницы блога.

    :Аргументы:
    - request: Объект запроса HTTP

    :Возвращает:
    - Ответ HTTP с рендером шаблона blog/index.html и контекстом, включающим постраничную выборку публикаций
    """
    template_name = 'blog/index.html'
    posts = filter_posts(Post.objects)
    page_obj = paginator_page(posts, 10, request)
    context = {'page_obj': page_obj}
    return render(request, template_name, context)


def post_detail(request, post_id):
    """
    Представление страницы отдельного поста.

    :Аргументы:
    - request: Объект запроса HTTP
    - post_id: Идентификатор поста

    :Возвращает:
    - Ответ HTTP с рендером шаблона blog/detail.html и контекстом, включающим сам пост, форму для комментариев и существующие комментарии
    """
    template_name = 'blog/detail.html'

    post = get_object_or_404(Post.objects.select_related(
        'category', 'author', 'location'), pk=post_id)
    if request.user != post.author:
        post = get_object_or_404(
            filter_posts(Post.objects), pk=post_id
        )
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    posts = filter_posts(category.posts)
    page_obj = paginator_page(posts, 10, request)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


def location_posts(request, location_slug):
    template_name = 'blog/location.html'
    location = get_object_or_404(
        Location.objects.filter(is_published=True),
        slug=location_slug
    )
    posts = filter_posts(location.posts)
    page_obj = paginator_page(posts, 10, request)
    context = {
        'location': location,
        'page_obj': page_obj
    }
    return render(request, template_name, context)


def user_profile(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User.objects, username=username)
    posts = (
        profile.posts
        .annotate(comment_count=Count('comments'))
        .select_related('category', 'author', 'location')
        .order_by("-pub_date")
    )

    page_obj = paginator_page(posts, 10, request)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


@login_required
def edit_profile(request):
    template_name = 'blog/user.html'
    username = request.user.get_username()
    instance = get_object_or_404(User, username=username)

    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=username)

    return render(request, template_name, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    instance = get_object_or_404(Comment, pk=comment_id)

    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'comment': instance,
    }

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template_name, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    instance = get_object_or_404(Comment, pk=comment_id)

    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    context = {'comment': instance}

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template_name, context)


def generate_slug(text):
    text = unidecode.unidecode(text)
    text = text.lower()

    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)

    text = text.strip('-')

    return text


@login_required
def create_post(request):
    """
    Функция создаёт новый пост в блоге.

    :Аргументы:
    - request: Объект HTTP-запроса Django
    """
    template = 'blog/create.html'
    form = PostForm(request.POST or None, request.FILES or None)
    context = {'form': form}

    if form.is_valid():
        post = Post()
        post.title = form.cleaned_data['title']
        post.text = form.cleaned_data['text']
        post.image = form.cleaned_data['image']
        post.pub_date = form.cleaned_data['pub_date']
        post.author = request.user

        if form.cleaned_data['location']:
            post.location = form.cleaned_data['location']
        else:
            location_name = form.cleaned_data['location_user']
            if Location.objects.filter(name=location_name).exists():
                post.location = Location.objects.get(
                    name=form.cleaned_data['location_user'])
            else:
                post.location = Location.objects.create(
                    name=form.cleaned_data['location_user'], slug=generate_slug(location_name))

        if form.cleaned_data['category']:
            post.category = form.cleaned_data['category']
        else:
            category_name = form.cleaned_data['category_user']
            if Category.objects.filter(title=category_name).exists():
                post.category = Category.objects.get(
                    name=form.cleaned_data['category_user'])
            else:
                post.category = Category.objects.create(
                    title=form.cleaned_data['category_user'], slug=generate_slug(category_name))

        post.save()
        return redirect('blog:profile', username=request.user.get_username())

    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    template_name = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)

    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    initial_data = {
        'title': instance.title,
        'text': instance.text,
        'pub_date': instance.pub_date.strftime('%Y-%m-%dT%H:%M'),
        'location_user': getattr(instance, 'location_user', ''),
        'location': getattr(instance, 'location', None),
        'category_user': getattr(instance, 'category_user', ''),
        'category': getattr(instance, 'category', None),
        'image': instance.image,
        'is_published': instance.is_published
    }

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            # Получаем очищенные данные из формы
            data = form.cleaned_data

            # Обновляем существующее сообщение
            instance.title = data['title']
            instance.text = data['text']
            instance.pub_date = data['pub_date']
            instance.location_user = data['location_user'] or ''
            instance.location = data['location'] or None
            instance.category_user = data['category_user'] or ''
            instance.category = data['category'] or None
            instance.is_published = data['is_published']

            # Если загружено новое изображение, заменяем старое
            if request.FILES.get('image'):
                instance.image = request.FILES['image']

            # Сохраняем изменения
            instance.save()

            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(initial=initial_data)

    context = {'form': form}
    return render(request, template_name, context)


@login_required
def delete_post(request, post_id):
    template_name = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)

    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    
    initial_data = {
        'title': instance.title,
        'text': instance.text,
        'pub_date': instance.pub_date.strftime('%Y-%m-%dT%H:%M'),
        'location_user': getattr(instance, 'location_user', ''),
        'location': getattr(instance, 'location', None),
        'category_user': getattr(instance, 'category_user', ''),
        'category': getattr(instance, 'category', None),
        'image': instance.image,
        'is_published': instance.is_published
    }

    form = PostForm(initial=initial_data)
    context = {'form': form}

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user)

    return render(request, template_name, context)


def user_profile(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User.objects, username=username)
    posts = (
        profile.posts
        .annotate(comment_count=Count('comments'))
        .select_related('category', 'author', 'location')
        .order_by("-pub_date")
    )

    page_obj = paginator_page(posts, 10, request)

    is_subscriber = False
    if request.user is not None:
        follow = Follow.objects.filter(
            Q(user_id=request.user.id) & Q(following_id=profile.id))
        if len(follow) != 0:
            is_subscriber = True

    context = {
        'profile': profile,
        'page_obj': page_obj,
        'is_subscriber': is_subscriber,
    }
    return render(request, template_name, context)


@login_required
def user_follow(request, username):
    user = request.user
    following = get_object_or_404(User.objects, username=username)

    Follow.objects.create(user=user, following=following)

    return redirect('blog:profile', username=following.username)


@login_required
def delete_follow(request, username):
    following = get_object_or_404(User.objects, username=username)
    instance = get_object_or_404(Follow.objects.filter(
        Q(user_id=request.user.id)
        & Q(following_id=following.id)
    ))
    instance.delete()

    return redirect('blog:profile', username=following.username)


@login_required
def following(request):
    followings = Follow.objects.select_related(
        'following').filter(user=request.user).order_by('-id')

    paginator = Paginator(followings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'blog/following.html', context)
