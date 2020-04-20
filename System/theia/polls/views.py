from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from .models import Question, Choice
from django.urls import reverse
from django.views import generic
from django.utils import timezone


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions"""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)                          # get the question and the id or throw 404.
    try:                                                                            # Try and send choice to server side for storage.
        selected_choice = question.choice_set.get(pk=request.POST['choice'])        # Set the choice.
    except (KeyError, Choice.DoesNotExist):                                         # If the choice doesn't exist or unselected throw exception.
        return render(request, 'polls/detail.html', {                               # Render a response to the exception and return.
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:                                                                           # Else.
        selected_choice.votes += 1                                                  # Increment number of votes for that choice.
        selected_choice.save()                                                      # Save the result of the selection.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))  # Return a response for the selection.
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
