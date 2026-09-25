from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from huggingface_hub import InferenceClient
from dotenv import load_dotenv

from fpdf import FPDF

import os


load_dotenv()

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not found in .env file")


client = InferenceClient(
    api_key=HF_TOKEN,
    provider="auto"
)


def delete_old_images():

    os.makedirs(
        "static/images",
        exist_ok=True
    )

    for index in range(1, 6):

        file_path = f"static/images/panel_{index}.png"

        if os.path.exists(file_path):

            os.remove(file_path)

            print(
                f"Deleted old Panel {index}"
            )


def create_story(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    return f"""
COMICCRAFT – {character_name}'S ADVENTURE
==========================================

STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}


PANEL 1 – THE BEGINNING 🌟

Scene:
{character_name} begins an exciting adventure in the {setting}.
The events are connected directly to this story idea:

{story_prompt}

Dialogue:
"{character_name}: Something tells me this adventure is only beginning..."

Narration:
A mysterious journey begins, and {character_name} is ready to discover what lies ahead.


PANEL 2 – THE DISCOVERY 🔮

Scene:
While exploring the {setting}, {character_name} discovers something unexpected
that is connected to the main story.

Dialogue:
"{character_name}: What is this? There must be something important behind it."

Narration:
The discovery reveals that the adventure is much bigger than expected.


PANEL 3 – THE DANGER 👹

Scene:
A dangerous obstacle, enemy, or mysterious force appears in the {setting}.
{character_name} must face the danger and protect what matters.

Dialogue:
"{character_name}: I won't run away. I'll face this!"

Narration:
The peaceful adventure suddenly becomes a dangerous challenge.


PANEL 4 – THE BATTLE ⚔️

Scene:
{character_name} uses courage, intelligence, and determination to overcome
the danger and move closer to solving the mystery.

Dialogue:
"{character_name}: This is my chance. I have to keep going!"

Narration:
After a difficult struggle, {character_name} finally gains the upper hand.


PANEL 5 – THE ENDING 🌅

Scene:
The main conflict is resolved. The {setting} becomes peaceful again,
and {character_name} discovers the meaning of the adventure.

Dialogue:
"{character_name}: We did it... but I feel like this isn't the end."

Narration:
The adventure ends with hope, leaving the door open for a new journey.


END OF COMIC
============
Created with ComicCraft AI.
"""


def create_panel_images(
    character_name,
    setting,
    tone,
    art_style
):

    delete_old_images()

    panels = [

        (
            "The Beginning",
            f"{character_name} enters the {setting} and begins an exciting adventure."
        ),

        (
            "The Discovery",
            f"{character_name} discovers a mysterious secret inside the {setting}."
        ),

        (
            "The Danger",
            f"A dangerous mysterious creature appears and threatens the {setting}. "
            f"{character_name} bravely faces the danger."
        ),

        (
            "The Battle",
            f"{character_name} fights the danger and protects the {setting}."
        ),

        (
            "The Ending",
            f"The danger is defeated. {character_name} stands peacefully inside "
            f"the beautiful {setting}."
        )

    ]

    image_paths = []

    for index, (scene_title, scene_description) in enumerate(
        panels,
        start=1
    ):

        prompt = f"""
Create ONE professional comic-book illustration.

Character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art Style:
{art_style}

Panel:
{scene_title}

Scene:
{scene_description}

Visual requirements:

- One single comic illustration.
- Full scene composition.
- Character clearly visible.
- Detailed environment.
- Cinematic lighting.
- Vibrant colors.
- High-quality comic artwork.
- Expressive character.
- Consistent character appearance.
- Adventure comic style.
- Dynamic composition.
- No multiple panels.
- No speech bubbles.
- No captions.
- No written words.
- No logos.
- No watermark.
"""

        try:

            image = client.text_to_image(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell"
            )

            file_path = (
                f"static/images/panel_{index}.png"
            )

            image.save(file_path)

            image_paths.append(
                f"/static/images/panel_{index}.png"
            )

            print(
                f"Panel {index} SUCCESS"
            )

        except Exception as error:

            print(
                type(error).__name__
            )

            print(
                str(error)
            )

            raise

    return image_paths


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


@app.post("/generate")
async def generate(request: Request):

    form_data = await request.form()

    story_prompt = form_data.get(
        "story_prompt",
        ""
    ).strip()

    character_name = form_data.get(
        "character_name",
        "Hero"
    ).strip()

    setting = form_data.get(
        "setting",
        "Enchanted Forest"
    ).strip()

    tone = form_data.get(
        "tone",
        "Adventure"
    ).strip()

    art_style = form_data.get(
        "art_style",
        "Comic Book"
    ).strip()


    story = create_story(
        story_prompt,
        character_name,
        setting,
        tone,
        art_style
    )


    try:

        image_paths = create_panel_images(
            character_name,
            setting,
            tone,
            art_style
        )

    except Exception as error:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": (
                    f"Image Generation Error: "
                    f"{type(error).__name__}: {error}"
                ),
                "story_prompt": story_prompt,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style
            }
        )


    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "story": story,
            "image_paths": image_paths,
            "story_prompt": story_prompt,
            "character_name": character_name,
            "setting": setting,
            "tone": tone,
            "art_style": art_style
        }
    )


@app.post("/download-pdf")
async def download_pdf(request: Request):

    form_data = await request.form()

    story = form_data.get(
        "story",
        ""
    ).strip()


    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        20
    )

    pdf.cell(
        0,
        15,
        "ComicCraft",
        ln=True,
        align="C"
    )

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        0,
        10,
        "AI Comic Story Creator",
        ln=True,
        align="C"
    )

    pdf.ln(8)


    for index in range(1, 6):

        image_path = (
            f"static/images/panel_{index}.png"
        )

        if os.path.exists(image_path):

            pdf.image(
                image_path,
                x=15,
                w=180
            )

            pdf.ln(5)


    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        0,
        10,
        "Comic Story",
        ln=True
    )

    pdf.ln(5)

    pdf.set_font(
        "Helvetica",
        size=10
    )

    safe_story = (
        story
        .encode("latin-1", "replace")
        .decode("latin-1")
    )

    pdf.multi_cell(
        0,
        7,
        safe_story
    )


    file_path = "comiccraft_story.pdf"

    pdf.output(file_path)


    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="ComicCraft_Story.pdf"
    )