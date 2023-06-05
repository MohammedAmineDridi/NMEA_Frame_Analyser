from tkinter import *
import os
import serial
import sys
import re

# ------------------------------------------------------- NMEA 1083/2000 part -----------------------------------------------------


# ********************************************************** NMEA 1083 ************************************************************

# WIND 

def Infos_Nmea_1083_WIND(nmea_1083_frame):

	if (not nmea_1083_frame.isnumeric() ) :

		#verifier trame wind format NMEA '0183' with (regex) .

		data_frame_wind = re.search("^[$]WIMWV,[0123456789.]*,T,[0123456789.]*,M,A[*][0123456789ABCDEF][0123456789ABCDEF]$", nmea_1083_frame)

		if data_frame_wind: #format correct
			
			
			msg_nmea_1083 = "yes , nmea 1083 wind frame is correct"
			print("nmea 1083 format wind correcte")
			#analyse frame nmea 1083 (extract informations from frame) .
			  	
			position_virgule_1 = nmea_1083_frame.find(',',0)
			position_virgule_2 = nmea_1083_frame.find(',',position_virgule_1+1)
			position_virgule_3 = nmea_1083_frame.find(',',position_virgule_2+1)
			position_virgule_4 = nmea_1083_frame.find(',',position_virgule_3+1)

			#extract informations WIND (direction+vitesse)
			direction_vent = nmea_1083_frame[position_virgule_1+1:position_virgule_2]
			vitesse_vent = nmea_1083_frame[position_virgule_3+1:position_virgule_4]
			print("WIND : direction = "+str(direction_vent)+" °"+" / vitesse = "+str(vitesse_vent)+" m/s") 
			msg_nmea_1083_wind_status = " NMEA 1083 WIND : direction = "+str(direction_vent)+" °"+" / vitesse = "+str(vitesse_vent)+" m/s"
			return direction_vent,vitesse_vent
			#last step , verifier le calcul de crc (pas besoin de crc now)

		else:

			msg_nmea_1083_wind_status = "nmea 1083 format wind not correct"
		  	#msg_nmea_1083 = "no , nmea 1083 wind frame not correct"
		  	#print("nmea 1083 format wind not correct")
			return "",""
	else :
		return "",""
 
#METEO 


def Infos_Nmea_1083_METEO(nmea_1083_frame):

	if (not nmea_1083_frame.isnumeric() ) :

		#nmea_1083_frame = int(nmea_1083_frame,2)

		#verifier trame wind format NMEA '0183' with (regex) .

		data_frame_meteo = re.search("^$IIMDA,0,I,[0123456789.]*,B,[0123456789.]*,C,[0123456789.]*[*][0123456789ABCDEF][0123456789ABCDEF]$", nmea_1083_frame)

		if data_frame_meteo: #format correct
			
			msg_nmea_1083 = "nmea 1083 format meteo correcte"
			print("nmea 1083 format meteo correcte")
			#analyse frame nmea 1083 (extract informations from frame) .
			  	
			position_virgule_1 = nmea_1083_frame.find(',',0)
			position_virgule_2 = nmea_1083_frame.find(',',position_virgule_1+1)
			position_virgule_3 = nmea_1083_frame.find(',',position_virgule_2+1)
			position_virgule_4 = nmea_1083_frame.find(',',position_virgule_3+1)
			position_virgule_5 = nmea_1083_frame.find(',',position_virgule_4+1)
			position_virgule_6 = nmea_1083_frame.find(',',position_virgule_5+1)
			position_virgule_7 = nmea_1083_frame.find(',',position_virgule_6+1)

			#extract informations WIND (direction+vitesse)
			pression = nmea_1083_frame[position_virgule_3+1:position_virgule_4]
			temperature = nmea_1083_frame[position_virgule_5+1:position_virgule_6]
			humidity = nmea_1083_frame[position_virgule_7+1:nmea_1083_frame.find("*")]
			print("METEO : pression = "+str( (float(pression)*1000) )+" Pa"+" / temperature = "+str(temperature) +" °C"+ " / humidity = " + humidity+" %") 
			msg_nmea_1083_meteo_status = "NMEA 1083 METEO : pression = "+str((float(pression)*1000))+" Pa"+" / temperature = "+str(temperature) +" °C"+ " / humidity = " + humidity+" %"
			#last step , verifier le calcul de crc (pas besoin de crc now)
			return str((float(pression)*1000)),temperature,humidity

		else:
			msg_nmea_1083_meteo_status = "nmea 1083 format wind not correct"
	  		#msg_nmea_1083 = "nmea 1083 format wind not correct"
	  		#print("nmea 1083 format wind not correct")
			return "","",""
	else :
		return "","",""


