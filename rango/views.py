from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page

def index(request):
    #construct a dictionary to pass to the template engine as its context
    # note the key bold message is the same as {{boldmessage }} in the template!
    # context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    # this queries category model to retrieve top 5 categories.
	
	category_list = Category.objects.order_by('-likes')[:5]
	
	page_list = Page.objects.order_by('-views')[:5]
	
	context_dict = {'categories': category_list, 'pages': page_list}
	
	return render(request, 'rango/index.html', context=context_dict)
	
def about(request):
	context_dict = {'boldmessage': "This tutorial was put together by Maxine"}
	return render(request, 'rango/about.html', context=context_dict)
	
def show_category(request, category_name_slug):
	context_dict = {}
	
	try:
		category = Category.objects.get(slug=category_name_slug)
		
		pages = Page.objects.filter(category=category)
		
		context_dict['pages'] = pages
		
		context_dict['category'] = category
	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None
	
	return render(request, 'rango/category.html', context_dict)