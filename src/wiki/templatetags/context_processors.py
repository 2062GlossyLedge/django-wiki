from wiki.models.account import UserProfile


def profile_picture(request):
    if request.user.is_authenticated:
        # Ensure a UserProfile instance exists for the current user
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        # If the profile image is not set, use the default image
        if not user_profile.profile_image:
            user_profile.profile_image = "profile_pics/default2.png"
            user_profile.save()  # Save only the current user's profile

        # Pass the profile picture URL to the template
        profile_picture = user_profile.profile_image.url
    else:
        profile_picture = None

    return {"profile_picture": profile_picture}