# ********************************************************** NMEA 2000 ************************************************************


#etape 1 : verifier la taille de trame ( 0 -> 2p93-1 )
#etape 2 : verifier wind/meteo 

def reverse_16bits(decimal_value):
    binary_value = bin(decimal_value)[2:]  # Convertir la valeur décimale en binaire
    padded_binary = binary_value.zfill(16)  # Ajouter des zéros à gauche pour obtenir une longueur de 16 bits
    reversed_binary = padded_binary[::-1]  # Inverser la séquence binaire
    reversed_decimal = int(reversed_binary, 2)  # Convertir le résultat inversé en décimal
    return reversed_decimal


def Infos_Nmea_2000_WIND(nmea_2000_frame) : #nmea frame = 93 bits (ID '29 bits' / Data '64 bits')

	if ( nmea_2000_frame.isnumeric()  ) :

		nmea_2000_frame = int(nmea_2000_frame,2)

		# step 1 : extract ID '29 bits' (priority + PGN + @)
		wind_priority = str ( ( int(nmea_2000_frame)>>(26+64))&7 )  
		wind_PGN = str( (int(nmea_2000_frame)>>(8+64))&131071 )   #  131071 = 2p17 - 1 
		wind_Address = str( (int(nmea_2000_frame)>>64)&(255) )   #  255 = 2p8 - 1 
		if (wind_PGN == "126992") : 
			print("wind PGN is detected")
			print("WIND : priority = " + wind_priority +" / PGN = " + wind_PGN + " / @ = " + wind_Address)	
			#step 2 : extract DATA '64 bits' (wind : vitesse + direction)
			wind_Sid = str( ((int(nmea_2000_frame)>>56)&255) )   # sid = data >> 56 & (2p8-1)
			wind_Vitesse_vent = str( reverse_16bits( ((int(nmea_2000_frame)>>40)&65535) ) / 1000 )  # vitesse vent = data >> 40 & (2p16-1)
			wind_Direction_vent = str ( reverse_16bits( ((int(nmea_2000_frame)>>24)&65535) ) * (180/3.14) ) # direction vent = data >> 24 & (2p16-1)
			print("WIND : SID = " + wind_Sid + " / Vitesse = "+wind_Vitesse_vent+" / Direction = "+wind_Direction_vent)
			return wind_priority,wind_PGN,wind_Address,wind_Sid,wind_Vitesse_vent,wind_Direction_vent
		else :
			print("wind PGN not detected")
			return "","","","","",""
	else :
		return "","","","","",""
	

