import pandas as pd
from sklearn.neighbors import NearestNeighbors
from django.contrib.auth.models import User
from .models import Book, Rating

def get_book_recommendations(user_id, n_neighbors=5):
    # Fetch ratings from the database
    ratings = Rating.objects.all().values("user_id", "book_id", "rating")
    df = pd.DataFrame(ratings)

    # If there are no ratings, return an empty list
    if df.empty:
        return []

    # Create a pivot table (User-Book Rating Matrix)
    user_book_matrix = df.pivot(index="user_id", columns="book_id", values="rating").fillna(0)

    # Check if the user exists in the dataset
    if user_id not in user_book_matrix.index:
        return []  # Return empty if the user has no ratings

    # Dynamically adjust `n_neighbors` to avoid errors
    num_users = len(user_book_matrix)
    adjusted_n_neighbors = min(n_neighbors, num_users - 1)  # Ensure it does not exceed available users

    # Fit the KNN model
    model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=adjusted_n_neighbors)
    model.fit(user_book_matrix)

    # Find the user's index in the matrix
    user_index = user_book_matrix.index.get_loc(user_id)

    # Get nearest neighbors
    distances, indices = model.kneighbors([user_book_matrix.iloc[user_index]])

    # Get recommended book IDs (excluding the user's own row)
    recommended_books = []
    for neighbor_idx in indices[0][1:]:  # Skip the first one (it's the user itself)
        top_books = user_book_matrix.iloc[neighbor_idx].sort_values(ascending=False)
        recommended_book_ids = top_books[top_books > 0].index.tolist()  # Books rated by similar users

        for book_id in recommended_book_ids:
            try:
                recommended_books.append(Book.objects.get(id=book_id))
            except Book.DoesNotExist:
                continue
    
    user_rated_books = Rating.objects.filter(user_id=user_id).values_list("book_id", flat=True)
    user_genres = Book.objects.filter(id__in=user_rated_books).values_list("genres", flat=True).distinct()

    # If not enough recommendations, add books from the same genre
    if len(recommended_books) < 5:
        additional_books = Book.objects.filter(genre__in=user_genres).exclude(id__in=[b.id for b in recommended_books])[:5-len(recommended_books)]
        recommended_books.update(additional_books)

    return recommended_books
