from .forms import OTPTokensSearchForm, VerifyOTPForm
from django.shortcuts import render
from django.contrib.auth import get_user_model, login, logout
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from django_flex_user.models import EmailToken, PhoneToken
from django_flex_user.validators import FlexUserUnicodeUsernameValidator
from django_flex_user.forms import FlexUserAuthenticationForm

UserModel = get_user_model()


def index(request):
    return render(request, 'test_project/index.html')


def sign_up_method_selector(request):
    return render(request, 'test_project/sign_up_method_selector.html')


def sign_up_with_username(request):
    return render(request, 'test_project/sign_up_with_username.html')


def sign_up_with_email(request):
    return render(request, 'test_project/sign_up_with_email.html')


def sign_up_with_phone(request):
    return render(request, 'test_project/sign_up_with_phone.html')


def sign_in(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FlexUserAuthenticationForm(request, request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            login(request, form.get_user())
            return HttpResponseRedirect(reverse('index'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = FlexUserAuthenticationForm()

    return render(
        request,
        'test_project/sign_in.html',
        {'form': form}
    )


def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse(index))


def search_otp_tokens(request):
    search_results_email_tokens = None
    search_results_phone_tokens = None

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = OTPTokensSearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
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

            # return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = OTPTokensSearchForm()

    return render(
        request,
        'test_project/password-reset/search.html',
        {
            'form': form,
            'search_results_email_tokens': search_results_email_tokens,
            'search_results_phone_tokens': search_results_phone_tokens
        }
    )


def verify_otp(request, token_id, token_type):
    try:
        if token_type == 'email':
            otp_token = EmailToken.objects.get(id=token_id)
        elif token_type == 'phone':
            otp_token = PhoneToken.objects.get(id=token_id)
        else:
            raise Http404
    except (EmailToken.DoesNotExist, PhoneToken.DoesNotExist):
        raise Http404

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = VerifyOTPForm(otp_token, request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/accounts/password-reset/change-password/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = VerifyOTPForm()
        otp_token.generate_password()

    return render(
        request,
        'test_project/password-reset/verify.html',
        {'form': form}
    )


def change_password(request):
    return render(request, 'test_project/password-reset/change_password.html')
