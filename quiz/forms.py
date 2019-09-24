#!/usr/bin/env python

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import Player, Answer


class PlayerCreationForm(forms.ModelForm):
    """
    A custom form for creating new :model:`quiz.Player` instance.
    Includes all the required fields, plus a repeated password.
    """
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput
    )

    class Meta:
        model = Player
        fields = ('nickname',)

    def clean_password2(self):
        """
        Check that the two password entries match and return
        the verified password.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """
        Save the provided password in hashed format.
        Return an instance of :model:`quiz.Player`.
        """
        player = super().save(commit=False)
        player.set_password(self.cleaned_data["password1"])

        if commit:
            player.save()

        return player


class PlayerChangeForm(forms.ModelForm):
    """
    A form for update a :model:`quiz.Player` instance.
    Includes all the fields on the user, but replaces the password field
    with admin's password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Player
        fields = ('nickname', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        """Return the initial password."""
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AnswerCreationForm(forms.ModelForm):
    """
    A custom form for creating new :model:`quiz.Answer` instances.
    Includes all the required fields.
    """
    answer_text = forms.CharField(
        label='Answer',
        widget=forms.Textarea(attrs={'rows':4}),
    )

    class Meta:
        model = Answer
        fields = ('answer_text',)

    def save(self, commit=True):
        """
        Override default Django save method.
        Return a instance of :model:`quiz.Answer`.
        """
        answer = super().save(commit=False)

        if commit:
            answer.save()

        return answer
