from pydantic import BaseModel, Field

# Request für Fragen an den Voice Agent. Pydantic validiert diesen.
class QuestionRequest(BaseModel):
    # Die Frage muss mindestens 1 Zeichen haben (leerer Input und zu viele Zeichen nicht erlaubt)
    question: str = Field(min_length=1, max_length=1000)

# Response mit der generierten Antwort.
class AnswerResponse(BaseModel):
    # Die generierte Antwort
    answer: str
    
    # Die ursprüngliche Frage (Echo)
    question: str

# Health Check Response.
class HealthResponse(BaseModel):
    # Status: "healthy" oder "unhealthy"
    status: str
    
    # Detailnachricht
    message: str
