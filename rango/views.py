from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm

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
#	return HttpResponse("Rango says here is the about page. <a href='/rango/'>View index page</a>")
#	prints out whether the method is a GET or a POST
	print(request.method)
#	prints out the user name, if noone is logged in it prints 'Anonymous User'
	print(request.user)
	return render(request, 'rango/about.html', {})
	
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
	
def add_category(request):
	form = CategoryForm()
	
	#A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		
		#Have we been provided with a valid form?
		if form.is_valid():
			form.save(commit=True)
			#now that the category is saved
			#we could give a confirmation message
			#but since the most recent category added is on the index page_list
			#then we can direct the user back to the index page_list
			return index(request)
		else:
			# The supplied form contained errors -
			# just print them to the terminal.
			print(form.errors)
	return render(request, 'rango/add_category.html', {'form' : form})
	
def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None
		
	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)
	
	context_dict = {'form':form, 'category': category}
	return render(request, 'rango/add_page.html', context_dict)