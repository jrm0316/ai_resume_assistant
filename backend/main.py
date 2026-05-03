from fastapi import FastAPI
from routes.chat import router as chat_router
from routes.upload import router as upload_router
from routes.analyze import router as analyze_router
from routes.match import router as match_router
from routes.compare import router as compare_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(match_router)
app.include_router(compare_router)
