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

		return Response({"detail": "This field may not be blank."}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
	"""View detail info of user"""

	def get(self, request, user_id):
		"""Get detail info of user with user_id"""
		user = get_user(user_id)
		serializer = UserDetailSerializer(user)

		return Response(serializer.data)

	def delete(self, request, user_id):
		"""Delete exeisting user with user_id"""
		user = get_user(user_id)
		user.delete()

		return Response(status=status.HTTP_204_NO_CONTENT)


class FriendListView(APIView):
	"""View list of user friends"""

	def get(self, request, user_id):
		"""Get list of all friends of user with user_id"""
		user = get_user(user_id)
		friends = user.get_friends()
		serializer = UserListSerializer(friends, many=True)

		return Response(serializer.data)


class FriendDeleteView(APIView):
	"""Delete user from friend list"""

	def delete(self, request, user_id, friend_id):
		"""Delete user with friend_id from friend list"""
		user = get_user(user_id)
		to_user = get_user(friend_id)

		try:
			req = FriendRequest.objects.get(from_user=user, to_user=to_user)
		except:
			return Response({"detail": "friend not found"}, status=status.HTTP_404_NOT_FOUND)

		req.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)



class OutgoingRequestListView(APIView):
	"""List of all outgoing requests with request_id, or create new"""

	def get(self, request, user_id):
		"""View list of outgoing friend requests"""
		user = get_user(user_id)

		outgoing_requests = []
		for req in FriendRequest.objects.filter(from_user=user):
			if not FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user):
				outgoing_requests.append(req)

		serializer = FriendRequestSerializer(outgoing_requests, many=True)

		return Response(serializer.data)


	def post(self, request, user_id):
		"""Creates new friend request from user with id user_id"""
		to_user = get_user(request.data.get("user_id"))
		user = get_user(user_id)

		if to_user.id == user.id:
			return Response({'detail': 'The user cannot send a friend request to himself'}, status=status.HTTP_400_BAD_REQUEST)

		if req := FriendRequest.objects.filter(from_user=user, to_user=to_user):
			serializer = FriendRequestSerializer(req[0])
			return Response(serializer.data, status=status.HTTP_201_CREATED)

		req = FriendRequest(from_user=user, to_user=to_user)
		req.save()
		serializer = FriendRequestSerializer(req)
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class OutgoingRequestDeleteView(APIView):
	"""Delete existing outgoing request with request_id"""

	def delete(self, request, user_id, request_id):
		"""Deletes friend request with request_id from request"""
		req = get_friend_request(request_id)
		req.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)



class IncomingRequestListView(APIView):
	"""List of all incoming friend requests"""

	def get(self, request, user_id):
		"""View list of incoming friend requests"""
		user = get_user(user_id)

		incoming_requests = []
		for req in FriendRequest.objects.filter(to_user=user):
			if not FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user):
				incoming_requests.append(req)

		serializer = FriendRequestSerializer(incoming_requests, many=True)

		return Response(serializer.data)


class IncomingRequestDetailView(APIView):
	"""Accept new friend request, or reject existing"""

	def put(self, request, user_id, request_id):
		"""Accept incoming friend request with request_id"""
		req = get_friend_request(request_id)

		if FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user):
			return Response({'detail': 'already in friends'}, status=status.HTTP_400_BAD_REQUEST)

		out_req = FriendRequest(from_user=req.to_user, to_user=req.from_user)
		out_req.save()

		serializer = FriendRequestSerializer(out_req)
		return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

	def delete(self, request, user_id, request_id):
		"""Reject incoming friend request with request_id"""
		req = get_friend_request(request_id)
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

	def get(self, request, user_id, oth_user_id):
		"""View relation between users"""
		user = get_user(user_id)
		oth_user = get_user(oth_user_id)

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
