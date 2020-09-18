from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


app_name = 'shelf '
urlpatterns = [
    path('shelf/create/', login_required(views.ShelfCreateView.as_view()), name='shelf/create/'),
    path('shelf/all/', login_required(views.ShelfListView.as_view()), name='shelf/all/'),
    path('shelf/<int:pk>/', login_required(views.ShelfDetailView.as_view()), name='shelf/'),
    path('shelf/<int:pk>/delete/', login_required(views.ShelfDeleteView.as_view()), name='shelf/delete/'),
    path('shelf/<int:pk>/edit/', login_required(views.ShelfUpdateView.as_view()), name='shelf/edit/'),

    path('bookcase/create/', login_required(views.BookCaseCreateView.as_view()), name='bookcase/create/'),
    path('bookcase/all/', login_required(views.BookCaseListView.as_view()), name='bookcase/all/'),
    path('bookcase/<int:pk>/', login_required(views.BookCaseDetailView.as_view()), name='bookcase/'),
    path('bookcase/<int:pk>/delete/', login_required(views.BookCaseDeleteView.as_view()), name='bookcase/delete/'),
    path('bookcase/<int:pk>/edit/', login_required(views.BookCaseUpdateView.as_view()), name='bookcase/edit/'),

    path('author/create/', login_required(views.AuthorCreateView.as_view()), name='author/create/'),
    path('author/all/', login_required(views.AuthorListView.as_view()), name='author/all/'),
    path('author/<int:pk>/', login_required(views.AuthorDetailView.as_view()), name='author/'),
    path('author/<int:pk>/delete/', login_required(views.AuthorDeleteView.as_view()), name='author/delete/'),
    path('author/<int:pk>/edit/', login_required(views.AuthorUpdateView.as_view()), name='author/edit/'),

    path('book/create/', login_required(views.BookCreateView.as_view()), name='book/create/'),
    path('book/all/', login_required(views.BookListView.as_view()), name='book/all/'),
    path('book/<int:pk>/', login_required(views.BookDetailView.as_view()), name='book/'),
    path('book/<int:pk>/delete/', login_required(views.BookDeleteView.as_view()), name='book/delete/'),
    path('book/<int:pk>/edit/', login_required(views.BookUpdateView.as_view()), name='book/edit/'),

    path('novel/create/', login_required(views.NovelCreateView.as_view()), name='novel/create/'),
    path('novel/all/', login_required(views.NovelListView.as_view()), name='novel/all/'),
    path('novel/<int:pk>/', login_required(views.NovelDetailView.as_view()), name='novel/'),
    path('novel/<int:pk>/delete/', login_required(views.NovelDeleteView.as_view()), name='novel/delete/'),
    path('novel/<int:pk>/edit/', login_required(views.NovelUpdateView.as_view()), name='novel/edit/'),

    path('user/register/', views.UserRegisterView.as_view(), name='user/register/'),
    path('user/detail/', login_required(views.UserDetailView.as_view()), name='user/detail/'),

]
