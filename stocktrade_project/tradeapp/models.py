from django.db import models
from django.conf import settings

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)

    def total_cost(self):
        return self.purchase_price * self.quantity
