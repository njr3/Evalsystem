import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation_system.settings')
django.setup()

from evaluations.models import Group, Presenter, Evaluator, Score, WeightConfig

# Clear existing
Score.objects.all().delete()
Evaluator.objects.all().delete()
Presenter.objects.all().delete()
Group.objects.all().delete()
WeightConfig.objects.all().delete()

# Config
WeightConfig.objects.create(name="Default Config", student_weight=20, tutor_weight=40, invited_weight=40,
                             tutor_password="tutor2024", invited_password="invited2024")

# Groups named Group 1 to Group 6
groups = []
sample_presenters = [
    ["Alice Mbaye", "Omar Diallo"],
    ["Fatou Ndiaye", "Moussa Sow"],
    ["Aminata Fall", "Ibrahima Ba"],
    ["Rokhaya Gueye", "Mamadou Diop"],
    ["Mariama Kane", "Cheikh Sy"],
    ["Aissatou Diallo", "Ousmane Niang"],
]
for i in range(1, 7):
    g = Group.objects.create(name=f"Group {i}", description=f"Presentation group {i}")
    for j, pname in enumerate(sample_presenters[i-1]):
        Presenter.objects.create(group=g, name=pname, order=j)
    groups.append(g)

# Evaluators
students = [Evaluator.objects.create(name=f"Student {i}", evaluator_type="student") for i in range(1, 6)]
tutors   = [Evaluator.objects.create(name=f"Tutor {i}",   evaluator_type="tutor")   for i in range(1, 3)]
invited  = [Evaluator.objects.create(name=f"Prof. Expert {i}", evaluator_type="invited") for i in range(1, 3)]

import random
random.seed(42)
for group in groups:
    for ev in students:
        Score.objects.create(group=group, evaluator=ev,
            content=round(random.uniform(2,4)*2)/2,
            presentation_skills=round(random.uniform(2,4)*2)/2,
            time_management=round(random.uniform(1.5,4)*2)/2,
            language=round(random.uniform(2,4)*2)/2,
            questions_answers=round(random.uniform(2,4)*2)/2)
    for ev in tutors:
        Score.objects.create(group=group, evaluator=ev,
            content=round(random.uniform(2,4)*2)/2,
            presentation_skills=round(random.uniform(2,4)*2)/2,
            time_management=round(random.uniform(2,4)*2)/2,
            language=round(random.uniform(2,4)*2)/2,
            questions_answers=round(random.uniform(2,4)*2)/2)
    for ev in invited:
        Score.objects.create(group=group, evaluator=ev,
            content=round(random.uniform(2.5,4)*2)/2,
            presentation_skills=round(random.uniform(2.5,4)*2)/2,
            time_management=round(random.uniform(2,4)*2)/2,
            language=round(random.uniform(2.5,4)*2)/2,
            questions_answers=round(random.uniform(2.5,4)*2)/2)

print("✅ Seed data: 6 groups (Group 1-6), presenter names, 5 students, 2 tutors, 2 invited")
