from django import forms
from .models import Score, Group, Evaluator


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['group', 'evaluator', 'content', 'presentation_skills',
                  'time_management', 'language', 'questions_answers', 'notes']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'evaluator': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 4, 'step': 0.5}),
            'presentation_skills': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 4, 'step': 0.5}),
            'time_management': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 4, 'step': 0.5}),
            'language': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 4, 'step': 0.5}),
            'questions_answers': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 4, 'step': 0.5}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'content': 'Content (/4)',
            'presentation_skills': 'Presentation Skills (/4)',
            'time_management': 'Time Management (/4)',
            'language': 'Language (/4)',
            'questions_answers': 'Questions & Answers (/4)',
        }
        help_texts = {
            'questions_answers': 'Fill in after Q&A session is completed.',
        }

    def clean(self):
        cleaned_data = super().clean()
        for field in ['content', 'presentation_skills', 'time_management', 'language']:
            val = cleaned_data.get(field)
            if val is not None and (val < 0 or val > 4):
                self.add_error(field, "Score must be between 0 and 4.")
        qa = cleaned_data.get('questions_answers')
        if qa is not None and (qa < 0 or qa > 4):
            self.add_error('questions_answers', "Score must be between 0 and 4.")
        return cleaned_data
