from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.db.models import Q
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin # For class views
from django.contrib.auth.mixins import PermissionRequiredMixin # For class views
from django.contrib.auth.decorators import login_required, permission_required # For function views
from django.utils.decorators import method_decorator # Needed to add the above decorators to class views
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from catalog.forms import RenewBookForm
from catalog.forms import RenewBookModelForm
from catalog.forms import BookInstanceCreateForm
from catalog.forms import BookInstanceUpdateForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author
from django import forms

# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    # ManyToManyField to a related model requires .all()
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # Get count of books with Harry in the title AND in the Fantasy genre
    harry_condition = Q(title__contains='Harry')
    fantasy_condition = Q(genre__name__contains='Fantasy')
    # Combine conditions using logical operators
    # For 'AND' conditions, use '&' (bitwise AND)
    # For 'OR' conditions, use '|' (bitwise OR)
    # For 'NOT' conditions, use '~' (bitwise NOT)
    combined_conditions = harry_condition & fantasy_condition
    # Apply the filter to your model using the filter() method
    num_books_harry_fantasy = Book.objects.filter(combined_conditions).count()

    # The 'all()' is implied by default because it is not a ManyToManyField to a related model
    num_authors = Author.objects.count()

    # Session Framework Implementation: Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_books_harry_fantasy': num_books_harry_fantasy,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list' # This is how we refer to it in jinja syntax in .html templates
    paginate_by = 10 # To access page 2 you would use the URL /catalog/books/?page=2
    
    #IMPORTANT NOTE: If you don't use the "queryset" attribute or "def get_queryset(self)", then default behavior for a generic.ListView...
    #...is to return ALL associated objects for the particular model (which, in this case, would be all Book objects)

    #queryset = Book.objects.filter(title__icontains='Harry')[:3] # Get 3 books containing the title Harry
    #template_name = 'books/book_list.html'  # Specify your own template name/location

    # Override the built-in get_queryset function as an alternate way of doing queryset commented out above
    #def get_queryset(self):
    #    return Book.objects.filter(title__icontains='Harry')[:3] # Get 3 books containing the title Harry

    # Override the built-in get_context_data function as an alternate way of doing "context = {}" similar to how we did with index() above
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model = Book
    context_object_name = 'book_detail' # This is how we refer to it in jinja syntax in .html templates

class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list' # This is how we refer to it in jinja syntax in .html templates
    paginate_by = 10 # To access page 2 you would use the URL /catalog/authors/?page=2

    # Pull in data from another Model objects via the below code:
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Fetch data from the Book Model
        all_books = Book.objects.all()
        # Add additional context data here
        context['all_books'] = all_books
        return context

class AuthorDetailView(generic.DetailView):
    model = Author
    context_object_name = 'author_detail' # This is how we refer to it in jinja syntax in .html templates

class BookInstanceListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    context_object_name = 'bookinstance_list'
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_all.html'
    paginate_by = 50

    #def get_queryset(self):
    #    return BookInstance.objects.all()

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    # In order to restrict our query to just the BookInstance objects for the current user, we re-implement get_queryset()
    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )
    
class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)
        #form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # If the form is valid, the built-in django.forms.Form cleaned_data dictionary should have a key called 'renewal_date'...
            # ...which is an attribute from the class RenewBookForm we used to create 'form'.
            # The value for the 'new_due_date' key comes from user input.
            # Process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['new_due_date']
            book_instance.borrower = form.cleaned_data['new_borrower']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_due_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(
            initial = {
                'new_due_date': proposed_due_date
            }
        )
        #B#form = RenewBookModelForm(initial={'due_date': proposed_due_date})
        #form = RenewBookForm()

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


#### BEGIN Views to Create/Update/Delete Authors ####
# IMPORTANT NOTE: CreateView, UpdateView, and DeleteView all use the same syntax as
# ModelForm in forms.py
# CreateView and UpdateView automatically use a template with name <model_name>_form.html,
# In this case, that would be author_form.html
# DeleteView automatically uses a template with name <model_name>_confirm_delete.html,
# In this case that would be author_confirm_delete.html
@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'catalog/author_form.html'
    initial = {'date_of_death': '11/06/2020'}
    success_url = reverse_lazy('authors') # After form is submitted, page redirects to author_list.html
    context_object_name = 'author_object'

@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    template_name = 'catalog/author_form.html'
    success_url = reverse_lazy('authors') # After form is submitted, page redirects to author_list.html
    context_object_name = 'author_object'

@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class AuthorDelete(DeleteView):
    model = Author
    template_name = 'catalog/author_confirm_delete.html'
    success_url = reverse_lazy('authors') # After form is submitted, page redirects to author_list.html
    context_object_name = 'author_object'
#### END Views to Create/Update/Delete Authors ####


#### BEGIN Views to Create/Update/Delete Books ####
@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    template_name = 'catalog/book_form.html'
    success_url = reverse_lazy('books') # After form is submitted, page redirects to book_list.html
    context_object_name = 'book_object'

@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    template_name = 'catalog/book_form.html'
    success_url = reverse_lazy('books') # After form is submitted, page redirects to book_list.html
    context_object_name = 'book_object'

@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class BookDelete(DeleteView):
    model = Book
    template_name = 'catalog/book_confirm_delete.html'
    success_url = reverse_lazy('books') # After form is submitted, page redirects to book_list.html
    context_object_name = 'book_object'
#### END Views to Create/Update/Delete Books ####


#### BEGIN Views to Create/Update/Delete BookInstances ####
@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class BookInstanceCreate(CreateView):
    model = BookInstance
    context_object_name = 'bookinstance_object'
    form_class = BookInstanceCreateForm  # Use the custom form class from forms.py
    template_name = 'catalog/bookinstance_form.html'
    success_url = reverse_lazy('bookinstances') # After form is submitted, page redirects to book_list.html
    context_object_name = 'bookinstance_object'

@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class BookInstanceUpdate(UpdateView):
    model = BookInstance
    context_object_name = 'bookinstance_object'
    form_class = BookInstanceUpdateForm  # Use the custom form class from forms.py
    template_name = 'catalog/bookinstance_form.html'
    success_url = reverse_lazy('bookinstances') # After form is submitted, page redirects to book_list.html

@method_decorator(login_required, name='dispatch') # IMPORTANT NOTE: "dispatch" is the method of the class view that is being targeted by the @method_decorator decorator.
@method_decorator(permission_required('catalog.can_mark_returned'), name='dispatch')
class BookInstanceDelete(DeleteView):
    model = BookInstance
    context_object_name = 'bookinstance_object'
    template_name = 'catalog/bookinstance_confirm_delete.html'
    success_url = reverse_lazy('bookinstances') # After form is submitted, page redirects to book_list.html
#### END Views to Create/Update/Delete BookInstances ####
