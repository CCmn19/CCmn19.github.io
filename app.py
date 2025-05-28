import os
import google.generativeai as genai
import markdown
import requests
from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configuración de Flask
app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuración de AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

MAX_HISTORY = 4  # Limite de historial de mensajes

@app.route("/", methods=["GET", "POST"])
def home():
    if "datos_usuario" not in session:
        session["datos_usuario"] = None
    if "history" not in session:
        session["history"] = []

    respuesta = None
    mensaje_bienvenida = None
    dieta_recomendada = None

    if request.method == "POST":
        # Si aún no tenemos los datos del usuario, los guardamos
        if not session["datos_usuario"]:
            nombre = request.form.get("nombre")
            peso = request.form.get("peso")
            altura = request.form.get("altura")
            edad = request.form.get("edad")
            sexo = request.form.get("sexo")
            informacion_adiconal = request.form.get("informacion_adicional")

            #calcular IMC
            altura_metros = float(altura) / 100  # Convertir cm a metros
            imc = float(peso) / (altura_metros ** 2)
            estado = ""
            dieta = ""
            
            if imc < 18.5:
                estado = "Bajo peso"
                dieta = "Dieta hipercalórica: rica en calorías saludables como frutos secos, aguacate, pastas y batidos."
            elif imc < 24.9:
                estado = "Peso normal"
                dieta = "Dieta equilibrada: frutas, verduras, proteínas magras, cereales integrales y grasas buenas."
            elif imc < 29.9:
                estado = "Sobrepeso"
                dieta = "Dieta hipocalórica: menos calorías, control de porciones y alimentos bajos en grasa."
            else:
                estado = "Obesidad"
                dieta = "Dieta baja en carbohidratos: proteínas, verduras y sin harinas ni azúcares refinados."

            session["datos_usuario"] = {
                "nombre": nombre,
                "peso": peso,
                "altura": altura,
                "edad": edad,
                "sexo": sexo,
                "informacion_adicional": informacion_adiconal,
                "dietas": None,
                "ejercicios": None,
            }

            mensaje_bienvenida = f"<strong>{nombre}</strong>, tu IMC es <strong>{imc:.2f}</strong> ({estado})."
            dieta_recomendada = f"<strong>✅ Dieta recomendada:</strong><br>{dieta}"
            return render_template("index.html",
                                   datos_usuario=session.get("datos_usuario"),
                                   respuesta=respuesta,
                                   history=session.get("history"),
                                   mensaje_bienvenida=mensaje_bienvenida,
                                   dieta_recomendada=dieta_recomendada)

        
        elif "dietas" in request.form and "ejercicios" in request.form:
            # Actualizar los datos del usuario
            session["datos_usuario"]["dietas"] = request.form.get("dietas")
            session["datos_usuario"]["ejercicios"] = request.form.get("ejercicios")
            return redirect("/")  # Redirigir para evitar reenvío de formulario


        else:
            # Ya tenemos los datos, ahora procesamos la pregunta
            mensaje = request.form.get("mensaje")

            datos = session["datos_usuario"]
            contexto = f"El usuario se llama {datos['nombre']}, pesa {datos['peso']} kg y mide {datos['altura']} cm. Tiene {datos['edad']} años y es {datos['sexo']}. Su informacíon a tomar en cuenta es {datos['informacion_adicional']}. Su dieta es {datos['dietas']} y su plan de ejercicio es {datos['ejercicios']}. Solo si el usuario te pregunta tu nombre di que eres un asistente virtual de IA especializado en nutrición y entrenamiento físico llamado Vita AI."

            prompt = f"{contexto}\n\nPregunta del usuario: {mensaje}"

            try:
                respuesta_modelo = model.generate_content(prompt)
                respuesta = respuesta_modelo.text

                # Guardar en el historial
                session["history"].append({"pregunta": mensaje, "respuesta": respuesta})

                if len(session["history"]) > MAX_HISTORY:
                    session["history"] = session["history"][-MAX_HISTORY:]

            except Exception as e:
                respuesta = f"Error al generar la respuesta: {str(e)}"

        return render_template("index.html",
                           datos_usuario=session.get("datos_usuario"),
                           respuesta=respuesta,
                           history=session.get("history"),
                           mensaje_bienvenida=mensaje_bienvenida,
                           dieta_recomendada=dieta_recomendada)
    
    return render_template("index.html",
                           datos_usuario=session.get("datos_usuario"),
                           respuesta=respuesta,
                           history=session.get("history"),
                           mensaje_bienvenida=mensaje_bienvenida,
                           dieta_recomendada=dieta_recomendada)
if __name__ == "__main__":
    app.run(debug=True)
