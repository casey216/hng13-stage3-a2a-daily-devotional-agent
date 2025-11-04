# app/agents/devotional_agent.py
from app.agents.picker import pick_random_verse
from app.agents.generator import generate_structured_devotional
from app.database import ArchiveSessionLocal, Devotional
from sqlalchemy.exc import SQLAlchemyError

class DevotionalAgent:
    """
    Orchestrates pick -> generate -> (optionally archive).
    """

    def run(self, topic: str | None = None, tone: str = "encouraging", archive: bool = True):
        # 1. pick a verse (topic optional)
        reference, verse_text = pick_random_verse(topic)

        # 2. generate devotional (LLM)
        devotional = generate_structured_devotional(reference, verse_text, tone)

        # 3. optionally archive
        if archive:
            try:
                session = ArchiveSessionLocal()
                d = Devotional(
                    title=devotional["title"],
                    scripture_ref=devotional["scripture_ref"],
                    scripture_text=devotional["scripture_text"],
                    reflection=devotional["reflection"],
                    application=devotional["application"],
                    prayer=devotional["prayer"],
                )
                session.add(d)
                session.commit()
                session.refresh(d)
                devotional["_archived_id"] = d.id
                session.close()
            except SQLAlchemyError:
                # Archive should not break the main flow; attach no id if failure
                devotional["_archived_id"] = None

        return devotional