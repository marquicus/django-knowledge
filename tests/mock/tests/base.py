from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from knowledge.models import Question, Response
User = get_user_model()


class TestCase(DjangoTestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'secret')
        self.joe = User.objects.create_user('joe', 'joedirt@example.com', 'secret')
        self.bob = User.objects.create_user('bob', 'bob@example.com', 'secret')
        self.anon = AnonymousUser()

        self.joe.first_name = 'Joe'
        self.joe.last_name = 'Dirt'
        self.joe.save()

        ## joe asks a question ##
        self.question = Question.objects.create(
            user = self.joe,
            title = 'What time is it?',
            body = 'Whenever I look at my watch I see the little hand at 3 and the big hand at 7.'
        )

        ## admin responds ##
        self.response = Response.objects.create(
            question = self.question,
            user = self.admin,
            body = 'The little hand at 3 means 3 pm or am, the big hand at 7 means 3:35 am or pm.'
        )