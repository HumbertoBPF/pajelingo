import random

import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.db.models import Q
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from selenium.webdriver.common.by import By

from languageschool.models import AppUser
from languageschool.tests.selenium.utils import assert_menu, WARNING_REQUIRED_FIELD_HTML, WARNING_EMAIL_WITH_SPACE_HTML, \
    WARNING_REQUIRED_EMAIL_FIREFOX_HTML, submit_form_user, get_form_error_message
from languageschool.tests.utils import get_valid_password, get_random_email, get_random_username, \
    get_too_short_password, get_too_long_password, get_password_without_letters, get_password_without_digits, \
    get_password_without_special_characters
from languageschool.utils import SIGN_UP_SUBJECT, SIGN_UP_MESSAGE
from languageschool.views.account import SUCCESSFUL_SIGN_UP, SUCCESSFUL_ACTIVATION, \
    ACTIVATION_LINK_ERROR
from pajelingo import settings
from pajelingo.validators.auth_password_validators import ERROR_LENGTH_PASSWORD, ERROR_LETTER_PASSWORD, \
    ERROR_DIGIT_PASSWORD, ERROR_SPECIAL_CHARACTER_PASSWORD
from pajelingo.validators.validators import ERROR_SPACE_IN_USERNAME, ERROR_NOT_CONFIRMED_PASSWORD, \
    ERROR_NOT_AVAILABLE_EMAIL, ERROR_NOT_AVAILABLE_USERNAME


