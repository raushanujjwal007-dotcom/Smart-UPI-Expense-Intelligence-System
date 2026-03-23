from django.db import models


class Transaction(models.Model):
    session_id = models.CharField(max_length=100)
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.FloatField()
    type = models.CharField(max_length=10) 
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)