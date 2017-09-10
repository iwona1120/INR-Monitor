from django.shortcuts import render, render_to_response
from .models import User, INR, Drug, UsedDrugs, TakenDrugs, test, prediction
from .forms import UserForm, LoginForm, INRForm, BasicinfoForm, takeINRForm, VisitForm, BasicOtherDrugForm, DrugForm
from .function import predict_dose, table_char, next_test,convert_to_table
from django.utils import timezone
from django.shortcuts import redirect
from django.db.models import Q
from datetime import datetime, timedelta
from decimal import *
from django.views.decorators.csrf import csrf_exempt
import math
import hashlib

def basicinfo(request):

	show = 'hidden'
	values =""
	user =""

	if request.session.has_key('userlogin'):

		user = request.session['userlogin']
		userlogin = request.session['userlogin']
		user = User.objects.get(login = user)
		show = "hidden"
		message = ""
		show_alert_already_set = "hidden"
		show_many_values = "hidden"
		show_defaults = "hidden"
		alerts = {''}
		drugs = Drug.objects.all()
		default_values = []
		defaults = ""
		table_days = ["all", "pon", "wt", "sr", "cz", "pt", "sb" "ndz"]
		if UsedDrugs.objects.filter(userlogin = user).count() == 0:
			show_alert_already_set = "visible"
		else:
			show_defaults = "visible"
			drug_INR = UsedDrugs.objects.filter(userlogin = user).filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol"))[0]
			dose = drug_INR.useddose
			dose = dose.split(';')
			if len(dose) !=1:
				show_many_values = "visble"
				default_values = {"all":'0', "pon":dose[0], "wt":dose[1], "sr":dose[2], "cz":dose[3], "pt":dose[4], "sb":dose[5], "ndz":dose[6]}

			else:

				default_values = {"all": dose[0], "pon":dose[0], "wt":dose[0], "sr":dose[0], "cz":dose[0], "pt":dose[0], "sb":dose[0], "ndz":dose[0]}

			alerts = {'show_alert_already_set':show_alert_already_set,'show_many_values':show_many_values, 'show_defaults':show_defaults}
			defaults = {'default_values':default_values, 'part':drug_INR.smallest_part, 'name':drug_INR.drugid, 'goal':user.wantedinr}
		if request.method == "POST":
			BasicInfo = BasicinfoForm(request.POST)

			if BasicInfo.is_valid():
				drugname = request.POST.get('drugname','')
				drugname = Drug.objects.get(drugid = drugname)
				wantedinr = request.POST.get('wantedinr','')
				partofdrug = request.POST.get('partofdrug','')
				#update wantedinr value
				user.wantedinr = wantedinr
				user.save()
				dailydose = []
				#get dailydose
				dailydose.append(request.POST.get('dailydose', ''))
				dailydose.append(request.POST.get('dailydoseman', ''))
				dailydose.append(request.POST.get('dailydosetu', ''))
				dailydose.append(request.POST.get('dailydosewen', ''))
				dailydose.append(request.POST.get('dailydoseth', ''))
				dailydose.append(request.POST.get('dailydosefr', ''))
				dailydose.append(request.POST.get('dailydosesat', ''))
				dailydose.append(request.POST.get('dailydosesan', ''))

				one_or_more = "one";
				dose = ""

				if dailydose[0] == "0":
					for i in range(1,8):
						if dailydose[i] != "0":
							one_or_more = "more"
						break

				if one_or_more == "one":
					dose = dailydose[0]
				else:
					for i in range(1,8):
						dose = dose + dailydose[i] +";"

				if  UsedDrugs.objects.filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol")).filter(userlogin = user).exists():

					used_drugs = UsedDrugs.objects.filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol")).filter(userlogin = user)

					for drug in used_drugs:
						drug.useddose = dose
						drug.drugid = drugname
						drug.smallest_part = partofdrug
						drug.save()
				else:
					used_drugs = UsedDrugs(userlogin = user, drugid = drugname,useddose = dailydose[0],smallest_part = partofdrug )
					used_drugs.save()


				#INR_obj = INR(userlogin = user, INRValue = INRValue, testdate =testdate)
				#INR_obj.save()
				return redirect('/inrtracker/home')
			else:
				show = "visible"
				message = "Spróbuj wypełnić formularz jeszcze raz. Nie wszytkie pola zostały wypełnione"
				return render(request, 'inrtracker/basicinfo.html',{'user':userlogin, 'message':message, 'show':show, 'drugs':drugs,'alerts':alerts , 'defaults':defaults})
		else:
			return render(request, 'inrtracker/basicinfo.html',{'user':user, 'message':message, 'show':show, 'drugs':drugs, 'alerts':alerts, 'defaults':defaults})
	else:
		return render( request,'inrtracker/login-form.html')

