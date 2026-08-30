from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginUserForm(AuthenticationForm):
    """Custom login form, needed mainly to attach the 'data_entry' CSS
    class to each field - the standard AuthenticationForm doesn't set
    any classes on its widgets, and HTML attributes/classes are only
    controllable from the form definition, not from the template
    directly."""

    username = forms.CharField(label="Login", widget=forms.TextInput(attrs={'class': 'data_entry'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'data_entry'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    """Custom registration form"""

    username = forms.CharField(label="Login", widget=forms.TextInput(attrs={'class': 'data_entry'}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'data_entry'}))
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput(attrs={'class': 'data_entry'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'data_entry', 'required': 'required'}),
            'first_name': forms.TextInput(attrs={'class': 'data_entry', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'data_entry', 'required': 'required'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("email already exists")
        return email