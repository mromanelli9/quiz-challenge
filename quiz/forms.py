#!/usr/bin/env python

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext as _

from .models import Player, Answer


class PlayerCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Player
        fields = ('nickname',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        player = super().save(commit=False)
        player.set_password(self.cleaned_data["password1"])

        if commit:
            player.save()

        return player

class PlayerChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Player
        fields = ('nickname', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

from crispy_forms.helper import FormHelper

class AnswerCreationForm(forms.ModelForm):
    """
    A form for creating new answers.
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
        answer = super().save(commit=False)

        if commit:
            answer.save()

        return answer