@csrf_exempt
def home(request):

	show = 'hidden'
	disabled1 = "visible"
	values =""
	user =""
	show_enter_data = "hidden"
	b ='Costam'

	if request.session.has_key('userlogin'):
		user = request.session['userlogin']
		user = User.objects.get(login = user)
		value= timezone.now()
		value1 = value.today().date()
		value2 = value.today().date() + timedelta(1)

		INR_from_db = INR.objects.filter(userlogin = user)
		last_INR = "No data"
		last_INR_date = "No data"
		dose_for_today = "No data"
		last_INR_id = ""

		perdiction_for_home = {'dose': "No data", 'date': "No data", 'message': "No data" }

		if INR_from_db.exists():
			last_INR_record = INR.objects.filter(userlogin=user).order_by('-testdate')[0]
			last_INR = last_INR_record.INRValue
			last_INR_date = last_INR_record.testdate
			last_INR_id = last_INR_record.id

		#wszytkie leki na INR dla tego użtkownika

		drugs = UsedDrugs.objects.filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol")).filter(userlogin = user)

		if drugs.exists():

			for drug in drugs:
				drugid = drug.drugid
				drugdose = drug.useddose
				drugname = drug.drugid.name
			drug = Drug.objects.get(drugid = str(drugid))
			#wyszukanie domyślnej wartości w zależności od dnia
			drugdose_table = drugdose.split(';')
			number_of_day = value.weekday()
			#sprawdzenie ilości elementów w tablicy
			if len(drugdose_table)> 1:

				dose_for_today = drugdose_table[number_of_day]
				weekly_dose = 0
				for i in range(len(drugdose_table)-1):
					weekly_dose = float(drugdose_table[i]) + weekly_dose

			else:
				dose_for_today = drugdose_table[0]
				weekly_dose = 7* float(dose_for_today)
			weekly_dose = round(weekly_dose,3)


			#sprawdzenie czy zażyte jakieś leki w danym dniu
			taken_drugs_today = TakenDrugs.objects.filter(userlogin = user).filter(takendate__gte = value1).filter(takendate__lte=value2).filter(drugid__name = "Warfarin")
			if len(taken_drugs_today)>0:
				disabled1 = "disabled"

		else:
			show_enter_data = "visible"
			drugname = ""
			# data kolejnej wizyty
		try:
			visits = test.objects.filter(userlogin = user).filter(nexttestdate__gte = value1).order_by('nexttestdate')[0]
			visit_days = visits.nexttestdate - value1
			visit_show_info = "hidden"
			visit_show_details = "visible"
		except:
			visits = "No data"
			visit_days = "No data"
			visit_show_info = "visible"
			visit_show_details = "hidden"

		visit = {'visit_details': visits, 'visit_days' :visit_days, 'visit_show_info':visit_show_info, 'visit_show_details':visit_show_details}
		perdiction_for_home = {'dose': "No data", 'date': "No data", 'message': "No data" }

		#zalecane dawki na podsawie wyników badań
		if prediction.objects.all() and last_INR_id !="":
			prediction_data = prediction.objects.get(INR_id = last_INR_id)

			predicted_table = prediction_data.predicted_dose
			table_prediction = predicted_table.split(";")
			predict_dose_for_today = table_prediction[number_of_day]
			perdiction_for_home = {'dose': predict_dose_for_today, 'date': prediction_data.predicted_data_test, 'message': prediction_data.prediction_message }


		if request.method == "POST":

			if 'INR_drug' in request.POST:
				taken_drug_add = takeINRForm(request.POST)

				if taken_drug_add.is_valid():
					#sprawdzenie czy w danym dniu lek został przyjęty

					dose = request.POST.get('dose','')
					#save taken drug
					TakenDrug_obj = TakenDrugs(userlogin = user, drugid = drug, takendate =value, dose = dose )
					TakenDrug_obj.save()
					disabled1 = "disabled"
			elif 'other_drug' in request.POST:
				fill_drug = request.POST.getlist('other_drugs[]' )
				for drug in fill_drug:
					drugid = int(drug)
					drug_dose = request.POST.get(drug)
					medicine = Drug.objects.get(drugid = drugid)
					taken_drug = TakenDrugs(userlogin = user, drugid = medicine,dose = drug_dose, takendate = value )
					taken_drug.save()
				if request.POST.get('new_drug')=="add":
					drug_dose = request.POST.get('add_new_drug')
					drug_id = request.POST.get('drugname')
					medicine = Drug.objects.get(drugid = drug_id)
					TakenDrug_obj = TakenDrugs(userlogin = user, drugid = medicine, takendate =value, dose = drug_dose )
					TakenDrug_obj.save()


			elif 'drug_to_delete' in request.POST:
				delete_drug = request.POST.getlist('drugs_to_delete[]')
				for drug in delete_drug:
					if TakenDrugs.objects.filter(id=drug).exists():
						del_drug = TakenDrugs.objects.get(id=drug)
						del_drug.delete()
						b= drug


		else:
			taken_drug_add = takeINRForm()

		#sprawdzenie czy brakuje jakiś wpisów z dni
		show_missed_dose = "hidden"

		value= timezone.now()
		today = value.today().date()
		user_creation = user.time_created
		ile_dni = today - user_creation
		ile_dni = ile_dni.days
		all_taken_drug = TakenDrugs.objects.filter(userlogin = user)
		useddurgs_user = UsedDrugs.objects.filter(userlogin = user).count()
		ile_wpisow = int(useddurgs_user)*ile_dni

		not_registered_values = ile_dni - int(len(all_taken_drug))
		if not_registered_values != 0:
			show_missed_dose = 'visible'

		#zbliżająca się wizyta
		show_visit = "hidden"
		#inne przyjmowane leki
		used_drugs = UsedDrugs.objects.filter(userlogin = user).exclude(drugid__name ="Warfarin").exclude(drugid__name = "Acenocumarol")
		table_used_drugs = []

		for drug in used_drugs:
			dose = drug.useddose
			dose_t = dose.split(";")
			if len(dose_t)==1:
				dose = float(dose_t[0])
			else:
				dose = float(dose_t[value.weekday()])

			a = {'name': drug.drugid.name, 'dose':dose, 'drugid':drug.drugid}
			table_used_drugs.append(a)

		if not isinstance(visit_days, str):
			if visit_days.days <= 3:
				show_visit = "visible"

		alerts = {'show_missed_dose':show_missed_dose , 'show_visit':show_visit, 'show_enter_data' : show_enter_data}
		# wszytkie przyjęte leki
		date_today= timezone.now()
		today = date_today.today().date()
		taken_drugs = TakenDrugs.objects.filter(userlogin = user).filter(takendate__gte = today)

		#dostępne leki w bazie lekow
		drugs_in_database = Drug.objects.exclude(name ="Warfarin").exclude(name = "Acenocumarol")



		return render(request, 'inrtracker/home.html',{'user':user, 'used_drugs':table_used_drugs, 'drugname':drugname, 'disabled1':disabled1, 'last_INR': last_INR, 'last_INR_date':last_INR_date , 'value2':value2 , 'dose_for_today': dose_for_today , 'visit' :visit , 'perdiction_for_home' : perdiction_for_home,'alerts':alerts, 'taken_drugs':taken_drugs, 'drugs_in_database':drugs_in_database, 'ile_dni':ile_dni})
	else:
		return render( request,'inrtracker/login-form.html', {show :'show'})

