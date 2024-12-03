from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from datetime import datetime

from history import history
from main import pdf_loader, spiltter, vector_stored, model
import main
from fetch_answer_database import find_similarity,fetch_answer_for_question

# Logging setup
logging.basicConfig(filename="logs/new.log", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()


"""<--------------------------------------------------- VARIABLES --------------------------------------------->"""

sessions={"76"}
vt_store = None
greetings = ["hi", "hello", "hey", "hlo", "hola","how are you","hi how are you"]



"""<----------------------------------------------------- CORS ------------------------------------------------->"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

"""<-------------------------------------------------------- CLASSES ----------------------------------------->"""



class QuestionRequest(BaseModel):
    question: str
    session_id:str



"""<-------------------------------------------------------- FUNCTIONS --------------------------------------->"""

def date_time():
        date=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
        return date

def format_answer(answer):
    answer=answer.replace("**","\\b")
    return answer


"""<-------------------------------------------------------- API ROUTES --------------------------------------->"""

@app.post("/create_vectors")
async def create_vectors(request:Request):
    """
    Endpoint to create vector store from a PDF.
    """
    logger.info(f"Request URL: {request.url} | Method: {request.method}\n")
    global vt_store
    try:
        start=time.time()
        # Load and process the PDF
        pdf = pdf_loader(main.file_path)
        split = spiltter(pdf)
        vt_store = vector_stored(split, main.embeddings, main.PATH)
        return JSONResponse(content={"message": "Vector Store Created Successfully","Time":f"{start-time.time()}secs"})
    except Exception as e:
        logger.error(f"Error in create_vectors: {e}")
        raise HTTPException(status_code=500, detail="Failed to create vector store")

@app.post("/rag_responses")
async def rag_response(question: QuestionRequest,request:Request):
    """
    Endpoint to get responses using RAG (Retrieval-Augmented Generation).
    """
    logger.info(f"Request URL: {request.url} | Method: {request.method}\n")
    global sessions
    start = time.time()

    if vt_store is None:
        logger.info("Vector store is not initialized. Call /create_vectors first.")
        return JSONResponse(content={"Error": "Vector store is not initialized. Call /create_vectors first."})

    if question.question.lower().strip() in greetings:
        greeting_response = "Hello! I'm EVA AI, developed by Ayan to assist you. How can I help you today?"
        return JSONResponse(content={"Answer": greeting_response, "Time": f"{round(time.time()-start, 2)}"})

    # if question.session_id in sessions:
    #     matched = find_similarity(question.question)  # Get similar questions
    #     logger.info(f"Matches Found In Database:{matched}")
    #     if matched != []:
    #         # Get the best match from the list
    #         best_match = matched[0][0]  # Extract the question from the tuple
    #         answer = fetch_answer_for_question(best_match) 
    #         logger.info(f"Answer Fetch:{answer[0]}")
    #         return JSONResponse(content={"Answer": answer[0], "Time": f"{round(time.time()-start, 2)}"})

    try:
        logger.info("Entering LLM Chain")
        answer = model(vt_store, question.question)  # Assuming this function works with the question
        logger.info("Answer Generated Sucessfully")
        answer = format_answer(answer.content)
        # history(question.question, "1", answer, 1223, 122, "01", date_time())
        logger.info(f"Time Taken: {round(time.time()-start, 2)}")
        sessions.add(question.session_id)
        return JSONResponse(content={"Answer": answer, "Time": f"{round(time.time()-start, 2)}"})

    except Exception as e:
        logger.error(f"Error in rag_response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")
    