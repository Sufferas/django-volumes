from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import ImageForm, ProjectForm, DokumenteForm
from .models import Image, Project, Imagethumbnail, Dokumente, project_directory_path_main_image

from PIL import Image as PILImage
import os
import io
import shutil
from os.path import splitext
import re

import fitz  # PyMuPDF
from django.contrib.auth.decorators import login_required


def create_pdf_thumbnail(pdf_path):
    # Öffne das PDF und greife auf die erste Seite zu
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap()

    # Extrahiere den Namen der Ursprungsdatei ohne die Erweiterung
    base_name = os.path.splitext(pdf_path)[0]
    thumbnail_name = f"{base_name}_thumbnail.png"

    pix.save(thumbnail_name)
    pdf_document.close()
    return thumbnail_name


def create_thumbnail(image_path, num, size=(195, 125)):
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
        thumbnail_path = os.path.join(thumbnail_dir, f"image_{num}_thumbnail.webp")

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


def convert_to_webp(original_image_path, num):
    if original_image_path:
        with PILImage.open(original_image_path) as image:
            dir_name, _ = os.path.split(original_image_path)
            # Definieren Sie den neuen Pfad und das Format
            new_image_path = os.path.join(dir_name, f"image_{num}.webp")
            # Konvertieren und speichern des Bildes im WEBP-Format
            image.save(new_image_path, 'WEBP')
            # Löschen der Originaldatei
            try:
                os.remove(original_image_path)
            except OSError as e:
                print(f"Fehler: {e.strerror}")

            return new_image_path
    return None


@login_required
def index(request):
    return render(request, "index.html")


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        imageform = ImageForm(request.POST, request.FILES)  # Erstellen einer Instanz von ImageForm
        dokumente_form = DokumenteForm(request.POST, request.FILES)  # Erstellen einer Instanz von ImageForm

        if form.is_valid() and imageform.is_valid():
            project = form.save(commit=False)
            project.user = request.user

            if 'expose_de' in request.FILES:
                # expose_de_file = request.FILES['expose_de']
                # Speichere das Projekt, um eine ID zu erhalten
                project.save()
                thumbnail_name = create_pdf_thumbnail(project.expose_de.path)
                project.expose_de_thumbnail = thumbnail_name
                project.save()
            if 'expose_en' in request.FILES:
                project.save()
                thumbnail_name = create_pdf_thumbnail(project.expose_de.path)
                project.expose_de_thumbnail = thumbnail_name
                project.save()
            if 'expose_ru' in request.FILES:
                project.save()
                thumbnail_name = create_pdf_thumbnail(project.expose_de.path)
                project.expose_de_thumbnail = thumbnail_name
                project.save()

            # Verarbeiten des Hauptbildes und des Hauptbild-Thumbnails
            if 'image_main' in request.FILES:
                main_image = request.FILES['image_main']
                project.image_main = main_image
                project.save()

                # print(f"Hauptbild gespeichert unter: {project.image_main.path}")

                # Konvertieren des Hauptbildes in WEBP und Umbenennen
                new_main_image_path = convert_to_webp(project.image_main.path, 0)  # Index 0 für das Hauptbild
                project.image_main = new_main_image_path
                project.save()

                # Optional: Thumbnail für das Hauptbild erstellen
                thumbnail_path = create_thumbnail(new_main_image_path, 0, size=(280, 196))  # Index 0 für das Hauptbild
                project.image_main_thumbnail = thumbnail_path
                project.save()

            files = imageform.cleaned_data['images']  # Zugriff auf die hochgeladenen Dateien
            for num, file in enumerate(files, start=1):
                image_instance = Image.objects.create(project=project, images=file)

                thumbnail_path = create_thumbnail(image_instance.images.path, num)
                Imagethumbnail.objects.create(image=image_instance, images_thumbnail=thumbnail_path)

                new_image_path = convert_to_webp(image_instance.images.path, num)
                image_instance.images = new_image_path
                image_instance.save()

                # print(f"Bild {index} gespeichert unter: {image_instance.images.path}")

            for file in request.FILES.getlist('dokumente'):
                dokument_instance = Dokumente.objects.create(project=project, dokumente=file)
                # print(f"Dokument gespeichert unter: {dokument_instance.dokumente.path}")

            messages.success(request, "New Project Added")
            return HttpResponseRedirect("/")
        else:
            print(form.errors, imageform.errors)
    else:
        form = ProjectForm()
        imageform = ImageForm()
        dokumente_form = DokumenteForm()

    return render(request, "create_project.html", {"form": form, "imageform": imageform, "dokumente_form": dokumente_form})


