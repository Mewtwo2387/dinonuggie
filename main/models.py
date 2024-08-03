from django.db import models

# Create your models here.
class Dinonuggies(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    count = models.IntegerField()
    last_claim = models.DateTimeField(blank=True, null=True)

