from django.urls import path, include



urlpatterns = [

    path('plotly_dash/', include('django_plotly_dash.urls')),
]