def Infos_Nmea_2000_METEO(nmea_2000_frame) : #nmea frame = 93 bits (ID '29 bits' / Data '64 bits')

	if ( nmea_2000_frame.isnumeric() ) :

		nmea_2000_frame = int(nmea_2000_frame,2)

		# step 1 : extract ID '29 bits' (priority + PGN + @)
		meteo_priority = str ( ( int(nmea_2000_frame)>>(26+64))&7 )  
		meteo_PGN = str( (int(nmea_2000_frame)>>(8+64))&131071 )   #  131071 = 2p17 - 1 
		meteo_Address = str( (int(nmea_2000_frame)>>64)&(255) )   #  255 = 2p8 - 1
		if (meteo_PGN == "130311") : 
			print("meteo PGN is detected")
			print("METEO : priority = " + meteo_priority +" / PGN = " + meteo_PGN + " / @ = " + meteo_Address)	
			#step 2 : extract DATA '64 bits' (wind : vitesse + direction)
			meteo_Sid = str( ((int(nmea_2000_frame)>>56)&255) )   # sid = data >> 56 & (2p8-1)
			meteo_Temperature = str( (reverse_16bits( ((int(nmea_2000_frame)>>32)&65535) ) / 100) - 273.15 )   # kelvin -> celcuis 
			meteo_Humidity = str ( reverse_16bits( ((int(nmea_2000_frame)>>16)&65535) ) * 0.004 ) 
			meteo_Pression = str ( reverse_16bits( ((int(nmea_2000_frame))&65535) ) /100 ) 
			print("METEO : SID = " + meteo_Sid + " / Temperature = "+meteo_Temperature+" / Humidity = "+meteo_Humidity+" / Pression = "+meteo_Pression)
			return meteo_priority,meteo_PGN,meteo_Address,meteo_Sid,meteo_Temperature,meteo_Humidity,meteo_Pression
		else :
			print("meteo PGN not detected")
			return "","","","","","",""
	else :
		return "","","","","","",""


# ---------------------------- end NMEA part ------------------------------------------------------------------------







def func_baudrate_selection(Baudrate):
	print("Baudrate = "+str(Baudrate)+" is selected")

def func_com_selection(COM_number):
	print("COM = "+COM_number+" is selected")


# ----------- final nmea analyse & data visualization GUI --------------------------

