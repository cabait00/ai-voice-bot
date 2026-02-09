from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import QuestionRequest, AnswerResponse, HealthResponse
from app.rag_service import RAGService
from app.config import settings


class VoiceAgentAPI:
    
    def __init__(self):
        # Erstelle FastAPI App
        self.app = FastAPI(
            title="PGN-plus-P Voice Agent",
            description="RAG-basierter Voice Agent",
            version="1.0.0"
        )
        
        # Konfiguriere CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,  # Aus Config
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Erstelle RAG Service
        self.rag_service = RAGService()
        
        # Registriere Event Handlers
        self._setup_events()
        
        # Registriere Routes
        self._setup_routes()
    
    def _setup_events(self):
        #Registriert Startup/Shutdown Events.
        @self.app.on_event("startup")
        async def startup():
            # Wird beim Server-Start ausgeführt. Initialisiert RAG Service.
            print("Initialisiere RAG Service")
            # Lädt Daten, erstellt Vector Store, erstellt QA Chain
            self.rag_service.initialize()
            print("RAG Service bereit!")
    
    def _setup_routes(self):
        # Definiert alle API Routes.
        @self.app.get("/", response_model=HealthResponse)
        async def root():
            # Root Endpoint - Einfacher Health Check.
            return HealthResponse(
                status="online",
                message="Voice Agent API läuft"
            )
        
        @self.app.get("/health", response_model=HealthResponse)
        # Detaillierter Health Check. Prüft ob RAG Service bereit ist.
        async def health():
            # Prüfe ob Vector Store existiert
            if self.rag_service.vectorstore is None:
                return HealthResponse(
                    status="unhealthy",
                    message="RAG Service nicht initialisiert"
                )
            
            return HealthResponse(
                status="healthy",
                message="Alle Systeme operational"
            )
        
        @self.app.post("/api/ask", response_model=AnswerResponse)
        # Beantwortet Fragen zum Produkt.
        async def ask(request: QuestionRequest):
            try:
                # Rufe RAG Service auf und trigger die RAG-Pipeline
                answer = self.rag_service.answer(request.question)
                
                # Erstelle Response
                return AnswerResponse(
                    answer=answer,
                    question=request.question
                )
                
            except Exception as e:
                # Bei Fehler: 500 Internal Server Error
                # Error Details werden nicht exposed (Security)
                raise HTTPException(
                    status_code=500,
                    detail="Fehler bei der Verarbeitung"
                )
    
    def get_app(self) -> FastAPI:
        # Gibt die FastAPI App zurück.
        return self.app
