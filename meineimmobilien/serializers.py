from rest_framework import serializers
from .models import Project, Image, Imagethumbnail, Dokumente, Dokumentethumbnail


class DynamicLanguageSerializer(serializers.ModelSerializer):
    description_preview = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'name', 'category', 'description_preview', 'image_main_thumbnail',
            'price', 'object_id', 'living_space', 'lot_size'
        ]

    def get_description_preview(self, obj):
        language = self.context['request'].query_params.get('label', 'de')
        description_attr = f'description_preview_{language}'
        description = getattr(obj, description_attr, None)
        return description


class ImageThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagethumbnail
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    thumbnail = ImageThumbnailSerializer(read_only=True)
    class Meta:
        model = Image
        fields = '__all__'


class DokumenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dokumente
        fields = '__all__'


class DokumenteThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dokumentethumbnail
        fields = '__all__'


class ProjectDetailSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, source='image_set', read_only=True)
    image_thumbnails = ImageThumbnailSerializer(many=True, source='imagethumbnail_set', read_only=True)
    dokumente = DokumenteSerializer(many=True, source='dokumente_set', read_only=True)
    dokumente_thumbnails = DokumenteThumbnailSerializer(many=True, source='dokumentethumbnail_set', read_only=True)

    def get_expose_url(self, instance, label):
        expose_field = getattr(instance, f'expose_{label}', None)
        if expose_field and hasattr(expose_field, 'url'):
            return self.context['request'].build_absolute_uri(expose_field.url)
        return None

    def get_expose_thumbnail_url(self, instance, label):
        expose_thumbnail_field = getattr(instance, f'expose_{label}_thumbnail', None)
        if expose_thumbnail_field and hasattr(expose_thumbnail_field, 'url'):
            return self.context['request'].build_absolute_uri(expose_thumbnail_field.url)
        return None

    def to_representation(self, instance):
        # Rufen Sie die Basisrepräsentation des Objekts ab
        representation = super(ProjectDetailSerializer, self).to_representation(instance)

        # Holen Sie das Sprachlabel aus dem Kontext
        label = self.context['request'].query_params.get('label', 'de')

        # Dynamische Anpassung der Felder basierend auf dem Sprachlabel
        representation['available_from'] = getattr(instance, f'available_from_{label}', '')
        representation['operating_costs'] = getattr(instance, f'operating_costs_{label}', '')
        representation['description_preview'] = getattr(instance, f'description_preview_{label}', '')
        representation['expose'] = self.get_expose_url(instance, label)
        representation['expose_thumbnail'] = self.get_expose_thumbnail_url(instance, label)
        representation['title'] = getattr(instance, f'title_{label}', '')
        representation['description'] = getattr(instance, f'description_{label}', '')
        representation['meta_description'] = getattr(instance, f'meta_description_{label}', '')
        representation['meta_keywords'] = getattr(instance, f'meta_keywords_{label}', '')

        return representation

    class Meta:
        model = Project
        fields = '__all__' # oder eine Liste spezifischer Felder