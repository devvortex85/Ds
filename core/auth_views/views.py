from allauth.account.views import LoginView as BaseLoginView
from allauth.account.views import SignupView as BaseSignupView
from allauth.account.views import PasswordResetView as BasePasswordResetView


class LoginView(BaseLoginView):
    """
    Custom login view that uses the consolidated auth_page.html template
    """
    template_name = "account/auth_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Sign In',
            'page_type': 'login',
            'show_sidebar': False,
        })
        return context


class SignupView(BaseSignupView):
    """
    Custom signup view that uses the consolidated auth_page.html template
    """
    template_name = "account/auth_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Sign Up',
            'page_type': 'signup',
            'show_sidebar': True,
        })
        return context


class PasswordResetView(BasePasswordResetView):
    """
    Custom password reset view that uses the consolidated auth_page.html template
    """
    template_name = "account/auth_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Password Reset',
            'page_type': 'password_reset',
            'show_sidebar': False,
            'reset_password_url': self.request.path,
        })
        return context