import os
import sys
import tkinter as tk


from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter, landscape, portrait

def crea_archivos (lista_sin_procesar): #lista de nombres de los archivos sin procesar
    sin_procesar = lista_sin_procesar
    for nombre_archivo in sin_procesar: #recorro la lista de nombres
        lista_pdf = procesar_archivo_txt(nombre_archivo) #primer proceso txt
        crear_pdf(lista_pdf, nombre_archivo) #le paso el archivo para procesar y el nombre del archivo de salida

def ajustar_tamano_fondo(ventana, fondo_label, imagen_fondo):
    nueva_ancho = ventana.winfo_width()
    nueva_alto = ventana.winfo_height()
    imagen_redimensionada = imagen_fondo.resize((nueva_ancho, nueva_alto))
    nuevo_fondo = ImageTk.PhotoImage(imagen_redimensionada)
    fondo_label.configure(image=nuevo_fondo)
    fondo_label.image = nuevo_fondo  # Actualiza la referencia del objeto de la imagen

def cerrar_ventana(ventana):
    ventana.destroy()
    sys.exit()  # Termina la ejecución del programa

def crear_interfaz_usuario(nombre_archivos):

    ventana = tk.Tk()
    ventana.title("Mision Beta 1.0")
    ventana.iconbitmap("fiserv_logo-1-368x184.ico")
    ventana.geometry("500x250")  # Tamaño de la ventana

    fondo_path = 'fondo_fiserv.png'   # Reemplaza con la ruta correcta
    if os.path.exists(fondo_path):
        imagen_fondo = Image.open(fondo_path)
        fondo = ImageTk.PhotoImage(imagen_fondo)
        
        fondo_label = tk.Label(ventana, image=fondo)
        fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Enlazar el evento de redimensionamiento al ajuste del fondo
        ventana.bind("<Configure>", lambda e: ajustar_tamano_fondo(ventana, fondo_label, imagen_fondo))

    # Agregar el botón para seleccionar el archivo
    boton_seleccionar = tk.Button(ventana, text= "Procesar archivos",command = lambda: crea_archivos(nombre_archivos))
    boton_seleccionar.pack(pady=20)       
    
    # Enlazar el evento de cerrar ventana
    ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana))

    # Iniciar el bucle principal de la interfaz de usuario
    ventana.mainloop()



def agregar_marca_de_agua(c, orientacion):
    '''
        Agrega el logo de la compania y lo acomoda según la orientacion del pdf

        parametros:
            c - objeto Canvas
            orientacion:
                H:horizontal
                V:vertical
    '''

    logo_path = 'agua.png'

    if orientacion == 'V':
        c.drawImage(logo_path, 200, 400)
        
    elif orientacion == 'H':
        c.drawImage(logo_path, 300, 350)

   

def crear_pdf(listapdf, nombre_archivo):

    global config #leemos la configuracion local
    name_arch = config['OUT'] + '\\' + nombre_archivo.rstrip('.TXT') + '.PDF'
    
    c = canvas.Canvas(name_arch)
    style = getSampleStyleSheet()["Normal"] #le damos el estilo normal predefinido para luego modificarlo
    style.fontName = 'Courier'
    style.fontSize = 7
    style.fontName = 'Courier-Bold' #negrita
    x_offset = -80
    cont = 0 #se utilizara para comtrolar la cantidad de lineas que se deben escribir en una hoja, dependera de la limite_lineas que se configura según la orientacion de la hoja
    limite_lineas = 90
    o = 'H'

    config_v = {
        'orientacion': portrait(letter),  #vertical
        'o' : 'V',
        'marco' : True,
        'base' : 584, #base del marco
        'altura' : 749, #altura del marco
        'grosor_linea' : 1, #grosor de la linea del marco
        'x_marco' : 13.0,
        'y_marco' : 26.0,
        'y' : 750,
        'tamaño_letra' : 7,
        'x_offset' : -75,
        'limite' : 90
        }

    config_h = {'orientacion':landscape(letter),
                'o' : 'H','marco' : True,
                'base' : 760, 'altura' : 584,
                'grosor_linea' : 1,
                'x_marco' : 13.0,
                'y_marco' : 13.0,
                'y' : 590,
                'tamaño_letra' : 7,
                'x_offset' : -85,
                'limite' : 70}
 
    for linea in listapdf:
        
        #si detecta un salto de linea o el contandor indica que la hoja llego al limite
        if '\f\n' in linea: #agrega el salto de página
                c.showPage()
                orientacion = landscape(letter)
                y = 550 ###cambiar esta variable de acá
                cont = 0
                continue
               
        elif 'FM0006' in linea or 'FL2007' in linea: #configuración del Formulario 0006

            orientacion = config_v['orientacion']
            c.setLineWidth(config_v['grosor_linea'])
            agregar_marca_de_agua(c, config_v['o']) #marca de agua
            c.rect(config_v['x_marco'], config_v['y_marco'], config_v['base'], config_v['altura'], stroke=1) #marco 
            style.fontSize = config_v['tamaño_letra'] #tamaño de la letra
            x_offset =  config_v['x_offset']# Offset del margen izquierdo
            y = config_v['y']
            c.setFont(style.fontName, style.fontSize)
            limite_lineas = config_v['limite']
            
            continue

        elif 'FL1000' in linea: #configuracion del formulario

            orientacion = config_h['orientacion']
            c.setLineWidth(config_h['grosor_linea'])
            agregar_marca_de_agua(c, config_h['o'])
            c.rect(config_h['x_marco'], config_h['y_marco'], config_h['base'], config_h['altura'], stroke=1)
            style.fontSize = config_h['tamaño_letra']
            x_offset =  config_h['x_offset']
            y = config_h['y']
            c.setFont(style.fontName, style.fontSize)
            limite_lineas = config_h['limite']
            
            continue
        
        else:  
            c.setFont(style.fontName, style.fontSize)
            

        c.setPageSize(orientacion)
        c.drawString(100 + x_offset, y, linea.rstrip())
        y -= 8
        cont += 1

        if cont == limite_lineas: #si llego al limite de lineas en una hoja, creo una nueva
            c.showPage()
            cont = 0
            if orientacion == portrait(letter):
                agregar_marca_de_agua(c, config_v['o'])
                c.rect(config_v['x_marco'], config_v['y_marco'], config_v['base'], config_v['altura'], stroke=1)
                y = config_v['y']
            else:
                agregar_marca_de_agua(c, config_h['o'])
                c.rect(config_h['x_marco'], config_h['y_marco'], config_h['base'], config_h['altura'], stroke=1)
                y = config_h['y']        
            
    c.save()
    

