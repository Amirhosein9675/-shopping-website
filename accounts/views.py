from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationsForm, UserVerifyCodeForm, UserLoginForm, UserForgetPasswordFrom, UserVerifyPasswordCodeForm, UserVerifyResetPasswordDoneForm
import random
from utils import send_otp_code
from .models import OtpCode, User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin


class UserRegisterView(View):
    form_class = UserRegistrationsForm
    template_name = 'accounts/user_register.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            send_otp_code(form.cleaned_data['phone'], random_code)
            OtpCode.objects.create(
                phone_number=form.cleaned_data['phone'], code=random_code)
            request.session['user_registration_info'] = {
                'phone_number': form.cleaned_data['phone'],
                'email': form.cleaned_data['email'],
                'full_name': form.cleaned_data['full_name'],
                'password': form.cleaned_data['password']
            }
            messages.success(request, 'we sent you a code', 'success')
            return redirect('accounts:verify_code')
        return render(request, self.template_name, {'form': form})


class UserVerifyCodeView(View):
    form_class = UserVerifyCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/verify.html', {'form': form})

    def post(self, request):
        user_session = request.session['user_registration_info']
        code_instance = OtpCode.objects.get(
            phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if code_instance.code == cd['code']:
                User.objects.create_user(
                    user_session['phone_number'], user_session['email'],
                    user_session['full_name'], user_session['password'])
                code_instance.delete()
                messages.success(request, 'you registred', 'success')
                return redirect('home:home')
            else:
                messages.error(request, 'code is wrong', 'danger')
                return redirect('accounts:verify_code')
        return redirect('home:home')


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'you are already authenticated', 'info')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd['phone'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'login successfuly', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(
                request, 'phone number or password is wrong', 'warning')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'you are logout', 'success')
        return redirect('home:home')


class UserForgetPasswordView(View):
    form_class = UserForgetPasswordFrom

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/forget.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.filter(phone_number=cd['phone']).exists()
            if user == False:
                messages.error(request, 'you are not register ', 'warning')
                return redirect('accounts:user_register')
            else:
                random_code = random.randint(1000, 9999)
                send_otp_code(cd['phone'], random_code)
                OtpCode.objects.create(
                    phone_number=cd['phone'], code=random_code)
                request.session['user_password_info'] = {
                    'phone_number': cd['phone'],
                }
                messages.success(request, 'we sent you a code', 'success')
                return redirect('accounts:password_verify')
        return render(request, 'accounts/forget.html', {'form': form})


class UserVerifyResetPasswordView(View):
    form_class = UserVerifyPasswordCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/resetpass.html', {'form': form})

    def post(self, request):
        user_session = request.session['user_password_info']
        code_instance = OtpCode.objects.filter(
            phone_number=user_session['phone_number']).latest('created')
        print(code_instance.code)
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if code_instance.code == cd['code']:
                code_instance.delete()
                return redirect('accounts:password_done')
            else:
                messages.error(request, 'code is wrong', 'warning')
                return redirect('accounts:password_verify')
        return render(request, 'accounts/resetpass.html', {'form': form})


class UserVerifyResetPasswordDoneView(View):
    form_class = UserVerifyResetPasswordDoneForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/pass_done.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        user_session = request.session['user_password_info']
        user = User.objects.get(phone_number=user_session['phone_number'])
        if form.is_valid():
            new_password = form.cleaned_data['password1']
            user.set_password(new_password)
            user.save()
            messages.success(
                request, 'password confrim successfuly', 'success')
            return redirect('home:home')
        return render(request, 'accounts/pass_done.html', {'form': form})
