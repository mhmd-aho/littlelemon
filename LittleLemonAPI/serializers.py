from rest_framework import serializers
from .models import MenuItem, Category
import bleach
class MenuItemSerializer(serializers.ModelSerializer):
    catigeryGet = CategorySerializer(read_only=True)
    catigery = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','catigeryGet','catigery']
    def validate_price(self,value):
        if value < 0:
            raise serializers.ValidationError("Price must be positive")
        return value
    def validate_catigery(self,value):
        if value < 0:
            raise serializers.ValidationError("Catigery must be positive")
        return value
    def validate_title(self,value):
        return bleach.clean(value)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title','slug']
    def validate_title(self,value):
        return bleach.clean(value)
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id','user','menuitem','quantity','unit_price','price']
        read_only_fields = ['user','unit_price','price']
    def validate_quantity(self,value):
        if value < 0:
            raise serializers.ValidationError("Quantity must be positive")
        return value
    def validate(self,attrs):
        attrs['unit_price'] = attrs['menuitem'].price
        attrs['price'] = attrs['menuitem'].price * attrs['quantity']
        return attrs
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','user','delivery_crew','status','total','date']
        read_only_fields = ['user','delivery_crew','total','date']