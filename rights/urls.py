from django.urls import path
from .views import RightsView

urlpatterns = {
    path("rights/<user_id>/", RightsView.as_view(), name="rights-detail"),  # GET, PUT
    path("rights", RightsView.as_view(), name="rights-add"),  # POST
}
