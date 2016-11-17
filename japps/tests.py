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
        test if the form is valid
        """
        token_form=get_token()(data={"user_token": missing_token})
        print token_form.is_valid()
        print token_form.is_bound
        print token_form.errors
        self.assertFalse(token_form.is_valid())
        token_form=get_token()(data={"user_token": expired_token})
        self.assertTrue(token_form.is_valid())
        token_form=get_token()(data={"user_token": valid_token})
