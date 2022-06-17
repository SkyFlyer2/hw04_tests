from posts.models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Создание записи посредством валидной формы"""

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': 'testuser'}))
        self.assertEqual(Post.objects.count(), 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.user,
                text='Тестовый текст'
            ).exists()
        )

    def test_edit_post(self):
        """Проверка редактирования записи через форму"""

        self.post = Post.objects.create(
            author=self.user,
            text='Отдельная запись',
            group=self.group
        )
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст после правки',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.user,
                text='Тестовый текст после правки'
            ).exists()
        )
