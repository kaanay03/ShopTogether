from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path("", views.home, name="Home"),
    path("feed/", views.feed, name="Feed"),
    path("friends/", views.friends, name="Friends"),
    path("requests/", views.requests, name="Requests"),
    # url(r'^requests/edit/(?P<id>\d+)/$', views.edit_request, {}, 'req_edit'),
    path("requests/edit/<str:id>", views.edit_request, {}, "Edit Request"),
    path("reimbursements/", views.reimbursements, name="Reimbursements"),
    path("history/", views.history, name="History"),
    path("terms-of-service/", views.terms, name="Terms of Service"),
    path("contact/", views.contact, name="Contact"),
    path("privacy-policy", views.privacy_policy, name="Privacy Policy"),
    path("about/", views.about, name="About")
]