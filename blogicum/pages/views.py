from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """
    Класс представления для отображения статической страницы "О нас".
    Наследуется от класса TemplateView, который предназначен для простых страниц,
    использующих один шаблон.

    :Атрибуты:
    - template_name: Путь к шаблону HTML, который будет использоваться для рендера страницы.
    """

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """
    Класс представления для отображения статической страницы "Правила".
    Аналогично классу AboutPage, наследуется от TemplateView.

    :Атрибуты:
    - template_name: Путь к шаблону HTML, который будет использоваться для рендера страницы.
    """
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """
    Функция-обработчик для отображения страницы ошибки 404 (страница не найдена).

    :Аргументы:
    - request: Объект запроса HTTP.
    - exception: Исключение, которое вызвало ошибку 404. Необязательно.

    :Возвращает: Ответ HTTP с рендером шаблона pages/404.html и статусом 404.
    """
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Функция-обработчик для отображения страницы ошибки 403 (CSRF-токен недействителен).

    :Аргументы:
    - request: Объект запроса HTTP.
    - reason: Причина сбоя CSRF (необязательный аргумент).

    :Возвращает:
    - Ответ HTTP с рендером шаблона pages/403csrf.html и статусом 403.
    """
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Функция-обработчик для отображения страницы ошибки 500 (внутренняя ошибка сервера).

    :Аргументы:
    - request: Объект запроса HTTP.

    :Возвращает:
    - Ответ HTTP с рендером шаблона pages/500.html и статусом 500.
    """
    return render(request, 'pages/500.html', status=500)
