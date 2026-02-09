import json
import os

from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


class RAGService:

    def __init__(self):
        # Erzeugung numerischer Vektoren aus Text.
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)

        # Splitter teilt lange Texte in überlappende Chunks.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        # LLM erzeugt am Ende die Antwort in natürlicher Sprache.
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            temperature=settings.openai_temperature,
            openai_api_key=settings.openai_api_key,
        )

        self.vectorstore = None
        self.qa_chain = None

    def initialize(self) -> None:
       
        #Initialisiert den RAG-Workflow (Dokumente laden -> Index bauen -> QA-Chain bauen).
        documents = self._load_documents()
        self._create_vector_store(documents)
        self._create_qa_chain()

    def _load_documents(self) -> list[Document]:
        
        # Lädt die JSON-Datei und erstellt daraus LangChain-Dokumente.
        path = settings.product_data_path

        # Abbruch mit Fehlermeldung, wenn die Daten fehlen oder ungültig sind
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Produktdaten nicht gefunden unter '{path}'. "
            )

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Minimal-Validierung des erwarteten Schemas.
        if not isinstance(data, dict) or "sections" not in data or not isinstance(data.get("sections"), dict):
            raise ValueError(
                "Produktdaten haben nicht das erwartete Format (erwartet: { sections: {...} }). "
                "Bitte sicherstellen, dass die Serienseite erfolgreich extrahiert wurde."
            )

        name = str(data.get("name") or "PGN-plus-P")
        url = str(data.get("url") or settings.product_url)
        sections: dict = data["sections"]

        beschreibung = str(sections.get("beschreibung") or "")
        technik = str(sections.get("technik") or "")
        vorteile = str(sections.get("vorteile") or "")
        versionen = str(sections.get("versionen") or "")

        # Sicherheitsprüfung: Wenn die Beschreibung zu kurz ist, sind die Daten sehr wahrscheinlich unbrauchbar.
        if len(beschreibung) < 80:
            raise ValueError(
                "Produktdaten wirken unvollständig: 'beschreibung' ist zu kurz. "
            )

        documents: list[Document] = []

        # Jede Sektion wird ein eigenes Dokument, um Retrieval zu verbessern.
        documents.append(
            Document(
                page_content=f"Quelle: Serienseite\nURL: {url}\n\nProdukt: {name}\n\nBESCHREIBUNG\n{beschreibung}",
                metadata={"source": "serienseite", "section": "beschreibung"},
            )
        )

        if technik:
            documents.append(
                Document(
                    page_content=f"Quelle: Serienseite\nURL: {url}\n\nProdukt: {name}\n\nTECHNIK\n{technik}",
                    metadata={"source": "serienseite", "section": "technik"},
                )
            )

        if vorteile:
            documents.append(
                Document(
                    page_content=f"Quelle: Serienseite\nURL: {url}\n\nProdukt: {name}\n\nVORTEILE\n{vorteile}",
                    metadata={"source": "serienseite", "section": "vorteile"},
                )
            )

        if versionen:
            documents.append(
                Document(
                    page_content=f"Quelle: Serienseite\nURL: {url}\n\nProdukt: {name}\n\nVERSIONEN\n{versionen}",
                    metadata={"source": "serienseite", "section": "versionen"},
                )
            )

        return documents

    def _create_vector_store(self, documents: list[Document]) -> None:
        
        # Erstellt den Chroma-Vektorindex aus den Dokumenten.
        splits = self.text_splitter.split_documents(documents)

        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory="./chroma_db",
        )

    def _create_qa_chain(self) -> None:
        
        # Baut die QA-Chain (Retriever + Prompt + LLM)
        template = (
            "Du bist ein freundlicher Produktexperte für den PGN-plus-P Parallelgreifer von SCHUNK.\n"
            "Beantworte die Kundenfrage ausschließlich basierend auf dem Kontext.\n"
            "Wenn der Kontext nicht reicht, sage offen, dass du es nicht sicher weißt, und schlage vor, welche Info fehlt.\n"
            "Antworte kurz (2-4 Sätze) und auf Deutsch.\n\n"
            "Kontext:\n{context}\n\n"
            "Frage: {question}\n"
            "Antwort:"
        )

        prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": settings.rag_top_k})

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
        )

    def answer(self, question: str) -> str:
        
        # Beantwortet eine Frage mit der aufgebauten RAG-Chain
        if self.qa_chain is None:
            raise RuntimeError("RAG Service ist nicht initialisiert.")

        response = self.qa_chain.invoke({"query": question})
        return response["result"]
