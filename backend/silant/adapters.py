from allauth.account.adapter import DefaultAccountAdapter

class NoSignupAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Регистрация только через админку
        return False
