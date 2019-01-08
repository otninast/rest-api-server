from django.contrib import admin

from rest_api_app import models


admin.site.register(models.MenuName)
admin.site.register(models.TrainingProgram)
admin.site.register(models.TrainingMenu)
admin.site.register(models.ResultTime)
admin.site.register(models.LapTime)
admin.site.register(models.ImageTest)
admin.site.register(models.Profile)
