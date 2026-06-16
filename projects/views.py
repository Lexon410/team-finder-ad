import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProjectForm
from .models import Project, Skill


def project_list(request):
    all_skills = Skill.objects.all().order_by('name')
    active_skill = request.GET.get('skill')
    projects = Project.objects.all().order_by('-created_at')
    if active_skill:
        projects = projects.filter(skills__name__iexact=active_skill)
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'projects': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return redirect('project_detail', project_id=project.id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner == request.user and project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})
    return JsonResponse({'status': 'error'}, status=403)


@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True
    return JsonResponse({'status': 'ok', 'participating': is_participant})


# ----- Эндпоинты для навыков (вариант 3) -----
def skill_autocomplete(request):
    q = request.GET.get('q', '')
    if q:
        skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
    else:
        skills = Skill.objects.none()
    data = [{'id': s.id, 'name': s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
def add_skill_to_project(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    skill_id = data.get('skill_id')
    skill_name = data.get('name')
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name.strip())
    else:
        return JsonResponse({'error': 'No skill identifier'}, status=400)

    if project.skills.filter(id=skill.id).exists():
        added = False
    else:
        project.skills.add(skill)
        added = True

    return JsonResponse({
        'id': skill.id,
        'name': skill.name,  # добавим name, чтобы было красиво
        'created': created,
        'added': added,
    })


@login_required
def remove_skill_from_project(request, project_id, skill_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    skill = get_object_or_404(Skill, id=skill_id)
    if not project.skills.filter(id=skill.id).exists():
        return JsonResponse({'error': 'Skill not in project'}, status=400)

    project.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
