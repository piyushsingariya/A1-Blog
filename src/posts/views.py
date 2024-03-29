from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Post, Author, PostView
from .forms import CommentForm, PostForm
from marketing.models import Signup

def get_user_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


def search(request):
    """
    url/?q="_____"
    will be our search query
    """
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset
    }
    return render(request, 'search.html', context)


def get_category_count():
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title'))
    return queryset


def index(request):
    featured_index = Post.objects.filter(featured=True)
    latest_posts = Post.objects.order_by('-timestamp')[0:3]
    gallery_posts = Post.objects.order_by('-timestamp')[0:4]

    if request.method == "POST":
        email = request.POST["email"]
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()

    context = {
        'object_list': featured_index,
        'latest_posts': latest_posts,
        'gallery': gallery_posts,
    }
    return render(request, 'index.html', context)


def blog(request):
    category_count = get_category_count()
    post_list = Post.objects.all()
    latest_posts = Post.objects.order_by('-timestamp')[0:3]
    paginator = Paginator(post_list, 4)

    # Getting requested page number
    page_requested_var = 'page'
    page = request.GET.get(page_requested_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
    context = {
        'queryset': paginated_queryset,
        'latest_posts': latest_posts,
        'page_number': page_requested_var,
        'category_count': category_count,

    }
    return render(request, 'blog.html', context)


def post(request, id):
    category_count = get_category_count()
    post1 = get_object_or_404(Post, id=id)
    latest_posts = Post.objects.order_by('-timestamp')[0:3]
    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post1)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post1
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': post1.id
            }))

    context = {
        'post': post1,
        'category_count': category_count,
        'latest_posts': latest_posts,
        'form': form,
    }
    return render(request, 'post.html', context)


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_user_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form,
    }
    return render(request, "post-create.html", context)


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None,
                    request.FILES or None,
                    instance=post)
    author = get_user_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form,
    }
    return render(request, "post-create.html", context)


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("post-list"))
