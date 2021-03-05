import telebot
import psycopg2
import array
from telebot import types
import urllib
import ssl

#Configuration for the connection to the database 
conexion = psycopg2.connect(host="XXX", database="XXXX", user="XXXX", password="XXXX")

#Token Telegram
API_TOKEN = 'XXXXXXXXXXXXXX'

#Initializing the bot
bot = telebot.TeleBot(API_TOKEN)

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
    Hola, Yo soy CovidUCIBot🇨🇺.
    Conmigo podrás recibir los datos actualizados del Centro Hospitalario UCI-MINSAP
    😷🤒🤧🥴\
    """)

# Handle /help'
@bot.message_handler(commands=['ayuda'])
def ayuda(message):
    bot.send_message(message.chat.id, """\
Hola, estos son los comandos que puedes utilizar:
😷 pacientes - Cantidad de pacientes ingresados
ℹ️ ayuda - Ayuda del bot.
🏥 capacidades - Cantidad de capacidades disponibles
🔨 mantenimiento - Cantidad de capacidades bloqueadas por mantenimiento
🚍 egresos - Cantidad de egresos en el día
🤒 ingresos - Cantidad de ingresos en el día
🚑 remitidos - Cantidad de remitidos en el día
⚕️ voluntarios - Cantidad de voluntarios y personal de salud \n
\
""")

# Handle '/pacientes' para saber la cantidad de pacientes
@bot.message_handler(commands=['pacientes'])
def totalAislados(message): 
    cur = conexion.cursor()
    #Query
    cur.execute( "SELECT * FROM aislado WHERE estado = 'Aislado' and manzana !='15';" )
    cont=0;
    #Iterating the array 
    for nombre in cur.fetchall() :
        cont=cont+1
    bot.send_message(message.chat.id, '😷 <b>Total de pacientes:</b> '+str(cont), parse_mode='HTML')

# Handle '/ingresos' para saber la cantidad de ingresos en el día
@bot.message_handler(commands=['ingresos'])
def totalingresos(message):    
    cur = conexion.cursor()
    #Query
    cur.execute( "SELECT * FROM aislado WHERE estado = 'Aislado' and date(fecha_ingreso) = date(now()) and manzana !='15';" )
    cont=0;
    #Iterating the array 
    for nombre in cur.fetchall() :
        cont=cont+1
    bot.send_message(message.chat.id, '🤒 <b>Ingresos en el día:</b> '+str(cont), parse_mode='HTML')

# Handle '/egresos' para saber la cantidad de egresos en el día
@bot.message_handler(commands=['egresos'])
def totalegresos(message):    
    cur = conexion.cursor()
    #Query
    cur.execute( "SELECT * FROM aislado WHERE estado = 'Alta' and date(fecha_salida) = date(now()) and manzana !='15';" )
    cont=0;
    #Iterating the array 
    for nombre in cur.fetchall() :
        cont=cont+1
    bot.send_message(message.chat.id, '🚍 <b>Egresos en el día:</b> '+str(cont), parse_mode='HTML')

# Handle '/remitidos' para saber la cantidad de remitidos en el día
@bot.message_handler(commands=['remitidos'])
def totalremitidos(message):    
    cur = conexion.cursor()
    #Query
    cur.execute( "SELECT * FROM aislado WHERE estado = 'Remitido' and date(fecha_salida) = date(now()) and manzana !='15';" )
    cont=0;
    #Iterating the array 
    for nombre in cur.fetchall() :
        cont=cont+1
    bot.send_message(message.chat.id, '🚑 <b>Remitidos en el día:</b> '+str(cont), parse_mode='HTML')
    # # Cerramos la conexión
    # conexion.close()          

# Handle '/voluntarios' para saber la cantidad de voluntarios
@bot.message_handler(commands=['voluntarios'])
def totalVoluntarios(message):   
    cur = conexion.cursor()
    #Query
    cur.execute( "SELECT * FROM voluntario WHERE activo = 't' and categoria NOT LIKE 'Personal Salud';" )
    cont_serv=0;
    #Iterating the array 
    for nombre in cur.fetchall() :
        cont_serv=cont_serv+1

    #Query
    cur.execute( "SELECT * FROM voluntario WHERE activo = 't' and categoria LIKE 'Personal Salud';" )
    cont_salud=0;
    #Iterating the array 
    for nombre in cur.fetchall() :
        cont_salud=cont_salud+1   

    #Query
    cur.execute( "SELECT * FROM voluntario WHERE activo = 't';" )
    cont_total=0;
    #Iterating the array 
    for nombre in cur.fetchall() :
        cont_total=cont_total+1  

    bot.send_message(message.chat.id, '🧹 <b>De servicio:</b> '+str(cont_serv)+'\n'+
                           '⚕️ <b>De Salud Pública:</b> '+str(cont_salud)+'\n'+
                           '👥 <b>Total:</b> '+str(cont_total)+'\n', parse_mode='HTML')

# Handle '/capacidades' para saber la cantidad de capacidades disponibles
@bot.message_handler(commands=['capacidades'])
def totalCapacidades(message):  
    cur = conexion.cursor()
    #Query
    cur.execute( "SELECT manzana,real_disponible FROM parte WHERE manzana !='15' and manzana !='Calabozo' and manzana !='19' and manzana !='16' ORDER by manzana ASC;" )
    arreglo = ""
    total = 0
    #Iterating the array 
    for manzana,real_disponible in cur.fetchall() :
        total = total + real_disponible
        aux = '🏨 <b>M-'+str(manzana)+':</b> '+str(real_disponible)+' capacidades disponibles\n'
        arreglo = arreglo + aux
        
    bot.send_message(message.chat.id, '<b>Cantidad de capacidades disponibles por manzana:</b>\n'+arreglo+'🏥 <b>Total disponible:</b> '+str(total)+' capacidades disponibles', parse_mode='HTML')
   
# Handle '/mantenimiento' para saber la cantidad de capacidades en mtto
@bot.message_handler(commands=['mantenimiento'])
def totalCapacidades(message):  
    cur = conexion.cursor()
    #Query
    cur.execute( "SELECT manzana,mtto FROM parte WHERE manzana !='15' and manzana !='Calabozo' and manzana !='19' and manzana !='16' ORDER by manzana ASC;" )
    arreglo = ""
    total = 0
    #Iterating the array 
    for manzana,mtto in cur.fetchall() :
        total = total + mtto
        aux = '🔨 <b>M-'+str(manzana)+':</b> '+str(mtto)+' capacidades\n'
        arreglo = arreglo + aux
        
    bot.send_message(message.chat.id, '<b>Cantidad de capacidades bloqueadas por mantenimiento:</b>\n'+arreglo+'🛠️ <b>Total en mantenimiento:</b> '+str(total)+' capacidades', parse_mode='HTML')

bot.polling()