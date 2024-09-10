"""Here is a very basic handling of accounts.
If you have your own account handling, don't worry,
just switch off account handling in
settings.WIKI_ACCOUNT_HANDLING = False

and remember to set
settings.WIKI_SIGNUP_URL = '/your/signup/url'
SETTINGS.LOGIN_URL
SETTINGS.LOGOUT_URL
"""

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView
from django.views.generic import FormView
from django.views.generic import UpdateView
from django.views.generic import View
from wiki import forms
from wiki.conf import settings
from wiki.models.account import UserProfile

User = get_user_model()


class Signup(CreateView):
    model = User
    form_class = forms.UserCreationForm
    template_name = "wiki/accounts/signup.html"

    def dispatch(self, request, *args, **kwargs):
        # Let logged in super users continue
        if not request.user.is_anonymous and not request.user.is_superuser:
            return redirect("wiki:root")
        # If account handling is disabled, don't go here
        if not settings.ACCOUNT_HANDLING:
            return redirect(settings.SIGNUP_URL)
        # Allow superusers to use signup page...
        if not request.user.is_superuser and not settings.ACCOUNT_SIGNUP_ALLOWED:
            c = {"error_msg": _("Account signup is only allowed for administrators.")}
            return render(request, "wiki/error.html", context=c)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["honeypot_class"] = context["form"].honeypot_class
        context["honeypot_jsfunction"] = context["form"].honeypot_jsfunction
        return context

    def get_success_url(self, *args):
        messages.success(
            self.request,
            _("You are now signed up... and now you can sign in!"),
        )
        return reverse("wiki:login")


class Logout(View):
    def dispatch(self, request, *args, **kwargs):
        if not settings.ACCOUNT_HANDLING:
            return redirect(settings.LOGOUT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        messages.info(request, _("You are no longer logged in. Bye bye!"))
        return redirect("wiki:root")


class Login(FormView):
    form_class = AuthenticationForm
    template_name = "wiki/accounts/login.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return redirect("wiki:root")
        if not settings.ACCOUNT_HANDLING:
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        self.request.session.set_test_cookie()
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        self.referer = request.session.get("login_referer", "")
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.referer = request.META.get("HTTP_REFERER", "")
        request.session["login_referer"] = self.referer
        return super().get(request, *args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        auth_login(self.request, form.get_user())
        messages.info(self.request, _("You are now logged in! Have fun!"))
        if self.request.GET.get("next", None):
            return redirect(self.request.GET["next"])
        if django_settings.LOGIN_REDIRECT_URL:
            return redirect(django_settings.LOGIN_REDIRECT_URL)
        else:
            if not self.referer:
                return redirect("wiki:root")
            return redirect(self.referer)


class Update(UpdateView):
    model = User
    form_class = forms.UserUpdateForm
    template_name = "wiki/accounts/account.html"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        """
        Save the initial referer
        """
        self.referer = request.META.get("HTTP_REFERER", "")
        request.session["login_referer"] = self.referer
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.referer = request.session.get("login_referer", "")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        pw = form.cleaned_data["password1"]
        if pw != "":
            self.object.set_password(pw)
        self.object.save()

        messages.info(self.request, _("Account info saved!"))

        # Redirect after saving
        if self.referer:
            return redirect(self.referer)
        if django_settings.LOGIN_REDIRECT_URL:
            return redirect(django_settings.LOGIN_REDIRECT_URL)
        return redirect("wiki:root")


from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import TemplateView


# Give the user the possibility to update their account and delete it
class UserAccountView(TemplateView):
    model = User
    template_name = "wiki/accounts/account_settings.html"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        """
        Save the initial referer
        """
        self.referer = request.META.get("HTTP_REFERER", "")
        request.session["login_referer"] = self.referer
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_form"] = forms.UserUpdateForm(instance=self.request.user)
        context["delete_form"] = forms.UserDeleteForm()
        context["img_form"] = forms.UserProfileImgForm()

        context["profile_picture"] = UserProfile.objects.get(
            user=self.request.user
        ).profile_image.url  # self.request.session.get("profile_picture", "")

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if "update_account" in request.POST:
            self.referer = request.session.get("login_referer", "")
            update_form = forms.UserUpdateForm(
                request.POST, request.FILES, instance=request.user
            )
            if update_form.is_valid():
                pw = update_form.cleaned_data["password1"]
                if pw != "":
                    self.object.set_password(pw)
                self.object.save()
                print("saved!")
        elif "delete_account" in request.POST:
            delete_form = forms.UserDeleteForm(request.POST)
            if delete_form.is_valid() and delete_form.cleaned_data["confirm_deletion"]:
                request.user.delete()
                print("deleted!")
                return redirect("wiki:root")
        elif "update_img" in request.POST:
            img_form = forms.UserProfileImgForm(request.POST, request.FILES)
            print(request.FILES)
            if img_form.is_valid():
                # Check if a UserProfile instance already exists for the current user - allows for updating the profile image instead of creating a new entry in db
                try:
                    # Fetch the existing user profile instance
                    user_profile = UserProfile.objects.get(user=request.user)
                    # Bind the form to the existing instance
                    img_form = forms.UserProfileImgForm(
                        request.POST, request.FILES, instance=user_profile
                    )
                except UserProfile.DoesNotExist:
                    # If no instance exists, create a new one
                    img_form = forms.UserProfileImgForm(request.POST, request.FILES)
                    user_profile = img_form.save(commit=False)
                    user_profile.user = request.user

                if img_form.is_valid():
                    # Save the updated instance
                    user_profile.save()
                    print("Profile picture updated successfully")
                else:
                    print("Form is not valid")
                    print(img_form.errors)

                self.request.session["profile_picture"] = user_profile.profile_image.url

                print("Profile image updated successfully!")
            else:
                print("Form is not valid.")
                print(img_form.errors)

        return self.get(request, *args, **kwargs)
