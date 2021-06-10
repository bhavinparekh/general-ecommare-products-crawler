from django.db import models
from jsonfield import JSONField


class Websites(models.Model):
    parent_website = models.CharField(max_length=250, default='')
    websites = models.CharField(max_length=250, default='')
    list_website = JSONField(null=True)

    def __str__(self):
        return self.parent_website


mylist = ['www.pqr.com/hitech/product',
          'www.def.com/lifestyle/data',
          'www.ghik.com/beauty/style',
          'www.klmnop.com/food/asian/spices'
          ]
