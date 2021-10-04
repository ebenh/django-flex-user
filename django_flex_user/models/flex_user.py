from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from phonenumber_field.modelfields import PhoneNumberField
from dirtyfields import DirtyFieldsMixin

from django_flex_user.validators import FlexUserUnicodeUsernameValidator
from django_flex_user.fields import CICharField
from django_flex_user.models.otp import EmailToken, PhoneToken


# Reference: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
# Reference: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html

class FlexUserManager(BaseUserManager):
    """
    Our custom implementation of django.contrib.auth.models.UserManager.
    """

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize email by lowercasing and IDNA encoding its domain part.

        :param email:
        :return:
        """
        if email is None:
            return None

        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
            email = email_name + '@' + domain_part.lower().encode('idna').decode('ascii')
        except UnicodeError:
            pass
        except ValueError:
            pass
        return email

    def _create_user(self, username=None, email=None, phone=None, password=None, **extra_fields):
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, phone, password, **extra_fields)

    def create_superuser(self, username=None, email=None, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, phone, password, **extra_fields)

    def get_by_natural_key(self, username=None, email=None, phone=None):
        if username is None and email is None and phone is None:
            raise ValueError('You must supply at least one of username, email or phone number')

        q = {}
        if username is not None:
            q.update({'username': username})
        if email is not None:
            q.update({'email': email})
        if phone is not None:
            q.update({'phone': phone})

        return self.get(**q)


class FlexUser(AbstractBaseUser, PermissionsMixin, DirtyFieldsMixin):
    """
    Our implementation django.contrib.auth.models.User.

    This user model is designed to give users the flexibility to sign up and sign in using their choice of username,
    email address or phone number.

    Our implementation is identical to django.contrib.auth.models.User except in the following ways:

        username field sets null=True and blank=True.

        email field sets null=True and blank = True.

        phone field is introduced. It defines unique=True, null=True and blank=True.

        first_name and last_name fields are omitted.

        For each of username, email and phone we set blank = True to preserve the ordinary functioning of the
        admin site. Setting blank = True on model fields results in form fields which have required = False set,
        thereby enabling users to supply any subset of username, email and phone when configuring a user on the
        admin site. Furthermore, when null = True and blank = True are set together on model fields, the value of empty
        form fields are conveniently coerced to None. Unfortunately, setting blank = True on model fields has the
        undesirable consequence that empty string values will not by rejected by clean_fields/full_clean methods. To
        remedy this, we reject empty string values for username, email and phone in our clean method (see below).

        clean method:
            - Ensures that at least one of username, email or phone is defined for the user.
            - Ensures that none of username, email and phone are equal to the empty string. We must do this
            because we set blank = True for each of these fields (see above).
            - Normalizes email in addition to username.

        get_username method returns one of username, email, phone or id. This method evaluates each of these
        fields in order and returns the first truthy value.

        natural_key method returns a tuple of username, email and phone.

        We place the following restrictions on username, email and phone:
            - It shouldn't be possible to interpret username as an email address or phone number
            - It shouldn't be possible to interpret email as a username or phone number
            - It shouldn't be possible to interpret phone as a username or email address

        These restrictions are enforced by field validators which apply the constraints below:
            - username may not begin with "+" or a decimal number, nor may it contain "@"
            - email must contain "@"
            - phone must contain "+" and may not contain "@"

        These constraints make it possible to receive an unspecified user identifier and infer whether it is a username,
        email address or phone number.
    """

    username_validator = FlexUserUnicodeUsernameValidator()

    email = models.EmailField(
        _('email address'),
        unique=True,
        null=True,  # new
        blank=True,  # new
        error_messages={
            'unique': _("A user with that email address already exists."),
        },
    )
    phone = PhoneNumberField(  # new
        _('phone number'),
        unique=True,
        null=True,
        blank=True,
        error_messages={
            'unique': _("A user with that phone number already exists."),
        },
    )
    # username = models.CharField(
    #     _('username'),
    #     max_length=150,
    #     unique=True,
    #     null=True,  # new
    #     blank=True,  # new
    #     help_text=_('150 characters or fewer. Letters, digits and ./-/_ only.'),
    #     validators=[username_validator],
    #     error_messages={
    #         'unique': _("A user with that username already exists."),
    #     },
    # )
    username = CICharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,  # new
        blank=True,  # new
        help_text=_('150 characters or fewer. Letters, digits and ./-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # We remove these fields from our user model implementation
    # first_name = models.CharField(_('first name'), max_length=30, blank=True)
    # last_name = models.CharField(_('last name'), max_length=150, blank=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = FlexUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        errors = {}

        if self.username is None and self.email is None and self.phone is None:
            errors[NON_FIELD_ERRORS] = 'You must supply at least one of {username}, {email} or {phone}.'.format(
                username=self._meta.get_field('username').verbose_name,
                email=self._meta.get_field('email').verbose_name,
                phone=self._meta.get_field('phone').verbose_name
            )

        # For fields which have blank = False:
        # django.db.models.fields.Field.clean first executes django.db.models.fields.Field.validate which raises an
        # exception if the field contains a blank value. If an exception is raised, the subsequent call to
        # django.db.models.fields.Field.run_validators is not made.
        #
        # For fields which have blank = True:
        # django.db.models.base.Model.clean_fields executes django.db.models.fields.Field.clean for each of its fields.
        # However, it skips this call for fields which contain a blank value.
        #
        # Therefore, validators are not run for blank values no matter what. So we cannot depend on validators to reject
        # empty values.

        if self.username == '':
            errors['username'] = 'This field may not be blank.'

        if self.email == '':
            errors['email'] = 'This field may not be blank.'

        if self.phone == '':
            errors['phone'] = 'This field may not be blank.'

        if errors:
            raise ValidationError(errors)

        # Normalize username and email
        self.username = self.normalize_username(self.username)
        self.email = FlexUser.objects.normalize_email(self.email)

    def get_username(self):
        """Return the identifying username for this user"""
        return self.username or self.email or (str(self.phone) if self.phone else None) or str(self.id)

    def natural_key(self):
        return self.username, self.email, self.phone


@receiver(pre_save, sender=FlexUser)
def my_pre__save_handler(sender, **kwargs):
    pass


@receiver(post_save, sender=FlexUser)
def my_post_save_handler(sender, **kwargs):
    user = kwargs['instance']

    if kwargs['created']:
        if user.email is not None:
            EmailToken.objects.create(user_id=user.id, email=user.email)
        if user.phone is not None:
            PhoneToken.objects.create(user_id=user.id, phone=user.phone)
    else:
        dirty_fields = user.get_dirty_fields(verbose=True)

        if 'email' in dirty_fields:
            if dirty_fields['email']['current'] is None:
                # If the new value for email is None, delete the token if it exists
                EmailToken.objects.filter(user_id=user.id).delete()
            elif dirty_fields['email']['saved'] is None:
                # If the old value for email is None and its new value is not None, create a new token
                # todo: construct this instance manually?
                EmailToken.objects.create(user=user, email=dirty_fields['email']['current'])
            else:
                # Otherwise, update the existing token
                email_token = EmailToken.objects.get(user=user)
                email_token.email = user.email
                email_token.reset_password()
                email_token.save()
        if 'phone' in dirty_fields:
            if dirty_fields['phone']['current'] is None:
                # If the new value for phone is None, delete the token if it exists
                PhoneToken.objects.filter(user_id=user.id).delete()
            elif dirty_fields['phone']['saved'] is None:
                # If the old value for phone is None and its new value is not None, create a new token
                # todo: construct this instance manually?
                PhoneToken.objects.create(user=user, phone=dirty_fields['phone']['current'])
            else:
                # Otherwise, update the existing token
                phone_token = PhoneToken.objects.get(user=user)
                phone_token.phone = user.phone
                phone_token.reset_password()
                phone_token.save()
