import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
from flask import Flask

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID del chat o grupo de Telegram
TARGET_URL = "https://turnoslab.ar/vacuna-dengue-fechas.php"  # URL a consultar
SEARCH_PATTERN = "Sin disponibilidad"  # Patrón a buscar en el HTML
DNI=os.getenv("DNI")

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

async def check_url_and_notify():
    async with aiohttp.ClientSession() as session:
        try:
            # Enviar datos form-data
            form_data = {
                "vacunatorio": "1",
                "dosis": "2",
                "documento": DNI
            }
            async with session.post(TARGET_URL, data=form_data) as response:
                if response.status != 200:
                    raise Exception(f"Error en la solicitud: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Verificar si el texto "Sin disponibilidad" está presente
                if "Sin disponibilidad" not in soup.text:
                    # Enviar mensaje si no está
                    await bot.send_message(chat_id=CHAT_ID, text=f"¡Disponibilidad detectada!")
                else:
                    print("Aún no hay disponibilidad.")

        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"Error: {e}")

async def periodic_task(interval):
    while True:
        await check_url_and_notify()
        await asyncio.sleep(interval)

# Flask endpoint para Heroku (mantener vivo el proceso)
@app.route("/")
def index():
    return "Bot corriendo."

if __name__ == "__main__":
    # Configurar asyncio para ejecutar la tarea periódicatry:
    loop = asyncio.new_event_loop()  # Crear un nuevo bucle de eventos
    asyncio.set_event_loop(loop)    # Establecerlo como el bucle actual
    loop.create_task(periodic_task(10 * 60))  # Ejecutar la tarea cada 10 minutos
    loop.run_forever()     
    
    
    # Ejecutar Flask en paralelo
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))