from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
urlpatterns=[
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('book/', views.book_table, name='book_table'),
    path('signup/', views.signup_view, name='signup'),
   path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
   path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

