from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm # For class RenewBookModelForm
from catalog.models import BookInstance
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
        help_text = "Enter a date between now and 4 weeks (default 3)."
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
class RenewBookModelForm(ModelForm):
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

