from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from django_otp.plugins.otp_email.models import EmailDevice

from phonenumber_field.modelfields import PhoneNumberField

from dirtyfields import DirtyFieldsMixin

from .validators import SPUnicodeUsernameValidator

from .fields import CICharField


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

    def _create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        user = self.model(username=username, email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, phone_number, password, **extra_fields)

    def create_superuser(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, phone_number, password, **extra_fields)

    def get_by_natural_key(self, username=None, email=None, phone_number=None):
        if username is None and email is None and phone_number is None:
            raise ValueError('You must supply at least one of username, email or phone number')

        q = {}
        if username is not None:
            q.update({'username': username})
        if email is not None:
            q.update({'email': email})
        if phone_number is not None:
            q.update({'phone_number': phone_number})

        return self.get(**q)


class SPUser(AbstractBaseUser, PermissionsMixin, DirtyFieldsMixin):
    """
    Our implementation django.contrib.auth.models.User.

    This user model is designed to give users the flexibility to sign up and sign in using their choice of username,
    email address or phone number.

    Our implementation is identical to django.contrib.auth.models.User except in the following ways:

        username field sets null=True and blank=True.

        email field sets null=True and blank = True.

        phone_number field is introduced. It defines unique=True, null=True and blank=True.

        first_name and last_name fields are omitted.

        For each of username, email and phone_number we set blank = True to preserve the ordinary functioning of the
        admin site. Setting blank = True on model fields results in form fields which have required = False set,
        thereby enabling users to supply any subset of username, email and phone_number when configuring a user on the
        admin site. Furthermore, when null = True and blank = True are set together on model fields, the value of empty
        form fields are conveniently coerced to None. Unfortunately, setting blank = True on model fields has the
        undesirable consequence that empty string values will not by rejected by clean_fields/full_clean methods. To
        remedy this, we reject empty string values for username, email and phone_number in our clean method (see below).

        clean method:
            - Ensures that at least one of username, email or phone_number is defined for the user.
            - Ensures that none of username, email and phone_number are equal to the empty string. We must do this
            because we set blank = True for each of these fields (see above).
            - Normalizes email in addition to username.

        get_username method returns one of username, email, phone_number or id. This method evaluates each of these
        fields in order and returns the first truthy value.

        natural_key method returns a tuple of username, email and phone_number.

        We place the following restrictions on username, email and phone_number:
            - It shouldn't be possible to interpret username as an email address or phone number
            - It shouldn't be possible to interpret email as a username or phone number
            - It shouldn't be possible to interpret phone_number as a username or email address

        These restrictions are enforced by field validators which apply the constraints below:
            - username may not begin with "+" or a decimal number, nor may it contain "@"
            - email must contain "@"
            - phone_number must contain "+" and may not contain "@"

        These constraints make it possible to receive an unspecified user identifier and infer whether it is a username,
        email address or phone number.
    """

    username_validator = SPUnicodeUsernameValidator()

    email = models.EmailField(
        _('email address'),
        unique=True,
        null=True,  # new
        blank=True,  # new
        error_messages={
            'unique': _("A user with that email address already exists."),
        },
    )
    phone_number = PhoneNumberField(  # new
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

        if self.username is None and self.email is None and self.phone_number is None:
            errors[NON_FIELD_ERRORS] = 'You must supply at least one of {username}, {email} or {phone_number}.'.format(
                username=self._meta.get_field('username').verbose_name,
                email=self._meta.get_field('email').verbose_name,
                phone_number=self._meta.get_field('phone_number').verbose_name
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

        if self.phone_number == '':
            errors['phone_number'] = 'This field may not be blank.'

        if errors:
            raise ValidationError(errors)

        # Normalize username and email
        self.username = self.normalize_username(self.username)
        self.email = SPUser.objects.normalize_email(self.email)

    def get_username(self):
        """Return the identifying username for this user"""
        return self.username or self.email or (str(self.phone_number) if self.phone_number else None) or str(self.id)

    def natural_key(self):
        return self.username, self.email, self.phone_number


@receiver(pre_save, sender=SPUser)
def my_pre__save_handler(sender, **kwargs):
    pass


@receiver(post_save, sender=SPUser)
def my_post_save_handler(sender, **kwargs):
    if kwargs['created']:
        EmailDevice.objects.create(name="default", user_id=kwargs['instance'].id, confirmed=False)
    if 'email' in kwargs['instance'].get_dirty_fields():
        email_device = EmailDevice.objects.get(user=kwargs['instance'], email=None)
        email_device.confirmed = False
        email_device.save(update_fields=['confirmed'])
