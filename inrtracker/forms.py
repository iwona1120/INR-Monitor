from django import forms
from .models import User, INR, test, Drug


class UserForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ('name', 'surname', 'login', 'password', 'wantedinr',)
		
class LoginForm(forms.Form):
		login = forms.CharField(max_length = 100)
		password = forms.CharField(widget = forms.PasswordInput())
		
		def clean_message(self):
			login = self.cleaned_data.get("login")
			dbuser = Dreamreal.objects.filter(name = login)
      
			if not dbuser:
				raise forms.ValidationError("User does not exist in our db!")
			return login
			

class INRForm(forms.ModelForm):

	class Meta:
		model = INR
		fields = ('INRValue','testdate',)

class BasicinfoForm(forms.Form):

	drugname = forms.CharField(max_length = 50)
	wantedinr  = forms.DecimalField(max_digits = 4, decimal_places=2)
	partofdrug = forms.DecimalField(max_digits = 4, decimal_places=2 ,required = False)
	dailydose = forms.DecimalField(max_digits = 4, decimal_places=2 ,required = False)
	dailydoseman = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosetu = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosewen = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydoseth = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosefr = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosesat = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosesan = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	
	
class takeINRForm(forms.Form):

	dose = forms.DecimalField(max_digits = 4, decimal_places=2)
	
	
class VisitForm(forms.Form):
	
	class Meta:
	
		model = test
		fields = ('nexttestdate', 'place', 'testtype', 'hour',)
		
class BasicOtherDrugForm(forms.Form):

	drugname = forms.CharField(max_length = 50)
	dailydose = forms.DecimalField(max_digits = 4, decimal_places=2 ,required = False)
	dailydoseman = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosetu = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosewen = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydoseth = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosefr = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosesat = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)
	dailydosesan = forms.DecimalField(max_digits = 4, decimal_places=2, required = False)

class DrugForm(forms.ModelForm):

	class Meta:
		model = Drug
		fields = ('name','activesub','units')