def procesar_archivo_txt(nombre_archivo_txt):
    '''

    '''

    global config
    name_arch = config['IN'] + '\\' + nombre_archivo_txt + '.TXT'
    
    lista_pdf = []
    con = 0

    with open(name_arch, "r") as file_IN:
        for linea in file_IN:
            primer_caracter = linea[0]
            resto_cadena = linea[1:]

            if not linea.strip():
                lista_pdf.append('\n')
                continue

            if primer_caracter == '1':
                if 'FIRST DATA' in resto_cadena:
                    
                    con = 1
                    lista_pdf.extend(['\f\n', formato,resto_cadena])

                elif 'DJDE' in resto_cadena: #guardo el dato del tipo de formulario que se debe usar para la hoja
                    formato = resto_cadena

                else:
                    lista_pdf.append('\f\n')
                    con = 0

            elif primer_caracter == '+':
                continue

            elif primer_caracter == ' ' or primer_caracter == '0':
                if 'DJDE' in resto_cadena:
                    continue
                
                lista_pdf.append(resto_cadena)

    return lista_pdf

def leer_config(ruta_archivo):
    '''
    Lee la configuracion del programa
    El txt debe contener todos los campos utilizados
 
    config['IN']: ruta de entrada
    config['out']: ruta de salida
    '''
    config = {}
    try:
        with open(ruta_archivo, 'r') as archivo:
            lineas = archivo.readlines()
            #ruta IN
            config['IN'] = lineas[0].strip()
            config['OUT'] = lineas[1].strip()
    except FileNotFoundError:
        print(f"El archivo '{ruta_archivo}' no se encontró.")
    except IOError:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
    return config
 
def lista_nombres_archivos (ruta_carpeta):
    '''
    devuelve una lista con los nombres de los archivos existentes en una carpeta especifica
    '''
    try:
        # Lista para almacenar nombres de archivos
        lista_de_nombres = []
        # Iterar sobre los archivos en la carpeta
        for archivo in os.listdir(ruta_carpeta):
            # Verificar si es un archivo .txt
            if archivo.endswith('.TXT') or archivo.endswith('.PDF'):
                lista_de_nombres.append(archivo[:-4])
        # Devolver la lista de nombres de archivos
        return lista_de_nombres
    except FileNotFoundError:
        print(f"La carpeta '{ruta_carpeta}' no se encontró.")
        return []
    except IOError:
        print(f"No se pudo leer la carpeta '{ruta_carpeta}'.")
        return []
 
def file_sin_procesar(ruta_in, ruta_out):
    '''
    devuelve los elementos de lista_in menos lista_out,
    se utilizara para obtener la lista de los elementos que aún no estan procesados
    '''
    try:
        #obtenemos las lista de los archivos que estan en las rutas de entrada y salida
 
        #TO_DO: seria mejor que la lista de salida las lea de un archivo que contenga el historial de los archivos procesados
        lista_in = lista_nombres_archivos(ruta_in)
        lista_out = lista_nombres_archivos(ruta_out)

        # Convertir ambas listas a conjuntos para realizar la diferencia
        set_in = set(lista_in)
        set_out = set(lista_out)
        # Obtener los archivos que están en lista_in pero no en lista_out
        archivos_faltantes = set_in - set_out
        # Devolver la lista de archivos faltantes
        return list(archivos_faltantes)

    except TypeError as e:
        print("Error:", e)
        return []

if __name__ == "__main__":

    config = leer_config('config.txt') #busca la configuracion donde se encuentra el script
    sin_procesar = file_sin_procesar(config['IN'], config['OUT']) #obtenemos la lista de los archivos sin procesar
    crear_interfaz_usuario(sin_procesar)
