from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.urls import resolve, reverse
from django.http import HttpResponseRedirect
from post.models import Post, Follow, Stream
from userauth.models import Profile
from django.core.paginator import Paginator
from django.db import transaction
from userauth.forms import EditProfileForm


# Create your views here.
def userProfile(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user).order_by("-posted")

    # profile stats
    post_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists

    context = {
        "posts": posts,
        "profile": profile,
        "post_count": post_count,
        "following_count": following_count,
        "followers_count": followers_count,
        "follow_status": follow_status,
    }
    return render(request, "profile.html", context)


def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)
    try:
        f, created = Follow.objects.get_or_create(follower=user, following=following)
        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[0:10]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(
                        post=post, user=user, date=post.posted, following=following
                    )
                    stream.save()
        return HttpResponseRedirect(reverse("profile", args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("profile", args=[username]))


def editProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile.picture = form.cleaned_data.get("picture")
            profile.first_name = form.cleaned_data.get("first_name")
            profile.last_name = form.cleaned_data.get("last_name")
            profile.location = form.cleaned_data.get("location")
            profile.bio = form.cleaned_data.get("bio")
            profile.save()
            return redirect("profile", profile.user.username)
    else:
        form = EditProfileForm(instance=profile)
    context = {
        "form": form,
    }
    return render(request, "edit-profile.html", context)
