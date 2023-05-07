from django.urls import path

from . import views


urlpatterns = [
	path('users/', views.UserListView.as_view(), name='user-list'),
	path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
	path('users/<int:user_id>/friends/', views.FriendsListView.as_view(), name='user-friends-list'),
	path('users/<int:user_id>/friends/<int:friend_id>/', views.FriendDeleteView.as_view(), name='user-firend-delete'),
	path('users/<int:user_id>/outgoing_requests/', views.OutgoingFriendRequestsListView.as_view(), name='outgoing-friend-requests-list'),
	path('users/<int:user_id>/outgoing_requests/<int:request_id>/', views.OutgoingFriendRequestsDeleteView.as_view(), name='outgoing-friend-requests-delete'),
	path('users/<int:user_id>/incoming_requests/', views.IncomingFriendRequestsListView.as_view(), name='incoming-friend-requests-list'),
	path('users/<int:user_id>/incoming_requests/<int:request_id>/', views.IncomingFriendRequestsDetailView.as_view(), name='incoming-friend-requests-detail'),
	path('users/<int:user_id>/friend_status/<int:oth_user_id>/', views.FriendRelationView.as_view(), name='friend-relation'),
]
