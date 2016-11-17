from django.test import TestCase
import views
import subprocess

# Create your tests here. -the CLI has to be installed to run the tests-
#create a blank token
missing_token=" "
#create an espired token
expired_token=subprocess.check_output(['auth-tokens-refresh', '-S']).split()[-1]
#and a valid one
token=subprocess.check_output(['auth-tokens-refresh', '-S']).split()[-1]

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
        data=missing_token
        form=views.get_token()
        print type(form)
        self.assertTrue(form.is_valid(), True)
        data=expired_token
        form=get_token()
        self.assertTrue(form.is_valid(), True)
        data=token
        form=get_token()
        self.assertTrue(form.is_valid(), True)
