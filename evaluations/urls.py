from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.dashboard_password, name='dashboard_password'),
    path('rankings/', views.rankings_view, name='rankings'),
    path('group/<int:pk>/', views.group_detail, name='group_detail'),
    path('evaluate/', views.eval_landing, name='eval_landing'),
    path('evaluate/<str:role>/', views.eval_form, name='eval_form'),
    path('evaluate/<str:role>/password/', views.eval_password, name='eval_password'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('admin-clear/', views.clear_data, name='clear_data'),
]
