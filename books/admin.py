from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Author)
admin.site.register(models.Book)
admin.site.register(models.Bookshelf)
admin.site.register(models.Format)
admin.site.register(models.Language)
admin.site.register(models.Subject)



