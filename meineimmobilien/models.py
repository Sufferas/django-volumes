from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
import os




def project_directory_path(instance, filename, extra_path=''):
    # Erstellen Sie einen gültigen Dateipfad, indem Sie ungültige Zeichen aus dem Projektnamen entfernen
    # project_name = ''.join(e for e in instance.name if e.isalnum())
    if isinstance(instance, Project):
        project_name = ''.join(e for e in instance.name if e.isalnum())
        # Wenn instance ein Image-Objekt ist und eine Beziehung zu Project hat
    elif hasattr(instance, 'project'):
        project_name = ''.join(e for e in instance.project.name if e.isalnum())
    else:
        # Fallback, falls instance weder Project noch Image ist
        project_name = 'default'

    # Datei wird zu /properties/<project_name>/<filename> hochgeladen
    return os.path.join('properties', project_name, extra_path, filename)


def project_directory_path_main_image(instance, filename):
    return project_directory_path(instance, filename, extra_path='main_image')


def project_directory_path_images(instance, filename):
    return project_directory_path(instance, filename, extra_path='images')


def project_directory_path_expose(instance, filename):
    return project_directory_path(instance, filename, extra_path='expose')


def project_directory_path_dokumente(instance, filename):
    return project_directory_path(instance, filename, extra_path='dokumente')



class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)

    CATEGORY_CHOICES = (
        ('commercial_lot', _('Gewerbegrundstück')),
        ('lot', _('Grundstück')),
        ('house', _('Haus')),
        ('hotel', _('Hotel')),
        ('pension', _('Pension')),
        ('apartment', _('Wohnung')),
        ('income_house', _('Zinshaus')),
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    description_preview_de = models.TextField(null=True, blank=True)
    description_preview_en = models.TextField(null=True, blank=True)
    description_preview_ru = models.TextField(null=True, blank=True)

    image_main = models.ImageField(upload_to=project_directory_path_main_image)
    image_main_thumbnail = models.ImageField(upload_to=project_directory_path_main_image)

    expose_de = models.FileField(upload_to=project_directory_path_expose)
    expose_en = models.FileField(upload_to=project_directory_path_expose)
    expose_ru = models.FileField(upload_to=project_directory_path_expose)

    # Titles in 3 languages
    title_de = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)

    # Description in 3 languages
    description_de = RichTextField()
    description_en = RichTextField()
    description_ru = RichTextField()

    object_id = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    CONDITION_CHOICES = (
        ('very_good', _('Sehr gut')),
        ('good', _('Gut')),
        ('needs_renovation', _('Renovierungsbedürftig')),
        ('first_occupancy', _('Erstbezug')),
    )
    condition = models.CharField(
        max_length=100,
        choices=CONDITION_CHOICES,
        default='very_good',  # Du kannst hier den Standardwert auf den häufigsten Wert setzen
        blank=True
    )

    available_from_de = models.CharField(max_length=100, blank=True, default=_(""))
    available_from_en = models.CharField(max_length=100, blank=True, default=_(""))
    available_from_ru = models.CharField(max_length=100, blank=True, default=_(""))

    operating_costs_de = models.CharField(max_length=100, blank=True, default=_(""))  # Betriebskosten
    operating_costs_en = models.CharField(max_length=100, blank=True, default=_(""))  # Betriebskosten
    operating_costs_ru = models.CharField(max_length=100, blank=True, default=_(""))  # Betriebskosten
    living_space = models.DecimalField(max_digits=9, decimal_places=1, null=True, blank=True)  # Wohnfläche
    lot_size = models.DecimalField(max_digits=9, decimal_places=1, null=True, blank=True)  # Grundstückfläche
    has_basement = models.BooleanField(default=False)  # Keller
    rooms = models.IntegerField(null=True, blank=True)  # Zimmer
    bathrooms = models.IntegerField(null=True, blank=True)  # Badezimmer
    terraces = models.IntegerField(null=True, blank=True)  # Terrassen
    toilets = models.IntegerField(null=True, blank=True)  # WC

    HEATING_TYPE_CHOICES = (
        ('oil', _('Öl')),
        ('gas', _('Gas')),
        ('district_heating', _('Fernwärme')),
        ('heat_pump', _('Wärmepumpe')),
    )
    HEATING_SYSTEM_CHOICES = (
        ('underfloor_heating', _('Fußbodenheizung')),
        ('radiators', _('Heizkörper')),
        ('infrared', _('Infrarotheizung')),
    )

    heating_type = models.CharField(
        max_length=50,
        choices=HEATING_TYPE_CHOICES,
        blank=True,
        default='',  # Leer, bedeutet keine Auswahl getroffen
    )
    heating_system = models.CharField(
        max_length=50,
        choices=HEATING_SYSTEM_CHOICES,
        blank=True,
        default='',  # Leer, bedeutet keine Auswahl getroffen
    )

    PARKING_TYPE_CHOICES = [
        ('garage', _('Garage')),
        ('lift_garage', _('Liftgarage')),
        ('driveway', _('Einfahrt')),
        ('unknown', _('Nicht bekannt')),
    ]
    # Eine durch Kommas getrennte Liste von Werten
    # parking_type = models.CharField(max_length=100, blank=True, default=_(""))
    parking_garage = models.BooleanField(default=False)
    parking_liftgarage = models.BooleanField(default=False)
    parking_einfahrt = models.BooleanField(default=False)
    parking_nicht_bekannt = models.BooleanField(default=False)
    parking_anzahl = models.IntegerField(null=True, blank=True)  # WC
    hwb_value = models.CharField(max_length=100, blank=True, default=_(""))  # HWB-Wert
    hwb_class = models.CharField(max_length=100, blank=True, default=_(""))  # HWB-Klasse

    # Maps Data
    latitude = models.FloatField()
    longitude = models.FloatField()
    umkreis = models.BooleanField(default=False)


    meta_description_de = models.CharField(max_length=255, blank=True, default='')
    meta_keywords_de = models.CharField(max_length=155, blank=True, default='')

    # SEO Metadaten in Englisch
    meta_description_en = models.CharField(max_length=255, blank=True, default='')
    meta_keywords_en = models.CharField(max_length=155, blank=True, default='')

    # SEO Metadaten in Russisch
    meta_description_ru = models.CharField(max_length=255, blank=True, default='')
    meta_keywords_ru = models.CharField(max_length=155, blank=True, default='')

    # Counter for page views
    view_count = models.IntegerField(default=0)



    def __str__(self):
        return self.name


class Image(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, )
    images = models.ImageField(upload_to=project_directory_path_images)


class Imagethumbnail(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, )
    images_thumbnail = models.ImageField(upload_to=project_directory_path_images)


class Dokumente(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, )
    dokumente = models.FileField(upload_to=project_directory_path_dokumente)

