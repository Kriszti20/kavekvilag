# context_processors.py
def user_context(request):
    return {
        'user': request.user  # A bejelentkezett felhasználó elérhető lesz, vagy AnonymousUs
    }