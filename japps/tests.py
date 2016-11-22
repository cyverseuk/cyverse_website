from django.test import TestCase, LiveServerTestCase
from .views import get_token
from django import forms
from django.urls import reverse

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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
        print "test_index"
        risposta=self.client.get('/')
        self.assertEqual(risposta.status_code, 200)
        self.assertTemplateUsed(risposta, 'japps/index.html')

    def test_loginform(self):
        """
        test if the form is valid when receiving a non blank string
        """
        print "test_loginform"
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
        print "test_app"
        ex_app="/GWasser-1.0.0u1"
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 200)

        #add test for the template, if the user is logged in and not

    def test_redirection(self):
        """
        test that you can reach the page
        """
        print "test_redirection"
        ex_app=""
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 301) #this is the code for redirection

    def test_unexisting_app(self):
        """
        test that invalid app name return 200 for not logged user and 500 for
        logged in users
        """
        print "test_unexisting_app"
        ex_app="/im_not_a_valid_app"
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 200)
        #apparently 500 is hidden for the test suite, may need to install selenium

    def test_invalid_app_name(self):
        """
        test for a name that for sure is not an app
        """
        print "test_invalid_app_name"
        ex_app="/im/anoth?er_notVal!d'app"
        risposta=self.client.get('/submission'+ex_app)
        self.assertEqual(risposta.status_code, 404)

class EndPageTest(TestCase):

    def test_submitted_redirect(self):
        """
        test that the user is redirected to main page for GET
        """
        print "test_submitted_redirect"
        risposta=self.client.get('/job_submitted/')
        self.assertEqual(risposta.status_code, 302)
        self.assertRedirects(risposta, '/',status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_submitted(self):
        """
        test that after POST the user reaches the right page
        """
        print "test_submitted"
        risposta=self.client.post("/submission/GWasser-1.0.0u1", {"user_token": valid_token})
        self.assertEqual(risposta.status_code, 200)
        #self.assertTemplateUsed(risposta, 'japps/job_submitted.html') #<-----this doesn't work i should submit a valid form to the server

    def test_expired_submission(self):
        """
        test that after POST with invalid token user retrieves the login form
        """
        print "test_expired_submission"
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
        """
        test that the title for each possible url contains CyVerse
        """
        print "test_tab_title"
        driver=self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse('japps:index')))
        self.assertIn("CyVerse", self.selenium.title)
        driver.get("%s%s" % (self.live_server_url, reverse('japps:go-to-index')))
        self.assertIn("CyVerse", self.selenium.title)
        #selenium.get("%s%s" % (self.live_server_url, reverse('japps:submission', args=["fakeapp"])))
        #self.assertIn("CyVerse", self.selenium.title)
        driver.get("%s%s" % (self.live_server_url, reverse('japps:job_submitted')))
        self.assertIn("CyVerse", self.selenium.title)

    def test_links(self):
        """
        test that the cyverse logo works as a link to the main page.
        Will test only one url as this is in the base and it's always the same
        -already verify this in the previous test-
        """
        print "test_links"
        timeout=50000 #if an error arise looking for #earlham_logo selector try to increase this before assess the failure
        driver=self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse('japps:job_submitted')))
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_css_selector('a > img#cyverse_logo'))
        result=driver.find_element_by_css_selector("a > img#cyverse_logo")
        result.click()

    def test_link2(self):
        """
        separating from previous test as i think sometimes it gives error cause
        it is present in both previous and next page.
        """
        print "test_link2"
        timeout=50000
        driver=self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse("japps:job_submitted")))
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_css_selector('a >img#earlham_logo'))
        result2=driver.find_element_by_css_selector("a > img#earlham_logo")
        result2.click()

    def test_app_selection(self):
        """
        test the following set of action:
        main_page -> token submission -> first app selection -> submit
        """
        print "test_app_selection"
        timeout=50000
        driver=self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse('japps:index')))
        driver.find_element_by_name("user_token").send_keys(valid_token)
        driver.find_element_by_tag_name("form").submit()
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name('ul'))
        app_list=driver.find_element_by_tag_name("ul")
        #apps=app_list.find_elements_by_tag_name("li")
        #for app in apps:
            #text=app.text
            #print text
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name("li"))
        first=app_list.find_element_by_css_selector("li a")
        #print first.text
        first.click()
        WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_tag_name("form"))
        button=driver.find_element_by_css_selector("form input").submit()

    def test_app_selection_invalid(self):
        """
        test the following set of action:
        main_page -> invalid token submission -> main_page
        """
        print "test_app_selection_invalid"
        timeout=50000
        driver=self.selenium
        driver.get("%s%s" % (self.live_server_url, reverse('japps:index')))
        driver.find_element_by_name("user_token").send_keys(expired_token)
        driver.find_element_by_tag_name("form").submit()
        #WebDriverWait(self.selenium, timeout).until(lambda driver: driver.find_element_by_css_selector("p.warning"))
        WebDriverWait(driver, timeout).until(EC.text_to_be_present_in_element((By.CLASS_NAME, "warning"), "Invalid Credentials"))
        warning=driver.find_element_by_css_selector("p.warning").text
        self.assertEqual(warning, "Invalid Credentials")

    def test_app_selection_no_token(self):
        """
        try to submit missing_token -> same page
        """
        print "test_app_selection_no_token"
        timeout=50000
        driver=self.selenium
        driver.implicitly_wait(10)
        driver.get("%s%s" % (self.live_server_url, reverse("japps:index")))
        driver.find_element_by_name("user_token").send_keys(missing_token)
        driver.find_element_by_tag_name("form").submit()
        warning=driver.find_element_by_css_selector("p.warning").text
        self.assertIn("user needs", warning)
