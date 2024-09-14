from django import forms
from django.contrib import admin
from .models import Mission, MultipleChoiceMission, MissionSubmission


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


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("question", "course", "type")
    list_filter = ("course", "type")
    search_fields = ("question",)
    inlines = [MultipleChoiceMissionInline]


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
