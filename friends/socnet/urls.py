from django.urls import path

from . import views


urlpatterns = [
	path('users/', views.UserListView.as_view(), name='user-list'),
	path('users/<int:user_pk>/', views.UserDetailView.as_view(), name='user-detail'),
	path('users/<int:user_pk>/friends/', views.FriendsListView.as_view(), name='user-friends-list'),
	path('users/<int:user_pk>/outgoing_requests/', views.OutgoingFriendRequestsListView.as_view(), name='outgoing-friend-requests-list'),
	path('users/<int:user_pk>/incoming_requests/', views.IncomingFriendRequestsListView.as_view(), name='incoming-friend-requests-list'),
	path('users/<int:user_pk>/friend_status/<int:oth_user_pk>/', views.FriendRelationView.as_view(), name='friend-relation'),
]
