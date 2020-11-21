from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from friendship.exceptions import AlreadyFriendsError
from friendship.models import Friend, FriendshipRequest
from main.forms import AddFriend, AddRequest, FulfillForm, ContactForm
from main.models import ItemRequest, Fulfillment
from users.models import Account
from django.db.models import Q
from django.contrib import messages
from datetime import datetime
from django.core.mail import EmailMessage
from django.core.exceptions import PermissionDenied


def home(request):
    if request.user.is_authenticated:
        return redirect("/feed")
    else:
        return render(request, 'main/home.html', {})


@login_required(login_url="/login")
def feed(request):
    all_friends = []
    friends = Friend.objects.filter(Q(to_user=request.user) | Q(from_user=request.user))

    for friend in friends:
        if request.user == friend.to_user:
            all_friends.append(Account.objects.get(id=friend.from_user_id))

    count = 0
    for f in all_friends:
        count += f.itemrequest.all().count()
        if count > 0:
            break

    empty = (count == 0)

    if request.method == "POST":
        for friend in all_friends:
            for item in friend.itemrequest.all():
                if request.POST.get("fulfill") == "i" + str(item.id):
                    form = FulfillForm(request.POST)
                    if form.is_valid():
                        req_user = friend
                        ff_user = request.user
                        name = item.name
                        amnt = form.cleaned_data["amount"]
                        f = Fulfillment(request_user=req_user, fulfill_user=ff_user, name=name, amount=amnt, is_paid=False)
                        f.save()

                        item.delete()

                        messages.success(request, "You have fulfilled the item: " + item.name + " for $" + str(f.amount) + ".")
                        return HttpResponseRedirect("/feed")

    form = FulfillForm()
    return render(request, 'main/feed.html', {"all_friends": all_friends, "empty": empty, "form": form})


@login_required(login_url="/login")
def friends(request):
    if request.method == "POST":
        if request.POST.get("add_friend"):
            add_form = AddFriend(request.POST)

            if add_form.is_valid():
                target_email = add_form.cleaned_data["email"]
                try:
                    target_user = Account.objects.get(email=target_email)
                except Account.DoesNotExist:
                    messages.error(request, "There is no user with that email address!")
                    return HttpResponseRedirect("/friends")

                try:
                    Friend.objects.add_friend(request.user, target_user)
                except AlreadyFriendsError:
                    messages.error(request, "You are already friends!")
                    return HttpResponseRedirect("/friends")
                messages.success(request, "You have sent a friend request to: " + target_user.email + ".")
                return HttpResponseRedirect("/friends")
        elif request.POST.get("unfriend"):
            for friend in Friend.objects.select_related("from_user", "to_user").filter(from_user=request.user).all():
                if request.POST.get("unfriend") == "f" + str(friend.id):
                    Friend.objects.remove_friend(request.user, friend.to_user)
                    messages.success(request, "Remove friend: " + friend.to_user.name + ".")
                    return HttpResponseRedirect("/friends")
        else:
            for request in FriendshipRequest.objects.filter(Q(from_user=request.user) | Q(to_user=request.user)):
                if request.POST.get("r" + str(request.id)) == "accept":
                    request.accept()
                    messages.success(request, "You are now friends with: " + request.from_user.name + ".")
                    return HttpResponseRedirect("/friends")
                elif request.POST.get("r" + str(request.id)) == "decline":
                    request.delete()
                    messages.success(request, "You have rejected the friend request from: " + request.from_user.name + ".")
                    return HttpResponseRedirect("/friends")
                elif request.POST.get("r" + str(request.id)) == "cancel":
                    request.cancel()
                    messages.success(request, "You have cancelled the friend request to: " + request.to_user.name + ".")
                    return HttpResponseRedirect("/friends")

    add_form = AddFriend()
    incoming_requests = FriendshipRequest.objects.filter(to_user=request.user)
    outgoing_requests = FriendshipRequest.objects.filter(from_user=request.user)
    all_friends = Friend.objects.select_related("from_user", "to_user").filter(from_user=request.user).all()

    return render(request, 'main/friends.html', {"add_form": add_form, "incoming_requests": incoming_requests, "outgoing_requests": outgoing_requests, "all_friends": all_friends})


