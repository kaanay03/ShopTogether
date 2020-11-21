from django.db import models
from hashid_field import HashidField, HashidAutoField
from users.models import Account


class ItemRequest(models.Model):
    id = HashidAutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="itemrequest", null=True)
    name = models.CharField(max_length=40, null=False)
    description = models.CharField(max_length=500, null=True)


class Fulfillment(models.Model):
    id=HashidAutoField(primary_key=True)
    request_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="fulfill_request", null=True)
    fulfill_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="fulfilled", null=True)

    name = models.CharField(max_length=40, null=False, default="Unknown Item")
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    is_paid = models.BooleanField(default=False)

    date_completed = models.DateTimeField(null=True)

    def __str__(self):
        return "From " + self.fulfill_user.name + " to " + self.request_user.name + " ($" + str(self.amount) + ")."