# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

User = get_user_model()

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
            }
    
    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'])
        return user
