from django.test import TestCase, LiveServerTestCase
from .views import get_token
from django import forms
from django.urls import reverse

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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
        self.assertTemplateUsed(risposta, 'japps/index.html')

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

        #add test for the template, if the user is logged in and not

    def test_redirection(self):
        """
        test that you can reach the page
        """
        ex_app=""
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 301) #this is the code for redirection

    def test_unexisting_app(self):
        """
        test that invalid app name return 200 for not logged user and 500 for
        logged in users
        """
        ex_app="/im_not_a_valid_app"
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 200)
        #apparently 500 is hidden for the test suite, may need to install selenium

    def test_invalid_app_name(self):
        """
        test for a name that for sure is not an app
        """
        ex_app="/im/anoth?er_notVal!d'app"
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 404)

class EndPageTest(TestCase):

    def test_submitted_redirect(self):
        """
        test that the user is redirected to main page for GET
        """
        risposta=self.client.get('/job_submitted/')
        self.assertEqual(risposta.status_code, 302)
        self.assertRedirects(risposta, '/',status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_submitted(self):
        """
        test that after POST the user reaches the right page
        """
        risposta=self.client.post("/submission/GWasser-1.0.0u1", {"user_token": valid_token})
        self.assertEqual(risposta.status_code, 200)
        #self.assertTemplateUsed(risposta, 'japps/job_submitted.html') #<-----this doesn't work i should submit a valid form to the server

    def test_expired_submission(self):
        """
        test that after POST with invalid token user retrieves the login form
        """
        risposta=self.client.post("/submission/GWasser-1.0.0u1", {"user_token": expired_token})
        self.assertEqual(risposta.status_code, 200)
        self.assertTemplateUsed(risposta, 'japps/index.html')

##################### selenium tests from here on ######################

class SeleniumTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium=webdriver.Firefox()
        super(SeleniumTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        #N.B. this will trow the following exception 'NoneType' object has no attribute 'path'
        #it has no consequences so don't worry about it.
        #it has been solved in one of the last commit to selenium but not in the pip version yet
        #will prob. be ok in the future
        super(SeleniumTestCase, self).tearDown()

    def test_tab_title(self):
        selenium = self.selenium
        selenium.get("%s%s" % (self.live_server_url, reverse('japps:index')))
        self.assertIn("CyVerse", self.selenium.title)
        selenium.get("%s%s" % (self.live_server_url, reverse('japps:go-to-index')))
        self.assertIn("CyVerse", self.selenium.title)
        selenium.get("%s%s" % (self.live_server_url, reverse('japps:submission', args=["fakeapp"])))
        self.assertIn("CyVerse", self.selenium.title)
        selenium.get("%s%s" % (self.live_server_url, reverse('japps:job_submitted')))
        self.assertIn("CyVerse", self.selenium.title)
