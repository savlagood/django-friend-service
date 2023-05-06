from django.http import Http404
from .models import User, FriendRequest


def get_user(pk):
	"""Returns User object or raises 404"""
	try:
		return User.objects.get(id=pk)
	except:
		raise Http404


def get_friend_request(pk):
	"""Returns FriendRequest object or raises 404"""
	try:
		return FriendRequest.objects.get(id=pk)
	except:
		raise Http404