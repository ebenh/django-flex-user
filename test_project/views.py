from .forms import OTPTokensSearchForm
from django.shortcuts import render
from django.contrib.auth import get_user_model

from django_flex_user.models import EmailToken, PhoneToken
from django_flex_user.validators import FlexUserUnicodeUsernameValidator

UserModel = get_user_model()


def index(request):
    return render(request, 'test_project/index.html')


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
