from django.shortcuts import get_object_or_404, render ,redirect
from django.views import View
from django.conf import settings
import stripe
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from django.contrib.auth import login, authenticate,logout
from .forms import BookForm,UserProfileForm,RatingForm
from django.http import HttpResponseForbidden,JsonResponse,FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Genre,Book,UserProfile,Rating,Payment,Cart,PurchasedBook
from datetime import date
from django.views.generic import ListView,DetailView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from .recommendation import get_book_recommendations

stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
# Create your views here.
class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')

class ContactView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'contact.html')

class CategoriesView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'categories.html')

class BlogView(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all().order_by('-id')  # Fetch all books, newest first
        for book in books:
            avg_rating = book.ratings.aggregate(Avg('rating'))['rating__avg']
            book.avg_rating = round(avg_rating, 1) if avg_rating else 0 
        today = date.today()
        return render(request, 'blog.html', {'books': books, 'today': today})

class AboutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')  

class SignupView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            login(request, user)  # Log the user in
            return redirect('index')  # Redirect to the home page after signup
        return render(request, 'signup.html', {'form': form})
class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'signin.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Log the user in
                return redirect('index')  # Redirect to the home page after login
        return render(request, 'signin.html', {'form': form}) 

class SignoutView(View):
    def get(self, request):
        logout(request)  # Log the user out
        return redirect('index')

class ChangepasswordView(View):
    def get(self, request):
        # Render the form for GET requests
        form = PasswordChangeForm(user=request.user)
        return render(request, 'changepassword.html', {'form': form})

    def post(self, request):
        # Handle form submission for POST requests
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('index')  
        else:
            messages.error(request, 'Please correct the error(s) below.')

        return render(request, 'changepassword.html', {'form': form})
        
class AddBookView(View):
    def get(self, request):
        if not request.user.is_superuser:  # Check if the user is not a superuser
            return HttpResponseForbidden("You are not authorized to add books.")
        form = BookForm()
        return render(request, 'add_books.html', {'form': form})

    def post(self, request):
        if not request.user.is_superuser:  # Restrict POST actions as well
            return HttpResponseForbidden("You are not authorized to add books.")
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()  # Save the book
            messages.success(request, 'Book added successfully!')
            return redirect('blog')  # Replace 'book_list' with your desired URL
        else:
            messages.error(request, 'Please correct the error(s) below.')
        return render(request, 'add_books.html', {'form': form})

class GenreListView(ListView):
    model = Genre
    template_name = 'categories.html'  # Replace with your template file
    context_object_name = 'genres'

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'genre_book.html'  # Replace with your template file
    context_object_name = 'genre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all()  # Fetch books related to this genre
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        #ratingdisplay
        avg_rating = book.ratings.aggregate(Avg('rating'))['rating__avg']
        context['book'].avg_rating = round(avg_rating, 1) if avg_rating else 0
        return context 

# class BookDetailView(DetailView):
#     model = Book
#     template_name = 'book_detail.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         book = self.get_object()  # Get the current book object

#         # Calculate average rating
#         avg_rating = book.ratings.aggregate(Avg('rating'))['rating__avg']
#         context['avg_rating'] = round(avg_rating, 1) if avg_rating else 0  # Add average rating to the context

#         return context    



class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

# Book Edit View
class BookUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'book_edit.html'

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.id})  # Change 'book_id' to 'pk'


# Book Delete View
class BookDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Book
    template_name = 'book_delete.html'
    success_url = reverse_lazy('blog')  # Ensure 'book_list' URL is defined

class ProfileView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        # Get or create the UserProfile for the logged-in user
        user_profile, created = UserProfile.objects.get_or_create(name=user)

        # Context to be passed to the template
        context = {
            'username': user.username,
            'phone_number': user_profile.phone_number if user_profile.phone_number != 'No Phone Number' else 'Not Provided',
            'profile_pic': user_profile.profile_pic.url if user_profile.profile_pic else None,  # If there's a profile pic, show the URL, else None
        }
        
        # Render the profile page
        return render(request, 'profile.html', context)

# ProfileEditView without using UpdateView
class ProfileEditView(View):
    def get(self, request, *args, **kwargs):
        user_profile = get_object_or_404(UserProfile, name=request.user)
        form = UserProfileForm(instance=user_profile)
        return render(request, 'profile_edit.html', {'form': form})

    def post(self, request, *args, **kwargs):
        user_profile = get_object_or_404(UserProfile, name=request.user)
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect back to profile page after saving
        else:
            print(form.errors)  # Debugging: Print form errors in the console
            return render(request, 'profile_edit.html', {'form': form})
        return render(request, 'profile_edit.html', {'form': form})

