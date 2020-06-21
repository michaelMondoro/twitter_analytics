from django.shortcuts import render
from django.http import HttpResponse
from .forms import SearchForm
from django.template.defaulttags import register

import twitter
import time
from time import ctime
import smtplib
from threading import Timer
import networkx as nx
import matplotlib.pyplot as plt
import pandas

#Connect with Twitter
CONSUMER_KEY = "YOUR KEY"
CONSUMER_SECRET = "YOUR SECRET"
ACCESS_TOKEN = "YOUR TOKEN"
ACCESS_TOKEN_SECRET = "YOUR SECRET"
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACCESS_TOKEN_SECRET,
                  tweet_mode='extended')



def tweet_volume(start_month, end_month, tweets):
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	return tweets/(abs(months.index(end_month) - months.index(start_month)) + 1)

def friendship_distance(u1, u2):
	friends = api.GetFriends(screen_name=u1)
	u1_friends = [friend.screen_name for friend in friends]
	friends = api.GetFriends(screen_name=u2)
	u2_friends = [friend.screen_name for friend in friends]
	common = [friend for friend in u1_friends if friend in u2_friends]

	return common

def get_user_data(request, user):
	results = api.GetUserTimeline(screen_name=request.POST.get(user), count=200)
	results = results + api.GetUserTimeline(screen_name=request.POST.get(user), count=200, max_id=results[len(results)-1].id)


	hashtags = []
	for tweet in results:
		for tag in tweet.hashtags:
			if tag.text not in hashtags: 
				hashtags.append(tag.text)

	latest = results[0]
	
	start_date = results[0].created_at.split()
	end_date = results[len(results)-1].created_at.split()
	
	volume = tweet_volume(start_date[1], end_date[1], len(results))
	

	return {'name': request.POST.get(user), 
			'hashtags':hashtags, 
			'latest':latest, 
			'volume':round(volume,2), 
			'data':results}

def home(request):
	context = {}
	u1_name = request.POST.get('user1')
	u2_name = request.POST.get('user2')

	if request.method == 'POST':
		user1_data = get_user_data(request,'user1')
		user2_data = get_user_data(request,'user2')
		common_friends = friendship_distance(u1_name, u2_name)
		context = {
			'user1':user1_data,
			'user2':user2_data,
			'img1': api.GetUser(u1_name).profile_img_url,
			'img2': api.GetUser(u2_name).profile_img_url,
			'common_friends':common_friends
		}


	return render(request, 'twittermap/home.html', context)




