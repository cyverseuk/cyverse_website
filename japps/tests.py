from django.test import TestCase
from .views import get_token
from django import forms


import subprocess

# Create your tests here. -the CLI has to be installed to run the tests-
#create a blank token
missing_token=" "
#create an espired token
expired_token=subprocess.check_output(['auth-tokens-refresh', '-S']).split()[-1]
#and a valid one
valid_token=subprocess.check_output(['auth-tokens-refresh', '-S']).split()[-1]

class IndexTest(TestCase):

    def test_index(self):
        """
        test that you can reach the page
        """
        risposta=self.client.get('/')
        self.assertEqual(risposta.status_code, 200)

    def test_loginform(self):
        """
        test if the form is valid when receiving a non blank string
        """
        token_form=get_token()(data={"user_token": missing_token})
        #print token_form.errors
        self.assertFalse(token_form.is_valid())
        self.assertTrue(token_form.is_bound)
        token_form=get_token()(data={"user_token": expired_token})
        self.assertTrue(token_form.is_valid())
        self.assertTrue(token_form.is_bound)
        token_form=get_token()(data={"user_token": valid_token})
        self.assertTrue(token_form.is_valid())
        self.assertTrue(token_form.is_bound)

class AppTest(TestCase):

    def test_app(self):
        """
        test that you can reach the page
        """
        ex_app="/GWasser-1.0.0u1"
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 200)

    def test_redirection(self):
        """
        test that you can reach the page
        """
        ex_app=""
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 301) #this is the code for redirection

    def test_unexisting_app(self):
        """
        test that invalid app name return 404
        """
        ex_app="/im_not_a_valid_app"
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 404)
