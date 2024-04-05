from django.urls import path
from .views import AccountView
from .views import MainView
urlpatterns = [
    path('accounts/<user_id>/<account_id>/', AccountView.as_view(), name='user_accounts'),
    path('accounts/add', AccountView.as_view(), name='add_account'),
]
