import time

from django import forms


class ContactForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        label='Email address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
            'placeholder': 'you@example.com',
        }),
    )
    message = forms.CharField(
        max_length=5000,
        label='Message',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 7,
            'placeholder': 'Write your message here...',
        }),
    )
    form_started = forms.IntegerField(widget=forms.HiddenInput)

    def clean_form_started(self):
        started = self.cleaned_data['form_started']
        if time.time() - started < 3:
            raise forms.ValidationError('Please take a moment before sending your message.')
        return started