from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Review(models.Model):
    reviewer = models.ForeignKey(Client)
    date = models.DateField()
    content = models.TextField()

    def __str__(self):
        return '%s (%s)' % (self.name, self.date)
