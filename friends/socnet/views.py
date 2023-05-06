from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import Http404

from .utils import get_user, get_friend_request
from .models import User, FriendRequest
from .serializers import UserListSerializer, UserDetailSerializer, FriendRequestSerializer



class UserListView(APIView):
	"""View list of users, create new or delete existing"""

	def get(self, request):
		"""Get list of all users"""
		users = User.objects.all()
		serializer = UserListSerializer(users, many=True)

		return Response(serializer.data)

	def post(self, request):
		"""Create new user wuth data from request"""
		serializer = UserListSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()
			detail_serializer = UserDetailSerializer(user)

			return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request):
		"""Delete exeisting user with user_id from request"""
		user = get_user(request.data.get('user_id'))
		user.delete()

		return Response(status=status.HTTP_204_NO_CONTENT)


class UserDetailView(APIView):
	"""View detail info of user"""

	def get(self, request, user_pk):
		"""Get detail info of user with user_pk"""
		user = get_user(user_pk)
		serializer = UserDetailSerializer(user)

		return Response(serializer.data)


class FriendsListView(APIView):
	"""View list of user friends, or delete user from friend list"""

	def get(self, request, user_pk):
		"""Get list of all friends of user with user_pk"""
		user = get_user(user_pk)
		friends = user.get_friends()
		serializer = UserListSerializer(friends, many=True)

		return Response(serializer.data)

	def post(self, request, user_pk):
		"""Delete user with user_id from friend list"""
		user = get_user(user_pk)
		to_user = get_user(request.data.get('user_id'))

		try:
			req = FriendRequest.objects.get(from_user=user, to_user=to_user)
		except:
			return Response(status=status.HTTP_400_BAD_REQUEST)

		req.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)



class OutgoingFriendRequestsListView(APIView):
	"""List of all outgoing requests with request_id, or create new, or delete existing"""

	def get(self, request, user_pk):
		"""View list of outgoing friend requests"""
		user = get_user(user_pk)
		outgoing_requests = FriendRequest.objects.filter(from_user=user)
		serializer = FriendRequestSerializer(outgoing_requests, many=True)

		return Response(serializer.data)


	def post(self, request, user_pk):
		"""Creates new friend request from user with id user_pk"""
		to_user = get_user(request.data.get("user_id"))
		user = get_user(user_pk)

		if to_user.id == user.id:
			return Response({'error': 'The user cannot send a friend request to himself'}, status=status.HTTP_400_BAD_REQUEST)

		if req := FriendRequest.objects.filter(from_user=user, to_user=to_user):
			serializer = FriendRequestSerializer(req[0])
			return Response(serializer.data, status=status.HTTP_201_CREATED)

		req = FriendRequest(from_user=user, to_user=to_user)
		req.save()
		serializer = FriendRequestSerializer(req)
		return Response(serializer.data, status=status.HTTP_201_CREATED)


	def delete(self, request, user_pk):
		"""Deletes friend request with request_id from request"""
		req = get_friend_request(request.data.get('request_id'))
		req.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)



class IncomingFriendRequestsListView(APIView):
	"""List of all incoming friend requests, or accept new, or reject existing"""

	def get(self, request, user_pk):
		"""GET to view list of incoming friend requests"""
		user = get_user(user_pk)
		incoming_requests = FriendRequest.objects.filter(to_user=user)
		serializer = FriendRequestSerializer(incoming_requests, many=True)

		return Response(serializer.data)

	def post(self, request, user_pk):
		"""POST to accept incoming friend request with request_id"""
		req = get_friend_request(request.data.get('request_id'))
		# out_req = FriendRequest(from_user=req.to_user, to_user=req.from_user)

		if FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user):
			return Response({'error': 'already in friends'}, status=status.HTTP_400_BAD_REQUEST)

		out_req = FriendRequest(from_user=req.to_user, to_user=req.from_user)
		out_req.save()

		serializer = FriendRequestSerializer(out_req)
		return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

	def delete(self, request, user_pk):
		"""DELETE to reject incoming friend request with request_id"""
		req = get_friend_request(request.data.get('request_id'))
		req.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
		


class FriendRelationView(APIView):
	"""
	Relations between users:
	- friends
	- outgoing request
	- incoming request
	- nothing
	"""

	def get(self, request, user_pk, oth_user_pk):
		"""View relation between users"""
		user = get_user(user_pk)
		oth_user = get_user(oth_user_pk)

		if (FriendRequest.objects.filter(from_user=user, to_user=oth_user) and
				FriendRequest.objects.filter(from_user=oth_user, to_user=user)):
			status = 'friends'

		elif FriendRequest.objects.filter(from_user=user, to_user=oth_user):
			status = 'outgoing request'
		elif FriendRequest.objects.filter(from_user=oth_user, to_user=user):
			status = 'incoming request'
		else:
			status = 'nothing'

		return Response({'status': status})
