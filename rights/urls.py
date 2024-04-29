from django.urls import path
from .views import RightsView

urlpatterns = {
    path('rights/<user_id>/', RightsView.as_view()),  # GET, PUT
    path('rights', RightsView.as_view()),  # POST
}
