from django.db import models
from datetime import datetime, date
from django.utils import timezone


class User(models.Model):
	
	name =models.CharField(max_length=20)
	surname = models.CharField(max_length = 40)
	login = models.CharField(max_length = 20, primary_key=True) 
	password = models.CharField(max_length = 20)
	wantedinr = models.DecimalField(max_digits=4, decimal_places=2)	
	time_created = models.DateField(default= date.today)
	
	def __str__(self):
		return self.login
		
		
class UsedDrugs(models.Model):
	
	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	drugid = models.ForeignKey('Drug', on_delete=models.CASCADE,)
	useddose = models.CharField(max_length = 40)
	smallest_part = models.DecimalField(max_digits=4, decimal_places=2, default = 0.5)
	
	def __str__(self):
		return self.useddose
		
class TakenDrugs(models.Model):
	
	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	drugid = models.ForeignKey('Drug', on_delete=models.CASCADE,)
	takendate = models.DateTimeField(default=datetime.now)
	dose = models.DecimalField(max_digits = 4, decimal_places=2)
	
	def __str__(self):
		return str(self.takendate)

class Drug(models.Model):

	drugid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=40)
	activesub = models.IntegerField()
	units = models.CharField(max_length=10)
	
	def __str__(self):
		return str(self.drugid)

class INR(models.Model):

	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	INRValue = models.DecimalField(max_digits=4, decimal_places=2)
	testdate = models.DateTimeField()
	
	def __str__(self):
		return str(self.INRValue)
		
class test(models.Model):

	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	nexttestdate = models.DateField(default= date.today)
	place = models.CharField(max_length = 60)
	testtype = models.CharField(max_length = 200)
	hour = models.TimeField(default = timezone.now())
	
	def __str__(self):
		return str(self.nexttestdate)

class Users(models.Model):
	
	name =models.CharField(max_length=20)
	surname = models.CharField(max_length = 40)
	login = models.CharField(max_length = 20, primary_key=True) 
	password = models.CharField(max_length = 20)
	wantedinr = models.DecimalField(max_digits=4, decimal_places=2)	
	def __str__(self):
		return self.login
		
class person(models.Model):
	name =models.CharField(max_length=20)
	surname = models.CharField(max_length = 40)
	login = models.CharField(max_length = 20, primary_key=True) 
	password = models.CharField(max_length = 20)
	wantedinr = models.DecimalField(max_digits=4, decimal_places=2)	
	def __str__(self):
		return self.login
		
class prediction(models.Model):

	predicted_dose = models.CharField(max_length = 40)
	INR_id = models.ForeignKey('INR', on_delete=models.CASCADE,)
	date_prediction = models.DateTimeField()
	predicted_data_test = models.DateTimeField(default = date.today)
	prediction_message = models.CharField(max_length = 100, default ="")
	
	def __str__(self):
		return self.predicted_dose
