from wiki.models.account import UserProfile


def profile_picture(request):
    if request.user.is_authenticated:
        # pass the profile picture url to the template, use default image if no profile picture is set
        UserProfile.objects.get_or_create(user=request.user)

        try:
            profile_picture = UserProfile.objects.get(
                user=request.user
            ).profile_image.url
        except:
            UserProfile.objects.update(profile_image="profile_pics/default2.png")
            profile_picture = UserProfile.objects.get(
                user=request.user
            ).profile_image.url
    else:
        profile_picture = None

    return {"profile_picture": profile_picture}
