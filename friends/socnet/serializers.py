from rest_framework import serializers

from .models import User, FriendRequest


class UserListSerializer(serializers.ModelSerializer):
	"""Shows list of users"""
	class Meta:
		model = User
		fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
	friends = serializers.SerializerMethodField()
	outgoing_requests = serializers.SerializerMethodField()
	incoming_requests = serializers.SerializerMethodField()

	def get_friends(self, obj):
		"""Returns list of friends"""
		out_req = FriendRequest.objects.filter(from_user=obj)
		
		friends = []
		for req in out_req:
			if len(FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user)):
				friends.append(req.to_user)

		return UserListSerializer(friends, many=True).data

	def get_outgoing_requests(self, obj):
		"""Returns list of outgoing friend requests"""
		out_req = []
		for req in FriendRequest.objects.filter(from_user=obj):
			if len(FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user)) == 0:
				out_req.append(req)

		return FriendRequestSerializer(out_req, many=True).data

	def get_incoming_requests(self, obj):
		"""Returns list of incoming friend requests"""
		in_req = []
		for req in FriendRequest.objects.filter(to_user=obj):
			if len(FriendRequest.objects.filter(from_user=req.to_user, to_user=req.from_user)) == 0:
				in_req.append(req)
				
		return FriendRequestSerializer(in_req, many=True).data

	class Meta:
		model = User
		fields = '__all__'


class FriendRequestSerializer(serializers.ModelSerializer):
	class Meta:
		model = FriendRequest
		fields = '__all__'
