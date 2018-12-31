from mock.tests.base import TestCase

from django.test.client import Client
from django.contrib.auth.models import AnonymousUser

from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from knowledge.models import Question, Response, Category
from django.contrib.auth import get_user_model
User = get_user_model()


class BasicViewTest(TestCase):
    def test_index(self):
        c = Client()

        r = c.get(reverse('knowledge_index'))
        self.assertEquals(r.status_code, 200)


    def test_list(self):
        c = Client()

        r = c.get(reverse('knowledge_list'))
        self.assertEquals(r.status_code, 200)


    def test_list_category(self):
        c = Client()

        r = c.get(reverse('knowledge_list_category', args=['notreal']))
        self.assertEquals(r.status_code, 404)

        category = Category.objects.create(title='Hello!', slug='hello')

        r = c.get(reverse('knowledge_list_category', args=['hello']))
        self.assertEquals(r.status_code, 200)


    def test_list_search(self):
        c = Client()

        r = c.get(reverse('knowledge_list') + '?title=hello!')
        self.assertEquals(r.status_code, 200)


    def test_thread(self):
        c = Client()

        question_url = reverse('knowledge_thread', args=[self.question.id, slugify(self.question.title)])

        r = c.get(reverse('knowledge_thread', args=[123456, 'a-big-long-slug']))
        self.assertEquals(r.status_code, 404)

        # this is private by default
        r = c.get(reverse('knowledge_thread', args=[self.question.id, 'a-big-long-slug']))
        self.assertEquals(r.status_code, 404)
    
        r = c.get(question_url)
        self.assertEquals(r.status_code, 404)

        c.login(username='joe', password='secret')

        r = c.get(reverse('knowledge_thread', args=[self.question.id, 'a-big-long-slug']))
        self.assertEquals(r.status_code, 301)

        r = c.get(question_url)
        self.assertEquals(r.status_code, 200)


        RESPONSE_POST = {
            'body': 'This is the response body friend!'
        }

        r = c.post(question_url, RESPONSE_POST)
        self.assertEquals(r.status_code, 302)

        # back to an anon user
        c.logout()

        # lets make it public...
        self.question.public()
    
        r = c.get(question_url)
        self.assertEquals(r.status_code, 200)

        # invalid responses POSTs are basically ignored...
        r = c.post(question_url, RESPONSE_POST)
        self.assertEquals(r.status_code, 200)


    def test_moderate(self):
        c = Client()

        r = c.get(reverse('knowledge_moderate', args=['question', self.question.id, 'public']))
        self.assertEquals(r.status_code, 404)

        r = c.post(reverse('knowledge_moderate', args=['question', self.question.id, 'public']))
        self.assertEquals(r.status_code, 404)

        r = c.post(reverse('knowledge_moderate', args=['response', self.response.id, 'public']))
        self.assertEquals(r.status_code, 404)


        c.login(username='admin', password='secret')

        r = c.post(reverse('knowledge_moderate', args=['question', self.question.id, 'notreal']))
        self.assertEquals(r.status_code, 404)

        # nice try buddy!
        r = c.post(reverse('knowledge_moderate', args=['user', self.admin.id, 'delete']))
        self.assertEquals(r.status_code, 404)

        # GET does not work
        r = c.get(reverse('knowledge_moderate', args=['question', self.question.id, 'public']))
        self.assertEquals(r.status_code, 404)

        self.assertEquals(Question.objects.get(id=self.question.id).status, 'private')
        r = c.post(reverse('knowledge_moderate', args=['question', self.question.id, 'public']))
        self.assertEquals(r.status_code, 302)
        self.assertEquals(Question.objects.get(id=self.question.id).status, 'public')

        r = c.post(reverse('knowledge_moderate', args=['response', self.response.id, 'public']))
        self.assertEquals(r.status_code, 302)

        r = c.post(reverse('knowledge_moderate', args=['question', self.question.id, 'delete']))
        self.assertEquals(r.status_code, 302)

        r = c.post(reverse('knowledge_moderate', args=['question', self.question.id, 'delete']))
        self.assertEquals(r.status_code, 404)


    def test_ask(self):
        c = Client()

        r = c.get(reverse('knowledge_ask'))
        self.assertEquals(r.status_code, 200)

        QUESTION_POST = {
            'title': 'This is a title friend!',
            'body': 'This is the body friend!',
            'status': 'private'
        }

        # invalid question POSTs are basically ignored...
        r = c.post(reverse('knowledge_ask'), QUESTION_POST)
        self.assertEquals(r.status_code, 200)

        c.login(username='joe', password='secret')

        # ...unless you are a user with permission to ask
        r = c.post(reverse('knowledge_ask'), QUESTION_POST)
        self.assertEquals(r.status_code, 302)