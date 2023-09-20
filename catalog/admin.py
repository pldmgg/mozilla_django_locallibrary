from django.contrib import admin
from .models import Author, Language, Genre, Book, BookInstance
from reversion.admin import VersionAdmin

# Define the admin class
# Original syntax: admin.site.register(Author)
@admin.register(Author)
class AuthorAdmin(VersionAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    #exclude = ['date_of_death']

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

# Original syntax: admin.site.register(Book)
@admin.register(Book)
class BookAdmin(VersionAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

# Original syntax: admin.site.register(BookInstance)
@admin.register(BookInstance)
class BookInstanceAdmin(VersionAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

# Register your models here.

#admin.site.register(Author)
admin.site.register(Language)
admin.site.register(Genre)
#admin.site.register(Book)
#admin.site.register(BookInstance)
