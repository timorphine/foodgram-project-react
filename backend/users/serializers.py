from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from .models import Follow, User


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'


class FollowReadSerializer(CustomUserSerializer):
    """Сериализатор обработки подписок пользователей."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        validators = [
            UniqueTogetherValidator(queryset=Follow.objects.all(),
                                    fields=['following', 'follower'])
        ]

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return UserRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(
            user=request.user, author=obj
        ).exists()


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = (
            'author',
            'user'
        )

    def to_representation(self, instance):
        return FollowReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
