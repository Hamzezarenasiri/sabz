import jwt
import pyotp
from django.conf import settings
from django.contrib.auth import get_user_model

USER = get_user_model()


def otp_generator(key):
    # Time based otp
    time_otp = pyotp.TOTP(key, interval=settings.OTP_INTERVAL,
                          digits=settings.SMS_VERIFY_CODE_LENGTH)
    return time_otp.now()


def send_sms_verify_code(phone_number):
    """

    :param phone_number:
    :return: status_code 200 :)
    """
    # Phone number must be international and start with a plus '+')
    user = USER.objects.get(phone_number=phone_number)
    key = user.key
    active_code_message = otp_generator(key=key)
    if settings.TESTING or settings.DEBUG and False:
        print('-----------------------',
              "active code message is",
              active_code_message,
              'for: ',
              phone_number,
              "-----------------------")
    else:
        # send_sms(receptor=phone_number, token=active_code_message)
        return active_code_message


def generate_session_token(phone_number):
    """
    Returns a unique random JWT token using Django's `SECRET_KEY`
    for identifying a particular device in subsequent calls.
    """
    data = {"device_%s_session_token" % phone_number: phone_number}
    return jwt.encode(data, settings.SECRET_KEY).decode()
