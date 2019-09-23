#!/usr/bin/env python

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from .models import Question, Reservation, Player, Answer
from .forms import PlayerCreationForm, AnswerCreationForm


def index(request):
    return render(request, 'quiz/index.html')


@login_required()
def question_home(request):
    """
    This represents the first page that starts the quiz.
    Here we query for availables questions and, based on that,
    we show the question page or a special one for no questions.

    Args:
        request: Web request.

    Returns:
        A Web response.

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
    The player should arrive here from quiz:question
    after having reserved the question.
    That will be created here (only if it's the first time).
    Here (in an abstract way) the players waits until the admin
    approves one reservation.

    Note: TODO: Maybe the reservation object creation should
                be handled differently (forms)?

    Args:
        request: Web request.
        question_id: id of the question to show.

    Returns:
        A Web response. Redirects to quiz:question if there's no
        question with question_id.

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
        return HttpResponseRedirect(reverse('quiz:question'))

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
    This view steers the player based on if he/she won the reservation.
    If the player won it, then he/she'll be redirected to the next phase,
    where an answer will be created and submitted.
    Otherwise, another view wll show he/she that he/she lost and can
    proceed with a new question.

    Args:
        request: Web request.
        question_id: id of the question that have been reserved.

    Returns:
        A Web response.
        Redirects to quiz:provide_answer if the player won the reservation,
        otherwise tpo quiz:reservation_lost.
        Redirects back to quiz:question if there's no
        question with question_id.

    """
    try:
        question = Question.objects.get(pk=question_id)

    except (KeyError, Question.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question'))

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
    The player arrive here if he/she lost the reservation race.
    The response will show a message about this.

    Args:
        request: Web request.
        question_id: id of the current question.
        approved_player: the player who won the reservation.

    Returns:
        A Web response. Redirects to quiz:question if there's no
        question with question_id.

    """
    page_template = 'quiz/question_reservation_lost.html'

    try:
        question = Question.objects.get(pk=question_id)

    except (KeyError, Question.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question'))

    return render(request, page_template, {
        'online_players': Player.objects.get_online_players(),
        'question': question,
        'approved_player': approved_player,
        'available_questions': Question.objects.questions_available()
    })


@login_required()
def provide_answer(request, question_id, reservation_id):
    """
    Next step of the question process: providing an answer.
    An AnswerCreationForm is used to create an Answer object
    when a POST data is provided.

    Args:
        request: Web request.
        question_id: id of the current question.
        reservation_id: id of the player reservation.

    Returns:
        A Web response. Redirects to quiz:question if there's no
        question with question_id or no reservation with reservation_id.

    """
    page_template = 'quiz/question/answer.html'

    # Security checks
    try:
        question = Question.objects.get(pk=question_id)
        reservation = Reservation.objects.get(pk=reservation_id)

    except (KeyError, Question.DoesNotExist, Reservation.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question'))

    # Get the player who won the reservation
    player = reservation.player

    answer = None

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

        # Make something visual in the template to indicate
        # that the player has to wait admin
        disable_form = True

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
            form.fields['answer_text'].disabled = True     # disable modifications
            disable_form = True

        else:
            # Otherwise create an empty form to be displayed
            form = AnswerCreationForm()
            disable_form = False

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
    This view steers the player based on if he/she answered correctly.
    If it is so, then a win-message page will be shown,
    otherwise a lost-message page.

    Args:
        request: Web request.
        question_id: id of the question that have been reserved.

    Returns:
        A Web response.
        Redirects to quiz:answer_correct if the player answered correctly,
        otherwise to quiz:quiz:answer_wrong
        Redirects back to quiz:question if there's no
        question with question_id or no answer with answer_id.

    """
    page_template_answer_correct = 'quiz/question/answer_correct.html'
    page_template_answer_wrong = 'quiz/question/answer_wrong.html'

    try:
        question = Question.objects.get(pk=question_id)
        answer = Answer.objects.get(pk=answer_id)

    except (KeyError, Question.DoesNotExist, Answer.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question_home'))

    # Render template based on the answer status
    if answer.status == Answer.STATUS_APPROVED:
        return render(request, page_template_answer_correct, {
            'online_players': Player.objects.get_online_players(),
            'question': question,
            'available_questions': Question.objects.questions_available(),
            'answer_id': answer_id
        })

    elif answer.status == Answer.STATUS_REJECTED:
        # Otherwise, to the lost page
        return render(request, page_template_answer_wrong, {
            'online_players': Player.objects.get_online_players(),
            'question': question,
            'available_questions': Question.objects.questions_available(),
            'answer_id': answer_id
        })

    else:
        # We should never be here, but handle it just in case
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question_home'))


@login_required()
def answer_correct(request, question_id, answer_id):
    """
    The player arrive here if he/she answered correctly.
    The response will show a message about this.

    Args:
        request: Web request.
        question_id: id of the question.
        answer_id: id of the answer.

    Returns:
        A Web response.
        Redirects back to quiz:question if there's no
        question with question_id or no answer with answer_id.

    """
    page_template = 'quiz/question/answer_correct.html'

    try:
        question = Question.objects.get(pk=question_id)
        answer = Question.objects.get(pk=answer_id)

    except (KeyError, Question.DoesNotExist, Answer.DoesNotExist):
        # TODO: display a message
        return HttpResponseRedirect(reverse('quiz:question'))

    # Return the 'you won' page
    return render(request, page_template, {
        'online_players': Player.objects.get_online_players(),
        'question': question,
        'form': form,
        'available_questions': Question.objects.questions_available(),
        'disable_form': disable_form,
        'answer_id': answer.id if answer else None
    })


def signup(request):
    page_template = 'quiz/account/signup.html'

    if request.method == 'POST':
        form = PlayerCreationForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.is_active = True
            player.save()
            # messages.success(request, 'Account created successfully')

            user = authenticate(
                username=player.nickname,
                password=form.cleaned_data.get('password1')
            )

            if user:
                login(request, user)

                return HttpResponseRedirect(reverse('quiz:question'))

            else:
                messages.warning(request,
                                 'Something went wrong with the '
                                 'authentication.'
                                 )

                return HttpResponseRedirect(reverse('quiz:login'))

    else:
        form = PlayerCreationForm()

    return render(request, page_template, {
        'form': form,
    })