class TestSignupSelenium:
    def successful_signup(self, live_server, selenium_driver):
        """
        Performs a successful signup with random credentials.

        :param live_server: live server Django pytest fixture
        :param selenium_driver: Selenium web driver

        :return: tuple with the random email and the random username.
        """
        selenium_driver.get(live_server.url + reverse("signup"))

        email = get_random_email()
        username = get_random_username()
        password = get_valid_password()

        submit_form_user(selenium_driver, email, username, password, password)

        return email, username

    @pytest.mark.django_db
    def test_signup_form_rendering(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url+reverse("signup"))

        inputs = selenium_driver.find_elements(By.CSS_SELECTOR, "form .form-control")
        inputs_email = inputs[0]
        inputs_username = inputs[1]
        inputs_password = inputs[2]
        inputs_password_confirmation = inputs[3]
        submit_buttons_form = selenium_driver.find_elements(By.CSS_SELECTOR, "form div .btn-success")

        assert len(inputs) == 4
        assert inputs_email.get_attribute("placeholder") == "Email address"
        assert inputs_username.get_attribute("placeholder") == "Username"
        assert inputs_password.get_attribute("placeholder") == "Password"
        assert inputs_password_confirmation.get_attribute("placeholder") == "Confirm your password"
        assert len(submit_buttons_form) == 1
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_signup(self, live_server, selenium_driver):
        email, username = self.successful_signup(live_server, selenium_driver)

        alert_success = selenium_driver.find_element(By.CLASS_NAME, "alert-success")

        assert alert_success.text == SUCCESSFUL_SIGN_UP
        assert User.objects.filter(username=username, email=email, is_active=False).exists()
        assert AppUser.objects.filter(user__username=username, user__email=email, user__is_active=False).exists()
        # Checking that the activation email was received
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == SIGN_UP_SUBJECT
        assert SIGN_UP_MESSAGE.split("{}")[1] in mail.outbox[0].body
        assert mail.outbox[0].to == [email]
        assert mail.outbox[0].from_email == settings.EMAIL_FROM
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_activate_account(self, live_server, selenium_driver):
        email, username = self.successful_signup(live_server, selenium_driver)

        activation_link = "http://" + mail.outbox[0].body.split("http://")[1]

        selenium_driver.get(activation_link)

        alert_success = selenium_driver.find_element(By.CLASS_NAME, "alert-success")

        assert alert_success.text == SUCCESSFUL_ACTIVATION
        assert User.objects.filter(username=username, email=email, is_active=True).exists()

    @pytest.mark.django_db
    def test_activate_account_invalid_token(self, live_server, selenium_driver):
        email, username = self.successful_signup(live_server, selenium_driver)

        activation_link = "http://" + mail.outbox[0].body.split("http://")[1] + get_random_string(5)

        selenium_driver.get(activation_link)

        alert_danger = selenium_driver.find_element(By.CLASS_NAME, "alert-danger")

        assert alert_danger.text == ACTIVATION_LINK_ERROR
        assert User.objects.filter(username=username, email=email, is_active=False).exists()

    @pytest.mark.parametrize(
        "email, username, password, is_password_confirmed, field, accepted_messages", [
            (get_random_email(), get_random_username(), "", True, "form .form-floating:nth-child(4) .form-control", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_email(), "", get_valid_password(), True, "form .form-floating:nth-child(3) .form-control", [WARNING_REQUIRED_FIELD_HTML]),
            ("", get_random_username(), get_valid_password(), True, "form .form-floating:nth-child(2) .form-control", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_string(random.randint(1, 10))+" "+get_random_email(), get_random_username(), get_valid_password(), True, "form .form-floating:nth-child(2) .form-control", [WARNING_EMAIL_WITH_SPACE_HTML, WARNING_REQUIRED_EMAIL_FIREFOX_HTML]),
            (get_random_email(), get_random_string(random.randint(1, 10))+" "+get_random_username(), get_valid_password(), True, "form-error", [ERROR_SPACE_IN_USERNAME]),
            (get_random_email(), get_random_username(), get_too_short_password(), True, "form-error", [ERROR_LENGTH_PASSWORD]),
            (get_random_email(), get_random_username(), get_too_long_password(), True, "form-error", [ERROR_LENGTH_PASSWORD]),
            (get_random_email(), get_random_username(), get_password_without_letters(), True, "form-error", [ERROR_LETTER_PASSWORD]),
            (get_random_email(), get_random_username(), get_password_without_digits(), True, "form-error", [ERROR_DIGIT_PASSWORD]),
            (get_random_email(), get_random_username(), get_password_without_special_characters(), True, "form-error", [ERROR_SPECIAL_CHARACTER_PASSWORD]),
            (get_random_email(), get_random_username(), get_valid_password(), False, "form-error", [ERROR_NOT_CONFIRMED_PASSWORD])
        ]
    )
    @pytest.mark.django_db
    def test_signup_form_error(self, live_server, selenium_driver, email, username, password, is_password_confirmed, field, accepted_messages):
        selenium_driver.get(live_server.url + reverse("signup"))

        confirmation_password = password if is_password_confirmed else get_valid_password()

        submit_form_user(selenium_driver, email, username, password, confirmation_password)

        is_valid_message = False

        for message in accepted_messages:
            is_valid_message = is_valid_message or (get_form_error_message(selenium_driver, field) == message)

        assert is_valid_message
        assert not User.objects.filter(username=username, email=email).exists()
        assert not AppUser.objects.filter(user__username=username, user__email=email).exists()
        assert_menu(selenium_driver)

    @pytest.mark.parametrize(
        "is_repeated_email, is_repeated_username", [
            (True, True),
            (True, False),
            (False, True)
        ]
    )
    @pytest.mark.django_db
    def test_signup_form_error_not_available_credentials(self, live_server, selenium_driver, account, is_repeated_email, is_repeated_username):
        user, _ = account()[0]
        selenium_driver.get(live_server.url + reverse("signup"))

        password = get_valid_password()

        email = user.email if is_repeated_email else get_random_email()
        username = user.username if is_repeated_username else get_random_username()

        submit_form_user(selenium_driver, email, username, password, password)

        form_errors = selenium_driver.find_elements(By.CLASS_NAME, "form-error")
        nb_errors = 0

        if is_repeated_email:
            assert form_errors[nb_errors].text == ERROR_NOT_AVAILABLE_EMAIL
            nb_errors += 1

        if is_repeated_username:
            assert form_errors[nb_errors].text == ERROR_NOT_AVAILABLE_USERNAME

        # Verifies if there is a user other than the fixture user with the specified credentials
        assert not User.objects.filter(username=username, email=email).filter(~Q(id=user.id)).exists()
        assert not AppUser.objects.filter(user__username=username, user__email=email).filter(~Q(user__id=user.id)).exists()
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_activate_account_after_signup_via_api(self, live_server, api_client, selenium_driver):
        url = reverse("user-api")

        payload = {
            "email": get_random_email(),
            "username": get_random_username(),
            "password": get_valid_password()
        }

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=payload["username"], email=payload["email"], is_active=False).exists()

        activation_link = "http://" + mail.outbox[0].body.split("http://")[1]
        activation_link = activation_link.replace("http://testserver", live_server.url)

        selenium_driver.get(activation_link)

        alert_success = selenium_driver.find_element(By.CLASS_NAME, "alert-success")

        assert alert_success.text == SUCCESSFUL_ACTIVATION
        assert User.objects.filter(username=payload["username"], email=payload["email"], is_active=True).exists()
