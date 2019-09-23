#!/usr/bin/env python

from django.db import models, IntegrityError
from django.db.models.query import QuerySet
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone
from django.contrib.sessions.models import Session


class PlayerManager(BaseUserManager):
    def create_user(self, nickname, email='', password=''):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not nickname:
            raise ValueError('Users must have a nickname.')

        player = self.model(nickname=nickname, email=email)
        player.set_password(password)
        player.save(using=self._db)

        return player

    def create_superuser(self, nickname, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
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
        Get the list of current players that are not an admin.

        Note: We assume that the session ends when closing the browser.
            SESSION_EXPIRE_AT_BROWSER_CLOSE has to be set to False
            in settings.py.

        Returns:
            A QuerySet with the current players.

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
    nickname = models.CharField(max_length=255, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=False,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)

    objects = PlayerManager()

    USERNAME_FIELD = 'nickname'

    # A list of the field names that will be prompted
    # for when creating a user via the createsuperuser management command.
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        """ Does the user have a specific permission? """
        return self.is_admin

    def has_module_perms(self, app_label):
        """ Does the user have permissions to view the app `app_label`? """
        return self.is_admin

    @property
    def is_staff(self):
        """ Is the user a member of staff? """
        return self.is_admin


class QuestionManager(models.Manager):
    def questions_available(self):
        query = QuerySet(self.model, using=self._db)

        return query.filter(status=Question.STATUS_LIVE).count()


class Question(models.Model):
    """
    Question's model: a question is created by the admin and can be answered
    by a player if reserved and approved by the admin.

    Attributes:
        STATUS_IDLE: Indicates that the question is created
                    but not yet displayed to the players.
        STATUS_LIVE: The player are reserving the question.
        STATUS_RESERVED: One player has reserved the question.
        STATUS_CLOSED: When a player has successfully answered a question.
        STATUS_CHOICES: A tuple encapsulating all the statuses.
        question_text: The content of the question.
        creation_date: Date and time of the question creation.
        status: Indicates in which status the question is.

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
        """Actions to perform before delete an istance of Question. """
        # Prevent delete if a question is 'Live' or 'Reserved'
        if ((self.status == Question.STATUS_LIVE) or
                (self.status == Question.STATUS_RESERVED)):
            raise PermissionDenied('You should not delete a question \
                                    if is \'Live\' or \'Reserved!\'')
        else:
            # No worries, you can delete it safely
            super(Question, self).delete(*args, **kwargs)

    def __str__(self):
        #return f'\'{self.question_text}\''
        return f'#{self.id}'


class ReservationManager(models.Manager):
    def create_reservation(self, question, player):
        reservation = self.model(
            question=question,
            player=player,
        )

        reservation.save(using=self._db)

        return reservation

class Reservation(models.Model):
    """
    Reservation's model: represents a user making a reservation
    for a specific question.

    Attributes:
        question: Links to the question.
        player: Links to the player.
        reservation_date: Date and time of the reservation.
        approved: If the reservation is approved, then the player
                can send an answer.

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
        # When saving a reservation, we need also to change
        # the question status as well.
        self._update_question_status()

        # Call parent save method
        super(Reservation, self ).save(*args,**kw )

    def _update_question_status(self):
        """
        Change question status to 'RESERVED' if a reservation has been
        approved and to 'LIVE' if the approval has been revoked.
        """
        if self.approved:
            self.question.status = Question.STATUS_RESERVED
        else:
            self.question.status = Question.STATUS_LIVE

        # Call question save method to make changes permanent
        self.question.save()

    def __str__(self):
        #return f'made by {self.player.nickname} on question {self.question}'
        return f'#{self.id}'


class Answer(models.Model):
    """
    Answer's model: an answer given to specific question tied to a reservation
    (one can answer only after a reservation and the approval from the admin).

    Attributes:
        answer_text: Text that contain the answer to a question.
        question: Links to the question.
        reservation: Links to the reservation.
        creation_date: Date and time of the question creation.
        STATUS_IDLE: The answer has just been created and thus is not approved
                    nor rejected.
        STATUS_APPROVED: Indicates that the answer is correct and thus approved.
        STATUS_REJECTED: The question is wrong and thus denied.
        status: Indicates in which status the answer is.
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
        # When saving a reservation, we need also to change
        # the question status as well.
        self._update_question_status()

        # Call parent save method
        super(Answer, self ).save(*args,**kw )

    def _update_question_status(self):
        """
        Change question status to 'CLOSED' if the answer has been
        approved or rejected.
        """
        if self.status == self.STATUS_IDLE:
            self.question.status = Question.STATUS_RESERVED
        else:
            self.question.status = Question.STATUS_CLOSED

        # Call question save method to make changes permanent
        self.question.save()

    def __str__(self):
        return f'#{self.id}'