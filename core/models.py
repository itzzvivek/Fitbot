from django.db import models
from django.contrib.auth.models import User

choices = [
    {'basic': 'Basic'}, 
    {'premium': 'Premium'}, 
]

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    membership_type = models.CharField(max_length=50, choices=choices)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class Subscription(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.client.user.username} - {self.plan_name}'


class Attendance(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    check_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.client.user.username} - {self.check_in_time}'