from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, get_object_or_404
from .models import MyUser, Profile, Follow
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


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


def profile_view(request):
    # ۱. بررسی ورود کاربر
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    # ۲. واکشی یا ساخت ایمن رکورد پروفایل
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # ۳. کلیه عملیات دریافت، اعتبارسنجی و ذخیره فقط در درخواست POST
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        email = request.POST.get("email", "").strip()
        bio = request.POST.get("bio", "").strip()
        avatar_image = request.FILES.get("avatar")

        # اعتبارسنجی عدم تکرار شماره تماس برای دیگران
        if (
            phone_number
            and MyUser.objects.filter(phone_number=phone_number)
            .exclude(id=request.user.id)
            .exists()
        ):
            messages.error(request, "این شماره تماس متعلق به فرکانس دیگری است.")
            return render(request, "accounts/profile.html")

        # اعتبارسنجی عدم تکرار ایمیل برای دیگران
        if (
            email
            and MyUser.objects.filter(email=email).exclude(id=request.user.id).exists()
        ):
            messages.error(request, "این آدرس ایمیل قبلاً در مدار ثبت شده است.")
            return render(request, "accounts/profile.html")

        # ذخیره داده‌های مدل کاربری (MyUser)
        user = request.user
        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        user.save()

        # ذخیره داده‌های نمایه (Profile)
        if full_name:
            profile.full_name = full_name
        if bio:
            profile.bio = bio
        if avatar_image:
            profile.avatar = avatar_image
        profile.save()

        messages.success(request, "اطلاعات هویتی و پایگاه شما با موفقیت ثبت شد.")
        return redirect("accounts:profile")

    # ۴. در درخواست GET صرفاً صفحه پروفایل نمایش داده می‌شود
    return render(request, "accounts/profile.html")


def toggle_follow(request, user_id):
    # ۱. بررسی احراز هویت
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    # ۲. واکشی کاربر هدف
    target_user = get_object_or_404(MyUser, id=user_id)

    # ۳. جلوگیری از فالو کردن خود
    if request.user == target_user:
        messages.error(request, "شما نمی‌توانید مدار خود را دنبال کنید!")
        return redirect(request.META.get("HTTP_REFERER", "posts:feed"))

    # ۴. وضعیت رابطه و اجرای Toggle
    target = Follow.objects.filter(follower=request.user, following=target_user)
    if target.exists():
        target.delete()
        messages.success(request, f"ارتباط شما با مدار {target_user.username} قطع شد.")
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        messages.success(
            request, f"شما اکنون در مدار {target_user.username} قرار دارید."
        )

    # ۵. بازگشت به صفحه قبلی
    return redirect(request.META.get("HTTP_REFERER", "posts:feed"))


def password_reset_request_view(request):
    # ۲. پردازش فرم ارسال ایمیل
    if request.method == "POST":
        email_input = request.POST.get("email", "").strip()

        if not email_input:
            messages.error(request, "لطفاً فرکانس ایمیل خود را وارد کنید.")
            return render(request, "accounts/password_reset.html")

        user = MyUser.objects.filter(email=email_input).first()

        # ۳. تولید کلید رمزنگاری‌شده و ارسال لینک در صورت وجود کاربر
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                reverse(
                    "accounts:password_reset_confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
            )

            subject = "فرمان بازیابی دسترسی به مدار InstaOrbit"
            message = (
                f"درود فضانورد {user.username}!\n\n"
                f"جهت تعیین رمز عبور جدید، پیوند زیر را باز کنید:\n"
                f"{reset_link}\n\n"
                f"اگر این درخواست از سوی شما ارسال نشده، آن را نادیده بگیرید."
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

        # ۴. پیام خروجی برای حفظ امنیت هویت کاربران
        messages.success(
            request,
            "اگر حساب فعالی با این ایمیل ثبت باشد، پیوند بازیابی برای شما مخابره شد.",
        )
        if request.user.is_authenticated:
            return redirect(request.META.get("HTTP_REFERER", "accounts:profile"))
        return redirect("accounts:login")

    # ۵. رندر صفحه در درخواست GET
    return render(request, "accounts/password_reset.html")


def password_reset_confirm_view(request, uidb64, token):
    # ۱. رمزگشایی شناسه کاربر از Base64 و واکشی از دیتابیس
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = MyUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    # ۲. بررسی معتبر بودن کاربر و امضای دیجیتال توکن
    if user is not None and default_token_generator.check_token(user, token):
        validlink = True

        # ۳. دریافت و اعتبارسنجی رمزهای عبور جدید در متد POST
        if request.method == "POST":
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            if not new_password or not confirm_password:
                messages.error(request, "لطفاً هر دو فیلد گذرواژه را تکمیل کنید.")
            elif new_password != confirm_password:
                messages.error(request, "گذرواژه جدید و تکرار آن یکسان نیستند.")
            elif len(new_password) < 8:
                messages.error(request, "گذرواژه مداری باید حداقل ۸ کاراکتر باشد.")
            else:
                # ۴. تغییر رمز، هش کردن در دیتابیس و باطل شدن خودکار توکن
                user.set_password(new_password)
                user.save()
                messages.success(
                    request,
                    "گذرواژه با موفقیت تغییر کرد. اکنون می‌توانید وارد مدار شوید.",
                )
                if request.user.is_authenticated:
                    return redirect("accounts:profile")
                return redirect("accounts:login")
    else:
        validlink = False

    # ۵. ارسال وضعیت معتبر بودن لینک به قالب HTML
    return render(
        request, "accounts/password_reset_confirm.html", {"validlink": validlink}
    )
