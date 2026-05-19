from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes.parse import router as parse_router
from src.api.routes.skills import router as skills_router
from src.api.routes.stats import router as stats_router
from src.api.routes.vacancies import router as vacancies_router


app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(vacancies_router)
app.include_router(stats_router)
app.include_router(parse_router)
app.include_router(skills_router)


@app.get("/")
def root():
    return FileResponse("frontend/index.html")