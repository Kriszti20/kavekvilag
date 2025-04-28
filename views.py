from django.shortcuts import render

def kezdolap(request):
    return render(request, 'kavezok/kezdolap.html')