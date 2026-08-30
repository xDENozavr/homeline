from django.shortcuts import render

def terms_of_use(request):
    return render(request, 'pages/terms_of_use.html')

def faq(request):
    return render(request, 'pages/faq.html')

def about_us(request):
    return render(request, 'pages/who_are_we.html')