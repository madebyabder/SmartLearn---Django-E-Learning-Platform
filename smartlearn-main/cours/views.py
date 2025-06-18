from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from .forms import ModuleForm, ContenuForm, CoursForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours, Module, Contenu, Choice, Question
from .models import Inscription, QuizResult,Category
from django.conf import settings
from admin_app.models import ActivityLog
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import os
# Create your views here.


def catalogue(request):
    selected_category = request.GET.get("category")  # e.g., 'dev', 'data', etc.

    if selected_category:
        cours_list = Cours.objects.filter(category=selected_category, is_published=True)
    else:
        cours_list = Cours.objects.filter(is_published=True)

    context = {
        "cours_list": cours_list,
        "categories": Category.choices,  # List of (key, label) tuples
        "selected_category": selected_category
    }

    return render(request, "cours/catalogue.html", context)

@login_required
def certificat(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id)

    # Set up PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificat_{cours.title}.pdf"'
    
    p = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Optional Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo_certif.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, width - 7*cm, height - 4*cm, width=5*cm, preserveAspectRatio=True, mask='auto')

    # Border
    p.setStrokeColor(colors.HexColor("#004080"))
    p.setLineWidth(4)
    margin = 1.5 * cm
    p.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # Title
    p.setFont("Helvetica-Bold", 30)
    p.setFillColor(colors.HexColor("#004080"))
    p.drawCentredString(width / 2, height - 4.5 * cm, "🎓 CERTIFICAT DE RÉUSSITE")

    # Recipient Name
    p.setFont("Helvetica", 16)
    p.setFillColor(colors.black)
    p.drawCentredString(width / 2, height - 7 * cm, "Ce certificat est décerné à :")

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 9 * cm, request.user.get_full_name())

    # Course Title
    p.setFont("Helvetica", 16)
    p.drawCentredString(width / 2, height - 11 * cm, "Pour avoir complété avec succès le cours suivant :")

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 13 * cm, cours.title)

    # Date + Signature
    date_str = timezone.now().strftime("%d/%m/%Y")
    p.setFont("Helvetica", 12)
    p.drawString(margin + 1 * cm, margin + 1.5 * cm, f"Date : {date_str}")

    p.drawString(width - 7 * cm, margin + 1.5 * cm, "Signature : __________________")

    p.showPage()
    p.save()
    return response


@login_required
def mes_cours_apprenant(request):
    inscriptions = Inscription.objects.filter(apprenant=request.user).select_related('cours')
    cours_inscrits = [inscription.cours for inscription in inscriptions]

    certification_status = {}
    for cours in cours_inscrits:
        modules = cours.modules.all()
        completed = True

        for module in modules:
            try:
                result = QuizResult.objects.get(user=request.user, module=module)
                if result.score < 60:
                    completed = False
                    break
            except QuizResult.DoesNotExist:
                completed = False
                break

        certification_status[cours.id] = completed

    return render(request, 'cours/mes_cours_apprenant.html', {
        'cours_inscrits': cours_inscrits,
        'certification_status': certification_status,
    })


def calculate_progress(cours, user):
    modules = Module.objects.filter(cours=cours)
    total = modules.count()
    passed = 0

    for module in modules:
        result = QuizResult.objects.filter(user=user, module=module).first()
        if result and result.score >= 60:
            passed += 1

    return int((passed / total) * 100) if total > 0 else 0


def course_catalogue(request):
    cours_list = Cours.objects.filter(is_published=True)
    return render(request, "cours/catalogue.html", {"cours_list": cours_list})


@login_required
def cours_content(request, cours_id):
    # Get the course and verify enrollment
    cours = get_object_or_404(Cours, id=cours_id)
    if not Inscription.objects.filter(cours=cours, apprenant=request.user).exists():
        messages.error(
            request, "Vous devez être inscrit pour accéder au contenu du cours.")
        return redirect('cours:cours_detail_public', cours_id=cours_id)

    # Get all modules ordered by position
    modules = Module.objects.filter(cours=cours).order_by(
        'order_position').prefetch_related('contenus')
    modules_with_access = []

    passed = 0
    total = modules.count()

    for i, module in enumerate(modules):
        if i == 0:
            # Always unlock the first module
            modules_with_access.append((module, True))
        else:
            prev_module = modules[i - 1]
            result = QuizResult.objects.filter(
                user=request.user, module=prev_module).first()
            is_unlocked = result and result.score >= 60
            modules_with_access.append((module, is_unlocked))

        # Track progress (count modules with passing score)
        result = QuizResult.objects.filter(
            user=request.user, module=module).first()
        if result and result.score >= 60:
            passed += 1

    progress_percent = int((passed / total) * 100) if total > 0 else 0

    return render(request, 'cours/cours_content.html', {
        'cours': cours,
        'modules_with_access': modules_with_access,
        'progress_percent': progress_percent,
        'MEDIA_URL': settings.MEDIA_URL,
    })


