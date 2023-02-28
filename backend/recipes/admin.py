from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)

admin.site.site_header = 'Управление сайтом Foodgram'
admin.site.site_title = 'Администратор сайта'


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}

    list_display = (
        'pk',
        'name',
        'hex_color',
        'slug'
    )
    list_editable = (
        'name',
        'hex_color',
        'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time'
    )
    list_editable = (
        'author',
        'name',
        'cooking_time',
        'image'
    )
    inlines = (IngredientInline,)
    list_filter = (
        'author',
        'name',
        'tags'
    )

    def in_favourites(self, obj):

        return obj.favorites__recipe.count()


@admin.register(Favorite)
class FavouritesAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'recipe'
    )
    list_filter = (
        'recipe',
    )


@admin.register(ShoppingCart)
class ShoppingListADmin(admin.ModelAdmin):

    list_display = (
        'user',
        'recipe'
    )
    list_filter = (
        'recipe',
    )
