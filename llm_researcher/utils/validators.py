from typing import List

from pydantic import BaseModel, Field

## GET RID OF THIS CRAP DPH

class Subtopic(BaseModel):
    task: str = Field(description="Task name", min_length=1)

class Subtopics(BaseModel):
    subtopics: List[Subtopic] = []

