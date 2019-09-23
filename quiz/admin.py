from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Question, Reservation, Player, Answer
from .forms import PlayerCreationForm, PlayerChangeForm


class PlayerAdmin(BaseUserAdmin):
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

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)


class ReservationInline(admin.TabularInline):
    model = Reservation
    readonly_fields = ('question', 'player', 'reservation_date', )

    # Order by reservation date
    ordering = ('reservation_date',)

    def has_add_permission(self, request):
        """Admin cannot add reservations. """
        return False

    def has_delete_permission(self, request, obj=None):
        """Admin cannot delete reservations. """
        return False


class AnswerInline(admin.StackedInline):
    model = Answer
    readonly_fields = ('question', 'player', 'creation_date', )

    # Order by reservation date
    ordering = ('creation_date',)

    def has_add_permission(self, request):
        """Admin cannot add answers. """
        return False

    def has_delete_permission(self, request, obj=None):
        """Admin cannot delete reservations. """
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Tells Django the options we want when you register the object. """
    #fields = ('question_text', 'creation_date', 'status',)
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
    list_display = ('question_text', 'creation_date', 'status',)

    # Activate filters in the right sidebar of the change list page
    list_filter = ['creation_date', 'status']

    # Enable a search box
    #search_fields = ['question_text']

    # Display as non-editable
    readonly_fields = ('creation_date',)

    # Order by creation_date
    ordering = ('creation_date',)

    # Make other models editable on the same page as a parent model
    inlines = [ReservationInline, AnswerInline]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Tells Django the options we want when you register the object. """

    readonly_fields = ('question', 'player', 'reservation_date',)

    fieldsets = (
        ('Linked to', {
            'classes': ('wide',),
            'fields': ('question', 'player'),
        }),
        ('Addition information', {
            'classes': ('wide',),
            'fields': ('reservation_date', 'approved'),
        }),
    )

    list_display = ('id', 'question_text', 'player', 'approved',)

    # Order by creation_date
    ordering = ('reservation_date',)

    def question_text(self, x):
        return x.question.question_text
    question_text.short_description = 'question text'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Tells Django the options we want when you register the object. """

    readonly_fields = ('question', 'player', 'creation_date',)

    fieldsets = (
        (None, {
            'fields': ('answer_text',)
        }),
        ('Addition information', {
            'classes': ('wide',),
            'fields': ('creation_date', 'status'),
        }),
        ('Linked to', {
            'classes': ('wide',),
            'fields': ('question', 'player'),
        }),
    )

    list_display = ('id', 'question_text', 'player', 'status',)

    # Order by creation_date
    ordering = ('creation_date',)

    def question_text(self, x):
        return x.question.question_text
    question_text.short_description = 'question text'