class PurchaseoptionsView(View):
    def get(self, request, *args, **kwargs):
        # Fetch the book by the provided pk in the URL
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        return render(request, 'purchaseoptions.html', {'book': book})

class SearchView(ListView):
    model = Book
    template_name = 'search.html'  # The template to render
    context_object_name = 'results'  # Name to use for the search results in the template

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # Get the search query from the URL
        if query:
            return Book.objects.filter(title__icontains=query)  # Search for items
        return Book.objects.none()  # Return an empty queryset if no query is provided

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')  # Pass the search query to the template
        return context  

@method_decorator(login_required, name='dispatch')
class RateBookView(LoginRequiredMixin, FormView):
    form_class = RatingForm
    template_name = 'rate.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        context['book'] = book
        return context

    def form_valid(self, form):
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        rating_value = form.cleaned_data['rating']
        Rating.objects.update_or_create(user=self.request.user, book=book, defaults={'rating': rating_value})
        return redirect('book_detail', pk=book.pk) 



class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=self.kwargs['pk'])  # Get the selected book
        user = request.user  # Get the logged-in user
        
        try:
            # Create the Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],  # Allow payment by card
                line_items=[{
                    'price_data': {
                        'currency': 'inr',  # Indian Rupees (INR)
                        'product_data': {'name': book.title},  # Book title
                        'unit_amount': int(book.price * 100),  # Convert to paise (INR cents)
                    },
                    'quantity': 1,
                }],
                mode='payment',  # Payment mode
                success_url=request.build_absolute_uri(reverse("payment_success")) + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
            )
            
            # Save the payment in the database
            Payment.objects.create(
                user=user,
                book=book,
                amount=book.price,  # Set the price
                stripe_payment_id=session.id,
                status='pending',  # Status will be pending initially
            )

            # Redirect to Stripe Checkout session
            return redirect(session.url)

        except Exception as e:
            return JsonResponse({'error': str(e)})


# class PaymentMethodSelectionView(View):
#     def get(self, request, *args, **kwargs):
#         book = get_object_or_404(Book, id=self.kwargs['pk'])
#         return render(request, 'payment_method_selection.html', {'book': book})
#     def post(self, request, *args, **kwargs):
#         book = get_object_or_404(Book, pk=self.kwargs['pk'])

#         # Process payment based on the selected method
#         payment_method = request.POST.get('payment_method')
#         if payment_method == 'cash_on_delivery':
#             # Handle cash on delivery logic
#             payment_status = 'pending'
#         elif payment_method == 'upi':
#             # Handle UPI payment logic
#             payment_status = 'pending'
#         elif payment_method == 'card':
#             # Redirect to Stripe or other card payment processing
#             payment_status = 'pending'
#         else:
#             payment_status = 'failed'
        
#         # Save the payment status in the database
#         Payment.objects.create(
#             user=request.user,
#             book=book,
#             amount=book.price,
#             status=payment_status
#         )

#         return render(request, 'payment_method_selection.html', {'book': book})

class PaymentMethodSelectionView(View):
    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=self.kwargs['pk'])
        return render(request, 'payment_method_selection.html', {'book': book})

    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        payment_method = request.POST.get('payment_method')

        if payment_method == 'cash_on_delivery':
            payment_status = 'pending'
            Payment.objects.create(user=request.user, book=book, amount=book.price, status=payment_status)
            return redirect('payment_success')  # Redirect to success page

        elif payment_method == 'upi':
            payment_status = 'pending'
            Payment.objects.create(user=request.user, book=book, amount=book.price, status=payment_status)
            return redirect('payment_success')  # Redirect after selection

        elif payment_method == 'card':
            # Redirect to Stripe Checkout session
            return redirect(reverse('create-checkout-session', kwargs={'pk': book.pk}))

        else:
            return render(request, 'payment_method_selection.html', {'book': book, 'error': 'Invalid payment method'})



class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "payment_success.html")


class PaymentCancelView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "payment_cancel.html")


# class StripeWebhookView(View):
#     def post(self, request, *args, **kwargs):
#         payload = request.body
#         sig_header = request.META['HTTP_STRIPE_SIGNATURE']

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, STRIPE_WEBHOOK_SECRET
#             )
#         except ValueError as e:
#             # Invalid payload
#             return JsonResponse({'error': 'Invalid payload'}, status=400)
#         except stripe.error.SignatureVerificationError as e:
#             # Invalid signature
#             return JsonResponse({'error': 'Invalid signature'}, status=400)