def nmea_Analyse_and_Display(NMEA_Frame):
		
	# -------- verifier NMEA 1083 ------------
	NMEA1083_Wind = Infos_Nmea_1083_WIND(NMEA_Frame)
	NMEA1083_Meteo = Infos_Nmea_1083_METEO(NMEA_Frame)


	# -------- verifier NMEA 2000 ------------


	NMEA2000_Wind =Infos_Nmea_2000_WIND(NMEA_Frame)
	NMEA2000_Meteo = Infos_Nmea_2000_METEO(NMEA_Frame)


	# -------- main ----------------------

	fenetre =Tk()
	fenetre.geometry('600x400')
	fenetre.title('NMEA 1083/2000 Frame Analyser')
	fenetre['bg'] = '#a6cee3'
	fenetre.resizable(height=False,width=False)

	#label nmea frame
	label_wind = Label(fenetre,text=str(NMEA_Frame))
	label_wind.place(x='10',y='40')


	#test frame : format wind/meteo (NMEA 1083)

	if ( len(NMEA1083_Wind[0]) != 0 and len(NMEA1083_Wind[1])!= 0 ) : 
		#label NMEA 1083 WIND status ===> 3 labels : NMEA 1083 WIND format / Vitesse vent / Direction vent  
		
		label_wind1 = Label(fenetre,text="NMEA 1083 WIND format",fg='#3300ff')
		label_wind1.place(x='200',y='100')

		label_wind2 = Label(fenetre,text="Vitesse vent = "+NMEA1083_Wind[1]+" m/s ")
		label_wind2.place(x='200',y='130')

		label_wind3 = Label(fenetre,text="Direction vent = "+NMEA1083_Wind[0]+" °")
		label_wind3.place(x='200',y='160')

		print("NMEA 1083 format WIND : direction vent = " + NMEA1083_Wind[0]+" ° / vitesse vent = "+ NMEA1083_Wind[1] +" m/s ")



	if ( len(NMEA1083_Meteo[0]) != 0 and len(NMEA1083_Meteo[1])!= 0  ) : 
		# label NMEA 1083 METEO status

		label_meteo1 = Label(fenetre,text="NMEA 1083 METEO format",fg='#3300ff')
		label_meteo1.place(x='200',y='100')

		label_meteo2 = Label(fenetre,text="Pression = "+NMEA1083_Meteo[0]+" Pa ")
		label_meteo2.place(x='200',y='130')

		label_meteo3 = Label(fenetre,text="Temperature = "+NMEA1083_Meteo[1]+" °C")
		label_meteo3.place(x='200',y='160')

		label_meteo4 = Label(fenetre,text="Humidity = "+NMEA1083_Meteo[2]+" %")
		label_meteo4.place(x='200',y='190')

		print("NMEA 1083 format METEO : pression = " + NMEA1083_Meteo[0]+" Pa / Temperature = "+NMEA1083_Meteo[1]+" °C / Humidity = "+NMEA1083_Meteo[2]+" %")

	if ( (len(NMEA1083_Wind[0]) == 0 and len(NMEA1083_Wind[1])== 0) and (len(NMEA1083_Meteo[0]) == 0 and len(NMEA1083_Meteo[1]) == 0) ) :
		print("format nmea 1083 wind/meteo non correcte")


	#test frame : wind/meteo format (NMEA 2000)

	if ( len(NMEA2000_Wind[0]) != 0 and len(NMEA2000_Wind[1])!= 0 and len(NMEA2000_Wind[2])!= 0 and len(NMEA2000_Wind[3])!= 0  and len(NMEA2000_Wind[4])!= 0 and len(NMEA2000_Wind[5])!= 0 ) : 
		# label NMEA 2000 WIND status

		label_wind_nmea2000_1 = Label(fenetre,text="NMEA 2000 WIND format",fg='#3300ff')
		label_wind_nmea2000_1.place(x='200',y='100')

		label_wind_nmea2000_2 = Label(fenetre,text="Priority = "+NMEA2000_Wind[0])
		label_wind_nmea2000_2.place(x='200',y='130')

		label_wind_nmea2000_3 = Label(fenetre,text="PGN = "+NMEA2000_Wind[1])
		label_wind_nmea2000_3.place(x='200',y='160')

		label_wind_nmea2000_4 = Label(fenetre,text="Address = "+NMEA2000_Wind[2])
		label_wind_nmea2000_4.place(x='200',y='190')

		label_wind_nmea2000_5 = Label(fenetre,text="SID = "+NMEA2000_Wind[3])
		label_wind_nmea2000_5.place(x='200',y='220')

		label_wind_nmea2000_6 = Label(fenetre,text="Vitesse vent = "+NMEA2000_Wind[4]+" m/s")
		label_wind_nmea2000_6.place(x='200',y='250')

		label_wind_nmea2000_7 = Label(fenetre,text="Direction vent = "+NMEA2000_Wind[5]+" °")
		label_wind_nmea2000_7.place(x='200',y='280')

		


	if ( len(NMEA2000_Meteo[0]) != 0 and len(NMEA2000_Meteo[1])!= 0 and len(NMEA2000_Meteo[2])!= 0 and len(NMEA2000_Meteo[3])!= 0  and len(NMEA2000_Meteo[4])!= 0 and len(NMEA2000_Meteo[5])!= 0 and len(NMEA2000_Meteo[6])!= 0  ) :
		# label NMEA 2000 METEO status


		label_meteo_nmea2000_1 = Label(fenetre,text="NMEA 2000 METEO format",fg='#3300ff')
		label_meteo_nmea2000_1.place(x='200',y='100')

		label_meteo_nmea2000_2 = Label(fenetre,text="Priority = "+NMEA2000_Meteo[0])
		label_meteo_nmea2000_2.place(x='200',y='130')

		label_meteo_nmea2000_3 = Label(fenetre,text="PGN = "+NMEA2000_Meteo[1])
		label_meteo_nmea2000_3.place(x='200',y='160')

		label_meteo_nmea2000_4 = Label(fenetre,text="Address = "+NMEA2000_Meteo[2])
		label_meteo_nmea2000_4.place(x='200',y='190')

		label_meteo_nmea2000_5 = Label(fenetre,text="SID = "+NMEA2000_Meteo[3])
		label_meteo_nmea2000_5.place(x='200',y='220')

		label_meteo_nmea2000_6 = Label(fenetre,text="Temperature = "+NMEA2000_Meteo[4]+" °C")
		label_meteo_nmea2000_6.place(x='200',y='250')

		label_meteo_nmea2000_7 = Label(fenetre,text="Humidity = "+NMEA2000_Meteo[5]+" %")
		label_meteo_nmea2000_7.place(x='200',y='280')

		label_meteo_nmea2000_8 = Label(fenetre,text="Pression = "+NMEA2000_Meteo[6]+" Pa")
		label_meteo_nmea2000_8.place(x='200',y='310')


	if ((len(NMEA1083_Wind[0]) == 0 and len(NMEA1083_Wind[1])== 0) and (len(NMEA1083_Meteo[0]) == 0 and len(NMEA1083_Meteo[1]) == 0) 
		and len(NMEA2000_Wind[0]) == 0 and len(NMEA2000_Wind[1])== 0 and len(NMEA2000_Wind[2])== 0 and len(NMEA2000_Wind[3])== 0  and len(NMEA2000_Wind[4])== 0 and len(NMEA2000_Wind[5])== 0
		and  len(NMEA2000_Meteo[0]) == 0 and len(NMEA2000_Meteo[1])== 0 and len(NMEA2000_Meteo[2])== 0 and len(NMEA2000_Meteo[3]) == 0  and len(NMEA2000_Meteo[4]) == 0 and len(NMEA2000_Meteo[5]) == 0 and len(NMEA2000_Meteo[6])== 0  ) :
		
		label_error = Label(fenetre,text="ERROR ! check your NMEA 1083/2000 Frame Format",fg='red')
		label_error.place(x='200',y='100')




	fenetre.mainloop()