@login_required
def list_immos(request):
    immobilien = Project.objects.all()  # Holen Sie alle Immobilien aus der Datenbank
    return render(request, 'list_immos.html', {'immobilien': immobilien})


@login_required
def delete_immo(request, immo_id):
    if request.method == "POST":
        immo = get_object_or_404(Project, pk=immo_id)
        project_name = immo.name
        immo.delete()

        # Pfad zum Projektordner
        project_folder_path = os.path.join(settings.MEDIA_ROOT, 'properties', project_name)

        # Überprüfen, ob der Ordner existiert und dann löschen
        if os.path.isdir(project_folder_path):
            shutil.rmtree(project_folder_path)
            success_message = f"Das Objekt '{project_name}' und der zugehörige Ordner wurden erfolgreich gelöscht."
        else:
            success_message = f"Das Objekt '{project_name}' wurde erfolgreich gelöscht, aber der Ordner wurde nicht gefunden."

        messages.success(request, success_message)
        return redirect('list-immo')  # Setzen


def get_highest_image_number(project):
    images = Image.objects.filter(project=project)
    highest_number = 0
    for image in images:
        # Extrahieren der Nummer aus dem Bildnamen
        filename = splitext(image.images.name)[0]  # Entfernt die Dateiendung
        match = re.search(r"_([0-9]+)$", filename)
        if match:
            number = int(match.group(1))
            highest_number = max(highest_number, number)
    return highest_number


