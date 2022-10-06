from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from urllib3 import HTTPResponse
from .models import CarMake, CarModel, CarDealer, DealerReview
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def test(request):
    #template = "test.html"
    context = {
      'fullName': "Erik Zeidler",
      'age': 28,
      'designation': "Software Engineer"
    }
    return render(request, 'djangoapp/test.html' , context)

# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html' , context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html' , context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/Eric.Zeidler%40melexis.com_djangoserver-space/capstone/get_dealerships"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/Eric.Zeidler%40melexis.com_djangoserver-space/capstone/get_review_new"
        # Get reviews from dealer_ID
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # Concat all dealer's short name
        review_list = ' '.join([review.review for review in reviews])
        sentiment_list = ' '.join(review.sentiment for review in reviews)
        # Return a list of dealer short name
        return HttpResponse(review_list, sentiment_list)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/Eric.Zeidler%40melexis.com_djangoserver-space/capstone/get_dealerships?id={dealer_id}"
        context['dealerships'] = get_dealers_from_cf(url)
        context['dealer'] = dealer_id
        context['cars'] = CarModel.objects.filter(dealership=dealer_id)
        print(context['cars'])

        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST" and request.user.is_authenticated:
        url_post = "https://eu-gb.functions.appdomain.cloud/api/v1/web/Eric.Zeidler%40melexis.com_djangoserver-space/capstone/post_review_new"
        context={}
        review_payload = dict()
        #review_payload["time"] = datetime.utcnow().isoformat()
        review_payload["dealership"] = dealer_id
        review_payload["name"] = request.POST.get('name', "")
        review_payload["review"] = request.POST.get('review', "")
        review_payload["purchased"] = request.POST.get('purchased', False)
        #print(review_payload)

        if review_payload['purchased']:
            car = CarModel.objects.filter(model_id=int(request.POST.get('car')))[0]
            review_payload['purchase']= "true"
            review_payload["purchase_date"] = request.POST.get('purchasedate')
            review_payload["car_model"] = car.name_model
            review_payload["car_year"] = car.year.strftime("%Y")
            review_payload["car_make"] = car.name_make.name_make
        else: 
            review_payload['purchase']= 'false'
            review_payload["purchase_date"] = ''
            review_payload["car_model"] = ''
            review_payload["car_year"] = ''
            review_payload["car_make"] = ''

        json_payload = json.dumps(review_payload)
        response = post_request(url_post,json_payload)
        print(json_payload)
        messages.success(request, 'Thank you for your review')
        #return HttpResponse(response)
        #return render(request, "index.html", context)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    elif request.user.is_authenticated != True:
        context={}
        context['error_message'] = "Please sign up first to leave a review!"
        return render(request, 'djangoapp/registration.html', context)   
