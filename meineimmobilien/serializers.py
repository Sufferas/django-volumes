from rest_framework import serializers
from .models import Project


class DynamicLanguageSerializer(serializers.ModelSerializer):
    description_preview = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'name', 'category', 'description_preview', 'image_main_thumbnail',
            'price', 'object_id'
        ]

    def get_description_preview(self, obj):
        language = self.context['request'].query_params.get('label', 'de')
        description_attr = f'description_preview_{language}'
        print(f"Sprache: {language}, Beschreibungsfeld: {description_attr}")
        description = getattr(obj, description_attr, None)
        print(f"Beschreibung: {description}")
        return description

