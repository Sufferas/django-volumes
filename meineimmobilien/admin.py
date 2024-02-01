from django.contrib import admin

from .models import Project,Image, Imagethumbnail, Dokumente, Dokumentethumbnail

# Register your models here.
admin.site.register(Project)
admin.site.register(Image)
admin.site.register(Imagethumbnail)
admin.site.register(Dokumente)
admin.site.register(Dokumentethumbnail)