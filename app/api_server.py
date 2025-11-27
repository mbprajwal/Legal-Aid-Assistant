from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn

# Import your chains
from src.combined_chain import CombinedLegalChatbot     
from src.document_chain import DocumentGeneratorChain
from src.voice_utils import transcribe_audio

app = FastAPI(title="Legal Aid Assistant API")

# Initialize chains
chat_chain = CombinedLegalChatbot()
doc_chain = DocumentGeneratorChain()

# ----------- MODELS -----------
class ChatRequest(BaseModel):
    user_query: str

class DocumentRequest(BaseModel):
    template_name: str
    user_inputs: dict
    user_query: str


# ----------- ENDPOINTS -----------

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    response = chat_chain.run(request.user_query)
    return {"response": response}


# @app.post("/document/generate")
# def generate_document(request: DocumentRequest):
#     pdf_path, text = doc_chain.generate(
#         template_name=request.template_name,
#         user_inputs=request.user_inputs,
#         user_query=request.user_query
#     )

#     return {
#         "message": "Document generated successfully",
#         "pdf_path": pdf_path,
#         "content_preview": text[:500]
#     }


# @app.post("/voice/chat")
# async def voice_chat_endpoint(file: UploadFile = File(...)):
#     # Save file temporarily
#     temp_path = f"temp_{file.filename}"
#     with open(temp_path, "wb") as f:
#         f.write(await file.read())

#     text = transcribe_audio(temp_path)
#     response = chat_chain.run(text)

#     return {
#         "transcription": text,
#         "response": response
#     }


@app.get("/session/reset")
def reset_memory():
    chat_chain.memory.reset()
    return {"status": "Memory cleared"}


if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)
