from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from .models import Movie, Genre, Review
from .forms import ReviewForm


# Create your views here.
def index(request):
    movies = Movie.objects.all()
    context = {'movies': movies,}
    return render(request, 'movies/index.html', context)


def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    reviews = movie.review_set.all()
    review_form = ReviewForm()
    context = {'movie': movie, 'reviews' : reviews, 'review_form': review_form,}
    return render(request, 'movies/detail.html', context)


@require_POST
def review_create(request, movie_pk):
    if request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.movie_id = movie_pk
            review.user = request.user
            review.save()
    return redirect('movies:detail', movie_pk)


@require_POST
def review_delete(request, movie_pk, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if review.user == request.user:
            review.delete()
        return redirect('movies:detail', movie_pk)
    return HttpResponse('You ar Unauthorized', status=401)


@login_required
def like(request, movie_pk):
    if request.is_ajax():
        movie = get_object_or_404(Movie, pk=movie_pk)
        if movie.like_users.filter(pk=request.movie.pk).exists():
            movie.like_users.remove(request.movie)
            liked = False
        else:
            movie.like_user.add(request.user)
            liked = True
        context = {'liked': liked,}
        return JsonResponse(context)
    else:
        return HttpResponseBadRequest

@login_required
def like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if movie.like_users.filter(pk=user.pk).exists():
        movie.like_users.remove(user)
    else:
        movie.like_users.add(user)
    return redirect('movies:detail', movie_pk)
