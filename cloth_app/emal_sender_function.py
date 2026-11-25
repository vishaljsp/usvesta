
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect

def sending_email_forget(subject,mesej,email):
    send_mail(
        subject,
        mesej,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    
def redirecting_previus_pege(request):
    previous_page=request.META.get('HTTP_REFERER', '/') 
    return redirect(previous_page)
    