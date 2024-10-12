def menu(request):
    items = {
        'common_items': [
            {'path': 'planner:contacts', 'text': 'Техподдержка'},
            {'path': 'planner:faq', 'text': 'FAQ'},
        ],
    }
    if request.user.is_authenticated:
        items['authenticated_items'] = [
            {
                'path': 'users:password_change',
                'text': 'Изменить пароль',
                'link_light': True
            },
        ]
    else:
        items['guest_items'] = [
            {'path': 'users:login', 'text': 'Войти'},
        ]
    return items
