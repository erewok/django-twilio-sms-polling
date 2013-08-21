from django.shortcuts import render_to_response
from django.http import HttpResponse

def contact(request):
    return render_to_response('main/contact_form.html')
