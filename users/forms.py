from django import forms
from . import models


class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    # form들을 validate&전처리하기 위한 메소드 (clean_필드명()으로 이름 작성해야 함)
    # def clean_email():
    #     email = self.cleaned_data.get("email") #사용자가 입력한 이메일
    #     try:
    #         models.User.objects.get(username=email)
    #         return email
    #     except meodels.User.DoesNotExist:
    #         raise form.ValidationError("User does not exist")

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = models.User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("Password is Wrong"))
        except models.User.DoesNotExist:
            self.add_error("email", forms.ValidationError("User does not exist"))


# class SignUpForm(forms.Form):

#     first_name = forms.CharField(max_length=80)
#     last_name = forms.CharField(max_length=80)
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)
#     password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         try:
#             models.User.objects.get(email=email)
#             raise forms.ValidationError("User already exists with that email")

#         except models.User.DoesNotExist:
#             return email

#     def clean_password1(self):
#         password1 = self.cleaned_data.get("password1")
#         password = self.cleaned_data.get("password")

#         if password != password1:
#             raise forms.ValidationError("Password confirmation does not match")
#         else:
#             return password

#     def save(self):  # 회원가입시 입력한 내용 저장해두기
#         first_name = self.cleaned_data.get("first_name")
#         last_name = self.cleaned_data.get("last_name")
#         email = self.cleaned_data.get("email")
#         password = self.cleaned_data.get("password")

#         user = models.User.objects.create_user(
#             username=email, email=email, password=password
#         )
#         user.first_name = first_name
#         user.last_name = last_name
#         user.save()


class SignUpForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = (
            "first_name",
            "last_name",
            "email",
        )  # 모델에 있는 필드들 가져오면 자동으로 clean까지 된다!

    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")
        if password != password1:
            raise forms.ValidationError("Password Confirmation does not match!")
        else:
            return password

    # ModelForm은 기본적으로 데이터베이스에 저장해주는 save 메소드를 가지고 있음
    # 하지만 비밀번호 등 설정을 위해 오버라이딩하자
    def save(self, *args, **kwargs):
        user = super().save(commit=False)  # commit=False로 하면 객체 생성하지만 db에는 저장하지 않음
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        user.username = email
        user.set_password(password)
        user.save()  # default는 commit=True
