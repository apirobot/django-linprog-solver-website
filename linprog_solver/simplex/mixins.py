from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from django.shortcuts import redirect, render_to_response

from .exceptions import SimplexInitException
from .utils import generate_latex_result


class SimplexInitMixin:

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except SimplexInitException as error:
            messages.add_message(request, messages.ERROR, str(error))
            return redirect('simplex:init')


class SimplexSolveActionMixin:
    template_name_success = 'simplex/simplex_result.html'

    def form_valid(self, form):
        """
        If the form is valid, solve linear programming problem.
        """
        solution = form.solve()
        if solution['success']:
            latex_result = generate_latex_result(
                form.get_values_of_objective_function_coefficients(),
                form.cleaned_data['tendency'],
                form.get_values_of_constraints(),
                solution,
            )
            return render_to_response(self.template_name_success, {'result': latex_result})
        else:
            messages.add_message(self.request, messages.ERROR,
                                 _("The algorithm can't find an optimal solution."))
            return self.render_to_response(self.get_context_data(form=form))