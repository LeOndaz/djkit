from django.db import models


class Human(models.Model):
    class Level(models.IntegerChoices):
        BEGINNER = 0
        INTERMEDIATE = 1
        ADVANCED = 2

    class MilitaryStatus(models.TextChoices):
        EXEMPTED = "exempted", "Exempted"
        SERVED = "served", "Served"
        POSTPONED = "postponed", "Postponed"

    name = models.CharField(max_length=128)
    level = models.IntegerField(choices=Level.choices)
    military_status = models.CharField(choices=MilitaryStatus.choices, max_length=128)
    email = models.EmailField()


class Pet(models.Model):
    name = models.CharField(max_length=256)
    human = models.ForeignKey(Human, on_delete=models.CASCADE, related_name="pets")


class Category(models.Model):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
