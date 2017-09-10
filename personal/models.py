from django.db import models
from datetime import datetime 

class User(models.Model):
	name =models.CharField(max_length=20)
	surname = models.CharField(max_length = 40)
	login = models.CharField(max_length = 20, primary_key=True) 
	password = models.CharField(max_length = 20)
	wantedinr = models.DecimalField(max_digits=4, decimal_places=2)	
	def __str__(self):
		return self.login
		
		
class UsedDrugs(models.Model):
	
	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	drugid = models.ForeignKey('Drug', on_delete=models.CASCADE,)
	useddose = models.CharField(max_length = 40)
	userlogin = models.CharField(max_length = 20, default="") 
	
	
	def __str__(self):
		return self.useddose
		
class TakenDrugs(models.Model):
	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	drugid = models.ForeignKey('Drug', on_delete=models.CASCADE,)
	takendate = models.DateTimeField(default=datetime.now, blank=True)
	dose = models.DecimalField(max_digits = 4, decimal_places=2)
	
	
	
	def __str__(self):
		return self.takendate

class Drug(models.Model):

	drugid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=40)
	activesub = models.IntegerField()
	units = models.CharField(max_length=10)
	
	def __str__(self):
		return self.name

class INR(models.Model):

	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	INRValue = models.DecimalField(max_digits=4, decimal_places=2)
	testdate = models.DateTimeField(auto_now = True)
	
	def __str__(self):
		return str(self.INRValue)
		
class test(models.Model):

	userlogin =models.ForeignKey('User', on_delete=models.CASCADE,)
	nexttestdate = models.DateField
	place = models.CharField(max_length = 60)
	testtype = models.CharField(max_length = 30)
	hour = models.DateTimeField(auto_now = True)
	
	def __str__(self):
		return self.nexttestdate