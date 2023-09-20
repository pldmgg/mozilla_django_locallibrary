from django.urls import path, re_path
from . import views

urlpatterns = [
    # Index/Home Page Url implementation
    path('', views.index, name='index'),
    
    #### BEGIN Book Views ####
    ## IMPORTANT: Original BooksListView path implementation ##
    # path('books/', views.BookListView.as_view(), {'template_name': 'books.html'}, name='books'),
    # The use of dictionary {'template_name': 'books.html'} demonstrates that we can pass additional options to the...
    # ...views.BookListView.as_view() function. So, the above path() statement would be the same as...
    # path('books/', views.BookListView.as_view(template_name='your_template.html'), name='books'),

    ## Shortened BooksListView implementation. ##
    # This demonstrates that the 3rd argument is not necessary because books.html is implied via the "name=" argument
    path('books/', views.BookListView.as_view(), name='books'),

    # BookDetailView Page Url implementation
    # Without regex
    #path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    # With Regex
    re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),

    # Books On Loan for the logged in user
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),

    # All Books On Loan
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),

    # Renew Books Page
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),

    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    #### END Book Views ####

    #### BEGIN Author Views ####
    # AuthorListView Page Url implementation
    path('authors/', views.AuthorListView.as_view(), name='authors'),

    # AuthorDetailView Page Url implementation
    # Without regex
    #path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    # With Regex
    re_path(r'^author/(?P<pk>\d+)$', views.AuthorDetailView.as_view(), name='author-detail'),

    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
    #### END Author Views ####
]