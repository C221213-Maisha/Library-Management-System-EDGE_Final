from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title", "authors", "publisher", "year_of_publishing",
            "isbn", "category", "copies_total", "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_year_of_publishing(self):
        year = self.cleaned_data["year_of_publishing"]
        if year > date.today().year:
            raise forms.ValidationError("Year of publishing can't be in the future.")
        return year

    def clean_copies_total(self):
        copies = self.cleaned_data["copies_total"]
        if copies < 1:
            raise forms.ValidationError("A book needs at least one copy.")
        return copies

    def clean_isbn(self):
        isbn = self.cleaned_data.get("isbn")
        if not isbn:
            return None
        isbn = isbn.replace("-", "").replace(" ", "")
        if not (len(isbn) in (10, 13) and isbn[:-1].isdigit()):
            raise forms.ValidationError("Enter a valid 10 or 13 digit ISBN.")
        return isbn

    def clean(self):
        cleaned_data = super().clean()
        copies_total = cleaned_data.get("copies_total")
        if copies_total is not None and self.instance.pk:
            borrowed = self.instance.copies_borrowed
            if copies_total < borrowed:
                self.add_error(
                    "copies_total",
                    f"{borrowed} cop{'y is' if borrowed == 1 else 'ies are'} "
                    "currently checked out, can't set the total below that.",
                )
        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]