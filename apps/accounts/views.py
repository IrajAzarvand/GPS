from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, Address
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm


class RegisterView(CreateView):
    """
    User registration view
    """
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save()
        # Create UserProfile
        UserProfile.objects.create(user=user)
        messages.success(self.request, _('Account created successfully. Please log in.'))
        return super().form_valid(form)


class LoginView(TemplateView):
    """
    User login view
    """
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserLoginForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _('Welcome back!'))
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, _('Invalid username or password.'))
        else:
            messages.error(request, _('Please correct the errors below.'))

        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


def logout_view(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('home')


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    User dashboard view
    """
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Recent orders
        context['recent_orders'] = user.orders.all()[:5]

        # Active subscriptions
        context['active_subscriptions'] = user.subscriptions.filter(status='active')[:3]

        # GPS devices
        context['gps_devices'] = user.gps_devices.filter(status='active')[:5]

        # Statistics
        context['total_orders'] = user.orders.count()
        context['total_devices'] = user.gps_devices.count()
        context['active_devices'] = user.gps_devices.filter(status='active').count()
        context['pending_orders'] = user.orders.filter(status='pending').count()

        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    User profile management view
    """
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully.'))
        return super().form_valid(form)


class AddressListView(LoginRequiredMixin, ListView):
    """
    User addresses list view
    """
    model = Address
    template_name = 'accounts/addresses.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return self.request.user.addresses.all()


class AddressCreateView(LoginRequiredMixin, CreateView):
    """
    Create new address view
    """
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:addresses')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Address added successfully.'))
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update address view
    """
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:addresses')

    def get_queryset(self):
        return self.request.user.addresses.all()

    def form_valid(self, form):
        messages.success(self.request, _('Address updated successfully.'))
        return super().form_valid(form)


def address_delete_view(request, pk):
    """
    Delete address view
    """
    address = get_object_or_404(request.user.addresses, pk=pk)
    if request.method == 'POST':
        address.delete()
        messages.success(request, _('Address deleted successfully.'))
        return redirect('accounts:addresses')
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


# Password reset views
class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view
    """
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Password reset done view
    """
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Password reset confirm view
    """
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Password reset complete view
    """
    template_name = 'accounts/password_reset_complete.html'
