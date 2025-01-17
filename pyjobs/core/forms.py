from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django_select2.forms import Select2MultipleWidget, Select2Widget

from pyjobs.core.models import Contact, Job, Profile, Skill


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "job_level",
            "company_name",
            "workplace",
            "remote",
            "state",
            "application_link",
            "company_email",
            "cellphone",
            "salary_range",
            "description",
            "requirements",
            "skills",
            "ad_interested",
        ]
        widgets = {"skills": Select2MultipleWidget}

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})

        for key, field in self.fields.items():
            if key in ["state", "salary_range", "job_level"]:
                field.choices = field.choices[:-1]


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "subject", "email", "message"]


class RegisterForm(UserCreationForm):
    github = forms.URLField(
        widget=forms.TextInput(
            attrs={"placeholder": "Preencha com o link do seu GitHub (não obrigatório)"}
        ),
        required=False,
    )

    linkedin = forms.URLField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Preencha com o link do seu Linkedin (não obrigatório)"
            }
        ),
        required=False,
    )

    portfolio = forms.URLField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Preencha com o link do seu portfolio (não obrigatório)"
            }
        ),
        required=False,
    )

    cellphone = forms.CharField(
        label="Celular",
        widget=forms.TextInput(attrs={"placeholder": "Preencha com o seu telefone"}),
        required=True,
    )

    skills_ = forms.ModelMultipleChoiceField(
        label="Skills", queryset=Skill.objects.all(), widget=Select2MultipleWidget
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        for fieldname in ["password1", "password2"]:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        instance = super(RegisterForm, self).save(commit=False)
        if commit:
            instance.save()

            profile = Profile(
                user=instance,
                github=self.cleaned_data["github"],
                linkedin=self.cleaned_data["linkedin"],
                portfolio=self.cleaned_data["portfolio"],
                cellphone=self.cleaned_data["cellphone"],
            )
            authenticate(
                username=instance.username, password=self.cleaned_data.get("password1")
            )
            profile.save()
            profile.skills = self.cleaned_data["skills_"]
            profile.save()
        return instance


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("github", "linkedin", "portfolio", "cellphone", "skills")
        widgets = {"skills": Select2MultipleWidget}
