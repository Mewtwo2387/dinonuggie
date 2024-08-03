from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpRequest
from django.template import loader
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import Dinonuggies
import logging
import requests
from datetime import datetime, timezone

def index(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('/login')
    
    template = loader.get_template('main/index.html')
    data = Dinonuggies.objects.filter(user=request.user).first()

    if not data:
        data = Dinonuggies.objects.create(user=request.user, count=0, last_claim=None)

    can_claim = data.last_claim is None or (datetime.now(timezone.utc) - data.last_claim).days >= 1

    return HttpResponse(template.render({'user':request.user, 'dinonuggies':data.count, 'can_claim':can_claim}, request))

def claim(request: HttpRequest) -> HttpResponse:
    data = Dinonuggies.objects.filter(user=request.user).first()

    if not data:
        data = Dinonuggies.objects.create(user=request.user, count=0, last_claim=None)

    if data.last_claim is not None and (datetime.now(timezone.utc) - data.last_claim).days < 1:
        return redirect('/')

    if data.last_claim is not None and (datetime.now(timezone.utc) - data.last_claim).days >= 2:
        data.streak = 0
    
    data.count += 50 + data.streak * 25
    data.streak += 1
    data.last_claim = datetime.now(timezone.utc)
    data.save()

    return redirect('/')


def google_login(request: HttpRequest) -> HttpResponse:
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={settings.GOOGLE_OAUTH2_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    
    logger = logging.getLogger("console")
    logger.info(f"ID:{settings.GOOGLE_OAUTH2_CLIENT_ID}")
    logger.info(f"Secret:{settings.GOOGLE_OAUTH2_CLIENT_SECRET}")
    logger.info(f"Redirect URI:{settings.GOOGLE_REDIRECT_URI}")
    logger.info(f"Redirecting to {auth_url}")

    return HttpResponseRedirect(auth_url)

def oauth2callback(request: HttpRequest) -> HttpResponse:
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "Missing code parameter"}, status=400)
    

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_r = requests.post(token_url, data=token_data)
    token_json = token_r.json()

    if "error" in token_json:
        return JsonResponse({"error": token_json["error"]}, status=400)

    access_token = token_json.get("access_token")
    id_token = token_json.get("id_token")


    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    user_info_params = {"access_token": access_token, "alt": "json"}
    user_info_r = requests.get(user_info_url, params=user_info_params)
    user_info = user_info_r.json()



    user, created = User.objects.get_or_create(username=user_info["email"], defaults={
        "first_name": user_info.get("given_name", ""),
        "last_name": user_info.get("family_name", ""),
        "email": user_info["email"],
    })


    auth_login(request, user)

    return redirect('/')

def logout(request: HttpRequest) -> HttpResponse:
    auth_logout(request)
    return redirect('/')