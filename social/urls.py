from django.urls import path
from .views import UserSearchView, FriendRequestView, FriendRequestActionView, FriendsListView, PendingFriendRequestsView

urlpatterns = [
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/', FriendRequestView.as_view(), name='friend-request'),
    path('friend-request/<int:request_id>/action/', FriendRequestActionView.as_view(), name='friend-request-action'),
    path('friends/', FriendsListView.as_view(), name='friends-list'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-requests'),
]
