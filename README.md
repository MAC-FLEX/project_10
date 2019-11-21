# pair project

## 1. 코드 리뷰

### Accounts App

#### models.py

```python
#accounts/models.py

class User(AbstractUser):
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followings')
```

유저간 follow 기능을 구현하기 위해서 User model에 ManyToManyField로 `followers`를 추가하고 related_name을 `followings`로 설정했습니다.



#### forms.py

```python
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model() # accounts.User
        fields = UserCreationForm.Meta.fields + ('email',)
```

Django에서 제공하는  UserCreationForm을 쓰면 유저에게 관리자 권한을 줄 위험성이 있어서

forms.py에서 새로운 UserCreationForm을 만들었습니다.



#### views.py

```python
def user_detail(request, user_pk):
    auth_user = get_object_or_404(get_user_model(), pk=user_pk)
    reviews = auth_user.review_set.all()
    movies = auth_user.like_movies.all()
    context = {'auth_user': auth_user, 'reviews': reviews, 'movies': movies}
    return render(request, 'accounts/detail.html', context)

@login_required
def follow(request, user_pk):
    person = get_object_or_404(get_user_model(), pk = user_pk)
    user = request.user
    if person != user:
        if person.followers.filter(pk=user.pk).exists():
            person.followers.remove(user)
        else:
            person.followers.add(user)
    return redirect('accounts:user_detail', person.pk)
```

`user_detail`에서  가져가야 하는 정보 중에 유저가 좋아요한 영화를 표현하기 위해서

Movie의 ManyToManyField인 like_users의 related_name인 `like_movies`를 썼습니다.

`follow`에서는 팔로우를 할 유저와 팔로우를 받을 유저를 구분하기 위해서 `person`과 `user`로 따로 변수를 썼습니다.



#### detail.html

```html
  {% for review in reviews %}
    <a href="{% url 'movies:detail' review.movie.pk %}"><h3>{{ review.movie.title }}</h3></a>
    
    {{ review.score }} | {{ review.content }}
    <hr>
  {% endfor %}

  {% with followings=auth_user.followings.all followers=auth_user.followers.all %}
    <h3>
    팔로잉: {{ followings|length }} |
    팔로워: {{ followers|length }}명
    </h3>
    <hr>
    {% if user != auth_user %}
      {% if user in followers %}
        <a href="{% url 'accounts:follow' auth_user.pk %}" role="button">UnFollow</a>
      {% else %}
        <a href="{% url 'accounts:follow' auth_user.pk %}" role="button">Follow</a>

      {% endif %}
    {% endif %}
  {% endwith %}
```

유저 상세페이지에서는 

- 해당 유저가 작성한 평점 정보와 
- 그 평점이 달린 영화로 이동할 수 있는 링크, 
- 유저의 팔로잉 및 팔로워 수를 보여주었습니다. 

해당 유저를 팔로우를 할 수 있도록 팔로우 기능 역시 유저 상세페이지에서 구현했습니다.





### Movie App

#### views.py

```python
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
```



#### Detail.html

![image-20191121145345545](C:\Users\student\AppData\Roaming\Typora\typora-user-images\image-20191121145345545.png)

```python
# views.py
def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    reviews = movie.review_set.all()
    review_form = ReviewForm()
    context = {'movie': movie, 'reviews' : reviews, 'review_form': review_form,}
    return render(request, 'movies/detail.html', context)
```



- 받아온 movie 의 인스턴스를 이용하여 영화정보를 나타냄.

```html
  <img src="{{ movie.poster_url}}" alt="#" width="300px">
  <p> 장르 :
    {% for genre in movie.genres.all %}
      {{ genre }}
    {% endfor %}
  </p>
  <p>관객 수 : {{ movie.audience }}</p>
  <p>줄거리 : {{ movie.description }}</p>
```



- movie 의 like_users.all 에 user 가 있고 없음을 판단하여, 좋아요의 하트의 색을 변경함.

```html
  <p class="card-text">
    <a href="{% url 'movies:like' movie.pk %}">
      {% if  user in movie.like_users.all %}
        <i class="fas fa-heart" style="color: crimson;"></i>
      {% else %}
        <i class="fas fa-heart" style="color: black;"></i>
      {% endif %}
    </a>
    {{ movie.like_users.all|length }}명이 이 글을 좋아합니다.
```



- movie.review_set.all()으로 그 영화에 대한 review를 reviews에 담는다.
- review_form = ReviewForm()으로 html에 사용될 review 작성폼을 정의함.

```html
  {% for review in reviews %}
    <div>
      평점 {{ review.score }}/ 댓글 {{ forloop.revcounter }} : {{ review.content }} / 작성자 : {{ review.user }}
      {% if review.user == request.user %}
        <form action="{% url 'movies:review_delete' movie.pk review.pk %}" method="POST" style="display: inline;">
          {% csrf_token %}
          <input type="submit" value="DELETE">
        </form>
      {% endif %}
    </div>
  {% empty %}
    <p><b>댓글이 없습니다.</b></p>
```



## 2. 느낀점

- 조수지

  git fork를 이용해서 협업을 처음 해 봤는데 아무래도 처음 다뤄보는 기능이다 보니 여러번 실수를 하게 되서 당황스러웠습니다. 제가 올린 자료를 팀원이 받지 못하기도 하고 브랜치가 아니라 마스터에서 작업하기도 하면서 git fork의 기능을 천천히 숙지하게 된 시간이었습니다.  

- 차진권

  git 협업 과정에서 어려움이 많았습니다. 처음 git을 활용한 협업 프로젝트여서 명령어 사용이나 흐름에 대해서 미숙했고 가장 문제가 되었던 부분은 feature환경에서 코드를 작성할 코드를 master 환경에서  작성했던 것입니다. 여러번의 커밋과 머지를 통해 익숙해질 수 있었습니다.