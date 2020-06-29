from django.shortcuts import render
from django.http import HttpResponse
from .forms import SearchForm
from django.template.defaulttags import register

import networkx as networkx
import twitter
import time
from time import ctime
import smtplib
from threading import Timer
import networkx as nx
import matplotlib.pyplot as plt
import pandas

#Connect with Twitter
CONSUMER_KEY = "l73kjRjMDlzNvZ67Kbw41RO63"
CONSUMER_SECRET = "VrrwIrIbzaITfQZEqZ4cOTiUW9sTJ4JsjJEg4jXmhTj7e9bdnA"
ACCESS_TOKEN = "983195774694682625-hJEVsEN3AkxjghEHdZup7S37fTanuBZ"
ACCESS_TOKEN_SECRET = "jljtQ60dF1BTQIYEzMCgH0EsqjV41Fn3pdD8M0M6jLe2O"
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACCESS_TOKEN_SECRET,
                  tweet_mode='extended')


def make_edgelist(user, nodelist, user2=None):
	edgelist = []
	i = 0
	while i < len(nodelist) - 1:
		edgelist.append((nodelist[i], user))
		if user2:
			edgelist.append((nodelist[i], user2))
		i += 1
	return edgelist


def map(user1_sn, user2_sn):

	u1_color = 'b'
	u2_color = 'g'
	common_color = 'y'

	user1 = api.GetUser(screen_name=user1_sn)
	user2 = api.GetUser(screen_name=user2_sn)
	u1_friends = api.GetFriends(screen_name=user1_sn)
	u2_friends = api.GetFriends(screen_name=user2_sn)
	u1_friend_names = [friend.screen_name for friend in u1_friends]
	u2_friend_names = [friend.screen_name for friend in u2_friends]
	user1_edgelist = make_edgelist(user1_sn, u1_friend_names)
	user2_edgelist = make_edgelist(user2_sn,u2_friend_names)

	# Create Graph
	g = nx.Graph()
	g.add_node(user1.screen_name)
	g.add_node(user2.screen_name)

	common_friends = []

	for friend in u1_friends:
		if friend.screen_name in u2_friend_names:
			common_friends.append(friend.screen_name)
		g.add_node(friend.screen_name)
		g.add_edge(user1.screen_name, friend.screen_name)

	for friend in u2_friends:
		g.add_node(friend.screen_name)
		g.add_edge(user2.screen_name, friend.screen_name)

	
	common_edges = make_edgelist(user1_sn, common_friends, user2=user2_sn)
	pos = nx.random_layout(g)
	nx.draw_networkx_nodes(g, pos, nodelist=u1_friend_names, node_color='b')
	nx.draw_networkx_nodes(g, pos, nodelist=u2_friend_names, node_color='g')
	nx.draw_networkx_nodes(g, pos, nodelist=common_friends, node_color='y')
	nx.draw_networkx_nodes(g, pos, nodelist=[user1.screen_name], node_color='r')
	nx.draw_networkx_nodes(g, pos, nodelist=[user2.screen_name], node_color='r')
	nx.draw_networkx_labels(g, pos, font_size=7)
	nx.draw_networkx_edges(g, pos, edgelist=common_edges, edge_color='b', width=.7, alpha=.4)
	#nx.draw_networkx_edges(g, pos, edgelist=user2_edgelist, edge_color='g', width=.7, alpha=.4)

	plt.title("Relational map of {} and {}".format(user1_sn, user2_sn))
	plt.savefig('map.pdf')


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
			'img1': api.GetUser(screen_name=u1_name).profile_image_url,
			'img2': api.GetUser(screen_name=u2_name).profile_image_url,
			'common_friends':common_friends
		}


	return render(request, 'twittermap/home.html', context)




