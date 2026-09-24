from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fpdf import FPDF
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )


def create_story(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):
    return f"""
COMICCRAFT – 5 PANEL COMIC
===========================

Title: The Mystery of {setting}

Panel 1 – The Discovery
Scene: {character_name} enters the {setting}.
Dialogue: "{character_name}: Something feels different here..."
Narration: The adventure begins.

Panel 2 – The Mystery
Scene: {character_name} notices something unusual.
Dialogue: "{character_name}: What could this be?"
Narration: A mysterious secret is waiting to be discovered.

Panel 3 – The Danger
Scene: A mysterious danger appears.
Dialogue: "{character_name}: I won't let you harm this place!"
Narration: The situation becomes dangerous.

Panel 4 – The Challenge
Scene: {character_name} faces the challenge bravely.
Dialogue: "{character_name}: I have to protect the {setting}!"
Narration: Courage helps the hero overcome the obstacle.

Panel 5 – The Ending
Scene: The {setting} becomes peaceful again.
Dialogue: "{character_name}: The {setting} is safe!"
Narration: The adventure ends with hope.

Story Idea: {story_prompt}
Tone: {tone}
Art Style: {art_style}
"""


@app.post("/generate")
async def generate(request: Request):

    form_data = await request.form()

    story_prompt = form_data.get("story_prompt", "").strip()
    character_name = form_data.get("character_name", "Hero").strip()
    setting = form_data.get("setting", "Enchanted Forest").strip()
    tone = form_data.get("tone", "Adventure").strip()
    art_style = form_data.get("art_style", "Comic Book").strip()

    story = create_story(
        story_prompt,
        character_name,
        setting,
        tone,
        art_style
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "story": story
        }
    )


@app.post("/download-pdf")
async def download_pdf(request: Request):

    form_data = await request.form()

    story = form_data.get("story", "").strip()

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "ComicCraft", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "AI Comic Story Creator", ln=True, align="C")

    pdf.ln(8)

    pdf.set_font("Helvetica", size=11)

    safe_story = story.encode(
        "latin-1",
        "replace"
    ).decode("latin-1")

    pdf.multi_cell(0, 7, safe_story)

    file_path = "comiccraft_story.pdf"

    pdf.output(file_path)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="ComicCraft_Story.pdf"
    )