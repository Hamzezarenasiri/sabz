import time

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..factories import UserFactory

USER = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.start = time.time()
        UserFactory.create_batch(10)

    def test_create_user_phone_number_successful(self):
        """
        Test creating a new user with a phone_number is successful
        """
        phone_number1 = '+989123456789'
        phone_number2 = '+989123456780'
        UserFactory.create(phone_number=phone_number2)
        USER.objects.create_user(phone_number=phone_number1, )
        self.assertEqual(USER.objects.get(phone_number=phone_number1).phone_number, phone_number1)
        self.assertEqual(USER.objects.get(phone_number=phone_number1).phone_number, phone_number1)
        self.assertFalse(USER.objects.get(phone_number=phone_number1).has_usable_password())
        self.assertTrue(USER.objects.get(phone_number=phone_number2).has_usable_password())
        self.assertTrue(USER.objects.get(phone_number=phone_number1).is_active)
        self.assertFalse(USER.objects.get(phone_number=phone_number1).is_staff)
        self.assertFalse(USER.objects.get(phone_number=phone_number1).is_superuser)

    def test_create_user_no_phone_number(self):
        """
        Test create new user with no phone number rises error
        """
        with self.assertRaises(TypeError):
            USER.objects.create_user(username='testuser123')
        with self.assertRaises(TypeError):
            USER.objects.create_user(username='testuser123', password='test1234')
        with self.assertRaises(TypeError):
            USER.objects.create_user(last_name='testuser123@yahoo.com', first_name='testuser123', password='test1234')
        with self.assertRaises(ValueError):
            USER.objects.create_user(phone_number='',
                                     password='test1234')

    def test_delete_user(self):
        """
        Test delete user
        """
        USER.objects.create_user(phone_number='09123465879', )
        self.assertTrue(USER.objects.get(phone_number='09123465879', ))
        USER.objects.get(phone_number='09123465879', ).delete()
        with self.assertRaises(USER.DoesNotExist):
            USER.objects.get(phone_number='09123465879', )
        USER.objects.filter(is_active=False).delete()
        self.assertEqual(USER.objects.filter(is_active=False).count(), 0)

    def tearDown(self):
        print("OK :) ---This Test Ran in %s seconds ---" % (time.time() - self.start))
