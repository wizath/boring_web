from fastapi import Depends

from app import app
from app.database import get_session, AsyncSession
from app.models import Note, NoteBase


@app.post("/list", response_model=list[Note])
async def create_note(db: AsyncSession = Depends(get_session)):
    items = await Note.list(db)
    return items


@app.post("/add", response_model=Note)
async def create_note(note: NoteBase, db: AsyncSession = Depends(get_session)):
    item = await Note.create(note, db)
    return item
