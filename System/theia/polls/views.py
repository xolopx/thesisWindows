from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from .models import Question, Choice
from django.urls import reverse


def index(request):
    return HttpResponse("Hello world. You're a the polls index.")


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)                   # Get the question using the question id from the url passed to the view. Throw 404 if doesn't exist.
    return render(request, 'polls/detail.html', {'question': question})      # Render the Response and return.


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


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


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]       # Retrieve the latest question list (logic = backend).
    template = loader.get_template('polls/index.html')                      # Retrieve template for web-page design (appearance = frontend).
    context = {                                                             # Context passes the information to the web-page and give it a label corresponding to what's found on web-page.
        'latest_question_list': latest_question_list,
    }
    # return HttpResponse(template.render(context, request))                  # We pass the response back to urls.py so that it can be like processed or something.

    return render(request, 'polls/index.html', context)                       # Returns a HttpResponse object of the given template rendered with the given context.




