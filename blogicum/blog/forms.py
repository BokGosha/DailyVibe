from django import forms
from .models import Comment, Location, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class PostForm(forms.Form):
    """
    Форма для создания или редактирования поста.

    :Поля:
    - title (CharField): Заголовок поста.
    - text (CharField): Основной текст поста.
    - pud_date (DateTimeField): Дата и время публикации.
    - location_user (CharField): Локация пользователя.
    - location (ModelChoiceField): Доступная локация.
    - category_user (CharField): Категория пользователя.
    - category (ModelChoiceField): Доступная категория.
    - image (ImageField): Изображение.
    """
    title = forms.CharField(max_length=256, label='Заголовок')
    text = forms.CharField(widget=forms.Textarea)
    pub_date = forms.DateTimeField(
        label='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.',
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }))
    location_user = forms.CharField(
        max_length=256,
        label='Своя локация',
        required=False)
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label='Локация',
        required=False)
    category_user = forms.CharField(
        max_length=256,
        label='Своя категория',
        required=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Категория',
        required=False)
    image = forms.ImageField(label='Фото', required=False)

    def clean(self):
        cleaned_data = super().clean()

        location = cleaned_data.get('location')
        location_user = cleaned_data.get('location_user')

        if location and location_user:
            self.add_error(
                'location',
                'Выберите только одну из опций: "Локация" или "Своя локация".')
        elif not location and not location_user:
            self.add_error('location', 'Нужно выбрать хотя бы одну из опций.')

        category = cleaned_data.get('category')
        category_user = cleaned_data.get('category_user')

        if category and category_user:
            self.add_error(
                'category',
                'Выберите только одну из опций: "Категория" или "Своя категория".')
        elif not category and not category_user:
            self.add_error('category', 'Нужно выбрать хотя бы одну из опций.')

        return cleaned_data


class CommentForm(forms.ModelForm):
    """
    Форма для добавления комментариев.

    :Поля:
    - text (TextArea): Текст комментария.
    """

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 30})
        }


class UserForm(forms.ModelForm):
    """
    Форма для изменения профиля пользователя.

    :Поля:
    - username: Юзернейм.
    - first_name: Имя.
    - last_name: Фамилия.
    - email: Почта.
    """

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)
