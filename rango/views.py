from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category

def index(request):
    #construct a dictionary to pass to the template engine as its context
    # note the key bold message is the same as {{boldmessage }} in the template!
    # context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    # this queries category model to retrieve top 5 categories.
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories': category_list}
	return render(request, 'rango/index.html', context=context_dict)
	
def about(request):
	context_dict = {'boldmessage': "This tutorial was created by Maxine"}
	return render(request, 'rango/about.html', context=context_dict)