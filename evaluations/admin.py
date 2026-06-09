from django.contrib import admin
from django.utils.html import format_html
from .models import Group, Presenter, Evaluator, Score, WeightConfig


class PresenterInline(admin.TabularInline):
    model = Presenter
    extra = 3
    fields = ['name', 'order']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'presenter_list', 'score_count', 'weighted_score']
    inlines = [PresenterInline]

    def presenter_list(self, obj):
        names = obj.get_presenter_names()
        return names or "—"
    presenter_list.short_description = "Presenters"

    def score_count(self, obj):
        return obj.scores.count()
    score_count.short_description = "# Scores"

    def weighted_score(self, obj):
        ws = obj.weighted_final_score()
        if ws is None:
            return "—"
        color = 'green' if ws >= 14 else ('orange' if ws >= 10 else 'red')
        return format_html('<strong style="color:{}">{}/20</strong>', color, ws)
    weighted_score.short_description = "Weighted Score"


@admin.register(Presenter)
class PresenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'order']
    list_filter = ['group']
    search_fields = ['name', 'group__name']


@admin.register(WeightConfig)
class WeightConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_weight', 'tutor_weight', 'invited_weight',
                    'total_weight_display', 'tutor_password', 'invited_password', 'is_active']
    list_editable = ['student_weight', 'tutor_weight', 'invited_weight', 'is_active']

    def total_weight_display(self, obj):
        t = obj.total_weight()
        color = 'green' if t == 100 else 'red'
        return format_html('<span style="color:{}">{}</span>', color, t)
    total_weight_display.short_description = "Total %"


@admin.register(Evaluator)
class EvaluatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'evaluator_type', 'email', 'score_count']
    list_filter = ['evaluator_type']
    search_fields = ['name', 'email']

    def score_count(self, obj):
        return obj.scores.count()
    score_count.short_description = "# Scores Given"


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['group', 'evaluator', 'evaluator_type_badge', 'content',
                    'presentation_skills', 'time_management', 'language',
                    'questions_answers', 'total_display']
    list_filter = ['evaluator__evaluator_type', 'group']
    search_fields = ['group__name', 'evaluator__name']

    def evaluator_type_badge(self, obj):
        colors = {'student': '#3b82f6', 'tutor': '#10b981', 'invited': '#8b5cf6'}
        color = colors.get(obj.evaluator.evaluator_type, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.evaluator.get_evaluator_type_display()
        )
    evaluator_type_badge.short_description = "Type"

    def total_display(self, obj):
        return format_html('<strong>{}/20</strong>', obj.total())
    total_display.short_description = "Total"
