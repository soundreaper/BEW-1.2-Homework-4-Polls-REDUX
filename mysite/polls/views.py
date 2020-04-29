from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .forms import QuestionCreateForm, ChoiceCreateForm

from .models import Choice, Question

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choice_form'] = ChoiceCreateForm()
        return context

    def post(self, request, pk):
        form = ChoiceCreateForm(request.POST)
        if form.is_valid:
            choice = form.save(commit=False)
            choice.question = Question.objects.get(pk=pk)
            choice.save()
            return HttpResponseRedirect(reverse('polls:detail', args=[pk]))
        # else if form is not valid
        context = {
          'choice_form': form,
          'question': Question.objects.get(pk=pk)
        }
        return render(request, 'polls/detail.html', context)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

class QuestionCreateView(LoginRequiredMixin, generic.edit.CreateView):
    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        context = {
          'form': QuestionCreateForm()
        }
        return render(request, 'polls/create.html', context)

    def post(self, request, *args, **kwargs):
        form = QuestionCreateForm(request.POST)
        if form.is_valid:
            question = form.save(commit=False) # don't save the question yet
            question.author = request.user
            question.save()
            return HttpResponseRedirect(
                reverse('polls:detail', args=[question.id]))
        # else if form is not valid
        return render(request, 'polls/create.html', { 'form': form })