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
