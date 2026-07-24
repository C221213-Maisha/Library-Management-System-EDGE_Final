from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookForm, UserRegistrationForm
from .models import Book, Borrow

BOOKS_PER_PAGE = 9


def staff_required(view_func):
    """Only staff accounts may add, edit, or delete catalog entries."""
    return user_passes_test(lambda u: u.is_staff, login_url="login")(view_func)


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")

    active_borrows = Borrow.objects.filter(user=request.user, returned=False)
    overdue_count = sum(1 for b in active_borrows if b.is_overdue)
    total_fines = sum(b.fine_amount for b in active_borrows if b.is_overdue)

    return render(request, "library/profile.html", {
        "active_count": active_borrows.count(),
        "overdue_count": overdue_count,
        "total_fines": total_fines,
    })


def home(request):
    return render(request, "library/home.html")


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}, your account is ready.")
            return redirect("profile")
    else:
        form = UserRegistrationForm()
    return render(request, "library/register.html", {"form": form})


def book_list(request):
    query = request.GET.get("q", "")
    publisher_filter = request.GET.get("publisher", "")
    category_filter = request.GET.get("category", "")

    books = Book.objects.all()

    if query:
        books = books.filter(title__icontains=query)
    if publisher_filter:
        books = books.filter(publisher__icontains=publisher_filter)
    if category_filter:
        books = books.filter(category=category_filter)

    paginator = Paginator(books, BOOKS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "library/book_list.html", {
        "page_obj": page_obj,
        "books": page_obj.object_list,
        "query": query,
        "publisher_filter": publisher_filter,
        "category_filter": category_filter,
        "categories": Book.CATEGORY_CHOICES,
    })


@staff_required
def book_form(request, id=None):
    book = get_object_or_404(Book, id=id) if id else None

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{form.instance.title}' saved to the catalog.")
            return redirect("book_list")
    else:
        form = BookForm(instance=book)

    return render(request, "library/book_form.html", {"form": form})


@staff_required
def book_delete(request, id):
    book = get_object_or_404(Book, id=id)
    title = book.title
    book.delete()
    messages.success(request, f"'{title}' removed from the catalog.")
    return redirect("book_list")


@login_required
def borrow_book(request, id):
    book = get_object_or_404(Book, id=id)

    if Borrow.objects.filter(user=request.user, book=book, returned=False).exists():
        messages.error(request, f"You already have '{book.title}' checked out.")
        return redirect("book_list")

    if not book.is_available:
        messages.error(request, f"'{book.title}' has no copies available right now.")
        return redirect("book_list")

    Borrow.objects.create(user=request.user, book=book)
    messages.success(request, f"You borrowed '{book.title}'. Due back in 7 days.")
    return redirect("borrowed_books")


@login_required
def return_book(request, id):
    borrow = get_object_or_404(Borrow, id=id, user=request.user)

    if borrow.returned:
        messages.error(request, "That book was already returned.")
    else:
        borrow.returned = True
        borrow.returned_date = date.today()
        borrow.save()
        if borrow.fine_amount:
            messages.success(
                request,
                f"'{borrow.book.title}' returned, ${borrow.fine_amount} fine for "
                f"{borrow.days_overdue} day(s) late.",
            )
        else:
            messages.success(request, f"'{borrow.book.title}' returned. Thanks!")

    return redirect("borrowed_books")


@login_required
def borrowed_books(request):
    borrows = Borrow.objects.filter(user=request.user)
    return render(request, "library/borrowed_books.html", {"borrows": borrows})


def search_books(request):
    query = request.GET.get("q")
    books = Book.objects.filter(title__icontains=query) if query else Book.objects.all()
    return render(request, "library/book_list.html", {"books": books})


@login_required
def fines(request):
    borrows = Borrow.objects.filter(user=request.user, returned=False, due_date__lt=date.today())
    total = sum(b.fine_amount for b in borrows)
    return render(request, "library/fines.html", {"borrows": borrows, "total_fines": total})