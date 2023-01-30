import base64
import io
import random
import string

from django.contrib import auth
from django.utils.crypto import get_random_string
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


def is_user_authenticated(client, user):
    """
    Verifies if the specified user is authenticated in the current session.

    :param client: Django client fixture
    :param user: instance of a user that we want to check that is authenticated
    :type user: User

    :return: boolean indicating if the specified user is authenticated
    """
    return auth.get_user(client).username == user.username


def get_basic_auth_header(username, password):
    credentials = base64.b64encode(f'{username}:{password}'.encode('utf-8'))
    return 'Basic {}'.format(credentials.decode('utf-8'))


def deserialize_data(data):
    """
    Deserialize the specified data payload into a dictionary.
    :param data: data to be deserialized

    :return: dictionary corresponding to the deserialized data payload.
    """
    json = JSONRenderer().render(data)
    stream = io.BytesIO(json)
    return JSONParser().parse(stream)


def is_model_objects_equal_to_dict_array(objects, dict_array, comparer):
    """
    Verifies if a dictionary array is equivalent to an array of objects using the specified comparer.

    :param objects: list of objects
    :type objects: list
    :param dict_array: list of dictionaries
    :type dict_array: list
    :param comparer: comparer object

    :return: boolean indicating if the list of objects and if the list of dictionaries are equivalent.
    """
    id_to_object = {}

    for obj in objects:
        id_to_object[obj.id] = obj

    for item in dict_array:
        obj = id_to_object.get(item.get("id"))

        if obj is None or not(comparer.are_equal(obj, item)):
            return False

        del id_to_object[item.get("id")]

    return True


def get_users(accounts):
    """
    Gets list of users associated with the specified list of accounts (an account here is a tuple with the user object
    and its corresponding password).
    :param accounts: list of tuples, each one containing a user object and its associated password
    :type accounts: list

    :return: list of users
    """
    users = []
    for user, password in accounts:
        users.append(user)

    return users


def get_valid_password():
    """
    Gets a random valid password. A valid password has a length between 8 and 30.

    :return: a random valid password
    """
    return password_factory(random.randint(8, 30), True, True, True)


def get_random_email():
    """
    Gets a random email address. A fake "@test.com" suffix is used.

    :return: a random email address
    """
    return get_random_string(random.randint(10, 20)) + "@test.com"


def get_random_username():
    """
    Gets a random username.

    :return: a random username
    """
    return get_random_string(random.randint(10, 20))


def get_too_short_password():
    """
    Gets a password with less than 8 characters, which is below the minimal length.

    :return: a too short password
    """
    return password_factory(random.randint(3, 7), True, True, True)


def get_too_long_password():
    """
    Gets a password with more than 30 characters, which is above the maximal length.

    :return: a too long password
    """
    return password_factory(random.randint(31, 50), True, True, True)


def get_password_without_letters():
    """
    Gets a random password without letters (alphabetic characters).

    :return: a random password without letters
    """
    return password_factory(random.randint(8, 30), False, True, True)


def get_password_without_digits():
    """
    Gets a random password without digits.

    :return: a random password without digits
    """
    return password_factory(random.randint(8, 30), True, False, True)


def get_password_without_special_characters():
    """
    Gets a random password without special characters.

    :return: a random password without special characters
    """
    return password_factory(random.randint(8, 30), True, True, False)


def password_factory(length, has_letters, has_digits, has_special_character):
    password = ""
    allowed_chars = ""

    if has_letters:
        allowed_chars += string.ascii_letters
        password += get_random_string(1, string.ascii_letters)

    if has_digits:
        allowed_chars += string.digits
        password +=  get_random_string(1, string.digits)

    if has_special_character:
        allowed_chars += string.punctuation
        password += get_random_string(1, string.punctuation)

    if length < len(password):
        return get_random_string(length, password)

    return password + get_random_string(length - len(password), allowed_chars)