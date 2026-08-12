import os
import json
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from vosk import Model, KaldiRecognizer

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

logger.info(">> [KINEMA BOOT] Iniciando Servidor STT Ultrarrápido...")

app = FastAPI()

try:
    vosk_model = Model(lang="es")
    logger.info(">> [KINEMA BOOT] Modelo Vosk cargado y listo.")
except Exception as e:
    logger.error(f"!! [ERROR] Fallo al cargar Vosk: {e}")
    vosk_model = None

@app.get("/")
async def root():
    return {"status": "Kinema STT Server Online"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("\n>> 🟢 BRAZO KINEMA CONECTADO.")
    
    estado_actual = "VIGILANDO"
    
    if vosk_model:
        reconocedor_vosk = KaldiRecognizer(vosk_model, 16000)

    try:
        while True:
            data = await websocket.receive()
            
            # --- MANEJO DE AUDIO EN TIEMPO REAL ---
            if "bytes" in data:
                audio_chunk = data["bytes"]
                
                # 1. ESPERANDO LA WAKE WORD "KINEMA"
                if estado_actual == "VIGILANDO" and vosk_model:
                    if reconocedor_vosk.AcceptWaveform(audio_chunk):
                        resultado = json.loads(reconocedor_vosk.Result())
                        texto_detectado = resultado.get("text", "").lower()
                    else:
                        resultado = json.loads(reconocedor_vosk.PartialResult())
                        texto_detectado = resultado.get("partial", "").lower()
                    
                    variantes_kinema = ["kinema", "cinema", "quema", "kíne", "kine"]
                    if any(palabra in texto_detectado for palabra in variantes_kinema):
                        logger.info(f"\n>> 🎯 ¡WAKE WORD DETECTADA! ({texto_detectado})")
                        estado_actual = "ESPERANDO_PREGUNTA"
                        reconocedor_vosk.Reset()
                        await websocket.send_text("WAKE") 
                
                # 2. PROCESANDO LA ORDEN EN VIVO (MÁXIMA VELOCIDAD)
                elif estado_actual == "GRABANDO" and vosk_model:
                    # Le damos el audio a Vosk al instante, no lo guardamos
                    reconocedor_vosk.AcceptWaveform(audio_chunk)

            # --- MANEJO DE ESTADOS ---
            elif "text" in data:
                msg = data["text"]
                
                if msg == "START" and estado_actual == "ESPERANDO_PREGUNTA":
                    estado_actual = "GRABANDO"
                    logger.info(">> 🎙️ Escuchando orden para el brazo...")
                
                elif msg == "STOP" and estado_actual == "GRABANDO":
                    logger.info(">> 🛑 Silencio. Enviando orden al instante...")
                    
                    if vosk_model:
                        # Extraemos el resultado que Vosk ya procesó mientras hablabas
                        resultado_final = json.loads(reconocedor_vosk.FinalResult())
                        texto_traducido = resultado_final.get("text", "").strip().lower()
                        
                        if texto_traducido:
                            logger.info(f">> 🗣️ COMANDO TRADUCIDO: '{texto_traducido}'")
                            await websocket.send_text(f"TEXTO:{texto_traducido}")
                        else:
                            logger.info(">> ❌ No se entendió el comando.")

                    await websocket.send_text("LIBERAR")
                    estado_actual = "VIGILANDO"
                    if vosk_model:
                        reconocedor_vosk.Reset()

    except WebSocketDisconnect:
        logger.warning("\n>> 🔴 BRAZO KINEMA DESCONECTADO.")
    except Exception as e:
        logger.error(f"\n>> !! Error general: {e}")

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=puerto)
