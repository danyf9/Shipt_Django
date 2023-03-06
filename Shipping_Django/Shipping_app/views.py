from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


# Create your views here.

class Home(View):
    @classmethod
    def get(cls, request):
        return render(request=request, template_name='Home.html')


class Base(View):
    @classmethod
    def get(cls, request):
        return render(request=request, template_name='Home.html')
