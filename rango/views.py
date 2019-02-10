from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val
# Updated the function definition
def visitor_cookie_handler(request):
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7],
	'%Y-%m-%d %H:%M:%S')
# If it's been more than a day since the last visit...
	if (datetime.now() - last_visit_time).days > 0:
		visits = visits + 1
#update the last visit cookie now that we have updated the count
		request.session['last_visit'] = str(datetime.now())

	else:
# set the last visit cookie
		request.session['last_visit'] = last_visit_cookie
# Update/set the visits cookie
	request.session['visits'] = visits


def index(request):
    #construct a dictionary to pass to the template engine as its context
    # note the key bold message is the same as {{boldmessage }} in the template!
    # context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    # this queries category model to retrieve top 5 categories.
	request.session.set_test_cookie()

	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list}
	
	response = render(request, 'rango/index.html', context=context_dict)

	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	print(request.session['visits'])
	return response
	
def about(request):
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED!")
		request.session.delete_test_cookie()
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

def register(request):
	# A boolean value for telling the template
	# whether the registration was successful.
	# Set to False initially. Code changes value to
	# True when registration succeeds.
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True
		else:
			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	return render(request,
					'rango/register.html',
					{'user_form': user_form,
					'profile_form': profile_form,
					'registered': registered})

def user_login(request):
# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
# Gather the username and password provided by the user.
# This information is obtained from the login form.
# We use request.POST.get('<variable>') as opposed
# to request.POST['<variable>'], because the
# request.POST.get('<variable>') returns None if the
# value does not exist, while request.POST['<variable>']
# will raise a KeyError exception.
		username = request.POST.get('username')
		password = request.POST.get('password')
# Use Django's machinery to attempt to see if the username/password
# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)
# If we have a User object, the details are correct.
# If None (Python's way of representing the absence of a value), no user
# with matching credentials was found.
		if user:
# Is the account active? It could have been disabled.
			if user.is_active:
# If the account is valid and active, we can log the user in.
# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
# An inactive account was used - no logging in!
				return HttpResponse("Your Rango account is disabled.")
		else:
# Bad login details were provided. So we can't log the user in.
			print("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")
	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
	# No context variables to pass to the template system, hence the
	# blank dictionary object...
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	return render(request, 'rango/restricted.html', {})
@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

