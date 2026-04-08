from django.shortcuts import render
from rest_framework.response import Response
from .models import MenuItem
from .serializers import MenuItemSerializer,CategorySerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User,Group
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view,permission_classes
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title']
    ordering_fields = ['price','title']
    def post(self, request,*args,**kwargs):
        if not request.user.is_staff:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().post(request,*args,**kwargs)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    def update(self,request,*args,**kwargs):
        is_manager = request.user.groups.filter(name='managers').exists()
        if not request.user.is_staff and not is_manager:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().update(request,*args,**kwargs)
    def destroy(self,request,*args,**kwargs):
        is_manager = request.user.groups.filter(name='managers').exists()
        if not request.user.is_staff and not is_manager:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().destroy(request,*args,**kwargs)
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    def post(self, request,*args,**kwargs):
        if not request.user.is_staff:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().post(request,*args,**kwargs)
class CartView(generics.ListCreateAPIView,generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Cart.objects.filter(user = self.request.user)
    def create(self, request, *args, **kwargs):
        serializer.save(user = request.user)
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
from datetime import date

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff: 
            return Order.objects.all()
        elif user.groups.filter(name='Managers').exists(): 
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists(): 
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user) 

    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)
        if cart_items.count() == 0:
            return Response({"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        total = sum([item.price for item in cart_items])
        order = Order.objects.create(
            user=request.user, 
            status=False, 
            total=total, 
            date=date.today()
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
        cart_items.delete()
        return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        if user.groups.filter(name='Delivery Crew').exists():
            if list(request.data.keys()) == ['status']:
                return super().patch(request, *args, **kwargs)
            return Response({"message": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def manager(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name = 'managers')
        managers.user_set.add(user)
        return Response({'message': 'User added to Manager group'}, status=status.HTTP_200_OK)
    return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
