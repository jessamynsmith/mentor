from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    reviewer = models.ForeignKey(Client, related_name='reviews')
    date = models.DateField()
    content = models.TextField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return '%s (%s)' % (self.reviewer.name, self.date)
