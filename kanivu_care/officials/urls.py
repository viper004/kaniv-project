from django.urls import path
from . import views

app_name = 'officials'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-official/', views.add_official, name='add_official'),
    path('financial-oversight/', views.financial_oversight, name='financial_oversight'),
    path('report-requests/', views.report_requests, name='report_requests'),
    path('fund-requests/', views.fund_requests, name='fund_requests'),
    path('approve-fund/<int:pk>/', views.approve_fund_request, name='approve_fund_request'),
    path('view-report-requests/', views.view_report_requests, name='view_report_requests'),
    path('complete-report-request/<int:pk>/', views.complete_report_request, name='complete_report_request'),
]
