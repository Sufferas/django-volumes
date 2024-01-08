from django import forms

from .models import Image, Project, Dokumente
from .validators import validate_image_extension


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['description_preview_de'].required = False  # Setzen Sie das Feld 'description' als optional
        self.fields['description_preview_en'].required = False  # Setzen Sie das Feld 'description' als optional
        self.fields['description_preview_ru'].required = False  # Setzen Sie das Feld 'description' als optional
        self.fields['expose_de'].required = False  # Setzen Sie das Feld 'description' als optional
        self.fields['expose_en'].required = False  # Setzen Sie das Feld 'description' als optional
        self.fields['expose_ru'].required = False
        self.fields['price'].required = False
        self.fields['condition'].required = False
        self.fields['available_from_de'].required = False
        self.fields['available_from_en'].required = False
        self.fields['available_from_ru'].required = False
        self.fields['operating_costs_de'].required = False
        self.fields['operating_costs_en'].required = False
        self.fields['operating_costs_ru'].required = False
        self.fields['living_space'].required = False
        self.fields['lot_size'].required = False
        self.fields['has_basement'].required = False
        self.fields['rooms'].required = False
        self.fields['bathrooms'].required = False
        self.fields['terraces'].required = False
        self.fields['toilets'].required = False
        self.fields['heating_type'].required = False
        self.fields['heating_system'].required = False
        self.fields['parking_type'].required = False
        self.fields['parking_garage'].required = False
        self.fields['parking_liftgarage'].required = False
        self.fields['parking_einfahrt'].required = False
        self.fields['parking_nicht_bekannt'].required = False
        self.fields['parking_anzahl'].required = False
        self.fields['hwb_value'].required = False
        self.fields['hwb_class'].required = False

        self.fields['meta_description_de'].required = False
        self.fields['meta_description_en'].required = False
        self.fields['meta_description_ru'].required = False

        self.fields['meta_keywords_de'].required = False
        self.fields['meta_keywords_en'].required = False
        self.fields['meta_keywords_ru'].required = False

    parking_type = forms.MultipleChoiceField(choices=Project.PARKING_TYPE_CHOICES,
                                             widget=forms.CheckboxSelectMultiple)



    class Meta:
        model = Project
        fields = [
            "name",
            "category",
            "is_active",
            'image_main',
            'description_preview_de', 'description_preview_en', 'description_preview_ru',
            "expose_de", "expose_en", "expose_ru",
            "title_de", "title_en", "title_ru",
            "description_de", "description_en", "description_ru",
            "object_id",
            "price",
            "condition",
            "available_from_de", "available_from_en", "available_from_ru",
            "operating_costs_de", "operating_costs_en", "operating_costs_ru",
            "living_space", "lot_size",
            "has_basement",
            "rooms", "bathrooms",
            "terraces",
            "toilets",
            "heating_type", "heating_system",
            "parking_garage", "parking_liftgarage", "parking_einfahrt", "parking_nicht_bekannt", "parking_anzahl",
            "hwb_value", "hwb_class",
            "latitude", "longitude", "umkreis",
            "meta_description_de", "meta_keywords_de",
            "meta_description_en", "meta_keywords_en",
            "meta_description_ru", "meta_keywords_ru",


        ]

    def clean_parking_type(self):
        return ','.join(self.cleaned_data['parking_type'])


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ImageForm(forms.ModelForm):
    images = MultipleFileField(label="Upload Images", required=False, validators=[validate_image_extension])  # Verwendung von MultipleFileField

    class Meta:
        model = Image
        fields = ("images",)


class DokumenteForm(forms.ModelForm):
    dokumente = MultipleFileField(label="Upload Dokumente", required=False, validators=[validate_image_extension])  # Verwendung von MultipleFileField

    class Meta:
        model = Dokumente
        fields = ("dokumente",)