@login_required(login_url="/login")
def requests(request):
    if request.method == "POST":
        if request.POST.get("add_request"):
            form = AddRequest(request.POST)

            if form.is_valid():
                name = form.cleaned_data["name"]
                desc = form.cleaned_data["description"]

                req = ItemRequest(name=name, description=desc)
                req.save()
                request.user.itemrequest.add(req)

                messages.success(request, "Successfully added a request for: " + req.name + ".")
                return HttpResponseRedirect("/requests")
        else:
            for item_req in request.user.itemrequest.all():
                if request.POST.get("r" + str(item_req.id)) == "cancel":
                    item_req.delete()
                    messages.success(request, "Successfully deleted your request for: " + item_req.name + ".")
                    return HttpResponseRedirect("/requests")

    form = AddRequest()
    all_requests = request.user.itemrequest.all()

    return render(request, 'main/requests.html', {"form": form, "requests": all_requests})


@login_required(login_url="/login")
def edit_request(request, id=None):
    if id:
        req = ItemRequest.objects.get(id=id)
        if req.user != request.user:
            raise PermissionDenied()
    else:
        req = None

    form = AddRequest(request.POST or None, instance=req)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponseRedirect("/requests")

    return render(request, 'main/editrequest.html', {"form": form})


@login_required(login_url="/login")
def reimbursements(request):
    if request.method == "POST":
        for item in Fulfillment.objects.filter(fulfill_user=request.user, is_paid=False):
            if request.POST.get("i" + str(item.id)) == "payed":
                item.is_paid = True
                item.date_completed = datetime.now()
                item.save()

                messages.success(request, "You have marked the item: " + item.name + " as paid by " + item.request_user.name + " .")
                return HttpResponseRedirect("/reimbursements")

    to_pay = Fulfillment.objects.filter(request_user=request.user, is_paid=False)
    to_be_paid = Fulfillment.objects.filter(fulfill_user=request.user, is_paid=False)

    return render(request, 'main/reimbursements.html', {"to_pay": to_pay, "to_be_paid": to_be_paid})


@login_required(login_url="/login")
def history(request):
    items_requested = Fulfillment.objects.filter(request_user=request.user, is_paid=True)
    items_bought = Fulfillment.objects.filter(fulfill_user=request.user, is_paid=True)

    return render(request, 'main/history.html', {"items_requested": items_requested, "items_bought": items_bought})


def terms(request):
    return render(request, 'main/termsofservice.html', {})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = 'ErrandsForMe Contact Submission - ' + form.cleaned_data['subject']
            message = render_to_string('main/contact_email.html', {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'subject': form.cleaned_data['subject'],
                'message': form.cleaned_data['message']
            })

            mail = EmailMessage(subject, message, 'ErrandsForMe <noreply@errandsfor.me>', ['contact@errandsfor.me'], headers={"Reply-To": str(form.cleaned_data['email'])})
            mail.send()

            messages.success(request, "Your message has been sent.")
            return HttpResponseRedirect("/contact")
        else:
            messages.error(request, "One ore more fields are invalid.")
            return HttpResponseRedirect("/contact")

    if request.user.is_authenticated:
        form = ContactForm(initial={'name': request.user.name, 'email': request.user.email})
    else:
        form = ContactForm()

    return render(request, 'main/contact.html', {"form": form})


def privacy_policy(request):
    return render(request, 'main/privacypolicy.html', {})


def about(request):
    return render(request, 'main/about.html', {})


def handler_404(request, exception):
    return render(request, 'main/404.html', status=404)


def handler_403(request, exception):
    return render(request, 'main/403.html', status=403)


def handler_500(request):
    return render(request,  'main/500.html', status=500)
