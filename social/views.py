from django.db.models import Q
from rest_framework import generics, status, permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from user.models import User
from .models import FriendRequest
from user.serializers import UserSerializer
from .serializers import FriendRequestSerializer, FriendRequestActionSerializer, FriendRequestSendSerializer
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter



@extend_schema(
    parameters=[
        OpenApiParameter(name='q', description='Search keyword', required=False, type=str)
    ]
)
class UserSearchView(generics.ListAPIView):
    """This view returns a list of users that match the search keyword"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        keyword = self.request.query_params.get('q', '')
        if '@' in keyword:
            return User.objects.filter(email__iexact=keyword)
        return User.objects.filter(Q(name__icontains=keyword))
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema(
    parameters=[
        OpenApiParameter(name='to_user_id', description='Friend request to this user', required=True, location=OpenApiParameter.QUERY, type=int)
    ]
)
class FriendRequestView(generics.GenericAPIView):
    """This view sends a friend request to a user"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestSendSerializer

    def post(self, request, *args, **kwargs):
        to_user_id = self.request.query_params.get('to_user_id')
        if not to_user_id:
            return Response({"error": "to_user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        to_user = User.objects.get(id=to_user_id)
        from_user = request.user

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='sent').exists():
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        recent_requests = FriendRequest.objects.filter(from_user=from_user, timestamp__gt=timezone.now() - timezone.timedelta(minutes=1)).count()
        if recent_requests >= 3:
            return Response({"error": "You have reached the limit of friend requests. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
        return Response({"success": "Friend request sent"}, status=status.HTTP_201_CREATED)

class FriendRequestActionView(APIView):
    """This view handles friend request actions"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestActionSerializer

    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        req_status = request.data.get('status')
        if req_status not in ['accepted', 'rejected']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        friend_request.status = req_status
        friend_request.save()
        return Response({"success": f"Friend request {req_status}"}, status=status.HTTP_200_OK)

class FriendsListView(generics.ListAPIView):
    """This view returns a list of users that are friends with the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        accepted_requests = FriendRequest.objects.filter(Q(from_user=user) | Q(to_user=user), status='accepted')
        friend_ids = [req.to_user.id if req.from_user == user else req.from_user.id for req in accepted_requests]
        return User.objects.filter(id__in=friend_ids)

class PendingFriendRequestsView(generics.ListAPIView):
    """This view returns a list of pending friend requests sent to the authenticated user"""
    serializer_class = FriendRequestSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only return pending friend requests sent to the authenticated user"""
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user, status='sent')
