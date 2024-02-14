from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from itertools import groupby
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import random

from .models import User, Mood, JournalEntry, CommunityPost, Comment

class Form(forms.Form):
    title =  forms.CharField(required=False, widget=forms.TextInput(attrs={'name':'title', 'id':'journalTitle', 'placeholder':'Entry title(optional)', 'class': 'form-control me-2 mood-box', 'autocomplete':'off'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'id':'journalEntry', 'name':'journalEntry', 'rows':'4', 'required':True, 'placeholder':'Your entry goes here...', 'class':'form-control me-2 search--box', 'style':'font-style: italic'}))

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email Address'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Confirm Password'}),
        }

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Password'}))


# Create your views here.
@login_required
def index(request):
    """This is the homepage of the app."""
    return render(request, 'zenjottapp/index.html', {
        'form': Form()
    })

@login_required
def journal(request):
    """This is the journal page of the app."""
    entries = JournalEntry.objects.filter(user=request.user).order_by('-update_time')
    return render(request, 'zenjottapp/journal.html', {
        'entries': entries
    })

@login_required
def memes(request):
    """This view displays memes for the user to laugh."""
    return render(request, 'zenjottapp/memes.html')

@login_required
def resources(request):
    """This views displays mental health tips and resources"""
    return render(request, 'zenjottapp/resources.html')

@login_required
def community(request):
    """This is the view that shows the community"""
    posts = CommunityPost.objects.all().order_by('-timestamp')

    grouped_posts = {}
    for date, posts in groupby(posts, key=lambda x: x.date):
        grouped_posts[date] = list(posts)
    return render(request, 'zenjottapp/community.html', {
        'grouped_posts': grouped_posts
    })

@login_required
def create(request):
    """This view allows to create a new community post"""
    return render(request, 'zenjottapp/create.html')

@login_required
def moodtracker(request):
    """This is the Mood Tracker view"""
    moods = Mood.objects.filter(user=request.user).order_by('-timestamp')
    mood_data_serializable = [{'timestamp': entry.timestamp.strftime('%Y-%m-%d'), 'mood': entry.mood} for entry in moods]
    return render(request, 'zenjottapp/moodtracker.html', {
        'moods': json.dumps(mood_data_serializable, cls=DjangoJSONEncoder),
        'whole_moods': moods
    })

@login_required
def entry(request, pk=None):
    """This view shows an individual journal entry"""
    entry = JournalEntry.objects.get(user=request.user, pk=pk)
    return render(request, 'zenjottapp/entry.html', {
        'entry': entry
    })

@login_required
@require_POST
def log_mood(request):
    """This view logs the mood inputted by the user"""
    try:
        mood = request.POST.get('mood')
        note = request.POST.get('note')

        if not mood:
            raise ValueError("Select a mood.")

        new_instance = Mood(user=request.user, mood=mood, note=note)
        new_instance.full_clean()
        new_instance.save()
        return redirect('index')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
@require_POST
def log_entry(request):
    """This view logs the journal entry inputted by the user"""
    try:
        form = Form(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            new_instance = JournalEntry(user=request.user, title=title, content=content, timestamp=timezone.now())
            new_instance.full_clean()
            new_instance.save()
            return redirect('index')
        else:
            return render(request, "zenjottapp/newentry.html", {
                "form": form
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
@require_POST
def make_post(request):
    """This view makes a community post."""
    try:
        user = request.user
        content = request.POST.get('newPost')
        if not content:
            raise ValueError("Write a Post.")

        new_instance = CommunityPost(user=user, content=content, timestamp=timezone.now())
        new_instance.full_clean()
        new_instance.save()
        return redirect('community')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def comment(request, pk):
    post = CommunityPost.objects.get(pk=pk)
    comments = Comment.objects.filter(post=post).order_by('-timestamp')
    if request.method == 'POST':
        user = request.user
        content = request.POST.get('content')
        if not content:
            raise ValueError("Write a comment.")
        
        new_instance = Comment(user=user, post=post, content=content, timestamp=timezone.now())
        new_instance.full_clean()
        new_instance.save()
        return redirect('community')
    return render(request, 'zenjottapp/comment.html', {
        'post': post,
        'comments': comments
    })
    
@login_required
def edit(request, pk):
    """This view allows to edit a journal entry"""
    entry = get_object_or_404(JournalEntry, pk=pk)
    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            entry.title = form.cleaned_data['title']
            entry.content = form.cleaned_data['content']
            entry.save()
            entry.short_content = entry.content[:200]
            entry.save()
            return redirect('entry', pk=pk)
    else:
        form = Form(initial={'title': entry.title, 'content': entry.content})
    return render(request, 'zenjottapp/edit.html', {'form': form, 'entry': entry })

@login_required
def new_entry(request):
    """This view logs the journal entry inputted by the user"""
    if request.method == 'POST':
        try:
            form = Form(request.POST)
            if form.is_valid():
                title = form.cleaned_data["title"]
                content = form.cleaned_data["content"]
                new_instance = JournalEntry(user=request.user, title=title, content=content, timestamp=timezone.now())
                new_instance.full_clean()
                new_instance.save()
                return redirect('journal')
            else:
                return render(request, "zenjottapp/newentry.html", {
                    "form": form
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'zenjottapp/newentry.html', {
        'form': Form()
    })

@login_required
def delete(request, pk=None):
    user=request.user
    entry = get_object_or_404(JournalEntry, pk=pk, user=user)
    entry.delete()
    return redirect('journal')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            form.save()
            login(request, request.user)
            return redirect('index')
        else:
            print("Form is not valid:", form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, 'zenjottapp/register.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        print(request.POST)
        form = UserLoginForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                print("User authenticated:", user)
                login(request, user)
                return redirect('index')
            else:
                message = "Incorrect Username/password"
                return render(request, 'zenjottapp/signin.html', {'form': form, 'message': message})

        else:
            print("Form is not valid:", form.errors)
    else:
        form = UserLoginForm()
    return render(request, 'zenjottapp/signin.html', {'form': form})

def signout(request):
    logout(request)
    return redirect('signin')