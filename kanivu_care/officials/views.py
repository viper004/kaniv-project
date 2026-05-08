from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from functools import wraps

from users.models import UserProfile
from members.models import memberRegistration
from volunteer.models import Campaign, Volunteer
from dashboard.models import FinanceModel, CollectionModel, AnnouncementModel
from web.models import DonationModel
from .models import ReportRequest, FundRequest
from .forms import OfficialRegistrationForm, ReportRequestForm, FundApprovalForm

def official_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role in ["office_staff", "principal", "chairman"]:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Officials only.")
        return redirect('/')
    return _wrapped_view

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, "Access denied. Superusers only.")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@superuser_required
def add_official(request):
    if request.method == "POST":
        form = OfficialRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data['role']
            profile.save()
            messages.success(request, f"Official {user.username} added successfully as {profile.role}.")
            return redirect('officials:add_official')
    else:
        form = OfficialRegistrationForm()
    
    officials = UserProfile.objects.filter(role__in=["office_staff", "principal", "chairman"])
    return render(request, 'officials/add_official.html', {'form': form, 'officials': officials})

@official_required
def dashboard(request):
    # System Monitoring: activities, members, campaigns
    total_members = memberRegistration.objects.count()
    total_volunteers = Volunteer.objects.count()
    active_campaigns = Campaign.objects.filter(end_date__gte=timezone.now().date()).count()
    recent_activities = AnnouncementModel.objects.order_by('-announced_date')[:10]
    
    # Financial Oversight summary
    total_donations = DonationModel.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    # Assuming CollectionModel has 'total' as amount
    total_collections = CollectionModel.objects.aggregate(Sum('total'))['total__sum'] or 0
    
    members = memberRegistration.objects.all().select_related('user', 'user__userprofile')
    volunteers = Volunteer.objects.all().select_related('user', 'user__userprofile')
    
    context = {
        'total_members': total_members,
        'total_volunteers': total_volunteers,
        'active_campaigns': active_campaigns,
        'recent_activities': recent_activities,
        'total_donations': total_donations,
        'total_collections': total_collections,
        'members': members,
        'volunteers': volunteers,
    }
    return render(request, 'officials/dashboard.html', context)

@official_required
def financial_oversight(request):
    donations = DonationModel.objects.all().order_by('-donated_date')
    collections = CollectionModel.objects.all().order_by('-collection_date')
    # Filter by date or type if needed
    return render(request, 'officials/financial_oversight.html', {
        'donations': donations,
        'collections': collections
    })

@official_required
def report_requests(request):
    if request.method == "POST":
        form = ReportRequestForm(request.POST)
        if form.is_valid():
            report_req = form.save(commit=False)
            report_req.requested_by = request.user
            report_req.save()
            messages.success(request, "Report request sent successfully.")
            return redirect('officials:report_requests')
    else:
        form = ReportRequestForm()
    
    my_requests = ReportRequest.objects.filter(requested_by=request.user).order_by('-requested_at')
    return render(request, 'officials/report_requests.html', {'form': form, 'requests': my_requests})

@official_required
def fund_requests(request):
    requests_list = FundRequest.objects.all().order_by('-submitted_at')
    return render(request, 'officials/fund_requests.html', {'requests': requests_list})

@official_required
def approve_fund_request(request, pk):
    fund_req = get_object_or_404(FundRequest, pk=pk)
    if request.method == "POST":
        form = FundApprovalForm(request.POST, instance=fund_req)
        if form.is_valid():
            action = form.save(commit=False)
            action.approved_by = request.user
            action.action_at = timezone.now()
            action.save()
            messages.success(request, f"Fund request {fund_req.title} status updated to {fund_req.status}.")
            return redirect('officials:fund_requests')
    else:
        form = FundApprovalForm(instance=fund_req)
    
@login_required(login_url='users:login')
def view_report_requests(request):
    role = request.user.userprofile.role
    # Also handle 'convenier' typo if it exists in DB vs model choices
    requests = ReportRequest.objects.filter(requested_to_role=role).order_by('-requested_at')
    
    context = {
        'requests': requests,
        'role': role
    }
    return render(request, 'officials/view_report_requests.html', context)

@login_required(login_url='users:login')
def complete_report_request(request, pk):
    req = get_object_or_404(ReportRequest, pk=pk)
    # Check if the user has the role to complete this
    if request.user.userprofile.role == req.requested_to_role:
        if request.method == "POST":
            if 'report_file' in request.FILES:
                req.report_file = request.FILES['report_file']
            req.is_completed = True
            req.save()
            messages.success(request, f"Report '{req.title}' has been submitted and marked as completed.")
    return redirect('officials:view_report_requests')