@login_required
def cours_detail_public(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id, is_published=True)
    inscrit = Inscription.objects.filter(
        cours=cours, apprenant=request.user).exists()
    progress_percent = 0

    if inscrit:
        modules = Module.objects.filter(cours=cours)
        total = modules.count()
        passed = 0

        for module in modules:
            result = QuizResult.objects.filter(
                user=request.user, module=module).first()
            if result and result.score >= 60:
                passed += 1

        progress_percent = int((passed / total) * 100) if total > 0 else 0

    return render(request, 'cours/detail_apprenant.html', {
        'cours': cours,
        'inscrit': inscrit,
        'progress_percent': progress_percent,
    })


@login_required
def take_quiz(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    questions = module.questions.prefetch_related('choices')

    if request.method == "POST":
        total = questions.count()
        correct = 0

        for question in questions:
            selected_choice_id = request.POST.get(f"question_{question.id}")
            if selected_choice_id:
                try:
                    selected_choice = Choice.objects.get(id=selected_choice_id)
                    if selected_choice.is_correct:
                        correct += 1
                except Choice.DoesNotExist:
                    pass

        score = int((correct / total) * 100) if total > 0 else 0
        QuizResult.objects.update_or_create(
            user=request.user,
            module=module,
            defaults={'score': score}
        )

        return render(request, 'cours/quiz_result.html', {
            'module': module,
            'score': score,
            'correct': correct,
            'total': total,
        })

    return render(request, 'cours/quiz.html', {
        'module': module,
        'questions': questions,
    })


@login_required
def inscrire_cours(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id)

    # Prevent a teacher from enrolling in their own course
    if cours.teacher == request.user:
        messages.error(
            request, "Vous ne pouvez pas vous inscrire à votre propre cours.")
        return redirect('dashboard:apprenant_dashboard')

    inscription_existante = Inscription.objects.filter(
        cours=cours, apprenant=request.user).exists()
    if inscription_existante:
        messages.info(request, "Vous êtes déjà inscrit à ce cours.")
    else:
        Inscription.objects.create(cours=cours, apprenant=request.user)
        messages.success(request, "Inscription réussie !")

    return redirect('cours:cours_detail_public', cours_id=cours.id)


@login_required
def mes_cours(request):
    user = request.user
    # Fetch only courses where the user is enrolled via Inscription model
    cours_inscrits = Cours.objects.filter(inscription__apprenant=user)
    return render(request, "dashboard/apprenant_dashboard.html", {"cours_inscrits": cours_inscrits})


@login_required
def liste_cours(request):
    liste_cours = Cours.objects.filter(is_published=True)
    return render(request, 'cours/liste_cours.html', {'liste_cours': liste_cours})


@login_required
def details_cours(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id, teacher=request.user)

    modules = cours.modules.order_by('order_position').prefetch_related('contenus', 'quiz')
    apprenant = request.user

    modules_with_access = []
    all_completed = True

    for index, module in enumerate(modules):
        is_accessible = True
        # Vérifie si le quiz du module précédent est réussi
        if index > 0:
            prev_module = modules[index - 1]
            try:
                result = QuizResult.objects.get(module=prev_module, apprenant=apprenant)
                if result.score < 60:
                    is_accessible = False
            except QuizResult.DoesNotExist:
                is_accessible = False

        modules_with_access.append((module, is_accessible))

        # Vérifie si ce module est terminé
        try:
            result = QuizResult.objects.get(module=module, apprenant=apprenant)
            if result.score < 60:
                all_completed = False
        except QuizResult.DoesNotExist:
            all_completed = False

    return render(request, 'cours/details_cours.html', {
        'cours': cours,
        'modules_with_access': modules_with_access,
        'certification_ready': all_completed
    })



@login_required
def add_cours(request):
    if request.method == "POST":
        form = CoursForm(request.POST, request.FILES)
        if form.is_valid():
            print("POST Data:", request.POST.dict())
            cours = form.save(commit=False)
            cours.teacher = request.user
            cours.is_published = True
            cours.save()
            ActivityLog.objects.create(
                user=request.user,
                action=f"a ajouté le cours « {cours.title} »"
            )

            module_titles = request.POST.getlist("module_title[]")
            module_orders = request.POST.getlist("module_order[]")

            for module_index, module_title in enumerate(module_titles):
                module = Module.objects.create(
                    cours=cours, title=module_title, order_position=module_orders[module_index])

                content_titles = request.POST.getlist(
                    f"content_title_{module_index}[]")
                content_descriptions = request.POST.getlist(
                    f"content_description_{module_index}[]")
                content_videos = request.POST.getlist(
                    f"video_url_{module_index}[]")

                for i in range(len(content_titles)):
                    Contenu.objects.create(
                        module=module,
                        title=content_titles[i],
                        description=content_descriptions[i],
                        video=content_videos[i] if i < len(
                            content_videos) else None,
                    )

                questions = request.POST.getlist(f"question_{module_index}[]")
                for question_index, question_text in enumerate(questions):
                    question = Question.objects.create(
                        module=module,
                        text=question_text
                    )
                    choices = request.POST.getlist(
                        f"choice_{module_index}_{question_index}[]")
                    correct_choice_index = request.POST.get(
                        f"correct_{module_index}_{question_index}")
                    for choice_index, choice_text in enumerate(choices):
                        is_correct = str(choice_index) == correct_choice_index
                        Choice.objects.create(
                            question=question,
                            text=choice_text,
                            is_correct=is_correct
                        )

            return redirect("cours:liste_cours")

    else:
        form = CoursForm()

    return render(request, "cours/add_cours.html", {"form": form})


def add_module(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id)
    if request.method == "POST":
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.cours = cours
            module.save()
            ActivityLog.objects.create(
                user=request.user,
                action=f"a ajouté le module « {module.title} » au cours « {cours.title} »"
            )
            return redirect('cours:liste_cours')  # or wherever appropriate
    else:
        form = ModuleForm()
    return render(request, 'cours/add_module.html', {'form': form, 'cours': cours})


def add_contenu(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    if request.method == "POST":
        form = ContenuForm(request.POST)
        if form.is_valid():
            contenu = form.save(commit=False)
            contenu.module = module
            contenu.save()
            return redirect('cours:liste_cours')
    else:
        form = ContenuForm()
    return render(request, 'cours/add_contenu.html', {'form': form, 'module': module})


@login_required
def modify_cours(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id, teacher=request.user)
    modules = Module.objects.filter(cours=cours).prefetch_related("contenus")
    if request.method == "POST":
        cours.title = request.POST.get("title")
        cours.description = request.POST.get("description")
        cours.is_published = "is_published" in request.POST
        cours.save()
        for module in modules:
            module_title = request.POST.get(f"module_title_{module.id}")
            module_order = request.POST.get(f"order_position_{module.id}")
            if module_title:
                module.title = module_title
            if module_order:
                module.order_position = module_order
            module.save()
            for contenu in module.contenus.all():
                contenu_title = request.POST.get(f"content_title_{contenu.id}")
                contenu_description = request.POST.get(
                    f"content_description_{contenu.id}")
                contenu_video = request.POST.get(f"video_{contenu.id}")
                if contenu_title:
                    contenu.title = contenu_title
                if contenu_description:
                    contenu.description = contenu_description
                if contenu_video:
                    contenu.video = contenu_video
                contenu.save()
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"a modifié le cours « {cours.title} »"
                )
        return redirect("cours:liste_cours")
    return render(request, "cours/modify_cours.html", {"cours": cours, "modules": modules})


@login_required
def modify_module(request, module_id):
    module = get_object_or_404(
        Module, id=module_id, cours__teacher=request.user)

    if request.method == "POST":
        module.title = request.POST.get("title")
        module.order_position = request.POST.get("order_position")
        module.save()
        return redirect('cours:details_cours', cours_id=module.cours.id)

    return render(request, 'cours/modify_module.html', {'module': module})


@login_required
def modify_contenu(request, contenu_id):
    contenu = get_object_or_404(
        Contenu, id=contenu_id, module__cours__teacher=request.user)

    if request.method == "POST":
        contenu.title = request.POST.get("title")
        contenu.description = request.POST.get("description")
        video_url = request.POST.get("video")

        if video_url:
            contenu.video = video_url

        if 'pdf' in request.FILES:
            contenu.pdf = request.FILES['pdf']

        contenu.save()
        return redirect('cours:details_cours', cours_id=contenu.module.cours.id)

    return render(request, 'cours/modify_contenu.html', {'contenu': contenu})


@login_required
def delete_cours(request, cours_id):
    cours = get_object_or_404(Cours, id=cours_id)
    cours.delete()
    ActivityLog.objects.create(
        user=request.user,
        action=f"a supprimé le cours « {cours.title} »"
    )
    return redirect('cours:liste_cours')


@login_required
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if module.cours.teacher != request.user:
        return HttpResponseForbidden("Vous n'avez pas la permission de supprimer ce module.")

    module.delete()
    return redirect('cours:liste_cours')


@login_required
def delete_contenu(request, contenu_id=None):
    print(f"Received contenu_id: {contenu_id}")
    contenu = get_object_or_404(Contenu, id=contenu_id)
    contenu.delete()
    return redirect('cours:liste_cours')

