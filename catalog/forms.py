from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm # For class RenewBookModelForm
from catalog.models import BookInstance
from catalog.models import Author
from .validators import *
from django.contrib.auth.models import User

#### BEGIN Custom Field Classes #####
class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, user: User) -> str:
        return f"{user.last_name}, {user.first_name}"

#### END Custom Field Classes #####

class RenewBookForm(forms.Form):
    # This is a form field
    new_due_date = forms.DateField(
        label = "New Due Date",
        required = True,
        widget = forms.DateInput(attrs={'placeholder': (datetime.date.today() + datetime.timedelta(weeks=3))}),
        validators = [
            # The Check_MinDateValue and Check_MaxDateValue functions take datetime.date as an argument and either errors or returns bool True.
            # In this context, they automatically use whatever is typed into this forms.DateField field as it's datetime.date argument
            # See validators.py for details
            #Check_MinDateValue,
            #Check_MaxDateValue
            # If you want to be able to pass multiple parameters to a function in this context, you have to use a class with appropriate method
            # The first argument remains unnamed and automatically grabs whatever content the forms.DateField field has. Additional
            # arguments must be named in order to be passed
            MinDateValidator(
                errmsg = 'Invalid date - renewal in past',
            ),
            MaxDateValidator(
                errmsg = 'Invalid date - renewal more than 4 weeks ahead'
            ),
        ],
        help_text = "Enter a date between now and 4 weeks (default 3).",
    )

    user_list = User.objects.all().order_by('last_name')
    # This is a form field
    new_borrower = CustomUserChoiceField(
        queryset = user_list, # Queryset of User objects
        required = True,
        empty_label = "Select a user",  # Optional: Add a default empty label
        label = "Choose a User",
    )

    # The above validators handle this logic already, so we don't really need this. We can just call the .new_due_date attribute in our View
    '''
    def clean_new_due_date(self):
        data = self.cleaned_data['new_due_date']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data
    '''

# You can also just pull the fields from the Model directly using ModelForm, but
# this approach is less flexible than the above using forms.Form    
class RenewBookModelForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        #fields = '__all__'
        fields = ['due_back', 'borrower', 'status']
        labels = {
            'due_back': _('New Due Date'),
            'borrower': _('New Borrower'),
            'status': _('Status')
        },
        widgets = {
            'new_due_date': forms.DateInput(
                attrs = {
                    'placeholder': (datetime.date.today() + datetime.timedelta(weeks=3))
                }
            ),
        },
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).'), 'status': _('')}

class AuthorUpdateForm(forms.Form):
    updated_first_name = forms.CharField(
        label = "Updated First Name",
        required = True,
        max_length = 100,
        help_text = "Enter the Author's first name",
    )
    updated_last_name = forms.CharField(
        label = "Updated Last Name",
        required = True,
        max_length = 100,
        help_text = "Enter the Author's last name",
    )
    updated_date_of_birth = forms.DateField(
        label = "Date of Birth",
        required = False,
        widget = forms.SelectDateWidget(
            years = range(1900, 2100)
        ),
    )
    updated_date_of_death = forms.DateField(
        label = "Date of Death",
        required = False,
        widget = forms.SelectDateWidget(
            years = range(1900, 2100)
        ),
    )

    def __init__(self, *args, **kwargs):
        author_id = kwargs.pop('author_id', None)
        super(AuthorUpdateForm, self).__init__(*args, **kwargs)

        # Now you can use the author_id to fetch the author and pre-fill the form fields
        if author_id is not None:
            author = Author.objects.get(pk=author_id)
            self.fields['updated_first_name'].initial = author.first_name
            self.fields['updated_last_name'].initial = author.last_name
            self.fields['updated_date_of_birth'].initial = author.date_of_birth
            self.fields['updated_date_of_death'].initial = author.date_of_death

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('updated_date_of_birth')
        date_of_death = cleaned_data.get('updated_date_of_death')
        first_name = cleaned_data.get('updated_first_name')
        last_name = cleaned_data.get('updated_last_name')

        if date_of_birth and date_of_death and date_of_birth >= date_of_death:
            raise forms.ValidationError('Date of death must be after date of birth.')

        if first_name and last_name and first_name == last_name:
            raise forms.ValidationError("First name and last name can't be the same.")

        return cleaned_data
    
class AuthorUpdateModelForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('date_of_birth')
        date_of_death = cleaned_data.get('date_of_death')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        # Make sure birth date is before death date
        Compare_Dates(birth_date = date_of_birth, death_date = date_of_death)

        # Make sure first and last name aren't the same
        Compare_FirstLastName(firstname = first_name, lastname = last_name)

        return cleaned_data

class BookInstanceCreateForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['id', 'book', 'imprint', 'due_back', 'borrower']
        
    due_back = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

class BookInstanceUpdateForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['imprint', 'due_back', 'borrower']
        
    due_back = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

