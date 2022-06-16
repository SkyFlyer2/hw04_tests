from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст, который не должен быть слишком коротким',
            group=cls.group
        )
        cls.guest_user_urls = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/testuser/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        cls.registered_user_urls = {
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""

        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_group_slug_exists_at_desired_location(self):
        """Страница /group/<slug>/ доступна любому пользователю."""

        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_profile_url_exists_at_desired_location(self):
        """Страница /profile/<username>/ доступна любому пользователю."""

        response = self.guest_client.get('/profile/testuser/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_exists_at_desired_location(self):
        """Страница /posts/<post_id>/ доступна любому пользователю."""

        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница - код 404."""

        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

# Серия тестов для авторизованного пользователя
    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/<post_id>/edit доступна только автору."""

        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""

        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_home_url_uses_correct_template(self):
        """Страница по адресу / использует шаблон posts/index.html."""

        response = self.authorized_client.get('/')
        self.assertTemplateUsed(response, 'posts/index.html')

# проверка шаблонов по адресам
    def test_urls_guest_user_template(self):
        """проверка шаблонов для гостя."""

        for address, template in self.guest_user_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_registered_user_template(self):
        """проверка шаблонов для авторизованного пользователя."""

        for address, template in self.registered_user_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
