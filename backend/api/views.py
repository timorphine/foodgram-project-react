from django.shortcuts import get_object_or_404
from rest_framework import  viewsets, status
from rest_framework.permissions import (
    IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from recipes.models import Recipe, Ingredient, Tag, Favorite, ShoppingCart
from users.models import User
from .serializers import (
    RecipeSerializer, IngredientSerializer, TagSerializer,
    RecipeReadSerializer, FavoriteSerializer, ShoppingCartSerializer
)
from users.serializers import CustomUserSerializer
from .permissions import UserIsAuthorOrReadOnly, IsAdmin


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [UserIsAuthorOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    @staticmethod
    def post_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @staticmethod 
    def delete_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        obj = get_object_or_404(model, user=user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer
        )

    @action(
            detail=True, methods=['DELETE'], 
            permission_classes=[UserIsAuthorOrReadOnly]
    )
    def delete_favorite(self, request, pk):
        return self.delete_for_actions(
            request=request, pk=pk, model=Favorite
        )

    @action(
        detail=True, methods=['POST'], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.post_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer
        )
    
    @action(
        detail=True, methods=['DELETE']
    )
    def delete_shopping_cat(self, request, pk):
        return self.delete_for_actions(
            request=request, pk=pk, model=ShoppingCart
        )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
