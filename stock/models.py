from django.db import models


class SearchDate(models.Model):
    search_date = models.DateField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.search_date)

