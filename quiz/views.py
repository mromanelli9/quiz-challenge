#!/usr/bin/env python

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from .models import Question, Reservation, Player, Answer
from .forms import PlayerCreationForm, AnswerCreationForm


def index(request):
    """
    Display the intro page of the app.

    **Template:**

    :template:`quiz/index.html`
    """
    return render(request, 'quiz/index.html')


@login_required()
def question_home(request):
    """
    The home page of the game, display an individual :model:`quiz.Question`.
    Allows the player to reserve it using a button.

    **Context**

    ``online_players``
        A query using the :model:`quiz.Player` manager.
    ``question``
        An instance of :model:`quiz.Question`.
    ``available_questions``
        A query using the :model:`quiz.Question` manager.

    **Template:**

    :template:`quiz/question/home.html`
        If a question is available.
    :template:`quiz/question/no_questions.html`
        If there are no LIVE questions.
    """
    # page templates
    page_template_show_question = 'quiz/question/home.html'
    page_template_no_questions = 'quiz/question/no_questions.html'

    # Check if there are new questions
    # By 'new' it means with status 'live'
    try:
        available_questions = Question.objects.filter(
            status=Question.STATUS_LIVE
        ).order_by('-creation_date')[:1]

        # Get the question to be displayed
        current_question = available_questions.get()

        # select the correct template
        page_template = page_template_show_question

    except Question.DoesNotExist:
        current_question = None
        page_template = page_template_no_questions

    return render(request, page_template, {
        'online_players': Player.objects.get_online_players(),
        'question': current_question,
        'available_questions': Question.objects.questions_available()
    })


@login_required()
def reservation(request, question_id):
    """
    The second step of the the game: the player has reserved a question.
    A :model:`quiz.Reservation` object will be created here
    (only if it's the first time).

    question_id is the id of the :model:`quiz.Question` to show.

    Redirects to :view:`quiz.question_home` if there's no
    :model:`quiz.Question` with question_id.

    **Context**

    ``online_players``
        A query using the :model:`quiz.Player` manager.
    ``question``
        An instance of :model:`quiz.Question`.
    ``available_questions``
        A query using the :model:`quiz.Question` manager.

    **Template:**

    :template:`quiz/question/reservation.html`
    """
    page_template = 'quiz/question/reservation.html'

    # Retrieve the question from the id
    try:
        question = Question.objects.get(pk=question_id)

    except (KeyError, Question.DoesNotExist):
        # TODO: display a message
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('quiz:question_home'))

    # Get auth player info
    player = request.user

    # Check if a reservation has already been made by this player
    reservation_query = Reservation.objects.filter(
        question=question,
        player=player
    ).count()

    # If this is the first time and thus it's my first reservation,
    # then create one
    if reservation_query == 0:
        reservation = Reservation.objects.create_reservation(question, player)
        # TODO: display a message

    return render(request, page_template, {
        'online_players': Player.objects.get_online_players(),
        'question': question,
        'available_questions': Question.objects.questions_available()
    })


