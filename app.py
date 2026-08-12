import os
import json
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from vosk import Model, KaldiRecognizer

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

logger.info(">> [KINEMA BOOT] Iniciando Servidor de Reconocimiento de Voz...")

app = FastAPI()

# =====================================================================
#  CARGA DEL MODELO VOSK (ESPAÑOL)
# =====================================================================
try:
    vosk_model = Model(lang="es")
    logger.info(">> [KINEMA BOOT] Modelo Vosk cargado y listo.")
except Exception as e:
    logger.error(f"!! [ERROR CRÍTICO] Fallo al cargar Vosk: {e}")
    vosk_model = None

# =====================================================================
#  RUTAS DEL SERVIDOR Y WEBSOCKET
# =====================================================================
@app.get("/")
async def root():
    return {"status": "Kinema STT Server Online", "websockets": "Activo en /ws"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("\n=======================================================")
    logger.info(">> [KINEMA WS] 🟢 BRAZO KINEMA CONECTADO EXITOSAMENTE.")
    logger.info("=======================================================\n")
    
    if vosk_model:
        reconocedor_vosk = KaldiRecognizer(vosk_model, 16000)

    try:
        while True:
            data = await websocket.receive()
            
            # RECIBIR AUDIO Y TRADUCIR A PALABRAS
            if "bytes" in data:
                audio_chunk = data["bytes"]
                
                if vosk_model:
                    # AcceptWaveform devuelve True cuando detecta un silencio (fin de frase)
                    if reconocedor_vosk.AcceptWaveform(audio_chunk):
                        resultado = json.loads(reconocedor_vosk.Result())
                        texto_detectado = resultado.get("text", "").strip().lower()
                        
                        if texto_detectado:
                            logger.info(f"   [VOSK TRADUJO]: '{texto_detectado}'")
                            # Se lo manda directo de regreso al ESP32
                            await websocket.send_text(f"TEXTO:{texto_detectado}")

    except WebSocketDisconnect:
        logger.warning("\n!! [KINEMA WS] 🔴 BRAZO KINEMA DESCONECTADO.")
    except Exception as e:
        logger.error(f"\n!! [KINEMA WS FATAL] Error general: {e}")

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    logger.info(f">> [KINEMA BOOT] Arrancando en el puerto {puerto}...")
    uvicorn.run(app, host="0.0.0.0", port=puerto)
