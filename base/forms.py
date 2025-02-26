from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import *



class RoomForm(ModelForm):
	class Meta:
		model = Room
		fields = '__all__'
		exclude = ['participants']
	
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super(RoomForm, self).__init__(*args, **kwargs)	
		if user.is_authenticated:
			# self.fields['topic'] = forms.TextInput(queryset=Topic.objects.all(), required=True)

			self.fields['description'].widget.attrs.update({'placeholder': 'Enter room description...'})
			self.fields['name'].widget.attrs.update({'placeholder': 'Enter room name...'})

			self.fields['host'].initial = user
			self.fields['host'].widget.attrs.update({'placeholder': user.username, 'class': 'form-control',})   

			self.fields['topic'].widget.attrs.update({ 'class': 'form-control',})
			self.fields['name'].widget.attrs.update({ 'class': 'form-control',})
			self.fields['description'].widget.attrs.update({ 'class': 'form-control',})

			if not user.is_staff:
				               
				self.fields['host'].widget = forms.TextInput(attrs={
					'readonly': 'readonly', 
					'placeholder': user.username,
					}) 
				self.fields['host'].disabled = True

			else:  # Admin user
				self.fields['host'].queryset = user.__class__.objects.all()  # Allow admins to choose any user




class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

