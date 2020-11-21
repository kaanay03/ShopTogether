from django.utils.safestring import mark_safe

from .models import Account
from .models import Profile
from social_django.models import UserSocialAuth
from django.db import IntegrityError
from django.contrib import messages


def create_user(request, response, user=None, *args, **kwargs):
    if not user:
        acc = Account(name=response['name'], email=response['email'])
        profile = Profile(user=acc, email_confirmed=True)

        try:
            acc.save()
            social_auth = UserSocialAuth(user=acc, provider='facebook', uid=response['id'])
            social_auth.save()
        except IntegrityError:
            messages.warning(request, mark_safe("An account with your Facebook email address already exists. <br/> Contact us if this is a mistake or you would like to request for your account to be deleted."))

