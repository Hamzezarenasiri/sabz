import time
from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from .. import factories
from ..functions import otp_generator

USER = get_user_model()
factory = APIRequestFactory()
request = factory.post('/notes/', {'title': 'new idea'}, format='json')


class VerificationAPITestCase(APITestCase):

    def setUp(self):
        self.phone_number = "09123456789"
        self.register_url = reverse("verification-register")
        self.verify_url = reverse('verification-verify')
        factories.UserFactory(phone_number=self.phone_number)

    def test_phone_registration_sends_message(self):
        data = {"phone_number": '09336958986', "first_name": 'Kazem', "last_name": 'Kazemi'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertContains(response, _('Authentication SMS sent'), status_code=201)
        self.assertEqual(response.status_code, 201)

    def test_verified_security_code(self):
        """
        Test to verify that a post call with valid security_code
        """
        data = {"phone_number": self.phone_number, 'name': "Jafar"}
        self.client.post(self.register_url, data, format='json')
        self.key = USER.objects.get(phone_number=self.phone_number).key
        data = {
            "phone_number": self.phone_number,
            "security_code": otp_generator(key=self.key)
        }
        response = self.client.post(self.verify_url, data, format='json')
        self.assertContains(response, _("Security code is valid."), status_code=200)

    def test_expired_or_invalid_security_code(self):
        """
        Test to verify that a post call with random invalid security_code then test with expired security _code
        """
        phone_number = '9123456789'
        data = {"phone_number": phone_number, "name": "Sepand"}
        self.client.post(self.register_url, data, format='json')
        self.key = USER.objects.get(phone_number=phone_number).key
        random_code = randint(10 ** (settings.SMS_VERIFY_CODE_LENGTH - 1),
                              10 ** settings.SMS_VERIFY_CODE_LENGTH - 1)
        data_fake_code = {
            "phone_number": self.phone_number,
            "security_code": random_code
        }
        response = self.client.post(self.verify_url, data_fake_code, format='json')
        self.assertContains(response, _("Security code is NOT valid or has expired."),
                            status_code=400, msg_prefix="message")
        data_fake_phone = {
            "phone_number": "09123456798",
            "security_code": otp_generator(key=self.key)
        }
        response = self.client.post(self.verify_url, data_fake_phone, format='json')
        self.assertContains(response, _("Security code is NOT valid or has expired."),
                            status_code=400, msg_prefix="message")

        data = {
            "phone_number": self.phone_number,
            "security_code": otp_generator(key=self.key)
        }
        time.sleep(2 * settings.OTP_INTERVAL)
        response = self.client.post(self.verify_url, data, format='json')
        self.assertContains(response, _("Security code is NOT valid or has expired."),
                            status_code=400, msg_prefix="message")

    def test_invalid_phone_number_and_invalid_security_code(self):
        """
        Test to verify that a post call with invalid phone_number in invalid security_code
        """
        random_code = randint(0, 10 ** (settings.SMS_VERIFY_CODE_LENGTH - 1) - 1)
        data_invalid = {
            "phone_number": '9712345478',
            "security_code": random_code
        }
        response = self.client.post(self.verify_url, data_invalid, format='json')
        self.assertContains(response, _("Enter a valid phone number."), status_code=400)
        self.assertContains(response, _(
            "Ensure this field has at least %d characters." % settings.SMS_VERIFY_CODE_LENGTH),
                            status_code=400)
        random_code = randint(10 ** settings.SMS_VERIFY_CODE_LENGTH,
                              10 ** (settings.SMS_VERIFY_CODE_LENGTH + 3))
        data_invalid = {
            "phone_number": '9712345478',
            "security_code": random_code
        }
        response = self.client.post(self.verify_url, data_invalid, format='json')
        self.assertContains(response, _("Enter a valid phone number."), status_code=400)
        self.assertContains(response, _(
            "Ensure this field has no more than %d characters." % settings.SMS_VERIFY_CODE_LENGTH),
                            status_code=400)

    def test_verify_other(self):
        response = self.client.get(self.verify_url)
        self.assertContains(response, 'Method \\"GET\\" not allowed.', status_code=405)

        response = self.client.get(self.register_url)
        self.assertContains(response, 'Method \\"GET\\" not allowed.', status_code=405)

    def test_register_by_valid_values(self):
        phone_number0 = '09123456788'
        phone_number_region = '+989123456788'
        phone_number_region_ = '989123456788'
        phone_number_ = '9123456788'
        self.assertEqual(USER.objects.count(), 1)
        data = {'phone_number': phone_number0, 'first_name': 'Fake NAme', 'last_name': 'Fake last NAme'}
        response = self.client.post(self.register_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = USER.objects.get(phone_number=phone_number0)
        self.assertEqual(user.phone_number, data['phone_number'])
        user = USER.objects.get(phone_number=phone_number_region_)
        self.assertEqual(user.phone_number, data['phone_number'])
        user = USER.objects.get(phone_number=phone_number_region)
        self.assertEqual(user.phone_number, data['phone_number'])
        user = USER.objects.get(phone_number=phone_number_)
        self.assertEqual(user.phone_number, data['phone_number'])
        self.assertEqual(user.first_name, data['first_name'])

    def test_register_by_valid_values_for_exist_user(self):
        phone_number0 = '09167076478'
        phone_number_ = '9167076478'
        old_name = 'FakeName'
        old_last_name = 'FakeName'
        USER.objects.create_user(phone_number0, first_name=old_name, last_name=old_last_name, )
        data = {'phone_number': phone_number_, 'first_name': 'Fa ke N Ame', 'last_name': 'Fa ke N Ame'}
        response = self.client.post(self.register_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = USER.objects.get(phone_number=phone_number0)
        self.assertEqual(user.phone_number, data['phone_number'])
        self.assertNotEqual(user.first_name, data['first_name'])

        self.assertEqual(user.first_name, old_name)

    def test_register_by_invalid_values(self):
        not_valid_phones = ['1', '12', '123456789', '0123456789', '98765432101',
                            '0989123456789',
                            '+09123456789',
                            '99167076478', 'aaaaaaaaaaaa', '911', '119', 'SOS', '96633212661', ]
        not_valid_names = ['a', 'ab', '',
                           'rwaresxwqgjdcajdbkasf'
                           '        llasmc,m.na'
                           '          kjfn;oakfa.fh f.kaslkx '
                           'afmax dnf,mabf jb kan kln fxaln ']
        for phone_number in not_valid_phones:
            for name in not_valid_names:
                data = {'phone_number': phone_number, 'first_name': name, 'last_name': name}
                response = self.client.post(self.register_url, data=data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(f'{_("Enter a valid phone number.")}', response.content.decode())
                f_name_len = len(data['first_name'])
                if f_name_len > 50:
                    self.assertIn(
                        '"first_name":["Ensure this field has no more than 50 characters."]',
                        response.content.decode())
                elif len(data['first_name']) == 0:
                    self.assertIn('"first_name":["This field may not be blank."]',
                                  response.content.decode())
                elif f_name_len < 50:
                    self.assertIn(
                        '"first_name":["Ensure this field has at least 3 characters."]',
                        response.content.decode())

        data = {'phone_number': None, 'first_name': ''}
        response = self.client.post(self.register_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('"first_name":["This field may not be blank."]',
                      response.content.decode())
        self.assertIn('"phone_number":["This field may not be null."]',
                      response.content.decode())

    class VerificationLoginAPIView(APITestCase):

        def setUp(self) -> None:
            self.register_url = reverse('v1:verification-login')
            self.phone_number = '09123456789'
            USER.objects.create_user(self.phone_number, name='FakeName', )

        def test_login_by_valid_values(self):
            self.assertEqual(USER.objects.count(), 1)
            data = {'phone_number': self.phone_number, }
            response = self.client.post(self.register_url, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_login_by_unregistered_phone_number(self):
            data = {'phone_number': '09123456777', }
            response = self.client.post(self.register_url, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('This phone number is not registered. Please register now',
                          response.content.decode())

        def test_login_by_invalid_values(self):
            not_valid_phones = ['1', '12', '123456789', '0123456789', '98765432101',
                                '0989123456789',
                                '+09123456789',
                                '99167076478', 'aaaaaaaaaaaa', '911', '119', 'SOS', '96633212661', ]
            for phone_number in not_valid_phones:
                data = {'phone_number': phone_number, }
                response = self.client.post(self.register_url, data=data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('"phone_number":["Enter a valid phone number."]',
                              response.content.decode())
            data = {'phone_number': None, }
            response = self.client.post(self.register_url, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('"phone_number":["This field may not be null."]',
                          response.content.decode())


class ProfileAPITestCase(APITestCase):

    def setUp(self):
        self.register_url = reverse("verification-register")
        self.verify_url = reverse('verification-verify')
        self.phone_number = "9123456589"
        data = {"phone_number": self.phone_number, "first_name": 'jeson', "last_name": 'jesoni'}
        self.client.post(self.register_url, data, format='json')
        self.key = USER.objects.get(phone_number=self.phone_number).key
        data = {
            "phone_number": self.phone_number,
            "security_code": otp_generator(key=self.key)
        }
        self.client.post(self.verify_url, data, format='json')
        self.profile_view_url = reverse("profile-view")

    def test_retrieve_profile(self):
        response = self.client.get(path=self.profile_view_url)
        self.assertContains(response, "first_name", )
