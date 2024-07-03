from django.shortcuts import render, redirect
from post.models import Tag, Stream, Follow, Post
from django.contrib.auth.decorators import login_required
from post.forms import newPostForm

# Create your views here.


def home(request):
    user = request.user
    posts = Stream.objects.filter(user=user)
    group_ids = []
    for post in posts:
        group_ids.append(post.post_id)
    post_items = Post.objects.filter(id__in=group_ids).all().order_by("-posted")
    context = {
        "post_items": post_items,
    }
    return render(request, "home.html", context)


def newPost(request):
    user = request.user
    tags_objs = []

    if request.method == "POST":
        form = newPostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get("picture")
            caption = form.cleaned_data.get("caption")
            tag_form = form.cleaned_data.get("tag")
            tags_list = list(tag_form.split("#"))
            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            p, created = Post.objects.get_or_create(
                Picture=picture, caption=caption, user_id=user
            )
            p.tags_list.set(tags_objs)
            p.save()
            return redirect("home")
    else:
        form = newPostForm()
        context = {
            "form": form,
        }
    return render(request, "post.html", context)


def messages(request):
    return render(request, "messages.html")


def profile(request):
    return render(request, "profile.html")


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")
