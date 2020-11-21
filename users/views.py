from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from users.forms import RegisterForm, EditAccountForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from users.tokens import account_activation_token
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from users.models import Account
from users.models import Profile


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your ErrandsForMe Account'
            message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })

            user.email_user(subject, message, 'ErrandsForMe <noreply@errandsfor.me>')

            messages.success(request, "Success! Check your inbox to confirm your account.")

            return HttpResponseRedirect("/account/login")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {"form": form})


def activate_account(request, uidb64, token, *args, **kwargs):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    try:
        user.profile
    except Profile.DoesNotExist:
        Profile(user=user, email_confirmed=False)
        user.save()

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account have been activated!')
        return HttpResponseRedirect("/")
    else:
        messages.warning(request, 'The confirmation link is invalid!')
        return HttpResponseRedirect("/")


@login_required(login_url="/login")
def edit_account(request):
    if request.method == "POST":
        form = EditAccountForm(request.POST)
        if form.is_valid():
            request.user.name = form.cleaned_data['name']
            if request.user.email != form.cleaned_data['email']:
                request.user.email = form.cleaned_data['email']
                request.user.is_active = False
                try:
                    request.user.profile.email_confirmed = False
                except Profile.DoesNotExist:
                    Profile(user=request.user, email_confirmed=False)
                    request.user.save()

                current_site = get_current_site(request)
                subject = 'Confirm Email Change for ErrandsForMe Account'
                message = render_to_string('users/account_activation_email.html', {
                    'user': request.user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
                    'token': account_activation_token.make_token(request.user)
                })

                request.user.email_user(subject, message, 'ErrandsForMe <noreply@errandsfor.me>')

                messages.success(request, "Your account has been updated. Check your inbox to confirm your new email.")
                request.user.save()

                return HttpResponseRedirect("/account/login")
            else:
                messages.success(request, "Saved account information.")

            request.user.save()
            return HttpResponseRedirect("/")
        else:
            messages.error(request, "One or more inputs was invalid! Try again.")

    form = EditAccountForm(initial={'name': request.user.name, 'email': request.user.email})

    if request.user.facebook_connected():
        form.fields['email'].widget.attrs['disabled'] = True
        form.fields['email'].help_text = 'Your account is connected through Facebook.'

    return render(request, 'users/editaccount.html', {'form': form})
