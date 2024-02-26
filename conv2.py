import PyPDF2
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet

def crear_pdf(lineas, nombre_archivo):
    c = canvas.Canvas(nombre_archivo, pagesize=landscape(letter))
    x_offset = -75
    style = getSampleStyleSheet()["Normal"]
    style.fontName = 'Courier'
    style.fontSize = 8
    y = 550

    for linea in lineas:
        if '\f\n' in linea:
            c.showPage()
            y = 550
            continue

        c.setFont(style.fontName, style.fontSize)
        c.drawString(100 + x_offset, y, linea.rstrip())
        y -= 10

    c.save()

def es_caratula(line):
    return "REPORTES PARA:" in line

def fin_pag(line):
    return "END;" in line

def rango(con):
    return con in range(1, 11) or con in range(20, 26) or con in range(38, 42) or con > 69

def procesar_archivo_txt(nombre_archivo_txt):
    lista_pdf = []
    con = 0
    caratula = False

    with open(nombre_archivo_txt, "r") as file_IN:
        for linea in file_IN:
            primer_caracter = linea[0]
            resto_cadena = linea[1:]

            if caratula:
                if rango(con) and not fin_pag(linea):
                    lista_pdf.append(resto_cadena)

                elif 'END;' in linea:
                    caratula = False

                con += 1
                continue

            if con == 50:
                lista_pdf.append('\f\n')
                con = 0
                continue

            if not linea.strip():
                lista_pdf.append('\n')
                continue

            if fin_pag(linea):
                continue

            if primer_caracter == '1':
                if 'FIRST DATA' in resto_cadena:
                    con = 1
                    lista_pdf.extend(['\f\n', resto_cadena])

                else:
                    lista_pdf.append('\f\n')
                    con = 0

            elif primer_caracter == '+':
                continue

            elif primer_caracter == ' ' or primer_caracter == '0':
                caratula = es_caratula(resto_cadena)
                lista_pdf.append(resto_cadena)
                con += 1

    return lista_pdf

def seleccionar_archivo_txt():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    nombre_archivo_txt = filedialog.askopenfilename(title="Selecciona un archivo TXT")

    return nombre_archivo_txt

if __name__ == "__main__":
    nombre_archivo_txt = seleccionar_archivo_txt()

    if nombre_archivo_txt:
        print("Archivo seleccionado:", nombre_archivo_txt)
        lista_pdf = procesar_archivo_txt(nombre_archivo_txt)
        nombre_archivo_pdf = "pruebas_horizontal.pdf"
        crear_pdf(lista_pdf, nombre_archivo_pdf)
        print(f"PDF creado exitosamente: {nombre_archivo_pdf}")
    else:
        print("No se seleccionó ningún archivo.")
