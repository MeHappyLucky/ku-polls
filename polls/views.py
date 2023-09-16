from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
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

    def get(self, request, *args, **kwargs):

        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, "Question does not exist")
            return redirect("polls:index")

        try:
            vote = Vote.objects.get(user=request.user, choice__in=self.object.choice_set.all())
            selected_choice = vote.choice
        except (Vote.DoesNotExist, TypeError):
            selected_choice = ""

        if not self.object.can_vote():
            return render(request, 'polls/results.html',
                          {'question': self.object, 'message': "Vote closed."})

        return render(request, self.template_name,
                      {"question": self.object, "selected_choice": selected_choice})


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
    messages.success(request, f'Your vote for "{question.question_text}" has been saved')
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
        return redirect('polls:index')
        # what if form is not valid?
        # we should display a message in signup.html
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
