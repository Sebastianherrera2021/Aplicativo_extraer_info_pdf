#pip install pdfplumber
#pip install openpyxl

import pdfplumber
import collections
import re
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading  # Asegúrate de que esto esté importado

# Función para procesar un solo PDF
def procesar_pdf(archivo):
    with pdfplumber.open(archivo) as pdf:
        texto_total = ""
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                texto_total += texto + "\n"  # Acumular el texto total
        return texto_total.lower()  # Devolver el texto en minúsculas

# Función para procesar todos los archivos PDF en la carpeta
def procesar_archivos(carpeta):
    palabras_con_un_punto = [' CONTRATO DE PRESTACION DE SERVICIOS No.','plazo de ejecución:', 'objeto:']
    palabras_con_dos_puntos = ['valor del contrato:', 'obligaciones:']

    # Inicializar una lista para almacenar los resultados
    resultados = []

    for archivo in os.listdir(carpeta):
        if archivo.endswith('.pdf'):
            texto_pdf = procesar_pdf(os.path.join(carpeta, archivo))  # Procesar el PDF

            # Contar cuántas veces aparece cada palabra/frase
            for palabra in palabras_con_un_punto + palabras_con_dos_puntos:
                coincidencias = re.findall(re.escape(palabra), texto_pdf, re.IGNORECASE)
                frecuencia = len(coincidencias)

                # Extraer el texto después de las palabras clave
                if palabra in palabras_con_un_punto:
                    patron = re.compile(re.escape(palabra) + r'\s*([^.]+)\.', re.IGNORECASE)
                    texto_extraido = patron.findall(texto_pdf)
                    texto_extraido = texto_extraido[0].strip() if texto_extraido else None
                else:  # Para palabras con dos puntos
                    patron = re.compile(re.escape(palabra) + r'\s*(.*?)(?=\.\.)', re.IGNORECASE | re.DOTALL)
                    texto_extraido = patron.findall(texto_pdf)
                    texto_extraido = texto_extraido[0].strip() if texto_extraido else None
                
                # Añadir los resultados a la lista
                resultados.append({
                    'Archivo': archivo,
                    'Clave': palabra,
                    'Frecuencia': frecuencia,
                    'Información': texto_extraido
                })

    # Crear DataFrame a partir de los resultados
    df = pd.DataFrame(resultados)
    df.to_excel('informacion_extraida.xlsx', index=False)
    messagebox.showinfo("Éxito", "El archivo Excel ha sido exportado como 'informacion_extraida.xlsx'")

# Función para seleccionar la carpeta y procesar los archivos
def seleccionar_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        threading.Thread(target=procesar_archivos, args=(carpeta,)).start()

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Procesador de PDFs")

# Crear un botón para seleccionar la carpeta
boton_seleccionar = tk.Button(root, text="Seleccionar carpeta con PDFs", command=seleccionar_carpeta)
boton_seleccionar.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()
