from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class BaseModel(models.Model):
    """
    Эта абстрактная модель служит основой для всех остальных моделей в приложении.
    Она включает общие поля, такие как is_published и created_at, которые могут быть использованы всеми дочерними моделями.

    :Поля:
    - is_published (BooleanField): Определяет, опубликована ли запись. По умолчанию установлено значение True.
    - created_at (DateTimeField): Дата и время создания записи. Устанавливается автоматически при создании объекта.
    """
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Location(BaseModel):
    """
    Модель представляет географическое местоположение, связанное с публикациями.
    Каждая запись может быть привязана к конкретному месту.

    :Поля:
    - name (CharField): Название места.
    - description (CharField): Краткое описание места.
    - slug (SlugField): Уникальный идентификатор, используемый в URL. Должен содержать только латинские буквы, цифры, дефисы и подчеркивания.
    """
    name = models.CharField(max_length=256, verbose_name='Название места')
    description = models.CharField(
        max_length=256, verbose_name='Описание места', blank=True)
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
        'латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(BaseModel):
    """
    Модель описывает тематические категории, к которым относятся публикации.
    Позволяет пользователям удобно находить контент по интересующим темам.

    :Поля:
    - title (CharField): Заголовок категории.
    - description (TextField): Подробное описание категории.
    - slug (SlugField): Уникальный идентификатор для URL.
    """
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
        'латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(BaseModel):
    """
    Основная модель для хранения публикаций. Каждая публикация может принадлежать одному автору, быть привязанной к конкретной категории и местоположению.

    :Поля:
    - title (CharField): Заголовок публикации.
    - text (TextField): Основной текст публикации.
    - pub_date (DateTimeField): Дата и время публикации. Можно задать отложенную публикацию, установив будущее время.
    - author (ForeignKey): Автор публикации. Связано с моделью пользователя.
    - location (ForeignKey): Географическое местоположение публикации. Может быть пустым.
    - category (ForeignKey): Тематическая категория публикации. Может быть пустой.
    - image (ImageField): Изображение, прикрепленное к публикации. Необязательное поле.
    """
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )

    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Модель для хранения комментариев к публикациям. Каждый комментарий принадлежит одной публикации и одному автору.

    :Поля:
    - text (TextField): Текст комментария.
    - post (ForeignKey): Публикация, к которой относится комментарий.
    - created_at (DateTimeField): Время создания комментария. Устанавливается автоматически.
    - author (ForeignKey): Автор комментария. Связано с моделью пользователя.
    """
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
