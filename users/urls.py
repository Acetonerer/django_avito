from django.urls import path
from .views import UserDetailView

urlpatterns = [
    path('user/<user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('user/add', UserDetailView.as_view(), name='user-add'),

]
