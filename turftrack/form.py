# turftrack/views.py
from django import forms
from django.shortcuts import render, redirect
from .form import TurfForm, JobPostForm
from .models import Turf, JobPost

# Home page view
def home(request):
    return render(request, 'home.html')

# Turf-related views
def add_turf(request):
    if request.method == 'POST':
        form = TurfForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('turf_list')  # replace with your turf list page
    else:
        form = TurfForm()
    return render(request, 'add_turf.html', {'form': form})

def turf_list(request):
    turfs = Turf.objects.all()
    return render(request, 'turf_list.html', {'turfs': turfs})

# JobPost-related views
def add_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_list')  # replace with your job list page
    else:
        form = JobPostForm()
    return render(request, 'add_job.html', {'form': form})

def job_list(request):
    jobs = JobPost.objects.all()
    return render(request, 'job_list.html', {'jobs': jobs})


class TurfForm(forms.ModelForm):
    class Meta:
        model = Turf
        fields = ['name', 'location', 'price_per_hour', 'description', 'image']  # owner excluded