@login_required
def edit_immo(request, immo_id):
    project = get_object_or_404(Project, pk=immo_id)
    old_expose_de_path = project.expose_de.path if project.expose_de else None
    old_expose_en_path = project.expose_en.path if project.expose_en else None
    old_expose_ru_path = project.expose_ru.path if project.expose_ru else None

    old_expose_de_thumbnail_path = project.expose_de_thumbnail.path if project.expose_de_thumbnail else None
    old_expose_en_thumbnail_path = project.expose_en_thumbnail.path if project.expose_en_thumbnail else None
    old_expose_ru_thumbnail_path = project.expose_ru_thumbnail.path if project.expose_ru_thumbnail else None

    image_instances = Image.objects.filter(project=project)

    if request.method == 'POST':

        form = ProjectForm(request.POST, request.FILES, instance=project)
        imageform = ImageForm(request.POST or None, request.FILES or None)
        dokumente_form = DokumenteForm(request.POST or None, request.FILES or None)

        image_form_valid = 'images' in request.FILES and imageform.is_valid()
        dokumente_form_valid = 'dokumente' in request.FILES and dokumente_form.is_valid()

        if form.is_valid():

            if 'expose_de' in request.FILES and old_expose_de_path:
                if os.path.isfile(old_expose_de_path):
                    os.remove(old_expose_de_path)
                if os.path.isfile(old_expose_de_thumbnail_path):
                    os.remove(old_expose_de_thumbnail_path)

                project.save()
                thumbnail_name = create_pdf_thumbnail(project.expose_de.path)
                project.expose_de_thumbnail = thumbnail_name
                project.save()
            if 'expose_en' in request.FILES and old_expose_en_path:
                if os.path.isfile(old_expose_en_path):
                    os.remove(old_expose_en_path)
                if old_expose_en_thumbnail_path is not None:
                    os.remove(old_expose_en_thumbnail_path)

                project.save()
                thumbnail_name = create_pdf_thumbnail(project.expose_en.path)
                project.expose_en_thumbnail = thumbnail_name
                project.save()
            if 'expose_ru' in request.FILES and old_expose_ru_path:
                if os.path.isfile(old_expose_ru_path):
                    os.remove(old_expose_ru_path)
                if old_expose_ru_thumbnail_path is not None:
                    os.remove(old_expose_ru_thumbnail_path)

                project.save()
                thumbnail_name = create_pdf_thumbnail(project.expose_ru.path)
                project.expose_ru_thumbnail = thumbnail_name
                project.save()

            # Verarbeiten des Hauptbildes und des Hauptbild-Thumbnails
            if 'image_main' in request.FILES:
                main_image = request.FILES['image_main']

                project.image_main = main_image
                # project.save()

                full_path = project_directory_path_main_image(project, main_image.name)
                absolute_path = os.path.join(settings.MEDIA_ROOT, full_path)

                new_main_image_path = convert_to_webp(absolute_path, 0)  # Index 0 für das Hauptbild

                # new_main_image_path = convert_to_webp(project.image_main.path, 0)  # Index 0 für das Hauptbild
                project.image_main = new_main_image_path
                project.save()

                # Optional: Thumbnail für das Hauptbild erstellen
                thumbnail_path = create_thumbnail(new_main_image_path, 0, size=(280, 196))  # Index 0 für das Hauptbild
                project.image_main_thumbnail = thumbnail_path
                project.save()

            form.save()

            # Hier Logik zum Speichern der Bilder und Dokumente hinzufügen.
            messages.success(request, 'Projekt wurde erfolgreich aktualisiert.')
            return HttpResponseRedirect(reverse('edit-immo', args=[immo_id]))

        if image_form_valid:
            files = imageform.cleaned_data['images']  # Zugriff auf die hochgeladenen Dateien

            highest_number = get_highest_image_number(project)
            start_index = highest_number + 1

            for num, file in enumerate(files, start=start_index):
                image_instance = Image.objects.create(project=project, images=file)

                thumbnail_path = create_thumbnail(image_instance.images.path, num)
                Imagethumbnail.objects.create(image=image_instance, images_thumbnail=thumbnail_path)

                # Imagethumbnail.objects.create(project=project, images_thumbnail=thumbnail_path)

                new_image_path = convert_to_webp(image_instance.images.path, num)
                image_instance.images = new_image_path
                image_instance.save()

            for file in request.FILES.getlist('dokumente'):
                Dokumente.objects.create(project=project, dokumente=file)

            messages.success(request, 'Bilder wurden erfolgreich aktualisiert.')
            return HttpResponseRedirect(reverse('edit-immo', args=[immo_id]))

        if dokumente_form_valid:
            for file in request.FILES.getlist('dokumente'):
                Dokumente.objects.create(project=project, dokumente=file)

            messages.success(request, 'Dokumente wurden erfolgreich aktualisiert.')
        messages.success(request, 'Es wurden keine änderungen vorgenommen!!!')
        return HttpResponseRedirect(reverse('edit-immo', args=[immo_id]))

    else:
        form = ProjectForm(instance=project)
        # Sie müssen die Logik implementieren, um die vorhandenen Bilder und Dokumente
        # als Instanzen für ImageForm und DokumenteForm zu übergeben,
        # z.B. mittels 'initial' oder indem Sie das Queryset für die Forms filtern.
        image_instances = Image.objects.filter(project=project)
        image_forms = [ImageForm(instance=image) for image in image_instances]

        # Falls Sie ein separates Formular zum Hinzufügen neuer Bilder haben
        add_image_form = ImageForm()
        dokumente_form = DokumenteForm()
        dokumente_instances = Dokumente.objects.filter(project=project)

        return render(request, 'edit_project.html', {
            'form': form,
            'image_forms': image_forms,
            'add_image_form': add_image_form,
            'dokumente_form': dokumente_form,
            'dokumente_instances': dokumente_instances,
            'project': project
    })


@login_required
def delete_image(request):
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        image = Image.objects.get(id=image_id)

        # Löschen des Bildes und des Thumbnails aus dem Dateisystem
        if image.images:
            if os.path.exists(image.images.path):
                os.remove(image.images.path)
        if image.thumbnail and image.thumbnail.images_thumbnail:
            if os.path.exists(image.thumbnail.images_thumbnail.path):
                os.remove(image.thumbnail.images_thumbnail.path)

        # Löschen des Bildobjekts und des Thumbnails aus der Datenbank
        image.delete()

        # Redirect zur Bearbeitungsseite
        return HttpResponseRedirect(reverse('edit-immo', args=[image.project.id]))

    # Bei GET-Request oder anderen Methoden
    return HttpResponseRedirect(reverse('list-immo'))


@login_required
def delete_dokument(request):
    if request.method == 'POST':
        dokument_id = request.POST.get('dokument_id')
        dokument = Dokumente.objects.get(id=dokument_id)

        # Löschen des Dokuments aus dem Dateisystem
        if dokument.dokumente:
            if os.path.exists(dokument.dokumente.path):
                os.remove(dokument.dokumente.path)

        # Löschen des Dokumentobjekts aus der Datenbank
        dokument.delete()

        # Redirect zur Bearbeitungsseite
        return HttpResponseRedirect(reverse('edit-immo', args=[dokument.project.id]))

    # Bei GET-Request oder anderen Methoden
    return HttpResponseRedirect(reverse('list-immo'))
