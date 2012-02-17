from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from desk.models import Question, Response


class BasicModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'secret')
        self.joe = User.objects.create_user('joe', 'joe@example.com', 'secret')
        self.bob = User.objects.create_user('bob', 'bob@example.com', 'secret')
        self.anon = AnonymousUser()

    def test_basic_question_answering(self):
        """
        Given a question asked by a real user, track answering and accepted states.
        """

        ## joe asks a question ##
        question = Question.objects.create(
            user = self.joe,
            title = 'What time is it?',
            body = 'Whenever I look at my watch I see the little hand at 3 and the big hand at 7.'
        )

        self.assertFalse(question.answered())
        self.assertFalse(question.accepted())


        ## admin responds ##
        response = Response.objects.create(
            question = question,
            user = self.admin,
            body = 'The little hand at 3 means 3 pm or am, the big hand at 7 means 3:35 am or pm.'
        )

        question = Question.objects.get(id=question.id) # refresh model

        self.assertTrue(question.answered())
        self.assertFalse(question.accepted())


        ## joe accepts the answer ##
        question.accept(response)

        question = Question.objects.get(id=question.id) # refresh model

        self.assertTrue(question.answered())
        self.assertTrue(question.accepted())


    def test_switching(self):
        question = Question.objects.create(
            user = self.joe,
            title = 'What time is it?',
            body = 'Whenever I look at my watch I see the little hand at 3 and the big hand at 7.'
        )

        self.assertEquals(question.status, 'private')

        question.public()
        self.assertEquals(question.status, 'public')

        question.internal()
        self.assertEquals(question.status, 'internal')

        question.private()
        self.assertEquals(question.status, 'private')


    def test_private_states(self):
        """
        Walk through the public, private and internal states for Question, and public, private,
        inherit and internal states for Response.

        Then checks who can see what with .can_view(<User>).
        """

        ## joe asks a question ##
        question = Question.objects.create(
            user = self.joe,
            title = 'What time is it?',
            body = 'Whenever I look at my watch I see the little hand at 3 and the big hand at 7.'
        )

        self.assertEquals(question.status, 'private')

        self.assertFalse(question.can_view(self.anon))
        self.assertFalse(question.can_view(self.bob))

        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))


        ## someone comes along and publicizes this question ##
        question.public()

        question = Question.objects.get(id=question.id) # refresh model
        self.assertEquals(question.status, 'public')

        # everyone can see
        self.assertTrue(question.can_view(self.anon))
        self.assertTrue(question.can_view(self.bob))

        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))


        ## someone comes along and internalizes this question ##
        question.internal()

        question = Question.objects.get(id=question.id) # refresh model
        self.assertEquals(question.status, 'internal')

        # only admin can see
        self.assertFalse(question.can_view(self.anon))
        self.assertFalse(question.can_view(self.bob))
        self.assertFalse(question.can_view(self.joe))

        self.assertTrue(question.can_view(self.admin))


        ## someone comes along and privatizes this question ##
        question.private()

        question = Question.objects.get(id=question.id) # refresh model
        self.assertEquals(question.status, 'private')
        
        self.assertFalse(question.can_view(self.anon))
        self.assertFalse(question.can_view(self.bob))

        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))


        ## admin responds ##
        response = Response.objects.create(
            question = question,
            user = self.admin,
            body = 'The little hand at 3 means 3 pm or am, the big hand at 7 means 3:35 am or pm.'
        )
        self.assertEquals(response.status, 'inherit')

        self.assertFalse(response.can_view(self.anon))
        self.assertFalse(response.can_view(self.bob))

        self.assertTrue(response.can_view(self.joe))
        self.assertTrue(response.can_view(self.admin))


        ## someone comes along and publicizes the parent question ##
        question.public()

        question = Question.objects.get(id=question.id) # refresh model
        response = Response.objects.get(id=response.id) # refresh model
        self.assertEquals(response.status, 'inherit')

        self.assertTrue(response.can_view(self.anon))
        self.assertTrue(response.can_view(self.bob))
        self.assertTrue(response.can_view(self.joe))
        self.assertTrue(response.can_view(self.admin))


        ## someone privatizes the response ##
        response.private()

        question = Question.objects.get(id=question.id) # refresh model
        response = Response.objects.get(id=response.id) # refresh model
        self.assertEquals(question.status, 'public')
        self.assertEquals(response.status, 'private')

        # everyone can see question still
        self.assertTrue(question.can_view(self.anon))
        self.assertTrue(question.can_view(self.bob))
        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))

        # only joe and admin can see the response though
        self.assertFalse(response.can_view(self.anon))
        self.assertFalse(response.can_view(self.bob))

        self.assertTrue(response.can_view(self.joe))
        self.assertTrue(response.can_view(self.admin))


        ## someone internalizes the response ##
        response.internal()

        question = Question.objects.get(id=question.id) # refresh model
        response = Response.objects.get(id=response.id) # refresh model
        self.assertEquals(question.status, 'public')
        self.assertEquals(response.status, 'internal')

        # everyone can see question still
        self.assertTrue(question.can_view(self.anon))
        self.assertTrue(question.can_view(self.bob))
        self.assertTrue(question.can_view(self.joe))
        self.assertTrue(question.can_view(self.admin))

        # only admin can see the response though
        self.assertFalse(response.can_view(self.anon))
        self.assertFalse(response.can_view(self.bob))
        self.assertFalse(response.can_view(self.joe))

        self.assertTrue(response.can_view(self.admin))
























