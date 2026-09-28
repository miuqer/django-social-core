from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from .models import MyUser


def register_view(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    if request.method == "POST":
        username_input = request.POST.get("username", "").strip()
        email_input = request.POST.get("email", "").strip()
        phone_input = request.POST.get("phone_number", "").strip()
        password_input = request.POST.get("password", "")
        confirm_password_input = request.POST.get("confirm_password", "")

        # ۱. اعتبارسنجی فیلدهای اجباری
        if (
            not username_input
            or not phone_input
            or not password_input
            or not confirm_password_input
        ):
            messages.error(request, "لطفاً تمام فیلدهای الزامی را تکمیل کنید.")
            return render(request, "accounts/register.html")

        # ۲. تطابق رمز عبور
        if password_input != confirm_password_input:
            messages.error(request, "رمز عبور و تکرار آن مطابقت ندارند.")
            return render(request, "accounts/register.html")

        # ۳. اعتبارسنجی شماره تلفن (طول ۱۱ رقم و شروع با ۰۹)
        if (
            not phone_input.isdigit()
            or len(phone_input) != 11
            or not phone_input.startswith("09")
        ):
            messages.error(request, "شماره همراه باید ۱۱ رقم بوده و با ۰۹ آغاز شود.")
            return render(request, "accounts/register.html")

        # ۴. بررسی یکتایی در پایگاه داده
        if MyUser.objects.filter(username=username_input).exists():
            messages.error(request, "این نام کاربری قبلاً در مدار ثبت شده است.")
            return render(request, "accounts/register.html")

        if MyUser.objects.filter(phone_number=phone_input).exists():
            messages.error(request, "این شماره تماس قبلاً ثبت شده است.")
            return render(request, "accounts/register.html")

        if email_input and MyUser.objects.filter(email=email_input).exists():
            messages.error(request, "این فرکانس ایمیل قبلاً استفاده شده است.")
            return render(request, "accounts/register.html")

        # ۵. ساخت کاربر جدید
        user = MyUser.objects.create_user(
            username=username_input,
            phone_number=phone_input,
            email=email_input if email_input else None,
            password=password_input,
        )

        messages.success(
            request, "فضانورد گرامی، ثبت‌نام با موفقیت انجام شد. اکنون وارد شوید."
        )
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    if request.method == "POST":
        username_input = request.POST.get("username", "").strip()
        password_input = request.POST.get("password", "")

        if not username_input or not password_input:
            messages.error(request, "شناسه کاربری و رمز عبور را وارد کنید.")
            return render(request, "accounts/login.html")

        # احراز هویت بر مبنای رمز هش‌شده
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"خوش آمدید، کاپیتان {user.username}!")
                next_url = request.GET.get("next")
                return redirect(next_url if next_url else "posts:feed")
            else:
                messages.error(request, "شناسه مداری شما غیرفعال شده است.")
        else:
            messages.error(request, "شناسه کاربری یا رمز عبور اشتباه است.")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "ارتباط با ایستگاه فضایی قطع شد. با موفقیت خارج شدید.")
    return redirect("accounts:login")
