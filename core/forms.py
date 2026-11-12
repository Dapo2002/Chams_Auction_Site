from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ALLOWED_DOMAINS = ('@chams.com', '@chamscampus.com')


class CustomUserCreationForm(UserCreationForm):
  email = forms.EmailField(
      required=True,
      help_text='Must be an official company email (@chams.com or @chamscampus.com)',
  )

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ('username', 'email')

  def clean_email(self):
    email = self.cleaned_data.get('email', '').lower()

    if not email.endswith(ALLOWED_DOMAINS):
      raise forms.ValidationError(
          'Registration is restricted to official company emails (@chams.com or'
          ' @chamscampus.com).'
      )

    if User.objects.filter(email=email).exists():
      raise forms.ValidationError(
          'An account with this email address already exists.'
      )

    return email