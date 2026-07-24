from django.contrib import admin

from .models import Book, Borrow


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "authors", "publisher", "category", "copies_total", "copies_available")
    list_filter = ("category", "publisher")
    search_fields = ("title", "authors", "isbn")


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "borrowed_date", "due_date", "returned", "is_overdue", "fine_amount")
    list_filter = ("returned",)
    search_fields = ("user__username", "book__title")
