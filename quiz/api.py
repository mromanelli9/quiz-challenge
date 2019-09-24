#!/usr/bin/env python
"""
api.py is a subfield of views, used only for asynchronous calls
made from web pages with Ajax and jQuery.
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import Question, Answer


@login_required()
def api_check_question_reservation(request, question_id=None):
    """
    Return if a :model:`quiz.Question` instance is reserved, that is,
    its status is set to RESERVED.
    """
    question = get_object_or_404(Question, pk=question_id)

    return JsonResponse({
        'question_reserved': question.status == Question.STATUS_RESERVED,
    })


@login_required()
def api_check_answer_status(request, answer_id=None):
    """
    Return if a :model:`quiz.Answer` instance is confirmed, that is,
    its status set to APPROVED or REJECTED.
    """
    answer = get_object_or_404(Answer, pk=answer_id)

    return JsonResponse({
        'answer_status': answer.status != Answer.STATUS_IDLE,
    })