def add_INR(request):

	if request.session.has_key('userlogin'):

		user = request.session['userlogin']
		userlogin = request.session['userlogin']
		user = User.objects.get(login = user)
		show = "hidden"
		message_alert = ""
		show_alert = "hidden"

		# suma faktycznie przyjetych leków
		value= timezone.now()
		value1 = value.today().date()
		value2 = value.today().date() - timedelta(7)

		taken_drug = TakenDrugs.objects.filter(userlogin = user).filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol")).filter(takendate__gte = value2).filter(takendate__lte=value1)
		#taken_drugs_today = TakenDrugs.objects.filter(userlogin = user).filter(takendate__gte = value1).filter(takendate__lte=value2).filter(drugid__name = "Warfarin")
		if len(taken_drug)!= 7:
			show_alert = "visible"

		a = len(taken_drug)

		if request.method == "POST":
			INR_add = INRForm(request.POST)

			if INR_add.is_valid():
				INRValue = request.POST.get('INRValue','')
				testdate = request.POST.get('testdate','')


				INR_obj = INR(userlogin = user, INRValue = INRValue, testdate =testdate)
				INR_obj.save()
				# zapisanie wartości zalecanych w zależności od INR
				testdate = datetime.strptime(testdate, '%Y-%m-%d')

				# suma leków w tygodniu zapisanych
				drug = UsedDrugs.objects.filter(userlogin = user).filter(Q(drugid__name="Warfarin")|Q(drugid__name="Acenocumarol"))[0]
				weeklydose = drug.useddose #dawka na tydzienien
				small_part = drug.smallest_part
				dose_w = 0
				table_dose = weeklydose.split(';')

				if len(table_dose) >1:
					for dose in table_dose:
						dose_w = dose_w + float(dose)
				else:
					dose_w = float(table_dose[0])*7

				w_dose = 0
				# dane z calego tygodnia zapisane
				if len(taken_drug) == 7:
					for medicine in taken_drug:
						w_dose = w_dose + medicine.dose
					dose_w = float(w_dose)

				# proba zmiany dawki na postawie wynikow badan i

				message = ""
				predicted_test_day = testdate
				predicted_table_char = ""
				INRValue = float(INRValue)

				if user.wantedinr == 2.5:
					# algortym do ustalnia INR
					if INRValue <1.5:
						#dodatkowa tabletka:
						message = "Wez dodatkową dawke oraz zwieksz dawkę o 15% w skali tygodnia."
						ratio = 1.15
						predicted_test_day = testdate + timedelta(days = 7)
						predicted_table = predict_dose(ratio, dose_w,small_part)

						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue >= 1.5 and INRValue <=1.8:
						message = "Zwiększ dawkę o 7.5% w skali tygodnia"
						ratio = 1.075
						predicted_test_day = testdate + timedelta(days = 14)
						predicted_table = predict_dose(ratio, dose_w,small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue > 1.8 and INRValue <=2.1:
						message = "Nie ma potrzeby zmiany dawki"

						predicted_table_char = table_char(table_dose,weeklydose)
						predicted_test_day = testdate + timedelta(days = 14)


					elif INRValue > 2.1 and INRValue <= 2.8:
						message = "Nie ma potrzeby zmiany dawki"
						predicted_table_char = table_char(table_dose,weeklydose)
						# kolejne badanie w zaleznosci od wynikow ostatnich INR
						query_INR = INR.objects.filter(userlogin = user).order_by('-testdate')
						day_amount = next_test(query_INR)
						predicted_test_day = testdate + timedelta(days = day_amount)

					elif INRValue > 2.8 and INRValue <=3.2:
						message = "Nie ma potrzeby zmiany dawki"
						predicted_table_char = table_char(table_dose,weeklydose)
						predicted_test_day = testdate + timedelta(days = 14)

					elif INRValue > 3.2 and INRValue <= 3.5:
						message = "Zmniejsz dawkę o 7.5% w skali tygodnia"
						ratio = 0.925
						predicted_test_day = testdate + timedelta(days = 14)
						predicted_table = predict_dose(ratio, dose_w,small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue > 3.5 and INRValue <= 4:
						message = "Zmniejsz dawkę o 15% w skali tygodnia"
						ratio = 0.85
						predicted_test_day = testdate + timedelta(days = 14)
						predicted_table = predict_dose(ratio, dose_w, small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue > 4 and INRValue <= 4.9:
						message = "Wstrzymaj przyjomwanie leku na 0 - 2 dni"
						ratio = 0.80
						predicted_test_day = testdate + timedelta(days = 7)
						predicted_table = predict_dose(ratio, dose_w, small_part)
						predicted_table_char = ";".join(map(str,predicted_table))
					elif INRValue > 4.9:
						message = "Skontaktuj się z lekarzem!"
						predicted_test_day = testdate
						predicted_table_char = "0;0;0;0;0;0;0;"

				elif user.wantedinr == 3:

					if INRValue <1.5:
						#dodatkowa tabletka:
						message = "Wez dodatkową dawkę oraz zwieksz dawkę o 15% w skali tygodnia "
						ratio = 1.15
						predicted_test_day = testdate + timedelta(days = 7)
						predicted_table = predict_dose(ratio, dose_w, small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue >= 1.5 and INRValue <=2.3:
						message = "Zwiększ dawkę o 7.5% w skali tygodnia. "
						ratio = 1.075
						predicted_test_day = testdate + timedelta(days = 14)
						predicted_table = predict_dose(ratio, dose_w, small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue > 2.3 and INRValue <=2.6:
						message = "Nie ma potrzeby zmiany dawki"

						predicted_table_char = table_char(table_dose,weeklydose)
						predicted_test_day = testdate + timedelta(days = 14)

					elif INRValue > 2.6 and INRValue <= 3.3:
						message = "Nie ma potrzeby zmiany dawki"
						predicted_table_char = table_char(table_dose,weeklydose)
						# kolejne badanie w zaleznosci od wynikow ostatnich INR
						query_INR = INR.objects.filter(userlogin = user).order_by['-testdate']
						day_amount = next_test(query_INR)
						predicted_test_day = testdate + timedelta(days = day_amount)

					elif INRValue > 3.3 and INRValue <=3.7:
						message = "Nie ma potrzeby zmiany dawki"
						predicted_table_char = table_char(table_dose,weeklydose)
						predicted_test_day = testdate + timedelta(days = 14)

					elif INRValue > 3.7 and INRValue <= 4:
						message = "Zmniejsz dawkę o 7.5% w skali tygodnia."
						ratio = 0.925
						predicted_test_day = testdate + timedelta(days = 14)
						predicted_table = predict_dose(ratio, dose_w, small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue > 4 and INRValue <= 4.5:
						message = "Wstrzymaj jedna dawke oraz zmniejsz dawkę o 10% w skali tygodnia"
						ratio = 0.9
						predicted_test_day = testdate + timedelta(days = 14)
						predicted_table = predict_dose(ratio, dose_w, small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue > 4.5 and INRValue <= 4.9:
						message = "Wstrzymaj przyjomwanie leku na 0 - 2 dni oraz zmniejsz dawkę o 20%"
						ratio = 0.80
						predicted_test_day = testdate + timedelta(days = 7)
						predicted_table = predict_dose(ratio, dose_w, small_part)
						predicted_table_char = ";".join(map(str,predicted_table))

					elif INRValue > 4.9:
						message = "Contact your doctor!"
						predicted_test_day = testdate
						predicted_table_char = "0;0;0;0;0;0;0"
				#wpisanie do bazy danych:
				prediction_obj = prediction(predicted_dose= predicted_table_char, INR_id = INR_obj, date_prediction = testdate, predicted_data_test = predicted_test_day , prediction_message = message)
				prediction_obj.save()

				#message = "Nie ma takiego leku"


				return redirect('/inrtracker/home')
			else:
				show = "visible"
				message_alert = "Spróbuj wypełnić formularz jeszcze raz. Nie wszytkie pola zostały wypełnione"
				return render(request, 'inrtracker/add_inr.html',{'user':userlogin,'value':value, 'message_alert':message_alert, 'show':show, 'taken_drug':taken_drug, 'show_alert':show_alert})
		else:
			login= INRForm()
			return render(request, 'inrtracker/add_inr.html',{'user':user, 'message_alert':message_alert,'value':value, 'show':show, 'taken_drug':taken_drug, 'show_alert': show_alert})
	else:
		return render( request,'inrtracker/login-form.html', {show :'show'})



def register(request):
	show = "hidden"
	message = ""
	if request.method == 'POST':

		form = UserForm(request.POST)
		message = form.is_valid()
		if form.is_valid():

			name = request.POST.get('name','')
			surname = request.POST.get('surname','')
			login = request.POST.get('login','')
			password = request.POST.get('password','')
			confirm = request.POST.get('confirm','')
			wanted = request.POST.get('wantedinr','')
			md5 = hashlib.md5()
			md5.update(password.encode())
			password = md5.hexdigest()
			con  = hashlib.md5()
			con.update(confirm.encode())
			confirm = con.hexdigest()

			if confirm == password:
				if not User.objects.filter(login = login).exists():
					User_obj = User(name = name, surname = surname, login = login, password = password, wantedinr = wanted)
					User_obj.save()
					message = "Rejstracja przebiegła pomyślnie"
					show = "visible"

				else:
					show = "visible"
					message = "Użytkownik o podanym loginie już istnieje"

			else:
				show = "visible"
				message = "Hasła się nie zgadzają"


	return render(request, 'inrtracker/login.html',{'message':message, 'show':show} )

def login(request):
	user =""
	show = "hidden"
	message = ""
	if request.method == "POST":
		login = LoginForm(request.POST)

		if login.is_valid():
			password = request.POST.get('password','')
			current_user = request.POST.get('login','')

			md5 = hashlib.md5()
			md5.update(password.encode())
			password = md5.hexdigest()

			try:
				user_from_db = User.objects.get(login = current_user)
				if user_from_db.password == password:
					request.session['userlogin'] = current_user
					user = request.session.has_key('userlogin')
					return redirect('/inrtracker/home')
				else:
					show = "visible"
					message = "Hasło jest niepoprawne."
					return render(request, 'inrtracker/login-form.html',{'user':user, 'message': message, 'show':show})

			except:
				login = LoginForm()
				show = "visible"
				message = "Nie ma użytkownika o podanym loginie."
				return render(request, 'inrtracker/login-form.html',{'user':user, 'message':message, 'show':show})
		else:
			show = "visible"
			message = "Spróbuj wypełnić formularz jeszcze raz. Nie wszytkie pola zostały wypełnione"
			return render(request, 'inrtracker/login-form.html',{'user':user, 'message':message, 'show':show})
	else:
		login= LoginForm()
		if request.session.has_key('userlogin'):
			return redirect('/inrtracker/home')
		else:
			return render(request, 'inrtracker/login-form.html',{'user':user, 'message':message, 'show':show})

def formview(request):
	show = 'hidden'

	if request.session.has_key('userlogin'):
		userlogin = request.session.has_key('userlogin')
		user = request.session['userlogin']
		return render(request, 'inrtracker/home.html', {'user':user})
	else:
		return render( request,'inrtracker/login-form.html', {'show' :show})

def logout(request):

	show = 'hidden'

	try:
		del request.session['userlogin']
	except:
		pass
	return render(request, 'inrtracker/logout.html', {show:'show'} )

def next_visit(request):


	if request.session.has_key('userlogin'):
		user = request.session['userlogin']
		user = User.objects.get(login = user)

		show = 'hidden'
		message =""

		if request.method == "POST":
			visit_add =VisitForm(request.POST)
			if visit_add.is_valid():
				visit_date = request.POST.get('nexttestdate','')
				visit_hour = request.POST.get('hour','')
				visit_goal = request.POST.get('testtype','')
				visit_place = request.POST.get('place','')
				visit_obj = test(userlogin = user, nexttestdate = visit_date, place = visit_place, testtype = visit_goal , hour = visit_hour)
				visit_obj.save()
				return redirect('/inrtracker/home')

		else:
			visit_add = VisitForm()
			return render(request, 'inrtracker/next_visit.html',{'user':user, 'message':message, 'show':show})
	else:
		return render( request,'inrtracker/login-form.html', {show :'show'})

def all_visits(request):


	if request.session.has_key('userlogin'):
		#user name
		user = request.session['userlogin']
		user = User.objects.get(login = user)

		visits = test.objects.filter(userlogin = user).order_by('-nexttestdate')

		return render(request, 'inrtracker/all_visits.html', {'visits' :visits})
	else:
		return render( request,'inrtracker/login-form.html')

def detail(request, pk):


	if request.session.has_key('userlogin'):
		#user name
		edit = ""
		user = request.session['userlogin']
		user = User.objects.get(login = user)

		visit = test.objects.get(id = pk)

		value= timezone.now()
		value1 = value.today().date()

		if visit.nexttestdate<value1:
			edit = "disabled"

		if request.method == "POST":
			visit_add =VisitForm(request.POST)
			if visit_add.is_valid():
				visit_date = request.POST.get('nexttestdate','')
				visit_hour = request.POST.get('hour','')
				visit_goal = request.POST.get('testtype','')
				visit_place = request.POST.get('place','')

				visit.nexttestdate = visit_date
				visit.hour = visit_hour
				visit.testtype = visit_goal
				visit.place = visit_place
				visit.save()

				return redirect('/inrtracker/home/all_visits/')

		else:
			visit_add = VisitForm()
			return render(request, 'inrtracker/detail.html', {'visit' : visit, 'edit':edit})

		return render(request, 'inrtracker/detail.html', {'visit' : visit, 'edit':edit})
	else:
		return render( request,'inrtracker/login-form.html')

def missed_dose(request):

	if request.session.has_key('userlogin'):
		#user name
		user = request.session['userlogin']
		user = User.objects.get(login = user)
		value= timezone.now()
		today = value.today().date()
		user_creation = user.time_created
		ile_dni = today - user_creation
		ile_dni = ile_dni.days
		date_cos = ""


		fill_date = []


		if request.method == "POST":
			fill_date = request.POST.getlist('missing_dates[]' )
			for info in fill_date:
				fill_value = request.POST.get(info)
				fill_date = str(info)

				date_cos = info.split(';')[0]
				drug_id = info.split(';')[1]
				drug = Drug.objects.get(drugid = str(drug_id))
				#drug_id = fill_value.split(';')[1]
				taken_obj = TakenDrugs(userlogin = user, dose = fill_value,drugid = drug, takendate = date_cos)
				taken_obj.save()


		#wszytkie leki jakie przyjmuje użytkownik
		medicine_save = UsedDrugs.objects.filter(userlogin = user)
		#wszytkie pobrane leki typu warfaryna od daty powstania uztkownika

		drug_missed =[];
		today = user_creation + timedelta(days = 12)

		tablica_wszytkie_dni = []
		tablica_zapisane_dni = []
		current_day = user_creation
		for i in range(ile_dni):
			current_day = current_day + timedelta(days = 1)
			tablica_wszytkie_dni.append(current_day)

		tab_missing_dates = []

		for medicine in medicine_save:
			all_drugs = TakenDrugs.objects.filter(userlogin = user).filter(drugid__name = medicine.drugid.name)

			for i in range(len(all_drugs)):
				drug = all_drugs[i]
				tablica_zapisane_dni.append(drug.takendate.date())

			tablica_wszytkie_dni1 = set(tablica_wszytkie_dni)
			tablica_zapisane_dni1 = set(tablica_zapisane_dni)

			missing_days = tablica_wszytkie_dni1.difference(tablica_zapisane_dni1)
			missing_days = sorted(missing_days)
			a = {"title": medicine.drugid,
				"table": missing_days}
			tab_missing_dates.append(a)

		return render(request, 'inrtracker/missed_dose.html', {'tab_missing_dates':tab_missing_dates})

	else:
		return render( request,'inrtracker/login-form.html')

def detail_prediction(request):

	if request.session.has_key('userlogin'):
		#user name
		edit = ""
		user = request.session['userlogin']
		user = User.objects.get(login = user)

		last_INR = INR.objects.filter(userlogin = user).order_by('-testdate')[0]
		prediction_data = prediction.objects.get(INR_id = last_INR)
		table_prediction = prediction_data.predicted_dose.split(';')

		suma_prediction = 0
		#suma tabeli: table_prediction tygodniowa
		for dose in table_prediction:
			suma_prediction = suma_prediction + float(dose)

		#suma wartości z ustawień
		used_drug_INR = UsedDrugs.objects.get(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol "), userlogin = user)
		dose_save = used_drug_INR.useddose

		dose_save_table = dose_save.split(';')
		if len(dose_save_table)==1:
			for i in range(6):
				dose_save_table.append(dose_save_table[0])

		#suma_dose = sum(int(i) for i in dose_save_table)
		suma_dose = 0

		for dose in dose_save_table:
			suma_dose = suma_dose + float(dose)

		change = suma_prediction/suma_dose - 1;
		message = ""
		if change>0:
			message = "% więcej"
			change = abs(change)*100
		elif change<0:
			message = "% mniej"
			change = abs(change)*100
		else:
			message = "bez zmian"
			change = ""

		#suma wartości zapisanych z całego tygodnia:
		value= timezone.now()
		value1 = value.today().date()
		value2 = value.today().date() - timedelta(7)

		taken_drug = TakenDrugs.objects.filter(userlogin = user).filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol")).filter(takendate__gte = value2).filter(takendate__lte=value1)
		#taken_drugs_today = TakenDrugs.objects.filter(userlogin = user).filter(takendate__gte = value1).filter(takendate__lte=value2).filter(drugid__name = "Warfarin")
		message_save = ""
		change_save = ""
		sum_saved = 0
		diff = ""
		diff_visible = "hidden"
		if len(taken_drug)!= 7:
			message_save = "brak wszytkich danych"
			change_save =""
			sum_saved = "brak wszytkich danych"

		else:
			for drug in taken_drug:
				sum_saved+= float(drug.dose)
			change_save = suma_prediction/sum_saved -1

			diff = suma_dose - sum_saved
			if diff >0:
				diff_visible = "visible"

			if change_save >0:
				message_save = "% więcej"
				change_save = abs(change_save)*100
			elif change_save<0:
				message_save = "% mniej"
				change_save = abs(change_save)*100
			else:
				message_save = "bez zmian"
				change_save = ""

		tabla_dni_tyg = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']
		medicine ={'suma_prediction' :suma_prediction, 'suma_dose':suma_dose, 'change':change, 'message':message, 'change_save':change_save,'message_save':message_save,'sum_saved':sum_saved,'diff':diff, 'diff_visible':diff_visible}
		prediction_D = {'date': prediction_data.date_prediction, 'message':prediction_data.prediction_message}
		tables = zip(tabla_dni_tyg,table_prediction,dose_save_table)
		if request.method == "POST":
			used_drug_INR.useddose = prediction_data.predicted_dose
			used_drug_INR.save()

		return render(request, 'inrtracker/detail_prediction.html', {'user':user, 'last_INR':last_INR, 'medicine':medicine,'tables':tables, 'dni_tyg':tabla_dni_tyg, 'prediction_D':prediction_D})

	else:
		return render( request,'inrtracker/login-form.html')

def all_taken_drugs(request):



	if request.session.has_key('userlogin'):
		#user name
		user = request.session['userlogin']
		user = User.objects.get(login = user)
		#wszytkie leki jakie przyjmuje użytkownik
		medicine = ""
		drugs = UsedDrugs.objects.filter(userlogin = user)
		if request.method == "POST":

			medicine = request.POST.get('drugname','')
			date_taken_drug = request.POST.get('date','')
			if medicine == "all_drugs":
				taken_drugs = TakenDrugs.objects.filter(userlogin = user).order_by('-takendate')
			else:
				taken_drugs = TakenDrugs.objects.filter(userlogin = user).filter(drugid = medicine).order_by('-takendate')
			if date_taken_drug != "":
				date_max = datetime.strptime(date_taken_drug, "%Y-%m-%d")
				date_max = date_max + timedelta(1)
				taken_drugs = taken_drugs.filter(takendate__gte = date_taken_drug).filter(takendate__lt = date_max)

		else:
			taken_drugs = TakenDrugs.objects.filter(userlogin = user).order_by('-takendate')

		return render(request, 'inrtracker/all_taken_drugs.html', {'taken_drugs' :taken_drugs, 'drugs':drugs, 'medicine':medicine})
	else:
		return render( request,'inrtracker/login-form.html')

def calendar(request):
	if request.session.has_key('userlogin'):
		#user name
		user = request.session['userlogin']
		user = User.objects.get(login = user)


		value= timezone.now()


		value1 = value.date().strftime("%Y-%m-%d")
		value2 = "takie tam"


		all_tests = test.objects.filter(userlogin = user)

		events = []

		for t in all_tests:
			title = t.testtype + " " + str(t.hour.strftime("%H:%M"))
			date = t.nexttestdate.strftime("%Y-%m-%d")
			event = {
			"title":title,
			"start":date}
			events.append(event)
		#przyjete leki

		taken_drugs_all = TakenDrugs.objects.filter(userlogin = user)

		for drug in taken_drugs_all:
			title = drug.drugid.name + " " + str(drug.dose) + " tab"
			date = drug.takendate.date().strftime("%Y-%m-%d")
			event = {
					"title": title,
					"date":date
					}
			events.append(event)

		# dawaka na kolejny miesiac
		used_drugs = UsedDrugs.objects.filter(userlogin = user)
		day = value + timedelta(days = 1)
		for drug in used_drugs:
			drug_dose_str = drug.useddose
			day =value + timedelta(days = 1)
			drug_dose_table = convert_to_table(drug_dose_str.split(';'))

			number_of_day = value.weekday()
			if len(drug_dose_table):
				for i in range(31):
					number_of_day = day.weekday()
					dose = drug_dose_table[number_of_day]
					drug_name = drug.drugid.name
					title = drug_name + " " + str(dose) +" tab"
					date = day.date().strftime("%Y-%m-%d")
					event = {
					"title": title,
					"date":date
					}
					events.append(event)
					day = day + timedelta(days = 1)
			else:
				for i in range(31):

					dose = drug_dose_table[0]
					drug_name = drug.drugid.name
					title = drug_name + " " + str(dose) +" tab"
					date = day.date().strftime("%Y-%m-%d")
					event = {
					"title": title,
					"date":date
					}
					events.append(event)
					day = day + timedelta(days = 1)


		return render(request, 'inrtracker/calendar.html' , {'events':events , 'today':value})
	else:
		return render( request,'inrtracker/login-form.html')
def all_other_medicine(request):

	if request.session.has_key('userlogin'):
		#user name
		user = request.session['userlogin']
		user = User.objects.get(login = user)
		show = "hidden"
		other_drugs = Drug.objects.exclude(name ="Warfarin").exclude(name = "Acenocumarol")
		delete_cos =""
		obj =""

		used_drugs = UsedDrugs.objects.filter(userlogin = user).exclude(drugid__name ="Warfarin").exclude(drugid__name = "Acenocumarol")
		if len(used_drugs)== 0:
			show = "visible"

		if request.method == "POST":
			delete_cos = request.POST.getlist('delete[]')
			for obj in delete_cos:
				if UsedDrugs.objects.filter(id = obj).exists():
					obj_to_delete = UsedDrugs.objects.get(id = obj)
					obj_to_delete.delete()

		return render(request, 'inrtracker/all_other_medicine.html', {'used_drugs':used_drugs, 'show':show ,'delete_cos':delete_cos , 'obj':obj} )

	else:
		return render( request,'inrtracker/login-form.html')

def add_new_medicine(request):
	if request.session.has_key('userlogin'):
		#user name
		user = request.session['userlogin']
		a = "false"

		if request.method == "POST":
			medicine_add =DrugForm(request.POST)
			a = medicine_add.is_valid()
			if medicine_add.is_valid():

				drug_name = request.POST.get('name','')
				drug_activesub = request.POST.get('activesub','')
				drug_unit = request.POST.get('units','')

				medicine_obj = Drug( name = drug_name, activesub = drug_activesub , units = drug_unit)
				medicine_obj.save()
				return redirect('/inrtracker/home')


		else:
			medicine_add = DrugForm()
			return render(request, 'inrtracker/add_new_medicine.html',{'user':user , 'a':a})
		return render(request, 'inrtracker/add_new_medicine.html' , {'user':user , 'a':a} )
	else:
		return render( request,'inrtracker/login-form.html')

def add_medicine(request):

	if request.session.has_key('userlogin'):
		#user name
		show = "hidden"
		user = request.session['userlogin']
		user = User.objects.get(login = user)
		other_drugs = Drug.objects.exclude(name ="Warfarin").exclude(name = "Acenocumarol")
		b= ""

		if request.method == "POST":
			BasicInfo = BasicOtherDrugForm(request.POST)

			if BasicInfo.is_valid():
				b = BasicInfo.is_valid()
				drugname = request.POST.get('drugname','')
				drugname = Drug.objects.get(drugid = drugname)
				#update wantedinr value
				dailydose = []
				#get dailydose
				dailydose.append(request.POST.get('dailydose', ''))
				dailydose.append(request.POST.get('dailydoseman', ''))
				dailydose.append(request.POST.get('dailydosetu', ''))
				dailydose.append(request.POST.get('dailydosewen', ''))
				dailydose.append(request.POST.get('dailydoseth', ''))
				dailydose.append(request.POST.get('dailydosefr', ''))
				dailydose.append(request.POST.get('dailydosesat', ''))
				dailydose.append(request.POST.get('dailydosesan', ''))

				one_or_more = "one";
				dose = ""
				if dailydose[0] == "0":
					for i in range(1,8):
						if dailydose[i] != "0":
							one_or_more = "more"
							break

				if one_or_more == "one":
					dose = dailydose[0]
				else:
					for i in range(1,8):
						dose = dose + dailydose[i] +";"

				if UsedDrugs.objects.filter(drugid = drugname).filter(userlogin = user).exists():
					a = UsedDrugs.objects.filter(drugid = drugname).filter(userlogin = user)[0]

					a.useddose = dose
					a.save()
				else:
					used_drugs = UsedDrugs(userlogin = user, drugid = drugname,useddose = dailydose[0])
					used_drugs.save()

				return redirect('/inrtracker/home/all_other_medicine')
			else:
				show = "visible"


		return render(request, 'inrtracker/add_medicine.html',{ 'other_drugs':other_drugs ,'show':show, 'b':b} )
	else:
		return render( request,'inrtracker/login-form.html')

def details_other(request,pk):

	if request.session.has_key('userlogin'):
		#user name
		edit = ""
		user = request.session['userlogin']
		user = User.objects.get(login = user)

		drug = UsedDrugs.objects.get(id = pk)

		dose = drug.useddose
		dose = dose.split(';')
		if len(dose) !=1:
			show_many_values = "visble"
			default_values = {"all":0, "pon":dose[0], "wt":dose[1], "sr":dose[2], "cz":dose[3], "pt":dose[4], "sb":dose[5], "ndz":dose[6]}

		else:
			for i in range(6):
				default_values = {"all": dose[0], "pon":dose[0], "wt":dose[0], "sr":dose[0], "cz":dose[0], "pt":dose[0], "sb":dose[0], "ndz":dose[0]}

		if request.method == "POST":

			delete = request.POST.get('delete','')

			dailydose = []
			#get dailydose
			dailydose.append(request.POST.get('dailydose', ''))
			dailydose.append(request.POST.get('dailydoseman', ''))
			dailydose.append(request.POST.get('dailydosetu', ''))
			dailydose.append(request.POST.get('dailydosewen', ''))
			dailydose.append(request.POST.get('dailydoseth', ''))
			dailydose.append(request.POST.get('dailydosefr', ''))
			dailydose.append(request.POST.get('dailydosesat', ''))
			dailydose.append(request.POST.get('dailydosesan', ''))

			one_or_more = "one";
			dose = ""
			if dailydose =="0":
				for i in range(1,8):
					if dailydose[i] != "0":
						one_or_more = "more"
						break

			if one_or_more == "one":
				dose = dailydose[0]
			else:
				for i in range(1,8):
					dose = dose + dailydose[i] +";"

			drug.useddose = dose
			drug.save()

			if delete == "delete":
				drug.delete()


			return redirect('/inrtracker/home/all_other_medicine/')

		else:
			visit_add = VisitForm()
			return render(request, 'inrtracker/details_other.html', {'default_values':default_values,'drug':drug})

		return render(request, 'inrtracker/details_other.html', {'default_values' : default_values,'drug':drug})
	else:
		return render( request,'inrtracker/login-form.html')

def statistic(request):

	if request.session.has_key('userlogin'):
		#user name
		edit = ""
		user = request.session['userlogin']
		user = User.objects.get(login = user)

		#drug.takendate.date().strftime("%Y-%m-%d")

		INR_values = INR.objects.filter(userlogin = user)
		b = ['Data', 'Wartość INR']
		data = []
		data.append(b)
		for one_INR in INR_values:
			test_data = one_INR.testdate.date().strftime("%Y-%m-%d")
			a = [str(test_data),float(one_INR.INRValue)]
			data.append(a)

		# dane do wykresu pobrana dawka/zalecana
		# wzięte leki w ostatnim tygodniu

		headers = ['Data','Pobrana dawka', 'Zalacana','Zapisana']
		data_drugs = []

		value= timezone.now()
		value1 = value.today().date()
		last_day = value1 - timedelta(7)
		one_value = []
		#wzięte zapisane leki
		drug_INR = taken_drugs_today = TakenDrugs.objects.filter(userlogin = user).filter(takendate__gte = last_day).filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol"))
		tab_saved_drugs = []
		tab_saved_drugs.append(headers)
		tab_taken_dose =[]
		pred_dose_tab = []
		used_drug_table = []
		sum_saved_drug = 0

		for i in range(7):
			one_value = [last_day.strftime("%Y-%m-%d")]
			if drug_INR.filter(takendate__gte = last_day).filter(takendate__lt=last_day + timedelta(1)).exists():
				drug = drug_INR.filter(takendate__gte= last_day)[0]
				one_value.append(float(drug.dose))
				tab_taken_dose.append(float(drug.dose))

			else:
				one_value.append(float(0))
				tab_taken_dose.append(float(0))

			pred_dose = prediction.objects.filter(INR_id__userlogin = user).filter(date_prediction__lte = last_day).order_by('-date_prediction')[0]
			#str_dose = str(pred_dose.predicted_dose)
			pred_dose_tab = pred_dose.predicted_dose.split(';')
			a = pred_dose_tab[last_day.weekday()]
			one_value.append(float(a))

			#zapisana dawka w ustawieniach
			used_drug = UsedDrugs.objects.filter(userlogin = user).filter(Q(drugid__name = "Warfarin")|Q(drugid__name = "Acenocumarol"))[0]
			used_drug_table = used_drug.useddose.split(';')
			if len(used_drug_table) == 1:
				c = used_drug_table[0]
				sum_saved_drug = 7*float(used_drug_table[0])
			else:
				c = used_drug_table[last_day.weekday()]

			one_value.append(float(c))

			tab_saved_drugs.append(one_value)

			last_day +=timedelta(1)

		#suma dawek w ostatnim tygodniu
		#dawka pobrana
		sum_taken_dose =0
		for i in tab_taken_dose:
			sum_taken_dose += i
		#dawka przewidywana
		sum_pred_dose = 0
		for i in pred_dose_tab:
			sum_pred_dose+= float(i)
		#dawka zapisana

		if sum_saved_drug ==0:
			for i in used_drug_table:
				sum_saved_drug += float(i)

		data_suma =[['Element', 'Suma tygodniowa dawek'],
		 ['Suma pobrana', sum_taken_dose],
		 ['Suma proponowana', sum_pred_dose],
		 ['Suma zapisana', sum_saved_drug]]





		return render(request, 'inrtracker/statistic.html',{ 'data_suma':data_suma, 'data':data, 'tab_saved_drugs':tab_saved_drugs,'last_day':last_day})
	else:
		return render( request,'inrtracker/login-form.html')

