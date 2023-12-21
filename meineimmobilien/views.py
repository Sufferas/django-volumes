from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .forms import ImageForm, ProjectForm, DokumenteForm
from .models import Image, Project, Imagethumbnail, Dokumente

from PIL import Image as PILImage
import os
import io




def create_thumbnail(image_path, index , size=(195, 125)):
    with PILImage.open(image_path) as img:
        # Skalieren des Bildes, sodass die kleinere Seite der Zielgröße entspricht
        img.thumbnail((size[0] * 2, size[1] * 2), PILImage.Resampling.LANCZOS)

        # Bestimmen der Größe und des Ausschnitts
        width, height = img.size
        left = (width - size[0]) / 2
        top = (height - size[1]) / 2
        right = (width + size[0]) / 2
        bottom = (height + size[1]) / 2

        # Zuschneiden des Bildes, um das gewünschte Seitenverhältnis zu erreichen
        thumb = img.crop((left, top, right, bottom))

        # Erstellen des Pfades für den Thumbnail-Ordner und des Dateinamens
        dir_name = os.path.dirname(image_path)
        thumbnail_dir = os.path.join(dir_name, 'thumbnail')
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_path = os.path.join(thumbnail_dir, f"image_{index}_thumbnail.webp")

        thumb.save(thumbnail_path, 'WEBP')
        return thumbnail_path


def resize_image(image, target_size_kb=500, quality=80, step=5):
    """Reduziert die Bildgröße schrittweise, bis die Zielgröße erreicht ist."""
    img_byte_arr = io.BytesIO()
    while True:
        image.save(img_byte_arr, format='WEBP', quality=quality)
        if img_byte_arr.tell() <= target_size_kb * 1024 or quality <= 10:
            break
        quality -= step  # Reduzieren der Qualität in kleinen Schritten
        img_byte_arr.seek(0)
    img_byte_arr.seek(0)
    return img_byte_arr


def convert_to_webp(original_image_path, index):
    if original_image_path:
        with PILImage.open(original_image_path) as image:
            dir_name, _ = os.path.split(original_image_path)

            # Definieren Sie den neuen Pfad und das Format
            new_image_path = os.path.join(dir_name, f"image_{index}.webp")

            # Konvertieren und speichern des Bildes im WEBP-Format
            image.save(new_image_path, 'WEBP')

            # Löschen der Originaldatei
            os.remove(original_image_path)

            return new_image_path
    return None


# Create your views here.
def index(request):
    return render(request, "index.html")


def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        imageform = ImageForm(request.POST, request.FILES)  # Erstellen einer Instanz von ImageForm
        dokumente_form = DokumenteForm(request.POST, request.FILES)  # Erstellen einer Instanz von ImageForm

        if form.is_valid() and imageform.is_valid():
            project = form.save(commit=False)
            project.user = request.user

            # Verarbeiten des Hauptbildes und des Hauptbild-Thumbnails
            if 'image_main' in request.FILES:
                main_image = request.FILES['image_main']
                project.image_main = main_image
                project.save()

                # Konvertieren des Hauptbildes in WEBP und Umbenennen
                new_main_image_path = convert_to_webp(project.image_main.path, 0)  # Index 0 für das Hauptbild
                project.image_main = new_main_image_path
                project.save()

                # Optional: Thumbnail für das Hauptbild erstellen
                thumbnail_path = create_thumbnail(new_main_image_path, 0, size=(280, 196))  # Index 0 für das Hauptbild
                project.image_main_thumbnail = thumbnail_path
                project.save()

            files = imageform.cleaned_data['images']  # Zugriff auf die hochgeladenen Dateien
            for index, file in enumerate(files, start=1):
                image_instance = Image.objects.create(project=project, images=file)
                thumbnail_path = create_thumbnail(image_instance.images.path, index)
                Imagethumbnail.objects.create(project=project, images_thumbnail=thumbnail_path)
                new_image_path = convert_to_webp(image_instance.images.path, index)
                image_instance.images = new_image_path
                image_instance.save()

            for file in request.FILES.getlist('dokumente'):
                Dokumente.objects.create(project=project, dokumente=file)

            messages.success(request, "New Project Added")
            return HttpResponseRedirect("/admin")
        else:
            print(form.errors, imageform.errors)
    else:
        form = ProjectForm()
        imageform = ImageForm()

    return render(request, "create_project.html", {"form": form, "imageform": imageform})


def list_immos(request):
    immobilien = Project.objects.all()  # Holen Sie alle Immobilien aus der Datenbank
    return render(request, 'list_immos.html', {'immobilien': immobilien})