@login_required()
def reservation_steer(request, question_id):
    """
    This view steers the player based on the reservation approval result.
    If the players won, then they'll be redirected to the next phase,
    where an answer will be created and submitted.
    Otherwise, another view wll show he/she that he/she lost and can
    proceed with a new question.

    question_id is the id of the :model:`quiz.Question` to show.

    Redirect to :view:`quiz.provide_answer` if the player won the reservation,
    otherwise to :view:`quiz.reservation_lost`.
    Redirect to :view:`quiz.question_home` if there's no question with
    question_id.

    **Context**

    ``online_players``
        A query using the :model:`quiz.Player` manager.
    ``question``
        An instance of :model:`quiz.Question`.
    ``available_questions``
        A query using the :model:`quiz.Question` manager.
    """
    try:
        question = Question.objects.get(pk=question_id)

    except (KeyError, Question.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question_home'))

    # Check if the player has won the reservation
    reservation_approved = Reservation.objects.filter(
        question=question, approved=True
    ).get()
    approved_player = str(reservation_approved.player.nickname)

    # Get authenticated/logged (current) player
    current_player = str(request.user)

    # If is the auth user that won, redirect to the answer page
    if approved_player == current_player:
        return HttpResponseRedirect(
            reverse('quiz:provide_answer',
                    args=(question.id, reservation_approved.id))
        )

    else:
        # Otherwise, to the lost page
        return HttpResponseRedirect(reverse(
                'quiz:reservation_lost',
                args=(question.id, approved_player,)
        ))


@login_required()
def reservation_lost(request, question_id, approved_player):
    """
    Display a 'you-lost' message.

    question_id is the id of the :model:`quiz.Question` to show.
    approved_player is the nickname of the :model:`quiz.Player` who
    won the reservation race.

    Redirect to :view:`quiz.question_home` if there's no
    :model:`quiz.Question` with question_id.

    **Context**

    ``online_players``
        A query using the :model:`quiz.Player` manager.
    ``question``
        An instance of :model:`quiz.Question`.
    ``approved_player``
        Nickname of a :model:`quiz.Player`.
    ``available_questions``
        A query using the :model:`quiz.Question` manager.

    **Template:**

    :template:`quiz/question/reservation_lost.html`
    """
    page_template = 'quiz/question_reservation_lost.html'

    try:
        question = Question.objects.get(pk=question_id)

    except (KeyError, Question.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question_home'))

    return render(request, page_template, {
        'online_players': Player.objects.get_online_players(),
        'question': question,
        'approved_player': approved_player,
        'available_questions': Question.objects.questions_available()
    })


@login_required()
def provide_answer(request, question_id, reservation_id):
    """
    Display the current question and the form to provide an answer.
    When data is provided, it creates a :model:`quiz.Answer` object.

    question_id is the id of the :model:`quiz.Question` to show.
    reservation_id is the id of the :model:`quiz.Reservation` linked
    to the auth player and current question.

    Redirect to :view:`quiz.question_home` if there's no
    :model:`quiz.Question` with question_id or :model:`quiz.Reservation`
    with reservation_id.

    **Context**

    ``online_players``
        A query using the :model:`quiz.Player` manager.
    ``question``
        An instance of :model:`quiz.Question`.
    ``form``
        An instance of AnswerCreationForm.
    ``available_questions``
        A query using the :model:`quiz.Question` manager.
    ``disable_form``
        A boolean for disable the button form.
    ``answer_id``
        An id of a :model:`quiz.Answer` object.

    **Template:**

    :template:`quiz/question/answer.html`
    """
    page_template = 'quiz/question/answer.html'

    # Security checks
    try:
        question = Question.objects.get(pk=question_id)
        reservation = Reservation.objects.get(pk=reservation_id)

    except (KeyError, Question.DoesNotExist, Reservation.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question_home'))

    # Get the player who won the reservation
    player = reservation.player

    # Default values: no answers and no form visible
    answer = None

    # This is used to make something visual in the template to indicate
    # that the player has to wait admin
    disable_form = False

    # If data from the post is provided
    if request.method == 'POST':
        # Create an AnswerCreationForm from POST data
        form = AnswerCreationForm(request.POST)

        # First we have to check if an answer already exist.
        # Note: only one answer allowed at this moment.
        if Answer.objects.filter(question=question).count() == 0:
            # If data is valid, create an Answer object
            if form.is_valid():
                answer = form.save(commit=False)

                # Link answer to question and player
                # TODO: Probably there's a better way
                answer.question = question
                answer.player = player

                answer.save()

                disable_form = True

            else:
                disable_form = False

    else:
        # You should think that now an empty form should be created.
        # Usually it is, but there's some cases in which the player
        # has already made an answer, then came back here.
        # In this case it's better to show his/here previous answer

        # So, first query for answer (this is also used to populate answer_id)
        answer_query = Answer.objects.filter(question=question)
        if answer_query:
            answer = answer_query.get()
            form = AnswerCreationForm(initial={
                'answer_text': answer.answer_text,
            })
            # Disable modifications.
            form.fields['answer_text'].disabled = True
            disable_form = True

        else:
            # Otherwise create an empty form to be displayed
            form = AnswerCreationForm()

    return render(request, page_template, {
        'online_players': Player.objects.get_online_players(),
        'question': question,
        'form': form,
        'available_questions': Question.objects.questions_available(),
        'disable_form': disable_form,
        'answer_id': answer.id if answer else None
    })


@login_required()
def answer_steer(request, question_id, answer_id):
    """
    Display a message to the player based on the result of the admin approval
    for the :model:`quiz.Answer` provided.

    question_id is the id of the :model:`quiz.Question` to show.
    answer_id is the id of the :model:`quiz.Answer` provided.

    Redirect to :view:`quiz.question_home` if there's no
    :model:`quiz.Question` with question_id or :model:`quiz.Answer`
    with answer_id.

    **Context**

    ``online_players``
        A query using the :model:`quiz.Player` manager.
    ``question``
        An instance of :model:`quiz.Question`.
    ``available_questions``
        A query using the :model:`quiz.Question` manager.

    **Template:**

    :template:`quiz/question/answer_correct.html`
        If the answer status is APPROVED.
    :template:`quiz/question/answer_wrong.html`
        If the answer status is REJECTED.
    """
    page_template_answer_correct = 'quiz/question/answer_correct.html'
    page_template_answer_wrong = 'quiz/question/answer_wrong.html'

    try:
        question = Question.objects.get(pk=question_id)
        answer = Answer.objects.get(pk=answer_id)

    except (KeyError, Question.DoesNotExist, Answer.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question_home_home'))

    # Render template based on the answer status
    if answer.status == Answer.STATUS_APPROVED:
        return render(request, page_template_answer_correct, {
            'online_players': Player.objects.get_online_players(),
            'question': question,
            'available_questions': Question.objects.questions_available(),
        })

    elif answer.status == Answer.STATUS_REJECTED:
        # Otherwise, to the lost page
        return render(request, page_template_answer_wrong, {
            'online_players': Player.objects.get_online_players(),
            'question': question,
            'available_questions': Question.objects.questions_available(),
        })

    else:
        # We should never be here, but handle it just in case
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question_home'))


def signup(request):
    """
    Display a PlayerCreationForm that allows the creation of a new player
    (not admin).

    Redirect to :view:`quiz.question_home` if the creation and authentication
    went well.
    Redirect to :view:`quiz.login` if an error occurred
    during the authentication.

    **Context**

    ``form``
        An instance of PlayerCreationForm.

    **Template:**

    :template:`quiz/account/signup.html`
    """
    page_template = 'quiz/account/signup.html'

    # If data is provided...
    if request.method == 'POST':
        # Populate the form.
        form = PlayerCreationForm(request.POST)
        if form.is_valid():
            # Create a new player from the form data.
            player = form.save(commit=False)
            player.is_active = True
            player.save()
            # messages.success(request, 'Account created successfully')

            # Try to authenticate the player
            user = authenticate(
                username=player.nickname,
                password=form.cleaned_data.get('password1')
            )

            # If it worked, then redirect him to the home page.
            if user:
                login(request, user)

                return HttpResponseRedirect(reverse('quiz:question_home'))

            else:
                # Otherwise he'll have to do it manually.
                # messages.warning(request,
                #                  'Something went wrong with the '
                #                  'authentication.'
                #                  )

                return HttpResponseRedirect(reverse('quiz:login'))

    else:
        # If no data (e.g. first time visiting the page),
        # create an empty form.
        form = PlayerCreationForm()

    return render(request, page_template, {
        'form': form,
    })
