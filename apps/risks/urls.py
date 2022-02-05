from django.urls import path, include
from apps.risks import views

app_name = 'risks'

urlpatterns = [
    path('record/', views.RiskRecordView.as_view(), name='risk_record'),
]