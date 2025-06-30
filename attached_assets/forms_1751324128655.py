from django import forms
from dron_map.models import Projects
from django.contrib import admin

class Projects_Form(forms.ModelForm):
	
	class Meta:
		model = Projects
		fields = '__all__'

admin.site.register(Projects)
