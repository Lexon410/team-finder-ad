from django import forms
from .models import Project
from constants import STATUS_CHOICES
from utils.validators import validate_github_url

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url']

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get('github_url'))

class ProjectEditForm(ProjectForm):
    class Meta(ProjectForm.Meta):
        fields = ProjectForm.Meta.fields + ['status']
        widgets = {
            'status': forms.Select(choices=STATUS_CHOICES),
        }