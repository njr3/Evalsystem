from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from decimal import Decimal


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_presenter_names(self):
        return ", ".join(p.name for p in self.presenters.all())

    def get_scores_by_type(self, evaluator_type):
        return Score.objects.filter(group=self, evaluator__evaluator_type=evaluator_type)

    def average_total_by_type(self, evaluator_type):
        scores = self.get_scores_by_type(evaluator_type)
        if not scores.exists():
            return None
        totals = [s.total() for s in scores]
        return round(sum(totals) / len(totals), 2)

    def weighted_final_score(self):
        config = WeightConfig.get_active()
        if not config:
            return None
        student_avg = self.average_total_by_type('student')
        tutor_avg = self.average_total_by_type('tutor')
        invited_avg = self.average_total_by_type('invited')
        total_weight = Decimal('0')
        weighted_sum = Decimal('0')
        for avg, weight in [(student_avg, config.student_weight),
                            (tutor_avg, config.tutor_weight),
                            (invited_avg, config.invited_weight)]:
            if avg is not None:
                weighted_sum += Decimal(str(avg)) * weight
                total_weight += weight
        if total_weight == 0:
            return None
        return round(float(weighted_sum / total_weight), 2)

    def score_breakdown(self):
        result = {}
        for et in ['student', 'tutor', 'invited']:
            scores = self.get_scores_by_type(et)
            if scores.exists():
                agg = scores.aggregate(
                    content=Avg('content'),
                    presentation_skills=Avg('presentation_skills'),
                    time_management=Avg('time_management'),
                    language=Avg('language'),
                    questions_answers=Avg('questions_answers'),
                )
                result[et] = {k: round(v, 2) if v else 0 for k, v in agg.items()}
                result[et]['total'] = self.average_total_by_type(et)
                result[et]['count'] = scores.values('evaluator').distinct().count()
        return result

    class Meta:
        ordering = ['name']


class Presenter(models.Model):
    """Admin registers presenter names per group. Forms show these pre-filled."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='presenters')
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0, help_text="Display order within group")

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    class Meta:
        ordering = ['group', 'order', 'name']
        unique_together = ('group', 'name')


class Evaluator(models.Model):
    EVALUATOR_TYPES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('invited', 'Invited Evaluator'),
    ]
    name = models.CharField(max_length=100)
    evaluator_type = models.CharField(max_length=10, choices=EVALUATOR_TYPES)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_evaluator_type_display()})"

    class Meta:
        ordering = ['evaluator_type', 'name']


SCORE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(4)]


class Score(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='scores')
    evaluator = models.ForeignKey(Evaluator, on_delete=models.CASCADE, related_name='scores')
    content = models.FloatField(validators=SCORE_VALIDATOR)
    presentation_skills = models.FloatField(validators=SCORE_VALIDATOR)
    time_management = models.FloatField(validators=SCORE_VALIDATOR)
    language = models.FloatField(validators=SCORE_VALIDATOR)
    questions_answers = models.FloatField(validators=SCORE_VALIDATOR, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def total(self):
        return round(self.content + self.presentation_skills + self.time_management
                     + self.language + (self.questions_answers or 0), 2)

    def percentage(self):
        return round((self.total() / 20) * 100, 1)

    def __str__(self):
        return f"{self.evaluator} -> {self.group} ({self.total()}/20)"

    class Meta:
        unique_together = ('group', 'evaluator')
        ordering = ['-submitted_at']


class WeightConfig(models.Model):
    name = models.CharField(max_length=100, default="Default Config")
    student_weight = models.DecimalField(max_digits=5, decimal_places=2, default=20,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)])
    tutor_weight = models.DecimalField(max_digits=5, decimal_places=2, default=40,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    invited_weight = models.DecimalField(max_digits=5, decimal_places=2, default=40,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)])
    tutor_password = models.CharField(max_length=100, default="tutor2024",
                                       help_text="Password for Tutor form AND dashboard access")
    invited_password = models.CharField(max_length=100, default="invited2024",
                                         help_text="Password for Invited Evaluator form")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()

    def total_weight(self):
        return self.student_weight + self.tutor_weight + self.invited_weight

    def student_pct(self):
        t = self.total_weight()
        return round(float(self.student_weight / t * 100), 1) if t else 0

    def tutor_pct(self):
        t = self.total_weight()
        return round(float(self.tutor_weight / t * 100), 1) if t else 0

    def invited_pct(self):
        t = self.total_weight()
        return round(float(self.invited_weight / t * 100), 1) if t else 0

    def __str__(self):
        return f"{self.name} (S:{self.student_weight}% T:{self.tutor_weight}% I:{self.invited_weight}%)"

    class Meta:
        verbose_name = "Weight Configuration"
