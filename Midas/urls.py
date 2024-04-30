from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import include
from usuarios.views import index, EmConstrucaoView
from django.contrib.auth.views import LoginView, LogoutView



urlpatterns = [
    path('', index, name='index'),
    path('wall_street/', admin.site.urls),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('despesas/', include('despesas.urls')),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('em_construcao/', EmConstrucaoView.as_view(), name='em_construcao'),
    path('relatorios/', include('relatorios.urls')),

]
