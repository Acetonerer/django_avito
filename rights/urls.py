from django.urls import path
from .views import RightsView

urlpatterns = [
    path('rights/<user_id>/', RightsView.as_view()),
]
