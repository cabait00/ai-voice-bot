from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Key wird aus Umgebungsvariable geladen
    openai_api_key: str
    
    # Welches OpenAI Modell verwenden
    openai_model: str = "gpt-3.5-turbo"
    
    # Wie kreativ soll das Modell sein
    openai_temperature: float = 0.3
    
    # Wie viele Dokumente sollen für Kontext verwendet werden
    rag_top_k: int = 3
    
    # Wie groß soll ein Text-Chunk sein
    chunk_size: int = 500
    
    # Überlappung zwischen Chunks
    chunk_overlap: int = 50
    
    # Port auf dem der Server läuft
    api_port: int = 8000
    
    # Erlaubte Frontend-Origins (CORS)
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Pfad zur JSON-Datei mit Produktinformationen aus der Schunk Webseite
    product_data_path: str = "product_data.json"
    
    # URL der Produktseite zum Scrapen
    product_url: str = "https://schunk.com/de/de/greiftechnik/parallelgreifer/pgn-plus-p/c/PGR_3228"
    
    class Config:
        # Lade Werte aus .env Datei
        env_file = ".env"


# Globale Settings-Instanz
settings = Settings()