#         # Handle the event
#         if event['type'] == 'checkout.session.completed':
#             session = event['data']['object']
#             # Update the payment status based on session ID
#             payment = Payment.objects.get(stripe_payment_id=session['id'])
#             payment.status = 'completed'
#             payment.save()

#         return JsonResponse({'status': 'success'}, status=200)
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except ValueError:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        # ✅ If the payment is successful, update the status
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            try:
                payment = Payment.objects.get(stripe_payment_id=session['id'])
                payment.status = 'completed'
                payment.save()
            except Payment.DoesNotExist:
                return JsonResponse({'error': 'Payment not found'}, status=404)

        return JsonResponse({'status': 'success'}, status=200)

class CartDetailView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        total_amount = sum(item.total_price() for item in cart_items)
        return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_amount': total_amount})




# View to add a book to the cart
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, book=book)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart_detail')

# View to remove a book from the cart
class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        cart_item = get_object_or_404(Cart, user=request.user, book_id=book_id)
        cart_item.delete()
        return redirect('cart_detail')

# View to update cart item quantity
class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        cart_item = get_object_or_404(Cart, user=request.user, book_id=book_id)
        new_quantity = int(request.POST.get('quantity', 1))

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()  # Remove if quantity is set to 0

        return redirect('cart_detail')

# Clear entire cart
class ClearCartView(LoginRequiredMixin, View):
    def post(self, request):
        Cart.objects.filter(user=request.user).delete()
        return redirect('cart_detail')

class PaymentSelectionmethoddownloadView(View):
    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=kwargs['pk'])  # Fixed self.kwargs issue
        return render(request, 'payment_selection_methoddownload.html', {'book': book})

    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=kwargs['pk'])  # Fixed self.kwargs issue
        payment_method = request.POST.get('payment_method')

        if payment_method in ['cash_on_delivery', 'upi']:
            payment_status = 'pending'
            Payment.objects.create(user=request.user, book=book, amount=book.price, status=payment_status)
            return redirect('download_payment_success')  # Redirect to success page

        elif payment_method == 'card':
            # Redirect to Stripe Checkout session
            return redirect(reverse('download_book_payment', kwargs={'pk': book.pk}))  # Fixed redirect issue

        else:
            return render(request, 'payment_selection_methoddownload.html', {'book': book, 'error': 'Invalid payment method'})  # Fixed template name        



class DownloadPaymentSuccessView(TemplateView):
    template_name = "download_payment_success.html"

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("book_id")
        book = get_object_or_404(Book, id=book_id)

        # Mark book as partially purchased (20% payment)
        purchased_book, created = PurchasedBook.objects.get_or_create(user=request.user, book=book)
        if not created and not purchased_book.partial_purchase:
            purchased_book.partial_purchase = True
            purchased_book.save()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book_id = kwargs.get("book_id")
        book = get_object_or_404(Book, id=book_id)
        context['book'] = book
        return context


class CreateDownloadCheckoutSessionView(View):
    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, id=book_id)
        user = request.user
        partial_price = int(float(book.price) * 0.2 * 100)  # Convert Decimal to float before math  # 20% of the book price (converted to cents)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': book.title},
                    'unit_amount': partial_price,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('download_payment_success', kwargs={'book_id': book.id})
            ),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )
        Payment.objects.create(
                user=user,
                book=book,
                amount=book.price,  # Set the price
                stripe_payment_id=session.id,
                status='pending',  # Status will be pending initially
            )

            # Redirect to Stripe Checkout session
            
        return redirect(session.url)

class DownloadBookView(View):
    @method_decorator(login_required)
    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)

        # Check if the user has made a partial payment (20%)
        if PurchasedBook.objects.filter(user=request.user, book=book, partial_purchase=True).exists():
            return FileResponse(book.book_file.open('rb'), as_attachment=True, filename=f"{book.book_file.name}.pdf")
        else:
            return HttpResponseForbidden("You need to pay 20% to download this book.")

class RecommendedBooksView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "recommended_books.html"
    context_object_name = "recommended_books"

    def get_queryset(self):
        return get_book_recommendations(self.request.user.id)


 # Assuming you have a CartItem model

stripe.api_key = settings.STRIPE_SECRET_KEY

class CartCreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        total_amount = request.POST.get("amount")
        

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": "Book Purchase",
                            },
                            "unit_amount": int(float(total_amount) * 100),  # Convert to paisa
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=request.build_absolute_uri(reverse("cartpayment_success")),
                cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
            )
            

            # Redirect to Stripe Checkout session
            
            return redirect(checkout_session.url)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class CartPaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Clear cart after successful payment
        Cart.objects.filter(user=request.user).delete()
        return render(request, "payment_success.html")

       