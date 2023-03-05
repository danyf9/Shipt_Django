from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


# Create your views here.

class Home(View):
    @classmethod
    def get(cls, request):
        return HttpResponse('Home')
