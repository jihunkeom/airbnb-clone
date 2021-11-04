from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class LoggedOutOnlyView(UserPassesTestMixin):
    # 로그인 안한 사람들이 특정 url에 접근하지 못하도록 하기 위해서 정의
    # 이걸 다른 뷰에서 사용하면 매번 test_func을 실행시킴
    # test func이 true 값을 반환하면 특정 작업 처리하도록!

    # 로그인 된 사람들은 이 뷰로 이동하려하면 아래 메세지 보여준다
    permission_denied_message = "Page Not Found"

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        # 로그인 된 사람들은 이 뷰로 이동할 수 없도록 하기!
        messages.error(self.request, "Can't go there")
        return redirect("core:home")


class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy("users:login")


class EmailLoginOnlyView(UserPassesTestMixin):
    # 카카오로 로그인 했으면 비밀번호 수정 못하도록

    def test_func(self):
        return self.request.user.login_method == "email"

    def handle_no_permission(self):
        messages.error(self.request, "Can't go there")
        return redirect("core:home")
