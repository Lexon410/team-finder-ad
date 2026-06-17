import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProjectForm, ProjectEditForm
from .models import Project, Skill
from constants import STATUS_CLOSED, STATUS_OPEN
from utils.pagination import paginate_queryset

def project_list(request):
    all_skills = Skill.objects.all()
    active_skill = request.GET.get('skill')
    projects = Project.objects.all()
    if active_skill:
        projects = projects.filter(skills__name__iexact=active_skill)
    page_obj = paginate_queryset(request, projects)
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
    form = ProjectForm(request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect('projects:project_detail', project_id=project.id)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return redirect('projects:project_detail', project_id=project.id)
    form = ProjectEditForm(request.POST or None, instance=project)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})
        form.save()
        return redirect('projects:project_detail', project_id=project.id)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})

@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user or project.status != STATUS_OPEN:
        return JsonResponse({'error': 'Доступ запрещён'}, status=HttpResponseForbidden.status_code)
    project.status = STATUS_CLOSED
    project.save()
    return JsonResponse({'status': 'ok', 'project_status': project.status})

@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    is_participant = project.participants.filter(id=request.user.id).exists()
    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({'status': 'ok', 'participating': not is_participant})

def skill_autocomplete(request):
    q = request.GET.get('q', '')
    if q:
        skills = Skill.objects.filter(name__istartswith=q)[:10]
    else:
        skills = Skill.objects.none()
    data = [{'id': s.id, 'name': s.name} for s in skills]
    return JsonResponse(data, safe=False)

@login_required
def add_skill_to_project(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=HttpResponseNotAllowed.status_code)

    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return JsonResponse({'error': 'Доступ запрещён'}, status=HttpResponseForbidden.status_code)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный JSON'}, status=HttpResponseBadRequest.status_code)

    skill_id = data.get('skill_id')
    skill_name = data.get('name')
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name.strip())
    else:
        return JsonResponse({'error': 'Не указан навык'}, status=HttpResponseBadRequest.status_code)

    if project.skills.filter(id=skill.id).exists():
        added = False
    else:
        project.skills.add(skill)
        added = True

    return JsonResponse({
        'id': skill.id,
        'name': skill.name,
        'created': created,
        'added': added,
    })

@login_required
def remove_skill_from_project(request, project_id, skill_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=HttpResponseNotAllowed.status_code)

    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return JsonResponse({'error': 'Доступ запрещён'}, status=HttpResponseForbidden.status_code)

    skill = get_object_or_404(Skill, id=skill_id)
    if not project.skills.filter(id=skill.id).exists():
        return JsonResponse({'error': 'Навык не найден в проекте'}, status=HttpResponseBadRequest.status_code)

    project.skills.remove(skill)
    return JsonResponse({'status': 'ok'})