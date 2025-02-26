from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.models import User
from .utils import check_toxicity



def loginPage(request):
    page = 'login'
    next_url = request.GET.get('next', 'login')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = username
		#Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect(next_url)
            #return render(request, "base/login_register.html", {"username":username})
        else:
            messages.error(request, "Error logging in. Please try again...")
            return redirect('login')

    else: 
        return render(request, "base/login_register.html", {'page': page})
    

@login_required(login_url='login')
def logoutUser(request):
	logout(request)
	messages.success(request, "You have been logged out...")
	return redirect('login')


def registerPage(request):
    page = 'register'
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            #Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered!")

            return redirect('login')
        #return redirect('/login/?username={}'.format(username))
        messages.error(request, "An error occurred during registration!")
    else:
        
        form = SignUpForm()
        return render(request, 'base/login_register.html', {'form':form, 'page': page})

    return render(request, 'base/login_register.html', {'page': page})


# @login_required(login_url='login')
def home(request):
    page = 'rooms'
    q = request.GET.get('q')
    rooms = Room.objects.all()
    topics = Topic.objects.all()

    room_count = rooms.count()
    room_messages = Message.objects.all()
    
    if q:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q,) |
            Q(host__username__icontains=q,) |
            Q(name__icontains=q,) |
            Q(description__icontains=q,)
            )
        room_count = rooms.count()

        room_messages = Message.objects.filter(
            Q(user__username__icontains=q,) |
            Q(room__topic__name__icontains=q,) |
            Q(room__name__icontains=q,) | 
            Q(body__icontains=q,) | 
            Q(room__description__icontains=q,)             
            )
        room_messages_count = room_messages.count()
    
    

    context = {
        'rooms': rooms, 
        'topics': topics, 
        'room_count': room_count, 
        'page': page,
        'room_messages': room_messages
        }
    return render(request, 'base/home.html', context)


# @login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        body = request.POST.get('body')

        analyze_request = {
            'comment': { 'text': body },
            'requestedAttributes': {'TOXICITY': {}}
            }
        
        toxicity_score = check_toxicity(analyze_request)
        
        if toxicity_score > 0.5: 
            error_message = "This comment contains inappropriate content and cannot be posted."
            messages.error(request, error_message)
            return redirect('room', pk=pk)

        if body.strip() == '':
            messages.error(request, "Please Provide a Valid Comment")
            return redirect('room', pk=pk)
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = body,
        )
        room.participants.add(request.user)
        return redirect('room', pk=pk)
    context = {
        'room': room, 
        'room_messages': room_messages, 
        'participants': participants
        }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    room = message.room
    room_messages = room.message_set.all()
    participants = room.participants.all()
    
    next_url = request.GET.get('next', 'room')

    if request.user.is_authenticated:
        
        if request.user == message.user or request.user.is_staff:
            if request.method == 'POST':
                message.delete()
                # return redirect(next_url)

                context = {
                    'room': room, 
                    'room_messages': room_messages, 
                    'participants': participants
                    }
                return render(request, 'base/room.html', context)
            else:
                return render(request, 'base/delete.html', {'obj':message})
    
        else:
            return HttpResponse("Permission Denied")
        
    else:
        return redirect('login')


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm(user=request.user)
    topics = Topic.objects.all()
    page = 'create-room'
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = RoomForm(request.POST, user=request.user)
            topic_id = request.POST.get('topic')
            topic = Topic.objects.get(id=topic_id)
                    
            if form.is_valid():
                host = form.cleaned_data['host']
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']

                
                if not request.user.is_staff:
                    host = request.user  # Ensure the current user is set as the host
               
                room = Room.objects.create(host=host, topic=topic, name=name, description=description)
                room.save()
                return redirect('home')

            messages.error(request, "An Error Occurred during Room Creation")
            return redirect('create-room')

        context={"form": form, "topics": topics, 'page': page}
        return render(request, 'base/room_form.html', context)
    else:
        return redirect('login')


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room, user=request.user)
    topics = Topic.objects.all()
    page = 'update-room'
    if request.user.is_authenticated:

        if request.user == room.host or request.user.is_staff:
            if request.method == 'POST':
                form = RoomForm(request.POST, instance=room, user=request.user)
                topic = request.POST.get('topic')
                print(request.POST)

                if form.is_valid():
                    host = form.cleaned_data['host']
                    name = form.cleaned_data['name']
                    description = form.cleaned_data['description']

                    room.topic.name = Topic.objects.get(id=int(topic))
                    room.name = name
                    room.description = description

                    if not request.user.is_staff:
                        room.host = request.user  # Ensure the current user is set as the host
                        room.save()
                    else:
                        room.host = host
                    room.save()
                    return redirect('home')
               
                messages.error(request, "An Error Occurred during Room Update")
                context = {'form': form, 'topics': topics}
                return render(request, 'base/room_form.html', context)
            else:
                form = RoomForm(instance=room, user=request.user)
                return render(request, 'base/room_form.html', {'form': form, 'topics': topics, "page": page})
        else:
            return HttpResponse('Permission Denied')
            
    else:
        return redirect('login')
    

@login_required(login_url='login')
def deleteRoom(request, pk):
    
    room = Room.objects.get(id=pk)
    
    if request.user.is_authenticated:    
        if request.user == room.host or request.user.is_staff:
            if request.method == 'POST':
                room.delete()
                return redirect('home')
            else:
                return render(request, 'base/delete.html', {'obj':room})
    
        else:
            return HttpResponse("Permission Denied")
        
    else:
        return redirect('login')
    

def userProfile(request, pk):
    page = 'profile'

    q = request.GET.get('q')

    user = User.objects.get(id=pk)
    topics = Topic.objects.all()

    rooms = user.room_set.all()
    room_count = rooms.count()

    room_messages = user.message_set.all()
    
    if q:
        rooms = rooms.filter(
            Q(topic__name__icontains=q,) |
            Q(host__username__icontains=q,) |
            Q(name__icontains=q,) |
            Q(description__icontains=q,)
            )
        room_count = rooms.count()

        room_messages = room_messages.filter(
            Q(user__username__icontains=q,) |
            Q(room__topic__name__icontains=q,) |
            Q(room__name__icontains=q,) | 
            Q(body__icontains=q,) | 
            Q(room__description__icontains=q,)             
            )
        room_messages_count = room_messages.count()


    topics = Topic.objects.all()

    if user == request.user:
        return redirect('login')
    

    context = {
        'user': user,
        'rooms': rooms,
        'room_count': room_count,
        'topics': topics,
        'room_messages': room_messages, 
        'page': page,
        'pk': pk,
        }
    return render(request, 'base/user_profile.html', context)