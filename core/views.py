from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Asset, Bid
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-log them in after registering
            return redirect('auction_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def auction_list(request):
  now = timezone.now()
  active_assets = Asset.objects.filter(
      is_active=True, end_time__gt=now
  ).order_by('end_time')
  closed_assets = Asset.objects.filter(is_active=True, end_time__lte=now)

  return render(
      request,
      'core/auction_list.html',
      {'active_assets': active_assets, 'closed_assets': closed_assets},
  )


@login_required
def auction_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    bids = asset.bids.all().order_by('-amount')

    if request.method == 'POST':
        if asset.is_closed:
            messages.error(request, 'This auction has ended.')
            return redirect('auction_detail', pk=pk)

       # try:
            # Convert input to float for numerical comparison
        amount = float(request.POST.get('amount', 0))

            # Dynamic validation based on Open vs Blind auction switch
        if asset.show_bids:
            min_required = float(asset.current_highest_bid) if asset.current_highest_bid else float(asset.starting_price)
            if amount <= min_required:
                messages.error(
                    request,
                    f'Your bid must be higher than the current highest bid (₦{min_required:,.2f}).'
                )
                return redirect('auction_detail', pk=pk)
        else:
                # Blind auction mode: must be at least the starting price
            min_required = float(asset.starting_price)
            if amount < min_required:
                messages.error(
                    request,
                    f'Your bid must be at least the starting price (₦{min_required:,.2f}).'
                )
                return redirect('auction_detail', pk=pk)

            # Save the valid bid
        Bid.objects.create(asset=asset, user=request.user, amount=amount)
        messages.success(request, 'Bid placed successfully!')
        return redirect('auction_detail', pk=pk)

        #except ValueError:
        messages.error(request, 'Please enter a valid numeric bid amount.')
        #except Exception:
        messages.error(request, 'Invalid bid submission. Please try again.')

    return render(
        request,
        'core/auction_detail.html',
        {'asset': asset, 'bids': bids},
    )