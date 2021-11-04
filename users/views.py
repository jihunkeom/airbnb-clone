import os
import requests
from django.utils import translation
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import View
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from . import forms, models, mixins


# class LoginView(View):

#     # 요청이 get방식일 경우
#     def get(self, request):
#         form = forms.LoginForm()
#         return render(request, "users/login.html", {"form": form})

#     # 요청이 post방식일 경우
#     def post(self, request):
#         form = forms.LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get("email")
#             password = form.cleaned_data.get("password")
#             user = authenticate(request, username=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect(reverse("core:home"))

#         return render(request, "users/login.html", {"form": form})


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    messages.info(request, f"See you later {request.user.first_name}")
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(mixins.LoggedOutOnlyView, FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()  # form.py에서 만든 save 메소드 실행
        # 회원가입 되면 자동으로 로그인까지 되도록!
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # todo: add success message
    except models.User.DoesNotExist:
        # todo: add error message
        pass

    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code", None)
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException("Can't get access token")
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)

                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                f"Please login with {user.login_method}"
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"Welcome Back {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile")
        else:
            raise GithubException("Can't get code")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    app_key = os.environ.get("KAKAO_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_key}&redirect_uri={redirect_uri}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code")

        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Can't get authorization code")
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()

        email = profile_json.get("kakao_account").get("email")
        if email is None:
            raise KakaoException("Please also give me your email!")
        properties = profile_json.get("properties")
        nickname = properties.get("nickname")
        profile_image = properties.get("profile_image")

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(f"Please log in with: {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                # avatar은 모델에서 파일필드로 정의했기 때문에 아래와 같이 따로 저장해줘야 함!
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(photo_request.content)
                )
        login(request, user)
        messages.success(request, f"Welcome Back {user.first_name}")
        return redirect(reverse("core:home"))
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):
    model = models.User
    context_object_name = "user_obj"  # 이렇게 해줘야 다른 사람의 프로필로 계속 바뀌는 상황 방지! 21.3 참고

    # def get_context_data(self, **kwargs):
    #     # 템플릿에 유저 정보에 대한 컨텍스트뿐만 아니라 다른 정보에 대한 컨텍스트도 넘겨주기 위해 정의!
    #     context = super().get_context_data(**kwargs)  # 유저 정보에대한 컨텍스트 불러오기
    #     # 이제 불러온 유저 정보 컨텍스트에 추가적인 컨텍스트 추가해주기
    #     context["hello"] = "Hello!"
    #     return context


class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    # 업데이트 성공하면 자동으로 모델에서 정의한 get_absolute_url로 보내준다!!

    model = models.User
    template_name = "users/update_profile.html"
    fields = (
        "email",
        "first_name",
        "last_name",
        "gender",
        "bio",
        "birthday",
        "language",
        "currency",
    )
    success_message = "Profile Updated!"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # email칸에 들어온 입력이 유효하면 username도 이메일로 저장해주기
        email = form.cleaned_data.get("email")
        self.object.username = email
        self.object.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        # 플레이스홀더 추가해주기
        form = super().get_form(form_class=form_class)
        form.fields["email"].widget.attrs = {"placeholder": "Email"}
        form.fields["first_name"].widget.attrs = {"placeholder": "First Name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last Name"}
        form.fields["gender"].widget.attrs = {"placeholder": "Gender"}
        form.fields["birthday"].widget.attrs = {"placeholder": "Date of Birth"}
        form.fields["language"].widget.attrs = {"placeholder": "Language"}
        form.fields["currency"].widget.attrs = {"placeholder": "Currency"}
        return form


class UpdatePasswordView(
    mixins.LoggedInOnlyView,
    mixins.EmailLoginOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):
    template_name = "users/update-password.html"
    success_message = "Password Updated!"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current Password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New Password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm New Password"
        }
        return form

    def get_success_url(self):
        # 비밀번호 변경 성공시 이동할 곳
        # 이 함수 정의 안하면 자동으로 password_change_done이라는 url로 이동하게 된다!
        return self.request.user.get_absolute_url()


# 유저가 호스트모드인지 아닌지에 따라서 보이는 화면 구성 다르게 할건데 호스트모드 여부는 데이터베이스에 저장안해도되!!
# -> 호스트모드 여부는 세션으로 처리 가능!!
@login_required
def switch_hosting(request):
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True

    return redirect(reverse("core:home"))


def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return HttpResponse(status=200)
