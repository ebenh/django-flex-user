import unicodedata
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from django_flex_user.forms import FlexUserAuthenticationForm
from django_flex_user.models.otp import EmailToken, PhoneToken

# Reference: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/

UserModel = get_user_model()


class FlexUserUsernameField(forms.CharField):
    """
    Re-implementation of django.contrib.auth.forms.UsernameField.

    It has been modified to accommodates null usernames because our custom user model allows them.
    """

    def to_python(self, value):
        # Original implementation:
        # return unicodedata.normalize('NFKC', super().to_python(value))
        # Our implementation:
        value = super().to_python(value)
        return unicodedata.normalize('NFKC', value) if isinstance(value, str) else value


class FlexUserCreationForm(UserCreationForm):
    """
    This class serves as the base class for the user creation form that is dynamically generated at runtime.
    """

    class Meta:
        """
        Here we shadow UserCreationForm.Meta so that we can redefine its field "field_classes". We do it this way
        because ModelAdmin doesn't provide any obvious way to specify our own value for "field_classes".

        The value of UserChangeForm.Meta.field_classes.username is not compatible with our custom user model and we do
        not want that value to be inherited by subclasses of this class.
        """
        field_classes = {'username': FlexUserUsernameField}


class FlexUserChangeForm(UserChangeForm):
    """
    This class serves as the base class for the user modification form that is dynamically generated at runtime.
    """

    class Meta:
        """
        The comment for FlexUserCreationForm.Meta applies here as well.
        """
        field_classes = {'username': FlexUserUsernameField}


class FlexUserAdmin(UserAdmin):
    # The fields to search when using the search widget on /admin/account/users/
    search_fields = ('username', 'email', 'phone')
    # The fields to display on /admin/account/users/
    list_display = ('username', 'email', 'phone', 'is_staff')
    # The fields to be displayed on the user creation form (/admin/account/user/add/)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )
    # The fields to be displayed on the user modification form (/admin/account/user/<int:user_id>/change/)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'phone', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    """
    The forms that are displayed on the admin site for user creation (/admin/account/user/add/) and user modification
    (/admin/account/user/<int:user_id>/change/) are programmatically generated by FlexUserAdmin based on the value of
    FlexUserAdmin.add_form and FlexUserAdmin.form respectively.

    To generate the form for creating users, FlexUserAdmin.get_form calls django.forms.models.modelform_factory which
    generates a new a class that extends the class specified in FlexUserAdmin.add_form. Furthermore, the newly
    generated class is assigned a nested Meta class that extends FlexUserAdmin.add_form.Meta. The resulting class is
    assigned the dynamically generated name "UserForm", which is a concatenation of FlexUserAdmin.model.__name__ and
    "Form".

    UserForm.Meta is assigned a "model" field which is assigned the value of FlexUserAdmin.model and a
    "fields" field which is assigned the value of FlexUserAdmin.add_fieldsets.
    
    The process for generating the form for modifying users is nearly identical. The difference being that
    django.forms.models.modelform_factory references FlexUserAdmin.form instead of FlexUserAdmin.add_form. The
    resulting class is still assigned the name "UserForm". Furthermore, the value of UserForm.Meta.fields is assigned
    to be FlexUserAdmin.fieldsets instead of FlexUserAdmin.add_fieldsets.
    """
    add_form = FlexUserCreationForm
    form = FlexUserChangeForm


# Register your models here.
admin.site.register(UserModel, FlexUserAdmin)
# admin.site.login_template = 'account/login.html'
admin.site.login_form = FlexUserAuthenticationForm


class EmailTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'email', 'verified', 'password', 'timeout', 'failure_count', 'expiration']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class PhoneTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'phone', 'verified', 'password', 'timeout', 'failure_count', 'expiration']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(EmailToken, EmailTokenAdmin)
admin.site.register(PhoneToken, PhoneTokenAdmin)
