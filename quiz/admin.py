#!/usr/bin/env python

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Question, Reservation, Player, Answer
from .forms import PlayerCreationForm, PlayerChangeForm


class PlayerAdmin(BaseUserAdmin):
    """Define a new (Player) Admin."""
    # The forms to add and change user instances
    form = PlayerChangeForm
    add_form = PlayerCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('nickname', 'email', 'date_joined', 'is_admin')
    list_filter = ('is_admin', 'is_active')
    fieldsets = (
        (None, {'fields': ('nickname', 'password')}),
        ('Personal info', {'fields': ('date_joined',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nickname', 'email', 'password1', 'password2')}
        ),
    )
    search_fields = ('nickname',)
    ordering = ('nickname',)
    filter_horizontal = ()

    readonly_fields = ('date_joined',)


# Now register the new UserAdmin...
admin.site.register(Player, PlayerAdmin)

# and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)


class ReservationInline(admin.TabularInline):
    """
    Define an inline admin descriptor for :model:`quiz.Reservation` model.
    This will be used to show all the question workflow (list reservation,
    approve, list answer, approve) on the question admin page.
    """
    model = Reservation
    readonly_fields = ('question', 'player', 'reservation_date', )

    # Order by reservation date
    ordering = ('reservation_date',)

    def has_add_permission(self, request, obj=None):
        """Admin should not add reservations."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Admin should not delete reservations. """
        return False


class AnswerInline(admin.StackedInline):
    """
    Define an inline admin descriptor for :model:`quiz.Answer` model.
    This will be used to show all the question workflow (list reservation,
    approve, list answer, approve) on the question admin page.
    """
    model = Answer
    readonly_fields = ('question', 'player', 'creation_date', )

    # Order by reservation date
    ordering = ('creation_date',)

    def has_add_permission(self,  request, obj=None):
        """Admin should not add answers."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Admin should not add answers. """
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Define an admin descriptor for :model:`quiz.Question` model.
    Almost the entire question workflow works around this descriptor.
    Withing this, we list also inline descriptors for
    :model:`quiz.Reservation` and :model:`quiz.Answer`.
    """
    fieldsets = (
        (None, {
            'fields': ('question_text', 'status'),
        }),
        ('Addition information', {
            'classes': ('wide',),
            'fields': ('creation_date',),
        }),
    )

    # Control which fields are displayed on the change list page
    # note: By default, Django displays the str() of each object
    list_display = ('id', 'cropped_question_text', 'creation_date', 'status',)

    # Activate filters in the right sidebar of the change list page
    list_filter = ['creation_date', 'status']

    # Enable a search box
    # search_fields = ['question_text']

    # Display as non-editable
    readonly_fields = ('creation_date',)

    # Order by creation_date
    ordering = ('creation_date',)

    # Make other models editable on the same page as a parent model
    inlines = [ReservationInline, AnswerInline]

    def cropped_question_text(self, x):
        """Returns a cropped question text at 30 chars."""
        return x.question_text[:30]
    cropped_question_text.short_description = 'question text'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Define the (full) admin descriptor for :model:`quiz.Reservation` model.
    """
    fieldsets = (
        (None, {
            'fields': ('approved',)
        }),
        ('Linked to', {
            'classes': ('wide',),
            'fields': ('question', 'player'),
        }),
        ('Addition information', {
            'classes': ('wide',),
            'fields': ('reservation_date',),
        }),
    )

    list_display = ('id', 'cropped_question_text', 'player', 'approved',)

    readonly_fields = ('question', 'player', 'reservation_date',)

    # Order by creation_date
    ordering = ('reservation_date',)

    def cropped_question_text(self, x):
        """Returns a cropped question text at 30 chars."""
        return x.question.question_text[:30]
    cropped_question_text.short_description = 'question text'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """
    Define the (full) admin descriptor for :model:`quiz.Answer` model.
    """
    fieldsets = (
        (None, {
            'fields': ('answer_text', 'status')
        }),
        ('Referred to', {
            'classes': ('wide',),
            'fields': ('question', 'player'),
        }),
        ('Addition information', {
            'classes': ('wide',),
            'fields': ('creation_date',),
        }),
    )

    readonly_fields = ('question', 'player', 'creation_date',)

    list_display = ('id', 'cropped_answer_text', 'question_id',
                    'player', 'status',)

    # Order by creation_date
    ordering = ('creation_date',)

    def cropped_answer_text(self, x):
        """Returns a cropped answer text at 30 chars."""
        return x.answer_text[:30]
    cropped_answer_text.short_description = 'answer text'

    def question_id(self, x):
        """Returns a the :model:`quiz.Question` id."""
        return x.question.id
    question_id.short_description = 'question id'






