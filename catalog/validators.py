import datetime
from django.core.validators import BaseValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Reference:https://docs.djangoproject.com/en/4.1/_modules/django/core/validators/

# Functions with multiple arguments don't work in the validators=[] context in forms.py
#def Check_MinDateValue(datedata: datetime.date, errmsg: str) -> bool:
#    # Check if a date is not in the past.
#    if datedata < datetime.date.today():
#        raise ValidationError(_(errmsg))
#    
#    return True

def Check_MinDateValue(
        datedata: datetime.date,
        errmsg: str = 'Invalid date - renewal in past'
    ) -> bool:

    # Check if a date is not in the past.
    if datedata < datetime.date.today():
        raise ValidationError(_(errmsg))
    
    return True
    
class MinDateValidator:
    # This contructor allows us to pass a custom errmsg when we create a MinDateValidator object
    # Setting errmsg=None means that is an optional argument at object creation time
    def __init__(self, errmsg=None):
        self.errmsg = errmsg

    # We need to use __call__ so that in the context of validators=[] for a
    # forms.xxxxField in forms.py automatically passes the user input as "value"
    def __call__(self, value: datetime.date) -> None:
        if not self.is_valid(value):
            error_message = "Invalid value provided."
            raise ValidationError(error_message, code="invalid_value")

    def is_valid(self, value) -> bool:
        # Implement your validation logic here.
        # Return True if the value is valid, False otherwise.
        if value < datetime.date.today():
            error_message = self.errmsg or "Invalid value provided."
            raise ValidationError(error_message, code="invalid_value")
        
        return True

def Check_MaxDateValue(
        datedata: datetime.date,
        errmsg: str = 'Invalid date - renewal more than 4 weeks ahead'
    ) -> bool:
    
    # Check if a date is in the allowed range (+4 weeks from today).
    if datedata > datetime.date.today() + datetime.timedelta(weeks=4):
        raise ValidationError(_(errmsg))
    
    return True
    
class MaxDateValidator:
    # This contructor allows us to pass a custom errmsg when we create a MinDateValidator object
    # Setting errmsg=None means that is an optional argument at object creation time
    def __init__(self, errmsg=None):
        self.errmsg = errmsg

    # We need to use __call__ so that in the context of validators=[] for a
    # forms.xxxxField in forms.py automatically passes the user input as "value"
    def __call__(self, value: datetime.date) -> None:
        if not self.is_valid(value):
            error_message = "Invalid value provided."
            raise ValidationError(error_message, code="invalid_value")

    def is_valid(self, value) -> bool:
        # Implement your validation logic here.
        # Return True if the value is valid, False otherwise.
        if value > datetime.date.today() + datetime.timedelta(weeks=4):
            error_message = self.errmsg or "Invalid value provided."
            raise ValidationError(error_message, code="invalid_value")
        
        return True
    
def Compare_Dates(
        birth_date: datetime.date,
        death_date: datetime.date,
        errmsg: str = 'Death Date is before Birth Date!'
    ) -> bool:
    
    # Check if a date is in the allowed range (+4 weeks from today).
    if death_date < birth_date:
        raise ValidationError(_(errmsg))
    
    return True

def Compare_FirstLastName(
        firstname: str,
        lastname: str,
        errmsg: str = "First name and last name can't be the same."
    ) -> bool:
    
    if firstname and lastname and firstname == lastname:
        raise forms.ValidationError(errmsg)
    
    return True


