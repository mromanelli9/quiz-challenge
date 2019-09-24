#!/usr/bin/env python

from django.db import models, IntegrityError
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone
from django.contrib.sessions.models import Session


class PlayerManager(BaseUserManager):
    """
    The Player manager overrides :model:`auth.BaseUserManager` methods for
    object creation, specifically for creating a user and a superuser.
    """
    def create_user(self, nickname, email='', password=None):
        """
        Returns a :model:`quiz.Player` given nickname, email and password.
        """
        if not nickname:
            raise ValueError('Users must have a nickname.')

        player = self.model(nickname=nickname, email=email)
        player.set_password(password)
        player.save(using=self._db)

        return player

    def create_superuser(self, nickname, email, password):
        """
        Returns a :model:`quiz.Player` with admin permissions, given nickname,
        email and password.
        """
        player = self.create_user(
            nickname=nickname,
            email=email,
            password=password,
        )
        player.is_admin = True
        player.save(using=self._db)

        return player

    @classmethod
    def get_online_players(cls):
        """
        Returns a :model:`query.QuerySet` with a list of current players
        that are not an admin.

        Note: We assume that the session ends when closing the browser.
            SESSION_EXPIRE_AT_BROWSER_CLOSE has to be set to False
            in settings.py.

        """
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())
        players_id_list = []

        for session in active_sessions:
            data = session.get_decoded()
            players_id_list.append(data.get('_auth_user_id', None))

        # Query all logged in users based on id list
        return Player.objects.filter(
            is_admin=False,
            id__in=players_id_list,
        )

class Player(AbstractBaseUser):
    """
    Encapsulate a classic player of the game, referred usually
    by its nickname.

    Note: when using the django shell or the admin panel to create
        a new player, it'll required to provide the email address.
    """
    nickname = models.CharField(max_length=255, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=False,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)

    # Model's manager
    objects = PlayerManager()

    # Name of the field used ad unique identifier.
    USERNAME_FIELD = 'nickname'

    # A list of the field names that will be prompted
    # for when creating a user via the createsuperuser management command.
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return self.is_admin

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return self.is_admin

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin


class QuestionManager(models.Manager):
    """
    The :model:`quiz.Question` manager provides a query shortcut
    to retrieve the question with LIVE status, aka available for the players.
    """
    def questions_available(self):
        """Returns a :model:`query.QuerySet` with the live questions."""
        query = models.query.QuerySet(self.model, using=self._db)

        return query.filter(status=Question.STATUS_LIVE).count()


class Question(models.Model):
    """
    A Question can be created only by the admin. Has a text, a creation date
    and a status.
    The status indicates in which 'phase' the question is: IDLE is for when
    that the question is created but not yet displayed to the players.
    When is LIVE then is ready to be shown to players.
    Is RESERVED when the admin has approved a reservation by a certain player.
    When is (correctly or not) answered then is CLOSED.
    """
    STATUS_IDLE = 0
    STATUS_LIVE = 1
    STATUS_RESERVED = 2
    STATUS_CLOSED = 3
    STATUS_CHOICES = (
        (STATUS_IDLE, 'Idle'),
        (STATUS_LIVE, 'Live'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_CLOSED, 'Closed'),
    )

    question_text = models.TextField()
    creation_date = models.DateTimeField('creation date', auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_IDLE)

    objects = QuestionManager()

    def delete(self, *args, **kwargs):
        """
        Actions to perform before deletion an instance of Question.
        Raises a PermissionDenied exception if the question is currently
        shown to players (status LIVE or RESERVED).
        """
        # Prevent delete if a question is 'Live' or 'Reserved'
        if ((self.status == Question.STATUS_LIVE) or
                (self.status == Question.STATUS_RESERVED)):
            raise PermissionDenied('You should not delete a question \
                                    if is \'Live\' or \'Reserved!\'')
        else:
            # No worries, you can delete it safely
            super(Question, self).delete(*args, **kwargs)

    def __str__(self):
        # Crop the displayed text to the first 30 chars,
        # in case the question is long.
        return self.question_text[:30]


class ReservationManager(models.Manager):
    """
    The :model:`quiz.Reservation` manager provides a custom method
    to create the object from a :model:`quiz.Question`
    and a :model:`quiz.Player`.
    """
    def create_reservation(self, question, player):
        reservation = self.model(
            question=question,
            player=player,
        )

        reservation.save(using=self._db)

        return reservation

class Reservation(models.Model):
    """
    A reservation is made by a :model:`quiz.Player` for a specific
    :model:`quiz.Question`. It will allow him, if approved, to answer
    a specific question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(
        'reservation date',
        auto_now_add=True
    )
    approved = models.BooleanField(default=False)

    objects = ReservationManager()

    def save(self, *args, **kw):
        """
        The default :model:`Model` save method is here overrode
        in order to change the question status accordingly.
        """
        # First, update the question status accordingly.
        self._update_question_status()

        # Call parent save method.
        super(Reservation, self ).save(*args,**kw )

    def _update_question_status(self):
        """
        Change :model:`quiz.Question` status to 'RESERVED' if a reservation
        has been approved and to 'LIVE' if the approval has been revoked.
        """
        if self.approved:
            self.question.status = Question.STATUS_RESERVED
        else:
            self.question.status = Question.STATUS_LIVE

        # Call question save method to make changes permanent.
        self.question.save()

    def __str__(self):
        return f'{self.player.nickname} on question {self.question.id}'


class Answer(models.Model):
    """
    Stores the answer provided by a :model:`quiz.Player`to a
    :model:`quiz.Question`.
    An answer is also tied to a :model:`quiz.Reservation` because the player
    can only answer after an approved reservation.
    The answer has a status too: it can be APPROVED if it's correct,
    or REJECTED if it's wrong. When the player send it it's in IDLE.
    """
    STATUS_IDLE = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2
    STATUS_CHOICES = (
        (STATUS_IDLE, 'Idle'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )
    answer_text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    creation_date = models.DateTimeField('creation date', auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_IDLE)

    def save(self, *args, **kw):
        """
        The default :model:`Model` save method is here overrode
        in order to change the question status accordingly.
        """
        # First, update the question status accordingly.
        self._update_question_status()

        # Call parent save method.
        super(Answer, self ).save(*args,**kw )

    def _update_question_status(self):
        """
        Change :model:`quiz.Question` status to 'CLOSED' if the answer
        has been approved or rejected.
        """
        if self.status == self.STATUS_IDLE:
            self.question.status = Question.STATUS_RESERVED
        else:
            self.question.status = Question.STATUS_CLOSED

        # Call question save method to make changes permanent.
        self.question.save()

    def __str__(self):
        # Crop the displayed text to the first 30 chars,
        # in case the question is long.
        return self.answer_text[:30]