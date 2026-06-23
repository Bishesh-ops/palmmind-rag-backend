from google import genai
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.vector_store import get_vector_store
from app.models.schemas import Interview
from app.services.memory import add_message_to_memory, get_chat_history

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def schedule_interview_tool(name: str, email: str, date: str, time: str) -> str:
    """
    Schedules an interview for a user with the given details.
    This docstring and type hints are read by Gemini to understand when to call it.
    """
    return "SUCCESS"


async def converse_with_rag(session_id: str, user_message: str, db: AsyncSession) -> str:
    """
    Coordinates Redis history, Pinecone vector search, and Gemini generation
    to deliver a context-aware answer or process an interview booking.
    """
    query_vector_response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=user_message,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )

    if not query_vector_response.embeddings:
        raise ValueError("Failed to generate query vector.")

    query_vector = query_vector_response.embeddings[0].values

    index = get_vector_store()
    search_results = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True
    )

    retrieved_chunks = []
    if search_results.get("matches"):
        for match in search_results["matches"]:
            metadata = match.get("metadata", {})
            if "text" in metadata:
                retrieved_chunks.append(metadata["text"])

    context_str = "\n---\n".join(retrieved_chunks)

    history = await get_chat_history(session_id, limit=6)

    contents_payload: list[types.Content] = []
    for msg in history:
        contents_payload.append(
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    contents_payload.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        )
    )

    system_instruction = (
          "You are an advanced AI assistant for PalmMind. "
          "Answer the user's questions accurately using ONLY the provided context below.\n"
          f"CONTEXT FROM DOCUMENTS:\n{context_str}\n\n"
          "CRITICAL INSTRUCTION FOR INTERVIEWS: If the user provides scheduling details "
          "(name, email, date, time), YOU MUST trigger the 'schedule_interview_tool' function. "
          "DO NOT generate a standard text response confirming the booking. "
          "YOU MUST USE THE FUNCTION CALL TOOL so the system can save the data."
      )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents_payload,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[schedule_interview_tool],
            temperature=0.2
        )
    )

    if response.function_calls:
        for call in response.function_calls:
            if call.name == "schedule_interview_tool":
                args = call.args
                if not args:
                    return "Failed to get information."
                name = str(args.get("name", ""))
                email = str(args.get("email", ""))
                date = str(args.get("date", ""))
                time = str(args.get("time", ""))

                if not name or not email or not date or not time:
                    incomplete_msg = "I can help you book that interview! Could you please provide your full name, email, preferred date, and time?"
                    await add_message_to_memory(session_id, "user", user_message)
                    await add_message_to_memory(session_id, "model", incomplete_msg)
                    return incomplete_msg

                new_interview = Interview(name=name, email=email, date=date, time=time)
                db.add(new_interview)
                await db.commit()

                success_msg = f"Perfect! I have successfully scheduled your interview for {date} at {time}. A confirmation has been logged for {name} ({email})."

                await add_message_to_memory(session_id, "user", user_message)
                await add_message_to_memory(session_id, "model", success_msg)
                return success_msg

    ai_text_response = response.text if response.text else "I am sorry, I could not process an answer."

    await add_message_to_memory(session_id, "user", user_message)
    await add_message_to_memory(session_id, "model", ai_text_response)

    return ai_text_response
