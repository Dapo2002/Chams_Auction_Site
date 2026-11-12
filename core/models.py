from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Category(models.Model):
  name = models.CharField(max_length=100)

  class Meta:
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.name


class Asset(models.Model):
  CONDITION_CHOICES = [
      ('EXCELLENT', 'Like New'),
      ('GOOD', 'Good / Minor Wear'),
      ('FAIR', 'Fair / Functional'),
      ('PARTS', 'For Spare Parts'),
  ]

  title = models.CharField(max_length=255)
  category = models.ForeignKey(
      Category, on_delete=models.SET_NULL, null=True, blank=True
  )
  description = models.TextField()
  condition = models.CharField(
      max_length=20, choices=CONDITION_CHOICES, default='GOOD'
  )
  image = models.ImageField(upload_to='asset_images/', null=True, blank=True)

  starting_price = models.DecimalField(
      max_digits=10, decimal_places=2, default=Decimal('0.00')
  )
  min_increment = models.DecimalField(
      max_digits=10, decimal_places=2, default=Decimal('500.00')
  )

  start_time = models.DateTimeField(default=timezone.now)
  end_time = models.DateTimeField()

  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title

  @property
  def current_highest_bid(self):
    highest = self.bids.order_by('-amount').first()
    return highest.amount if highest else self.starting_price

  @property
  def winning_bidder(self):
    highest = self.bids.order_by('-amount').first()
    return highest.user if highest else None

  @property
  def is_closed(self):
    return timezone.now() >= self.end_time or not self.is_active


class Bid(models.Model):
  asset = models.ForeignKey(
      Asset, on_delete=models.CASCADE, related_name='bids'
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  timestamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-amount']

  def clean(self):
    if self.asset.is_closed:
      raise ValidationError('This auction is already closed.')

    current_high = self.asset.current_highest_bid
    min_required = current_high + self.asset.min_increment

    if self.amount < min_required:
      raise ValidationError(
          f'Bid must be at least ₦{min_required} (Current: ₦{current_high} +'
          f' Min Inc: ₦{self.asset.min_increment})'
      )

  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)

  def __str__(self):
    return f'{self.user.username} - ₦{self.amount} on {self.asset.title}'