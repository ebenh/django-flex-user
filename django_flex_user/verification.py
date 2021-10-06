from django.urls import reverse
from django.contrib.auth import get_user_model

from social_core.pipeline.partial import partial
from social_core.exceptions import InvalidEmail

UserModel = get_user_model()


def email_validation_link(strategy, backend, code, partial_token):
    """
    Our email verification function for social-auth-app-django. It's called by the mail_validation partial pipeline
    function to send verification emails.

    See SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION.

    :param strategy:
    :param backend:
    :param code:
    :param partial_token:
    :return:
    """
    url_prefix = strategy.build_absolute_uri(
        reverse('social:complete', args=(backend.name,))
    )

    url_postfix = f'?verification_code={code.code}&partial_token={partial_token}'

    url = f'{url_prefix}{url_postfix}'

    print(url)


@partial
def mail_validation(backend, details, is_new=False, *args, **kwargs):
    """
    Our email address validation pipeline function for social-auth-app-django. It's identical to
    social_core.pipeline.mail.mail_validation except in the following ways:

    - An email address needs to be validated only if the social account isn't yet associated with a user (i.e. is_new is
    True) and there is an existing user already associated with the email address
    - The email address to be validated is returned in the query string of the redirect URL as well as being stored in
    the session

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
                      ((is_new and UserModel.objects.filter(email__iexact=details['email'])) or backend.setting(
                          'PASSWORDLESS', False))
    # todo: call userModel._default_manager.normalize_email() on input email before searching db?

    if requires_validation and send_validation:
        data = backend.strategy.request_data()
        if 'verification_code' in data:
            backend.strategy.session_pop('email_validation_address')
            if not backend.strategy.validate_email(details['email'],
                                                   data['verification_code']):
                raise InvalidEmail(backend)
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
