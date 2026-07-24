from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date

BORROW_DAYS = 7
FINE_PER_DAY = 1  # dollars charged for each day an item is overdue


def get_due_date():
    return date.today() + timedelta(days=BORROW_DAYS)


class Book(models.Model):
    CATEGORY_CHOICES = [
        ("fiction", "Fiction"),
        ("non_fiction", "Non-fiction"),
        ("science", "Science"),
        ("history", "History"),
        ("technology", "Technology"),
        ("biography", "Biography"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=200)
    publisher = models.CharField(max_length=100)
    year_of_publishing = models.PositiveIntegerField()
    isbn = models.CharField(
        "ISBN", max_length=13, unique=True, blank=True, null=True,
        help_text="Optional. 10 or 13 digit ISBN.",
    )
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="other",
    )
    description = models.TextField(blank=True)
    copies_total = models.PositiveIntegerField(
        default=1, help_text="How many physical copies the library owns.",
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def copies_borrowed(self):
        """Copies currently checked out and not yet returned."""
        return self.borrow_set.filter(returned=False).count()

    @property
    def copies_available(self):
        """Computed, not stored — so it can never drift out of sync."""
        return max(self.copies_total - self.copies_borrowed, 0)

    @property
    def is_available(self):
        return self.copies_available > 0


class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(default=get_due_date)
    returned = models.BooleanField(default=False)
    returned_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_date"]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    @property
    def is_overdue(self):
        """Currently checked out and past its due date."""
        return not self.returned and date.today() > self.due_date

    @property
    def days_overdue(self):
        end = self.returned_date if self.returned and self.returned_date else date.today()
        return max((end - self.due_date).days, 0)

    @property
    def fine_amount(self):
        """Dollars owed for lateness — applies whether or not it's been returned yet."""
        return self.days_overdue * FINE_PER_DAY