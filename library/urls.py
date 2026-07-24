from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('books/', views.book_list, name='book_list'),
    path('books/form/', views.book_form, name='book_form'),
    path('books/add/', views.book_form, name='book_add'),
    path('books/edit/<int:id>/', views.book_form, name='book_edit'),
    path('books/delete/<int:id>/', views.book_delete, name='book_delete'),
    path('books/borrow/<int:id>/', views.borrow_book, name='borrow_book'),
    path('books/return/<int:id>/', views.return_book, name='return_book'),
    path('borrowed/', views.borrowed_books, name='borrowed_books'),
    path('search/', views.search_books, name='search_books'),
    path('fines/', views.fines, name='fines'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
]
