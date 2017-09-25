import math


def predict_dose(ratio, weekly_dose, opcja):
    table_new_dose = []

    new_weekly_dose = weekly_dose * ratio
    if opcja == 0.25:
        day_dose = round(new_weekly_dose / 7 * 4) / 4
    elif opcja == 0.5:
        day_dose = round(new_weekly_dose / 7 * 2) / 2

    diff = new_weekly_dose - day_dose * 7
    for i in range(7):
        table_new_dose.append(day_dose)

    suma = sum(table_new_dose)

    diff = suma/weekly_dose

    i = 0
    while diff>(ratio + 0.025):
         table_new_dose[int(math.fmod(i * 2, 7))] -= opcja
         i+=1
         diff = sum(table_new_dose)/weekly_dose
    while diff < (ratio - 0.025):
        table_new_dose[int(math.fmod(i * 2, 7))] += opcja
        i += 1
        diff = sum(table_new_dose) / weekly_dose

    return table_new_dose

def next_test(query_INR):

	days = 7;

	if len(query_INR) <=4:
		for i in range(len(query_INR)):
			if query_INR[i].INRValue >=2:
				days =  7*(i+1)
			else:
				break
	else:
		for i in range(4):
			if query_INR[i].INRValue >= 2:
				days = 7 * (i + 1)
			else:
				break
	return days

def table_char(table_dose, weekly_dose):
    new_value = []
    if len(table_dose) == 1:
        for i in range(7):
            new_value.append(weekly_dose)
        predicted_table_char=";".join(new_value)

    else:
        predicted_table_char = weekly_dose

    return predicted_table_char

def convert_to_table(a):
    if len(a) == 1:
        for i in range(6):
            a.append(a[0])
    return a