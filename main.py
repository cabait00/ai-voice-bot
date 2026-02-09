from app.api import VoiceAgentAPI

# Erstelle API-Instanz
api = VoiceAgentAPI()

# Entry Point
if __name__ == "__main__":
    import uvicorn
    
    # Starte Server und gib die FastAPI-Instanz zurück
    uvicorn.run(
        api.get_app(),
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
