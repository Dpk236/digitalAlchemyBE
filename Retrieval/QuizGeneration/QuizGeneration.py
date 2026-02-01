from Services.SummarizeChunks.parallel_map_chunk import summarize_video_chunks
# from Services.SummarizeChunks.summarize_chunks import summarize_chunks_by_interval
# from Retrieval.SummarizeQuery.SummarizeAllChunks import summarize_video_chunks
from Helpers.QuizMemory.StoreQuizQuestions import store_quiz_questions
from utility.quiz_parser import parse_quiz_html
from Retrieval.QuizGeneration.generate_quiz_from_context import generate_quiz_from_context
from Retrieval.SummarizeQuery.SummarizeQuery import retrieve_all_chunks_by_video_id, retrieve_by_summarize_query
from store.vector_store import vector_store_ready
from utility.quiz_parser import parse_quiz_html
import json
import os
from pathlib import Path

from Context.socket_context import socket_context

def quiz_generation(query: str, video_id: str, user_id: str = "test_user", session_id: str = "test_session"):
    # user_id = socket_context.get_video("user_id")
    # session_id = socket_context.get_video("session_id")

    try:
        new_docs = retrieve_all_chunks_by_video_id(
            vector_store=vector_store_ready(),
            video_id=video_id,
        )
        summary_file = f"video_{video_id}_summaries.json"
        video_summaries = None
        if os.path.exists(summary_file):
            with open(summary_file, "r") as f:
                video_summaries = json.load(f)
                print(f"Loaded existing summaries from {summary_file}")
        summarize_video = video_summaries if video_summaries else summarize_video_chunks(
                new_docs)
        print("Context for quiz generation:", query, summarize_video)
            # 3. Generate quiz using the retrieved context
        quiz_data = generate_quiz_from_context(
                query=query, context=summarize_video)
        parsed = parse_quiz_html(quiz_data)
        store_quiz_questions(
                user_id=user_id,
                lecture_id=video_id,
                session_id=session_id,
                quiz_questions=parsed
        )
        return {
                "type": "quiz_generation",
                "message": "Quiz generated successfully.",
                "query": query,
                "response": quiz_data
        }
    except Exception as e:
        print("🔥 Quiz generation error:", e)
        return {
            "type": "quiz_generation",
            "message": "An error occurred during quiz generation.",
            "query": query,
            "response": None
        }
