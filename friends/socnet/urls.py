from django.urls import path

from . import views


urlpatterns = [
	path('users/', views.UserListView.as_view(), name='user-list'),
	path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
	path('users/<int:user_id>/friends/', views.FriendListView.as_view(), name='friend-list'),
	path('users/<int:user_id>/friends/<int:friend_id>/', views.FriendDeleteView.as_view(), name='firend-delete'),
	path('users/<int:user_id>/outgoing_requests/', views.OutgoingRequestListView.as_view(), name='outgoing-request-list'),
	path('users/<int:user_id>/outgoing_requests/<int:request_id>/', views.OutgoingRequestDeleteView.as_view(), name='outgoing-request-delete'),
	path('users/<int:user_id>/incoming_requests/', views.IncomingRequestListView.as_view(), name='incoming-friend-requests-list'),
	path('users/<int:user_id>/incoming_requests/<int:request_id>/', views.IncomingRequestDetailView.as_view(), name='incoming-request-detail'),
	path('users/<int:user_id>/friend_status/<int:oth_user_id>/', views.FriendRelationView.as_view(), name='friend-relation'),
]
