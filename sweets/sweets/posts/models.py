from django.db import models


# Create your models here.
class Couriers(models.Model):
    courier_id = models.IntegerField(auto_created=True, primary_key=True, unique=True)
    courier_type_ch = (
        ('foot', 'foot'),
        ('bike', 'bike'),
        ('car', 'car'),
    )
    courier_type = models.CharField(max_length=255, choices=courier_type_ch, blank=False)
    regions = models.CharField(max_length=255, blank=False)
    working_hours = models.CharField(max_length=255, blank=False)
    assign_time_current_for_delivery = models.DateTimeField(null=True)

    # class Meta:
    #     ordering = ['created']


class Orders(models.Model):
    order_id = models.IntegerField(auto_created=True, primary_key=True, unique=True)
    weight = models.FloatField(blank=False)
    region = models.IntegerField(blank=False)
    delivery_hours = models.CharField(max_length=255, blank=False)
    courier = models.ForeignKey(Couriers, on_delete=models.CASCADE, null=True, blank=True)
    complete = models.BooleanField(default=False)
    complete_time = models.DateTimeField(null=True)
    assign_time = models.DateTimeField(null=True)
