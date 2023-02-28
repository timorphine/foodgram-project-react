from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User
from users.serializers import CustomUserSerializer, FollowSerializer

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import UserIsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = [UserIsAuthorOrReadOnly, ]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

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

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated]
            )
    def favorite(self, request, pk):
        return self.post_for_actions(
            request=request, pk=pk, serializers=FavoriteSerializer
        )

    @favorite.mapping.delete
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

    @shopping_cart.mapping.delete
    def delete_shopping_cat(self, request, pk):
        return self.delete_for_actions(
            request=request, pk=pk, model=ShoppingCart
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shop_list = {}
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount'
        )
        for value in ingredients:
            name = value[0]
            if name not in shop_list:
                shop_list[name] = {
                    'measurement_unit': value[1],
                    'amount': value[2]
                }
            else:
                shop_list[name]['amount'] += value[2]
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; ', 'filename="shopping_list.pdf"'
        )
        pdfmetrics.registerFont(
            TTFont('BebasNeue_Book', 'data/BebasNeue_Book.ttf', 'UTF-8')
        )
        pdfmetrics.registerFont(
            TTFont('BebasNeue_Bold', 'data/BebasNeue_Bold.ttf', 'UTF-8')
        )
        page = canvas.Canvas(response)
        page.setFont('BebasNeue_Bold', size=30)
        page.drawString(200, 800, 'PROJECT FOODGRAM')
        page.setFont('BebasNeue_Book', size=22)
        page.drawString(230, 760, 'Список покупок')
        page.setFont('BebasNeue_Book', size=16)
        height = 700
        for x, (name, data) in enumerate(shop_list.items(), 1):
            page.drawString(
                70, height, (f'{x}. {name}  –  {data["amount"]} '
                             f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    filter_backends = [IngredientFilter]
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тега."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class CustomUserViewSet(UserViewSet):
    """Вьюсет юзера."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]


class FollowViewSet(APIView):
    """Вьюсет подписок."""

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        author = get_object_or_404(User, id=user_id)
        if author == request.user:
            return Response(
                'Нельзя подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
            user=request.user,
            author_id=user_id
        ).exists():
            return Response(
                'Вы уже подписаны на этого автора',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        get_object_or_404(User, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на автора'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowReadView(ListAPIView):
    """Вью для отображения подписок."""

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
