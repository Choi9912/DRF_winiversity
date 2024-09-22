from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    CodeSubmissionMission,
    Mission,
    MultipleChoiceMission,
    MissionSubmission,
)


class MultipleChoiceMissionAdminForm(forms.ModelForm):
    option_a = forms.CharField(max_length=200, required=True, label="옵션 A")
    option_b = forms.CharField(max_length=200, required=True, label="옵션 B")
    option_c = forms.CharField(max_length=200, required=True, label="옵션 C")
    option_d = forms.CharField(max_length=200, required=True, label="옵션 D")
    option_e = forms.CharField(max_length=200, required=True, label="옵션 E")

    class Meta:
        model = MultipleChoiceMission
        fields = ["correct_answer"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            options = self.instance.get_options()
            for i, option in enumerate(["A", "B", "C", "D", "E"]):
                if i < len(options):
                    self.fields[f"option_{option.lower()}"].initial = options[i]

    def save(self, commit=True):
        instance = super().save(commit=False)
        options = [
            self.cleaned_data[f"option_{option.lower()}"]
            for option in ["A", "B", "C", "D", "E"]
        ]
        instance.set_options(options)
        if commit:
            instance.save()
        return instance


class MultipleChoiceMissionInline(admin.StackedInline):
    model = MultipleChoiceMission
    form = MultipleChoiceMissionAdminForm
    extra = 1
    classes = ("multiple-choice-mission",)


class CodeSubmissionMissionInline(admin.StackedInline):
    model = CodeSubmissionMission
    extra = 1
    classes = ("code-submission-mission",)


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("question", "course", "type")
    list_filter = ("course", "type")
    search_fields = ("question",)
    inlines = [MultipleChoiceMissionInline, CodeSubmissionMissionInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["type"].widget.attrs[
            "onchange"
        ] = "toggleMissionType(this.value);"
        return form

    class Media:
        js = ("admin/js/mission_type_toggle.js",)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["mission_type_script"] = mark_safe(
            """
        <script>
            function toggleMissionType(type) {
                var multipleChoiceDiv = document.querySelector('.multiple-choice-mission');
                var codeSubmissionDiv = document.querySelector('.code-submission-mission');
                
                if (type === '5지선다형') {
                    multipleChoiceDiv.style.display = 'block';
                    codeSubmissionDiv.style.display = 'none';
                } else if (type === '코드 제출형') {
                    multipleChoiceDiv.style.display = 'none';
                    codeSubmissionDiv.style.display = 'block';
                }
            }

            document.addEventListener('DOMContentLoaded', function() {
                var typeSelect = document.getElementById('id_type');
                toggleMissionType(typeSelect.value);
            });
        </script>
        """
        )
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )


@admin.register(MultipleChoiceMission)
class MultipleChoiceMissionAdmin(admin.ModelAdmin):
    form = MultipleChoiceMissionAdminForm
    list_display = ("mission", "get_options_display", "correct_answer")

    def get_options_display(self, obj):
        return ", ".join(obj.get_options())

    get_options_display.short_description = "Options"


@admin.register(MissionSubmission)
class MissionSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "mission", "is_correct", "submitted_at")
    list_filter = ("is_correct", "mission__course")
    search_fields = ("user__username", "mission__question")
    readonly_fields = ("submitted_at",)


class CodeSubmissionMissionAdmin(admin.ModelAdmin):
    list_display = ("mission", "problem_description")
    search_fields = ("mission__question", "problem_description")
