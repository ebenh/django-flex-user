from .forms import (OTPTokensSearchForm, VerifyOTPForm, SignUpWithUsernameForm, SignUpWithEmailForm,
                    SignUpWithPhoneForm, UserForm)
from django.shortcuts import render
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from django_flex_user.models import EmailToken, PhoneToken
from django_flex_user.validators import FlexUserUnicodeUsernameValidator
from django_flex_user.forms import FlexUserAuthenticationForm

UserModel = get_user_model()


def index(request):
    return render(request, 'test_project/index.html')


def sign_up(request):
    return render(request, 'test_project/sign_up/index.html')


def sign_up_username(request):
    if request.method == 'POST':
        form = SignUpWithUsernameForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django_flex_user.backends.FlexUserModelBackend')
            return HttpResponseRedirect(reverse('index'))
    else:
        form = SignUpWithUsernameForm()

    return render(
        request,
        'test_project/sign_up/username.html',
        {'form': form}
    )


def sign_up_email(request):
    if request.method == 'POST':
        form = SignUpWithEmailForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django_flex_user.backends.FlexUserModelBackend')
            return HttpResponseRedirect(reverse('index'))
    else:
        form = SignUpWithEmailForm()

    return render(
        request,
        'test_project/sign_up/email.html',
        {'form': form}
    )


def sign_up_phone(request):
    if request.method == 'POST':
        form = SignUpWithPhoneForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django_flex_user.backends.FlexUserModelBackend')
            return HttpResponseRedirect(reverse('index'))
    else:
        form = SignUpWithPhoneForm()

    return render(
        request,
        'test_project/sign_up/phone.html',
        {'form': form}
    )


def sign_in(request):
    if request.method == 'POST':
        form = FlexUserAuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
    else:
        form = FlexUserAuthenticationForm()

    return render(
        request,
        'test_project/sign_in.html',
        {'form': form}
    )


def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def account(request):
    return render(
        request,
        'test_project/account/index.html'
    )


@login_required()
def user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserForm(instance=request.user)

    email_token = EmailToken.objects.filter(user=request.user).first()
    phone_token = PhoneToken.objects.filter(user=request.user).first()

    return render(
        request,
        'test_project/account/user.html',
        {
            'form': form,
            'email_token': email_token,
            'phone_token': phone_token
        }
    )


@login_required()
def password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('sign-in'))
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        'test_project/account/password.html',
        {'form': form}
    )


def verify_user(request, token_type, token_id, password=None):
    try:
        if token_type == 'email':
            otp_token = EmailToken.objects.get(id=token_id)
        elif token_type == 'phone':
            otp_token = PhoneToken.objects.get(id=token_id)
        else:
            raise Http404
    except (EmailToken.DoesNotExist, PhoneToken.DoesNotExist):
        raise Http404

    if request.method == 'POST':
        form = VerifyOTPForm(otp_token, request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('user'))
    else:
        if password:
            form = VerifyOTPForm(otp_token, data={'password': password})
            if form.is_valid():
                return HttpResponseRedirect(reverse('user'))
        else:
            form = VerifyOTPForm()
            otp_token.generate_password()

    return render(
        request,
        'test_project/forgot_password/verify.html',
        {
            'form': form,
            'otp_token': otp_token
        }
    )


def forgot_password(request):
    search_results_email_tokens = None
    search_results_phone_tokens = None

    if request.method == 'POST':
        form = OTPTokensSearchForm(request.POST)
        if form.is_valid():
            user_identifier = form.cleaned_data['user_identifier']

            q = {}
            try:
                # See if value is a username
                username_validator = FlexUserUnicodeUsernameValidator()
                username_validator(user_identifier)
            except ValidationError:
                # See if value is an email address or phone number
                if '@' in user_identifier:
                    q = {'user__email': UserModel.objects.normalize_email(user_identifier)}
                else:
                    q = {'user__phone': user_identifier}
            else:
                q = {'user__username': UserModel.normalize_username(user_identifier)}

            search_results_email_tokens = EmailToken.objects.filter(**q)
            search_results_phone_tokens = PhoneToken.objects.filter(**q)
    else:
        form = OTPTokensSearchForm()

    return render(
        request,
        'test_project/forgot_password/index.html',
        {
            'form': form,
            'search_results_email_tokens': search_results_email_tokens,
            'search_results_phone_tokens': search_results_phone_tokens
        }
    )


def forgot_password_verify(request, token_type, token_id, password=None):
    try:
        if token_type == 'email':
            otp_token = EmailToken.objects.get(id=token_id)
        elif token_type == 'phone':
            otp_token = PhoneToken.objects.get(id=token_id)
        else:
            raise Http404
    except (EmailToken.DoesNotExist, PhoneToken.DoesNotExist):
        raise Http404

    if request.method == 'POST':
        form = VerifyOTPForm(otp_token, request.POST)
        if form.is_valid():
            auth_token = default_token_generator.make_token(otp_token.user)
            request.session['auth_token'] = auth_token
            return HttpResponseRedirect(reverse('password-reset', args=(otp_token.user.id,)))
    else:
        if password:
            form = VerifyOTPForm(otp_token, data={'password': password})
            if form.is_valid():
                auth_token = default_token_generator.make_token(otp_token.user)
                request.session['auth_token'] = auth_token
                return HttpResponseRedirect(reverse('password-reset', args=(otp_token.user.id,)))
        else:
            form = VerifyOTPForm()
            otp_token.generate_password()

    return render(
        request,
        'test_project/forgot_password/verify.html',
        {
            'form': form,
            'otp_token': otp_token
        }
    )


def password_reset(request, pk):
    user = get_object_or_404(UserModel, pk=pk)
    auth_token = request.session.get('auth_token')
    if not default_token_generator.check_token(user, auth_token):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('sign-in'))
    else:
        form = SetPasswordForm(user)

    return render(
        request,
        'test_project/forgot_password/password_reset.html',
        {'form': form}
    )
