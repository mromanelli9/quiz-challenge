#!/usr/bin/env python
"""
api.py is a subfield of views, used only for asynchronous calls
made from web pages with Ajax and jQuery.
All the function names start with 'api_' prefix to enforce the fact
that are not django views.
"""
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Question, Reservation, Answer


@login_required()
def api_check_reservation_status(request):
    """
    Check the status (approved or not) of a specific reservation.

    Args:
        request: Web request.

    Returns:
        A json data.

    """
    question_id = request.GET.get('question_id', None)

    # Proceed only if input data is available
    if question_id is None:
        response = JsonResponse({
            'error': 'No input data provided.'
        })
        response.status_code = 400

        return response

    # Check if input data is plausible
    try:
        # Get the input question
        question = Question.objects.get(pk=question_id)


    except (KeyError, Question.DoesNotExist) as err:
        response = JsonResponse({
            'error': 'There is no such question.'
        })
        response.status_code = 400

        return response

    # Now, query if there are reservation approved for this question.
    reservations_approved = Reservation.objects.filter(
        question=question, approved=True
    )

    # Set 'is_question_reserved' to True if the above query
    # dind't return and empty set (thus, the reservation is approved)
    return JsonResponse({
        'is_question_reserved': not not reservations_approved
    })


@login_required()
def api_check_answer_status(request):
    """
    Check the status (approved or not) of a specific answer.

    Args:
        request: Web request.

    Returns:
        A json data.

    """
    answer_id = request.GET.get('answer_id', None)

    # Proceed only if input data is available
    if answer_id is None:
        response = JsonResponse({
            'error': 'No input data provided.'
        })
        response.status_code = 400

        return response

    # Check if input data is plausible
    try:
        # Get the input question
        answer = Answer.objects.get(pk=answer_id)

    except (KeyError, Answer.DoesNotExist) as err:
        response = JsonResponse({
            'error': 'There is no such question.'
        })
        response.status_code = 400

        return response

    answer_been_checked = False if (answer.status == Answer.STATUS_IDLE) \
        else True

    # Now, check if the answer has been approved
    return JsonResponse({
        'is_answer_been_checked': answer_been_checked,
    })
