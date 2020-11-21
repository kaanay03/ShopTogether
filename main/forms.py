from django import forms

from main.models import ItemRequest


class AddFriend(forms.Form):
    email = forms.EmailField(label="Email: ", required=True)


class AddRequest(forms.ModelForm):
    name = forms.CharField(label="Item Name: ", max_length=40)
    description = forms.CharField(label="Item Description/Notes: ", max_length=500, widget=forms.Textarea)

    class Meta():
        model = ItemRequest
        fields = ["name", "description"]


class FulfillForm(forms.Form):
    amount = forms.DecimalField(label="Amount Paid: ", decimal_places=2, max_digits=6, widget=forms.NumberInput(attrs={'placeholder': 'Amount Paid ($)'}))


class ContactForm(forms.Form):
    name = forms.CharField(label="Name", max_length=40, required=True)
    email = forms.EmailField(label="Email", required=True)
    subject = forms.CharField(max_length=70)
    message = forms.CharField(label="Message", max_length=1000, widget=forms.Textarea)