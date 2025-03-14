from django.urls import path
from . import views
from .views import IndexView, ContactView, CategoriesView, BlogView, AboutView, SignupView,LoginView,SignoutView,ChangepasswordView,AddBookView,GenreDetailView,GenreListView,BookDetailView,BookUpdateView,BookDeleteView,ProfileView,ProfileEditView,PurchaseoptionsView,SearchView,RateBookView,CreateCheckoutSessionView,PaymentSuccessView,PaymentCancelView,PaymentMethodSelectionView,StripeWebhookView
from .views import CartDetailView,AddToCartView,RemoveFromCartView,UpdateCartView,ClearCartView,PaymentSelectionmethoddownloadView,CreateDownloadCheckoutSessionView,DownloadPaymentSuccessView,DownloadBookView,RecommendedBooksView,CartCreateCheckoutSessionView,CartPaymentSuccessView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('about/', AboutView.as_view(), name='about'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', LoginView.as_view(), name='signin'),
    path('signout/', SignoutView.as_view(), name='signout'),
    path('changepassword/',ChangepasswordView.as_view(),name='changepassword'),
    path('add_books/',AddBookView.as_view(),name='add_books'),
    path('categories/', GenreListView.as_view(), name='categories'), 
    path('genre/<int:pk>/', GenreDetailView.as_view(), name='genre_book'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('book_edit/<int:pk>/', BookUpdateView.as_view(), name='book_edit'),  # Change 'book_id' to 'pk'
    path('book/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),  # Change 'book_id' to 'pk'
    path('profile/', ProfileView.as_view(), name='profile'),  # Profile view
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('purchase-options/<int:pk>/', PurchaseoptionsView.as_view(), name='purchase-options'),
    path('search/', SearchView.as_view(), name='search'),
    path('rate/<int:pk>/', RateBookView.as_view(), name='rate'),
    path('payment-methods/<int:pk>/', PaymentMethodSelectionView.as_view(), name='payment_methods'),
    path('create-checkout-session/<int:pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment-cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart/add/<int:book_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:book_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update/<int:book_id>/', UpdateCartView.as_view(), name='update_cart'),
    path('cart/clear/', ClearCartView.as_view(), name='clear_cart'),
    path('payment/download-selection/<int:pk>/', PaymentSelectionmethoddownloadView.as_view(), name='payment_selection_download'),
    path('download/pay/<int:book_id>/', CreateDownloadCheckoutSessionView.as_view(), name='download_book_payment'),
    path('download/success/<int:book_id>/', DownloadPaymentSuccessView.as_view(), name='download_payment_success'),
    path('download/<int:book_id>/', DownloadBookView.as_view(), name='download_book'),
    path("recommendations/", RecommendedBooksView.as_view(), name="book-recommendations"),
    path("cartcreate-checkout-session/", CartCreateCheckoutSessionView.as_view(), name="cartcreate_checkout_session"),
    path("cartpayment-success/", CartPaymentSuccessView.as_view(), name="cartpayment_success"),
]

    