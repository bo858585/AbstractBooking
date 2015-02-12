from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


class HomepageView(TemplateView):
    template_name = "homepage.html"


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)
