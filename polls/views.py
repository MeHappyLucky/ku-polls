from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    """ Displays a list of the latest published questions. """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """ Displays details of a specific question. """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """ Displays the results of a specific question. """
    model = Question
    template_name = 'polls/results.html'


@login_required
def vote(request, question_id):
    """ This function handles the voting actions. """

    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    # selected_choice.votes += 1
    # selected_choice.save()
    this_user = request.user
    # TODO: confirm the logic of this try and except
    #  : this was put to made sure that one user have one vote
    try:
        # if exists, the user already cast their vote
        # find a vote for this user and this question
        this_vote = Vote.objects.get(user=this_user, choice__question=question)
        # update their vote
        this_vote.choice = selected_choice
    except Vote.DoesNotExist:
        # if DoesNotExist, add it.
        # No matching vote: the user have yet to vote
        # add a new vote
        this_vote = Vote(user=this_user, choice=selected_choice)

    this_vote.save()
    # TODO: Use messages to display a confirmation on the results page.

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
