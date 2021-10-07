from django.contrib.auth import get_user_model

from social_core.pipeline.partial import partial
from social_core.exceptions import InvalidEmail

from django_flex_user.models import EmailToken

UserModel = get_user_model()


@partial
def mail_validation(backend, details, is_new=False, *args, **kwargs):
    """
    Our email address validation pipeline function for social-auth-app-django. It's identical to
    social_core.pipeline.mail.mail_validation except in the following ways:

    - An email address needs to be validated only if the social account isn't yet associated with a user (i.e. is_new is
    True) and there is an existing user already associated with that email address
    - The email address to be validated is returned in the query string of the redirect URL as well as being stored in
    the session
    - When the user verifies the email address, we update the corresponding django_flex_user.models.EmailToken
    object's verified field to True

    There exists a very unlikely race condition where in the seconds between checking whether an email address is
    associated with a user user and creating a new user with that email address, a different registrant can create an
    account using that same email address and subsequently have that account hijacked by the first registrant.

    :param backend:
    :param details:
    :param is_new:
    :param args:
    :param kwargs:
    :return:
    """
    requires_validation = backend.REQUIRES_EMAIL_VALIDATION or \
                          backend.setting('FORCE_EMAIL_VALIDATION', False)
    # send_validation = details.get('email') and \
    #                   (is_new or backend.setting('PASSWORDLESS', False))
    send_validation = details.get('email') and \
                      (
                              (is_new and UserModel.objects.filter(email__iexact=details['email']).exists()) or \
                              backend.setting('PASSWORDLESS', False)
                      )
    # todo: call userModel._default_manager.normalize_email() on input email before searching db?

    if requires_validation and send_validation:
        data = backend.strategy.request_data()
        if 'verification_code' in data:
            backend.strategy.session_pop('email_validation_address')
            if not backend.strategy.validate_email(details['email'],
                                                   data['verification_code']):
                raise InvalidEmail(backend)
            else:
                # Update django-flex-user's internal state
                user = UserModel.objects.get(email__iexact=details['email'])
                email_token = EmailToken.objects.get(user=user)
                email_token.verified = True
                email_token.save(update_fields=['verified'])
        else:
            current_partial = kwargs.get('current_partial')
            backend.strategy.send_email_validation(backend,
                                                   details['email'],
                                                   current_partial.token)
            backend.strategy.session_set('email_validation_address',
                                         details['email'])
            return backend.strategy.redirect(
                backend.strategy.setting('EMAIL_VALIDATION_URL') + f"?v={details['email']}"
            )