# -----------------------------------------------------


# ------------ read from serial port -------------------


def Read_from_serial_port(COM_number,Baudrate):
	print("COM = "+str(COM_number)+ " / Baudrate = "+str(Baudrate))
	#nmea_Analyse_and_Display("WIMWV,10.2,T,23.55,M,A*F5")
	s=serial.Serial(str(COM_number),Baudrate,timeout=1) # arg1 = COMx
	if (s.isOpen()):
		i = 0
		while(i < 1):
			if (s.in_waiting>0):
				b=s.readline()
				try :
					NMEA_Frame=b.decode('utf-8').strip()
					print(NMEA_Frame)
					i = 2
				except UnicodeDecodeError:
					print("Error decoding the received data.")
		nmea_Analyse_and_Display(NMEA_Frame)
	    #analyse de trame 'NMEA' .

# ------------------------------------------------


# ---------------- GUI : select 'COMx' & 'BaudRate'

ws = Tk()
ws.title('Choose your Serial Port & Baudrate')
ws.geometry('400x300')
ws.config(bg='#a6cee3')


def display_selected():
    choice_port = variable_com.get()
    choice_baudrate = variable_baudrate.get()
    print("choice : COM = " + choice_port + " / Baudrate = " + choice_baudrate)
    #execute python script 1 , after choosing the port
    Read_from_serial_port(choice_port,choice_baudrate)

# select : COMx 

coms = ['COM1','COM2', 'COM3','COM4','COM5','COM6','COM7','COM8','COM9']

# setting variable for Integers
variable_com = StringVar()
variable_com.set(coms[0])

# creating widget
dropdown = OptionMenu(
    ws,
    variable_com,
    *coms,
    command=func_com_selection
)

# positioning widget
dropdown.pack(expand=True)


# select : Baudrate

baud_rates = [1200,2400,4800,9600,14400,19200,38400,57600,115200,128000] # list of baudrates .

# setting variable for Integers
variable_baudrate = StringVar()
variable_baudrate.set(baud_rates[3])

# creating widget
dropdown = OptionMenu(
    ws,
    variable_baudrate,
    *baud_rates,
    command=func_baudrate_selection
)

# positioning widget
dropdown.pack(expand=True,pady=50)


# button to validate (COM & Baudrate)
B = Button(ws, text ="✓ validate",command = display_selected , bg='#b4eeb4' , border = 5)

B.pack(pady=8)

# infinite loop 
ws.mainloop()