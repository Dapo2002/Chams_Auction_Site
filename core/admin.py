from django.contrib import admin
from .models import Asset, Bid, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name',)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
  list_display = (
      'title',
      'category',
      'starting_price',
      'current_highest_bid',
      'end_time',
      'is_active',
  )
  list_filter = ('category', 'condition', 'is_active')
  search_fields = ('title', 'description')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
  list_display = ('asset', 'user', 'amount', 'timestamp')
  readonly_fields = ('timestamp',)
