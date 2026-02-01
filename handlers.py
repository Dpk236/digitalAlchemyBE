from enum import Enum
import os
from Enums.explanation_mode_enum import ExplanationMode
from ContextRetrievel.sorted_context_based_query import SortedContextBasedQuery
from LLMQueries.get_fallback_response import get_fallback_response_query
from LLMQueries.get_notes import get_notes_query
from utility.reranker import rerank_documents
from Helpers.Summary.summary_cache import cache_video_notes, cache_video_summaries, get_cached_video_notes, get_cached_video_summaries
from Retrieval.SummarizeQuery.SummarizeAllChunks import summarize_video_chunks
from utility.build_context import build_context
from Helpers.QuizMemory.FetchQuizQuestion import get_quiz_question
from utility.quiz_explanation import extract_question_id
from Retrieval.QuizGeneration.QuizGeneration import quiz_generation
from store.vector_store import get_qdrant_client, vector_store_ready
from Retrieval.TimestampQuery.timestamp_query import retrieve_by_timestamp
from Retrieval.SummarizeQuery.SummarizeQuery import (retrieve_by_summarize_query,
                                                     retrieve_all_chunks_by_video_id, fetch_all_chunks_from_qdrant)
from ask_query import get_user_query
import json
from qdrant_client.models import Filter, FieldCondition, MatchValue
from openai import OpenAI
from qdrant_client import QdrantClient
RETRIEVAL_STAGES = [2, 4, 8, 16]   # max cap based on cost

def is_context_insufficient(answer: str) -> bool:
    triggers = [
        "not clearly explained in the lecture",
        "insufficient information",
        "not mentioned in the context",
        "context does not mention this term",
        "not mentioned",
        "context does not contain",
    ]
    return any(t in answer.lower() for t in triggers)


from Services.Embedding.sentence_transform_embeddings import SentenceTransformerEmbeddings

embedding_model = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")

def embed_text(text):
    return embedding_model.embed_query(text)


def handle_context_retrieval(query: str, chat_history=[], video_id=None):
    video_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.video_id",
                match={"value": str(video_id)}
            )
        ]
    )
    search_result = vector_store_ready().similarity_search(
        query=query,
        k=6,
        filter=video_filter,
    )
    # print("Search Result:", len(search_result))
    docs_sorted = sorted(
        search_result,
        key=lambda d: d.metadata.get("start_time", 0)
    )
    # print("Search Result Length:", search_result)
    context = build_context(docs_sorted)
    # print(best_docs, "best_docsbest_docs", context)
    result = get_user_query(query, context, chat_history=chat_history)
    return {
        "type": "context_retrieval",
        "message": "Routing to vector search + LLM explanation",
        "query": query,
        "response": result
    }


def handle_quiz_generation(query: str, video_id=None):
    # video_id passed from arguments
    result = quiz_generation(query=query, video_id=video_id)
    return result


def handle_example_request(query: str):
    return {
        "type": "example_request",
        "message": "Routing to explanation with examples",
        "query": query
    }


def handle_timestamp_query(query: str, chat_history=[], summary:str = "", video_id=None):
    print("Handling timestamp query...", vector_store_ready())
    # video_id passed
    docs = retrieve_by_timestamp(
        vector_store=vector_store_ready(),
        video_id=video_id,
        query=query
    )

    if not docs:
        return "This part is not clearly explained at that time in the lecture."
    context = build_context(docs)

    result = get_user_query(query, context, chat_history=chat_history, summary=summary)
    return {
        "type": "timestamp_query",
        "message": "Routing to timestamp query section",
        "query": query,
        "response": result
    }


def handle_fallback(query: str):
    return {
        "type": "fallback",
        "message": "Unable to determine intent clearly",
        "query": query
    }


def handle_summarize_video(query: str, chat_history=[], key: str = ""):
    parts = key.split(":")
    if len(parts) >= 3:
        video_id = parts[2]
    else:
        video_id = "unknown"
    if get_cached_video_summaries(video_id):
        summarize_video = get_cached_video_summaries(video_id)
        print(f"Using cached summaries for video {video_id}")
        return {
            "type": "summarize_video",
            "message": "Routing to summarize video section (from cache)",
            "query": query,
            "response": summarize_video
        }
    docs = retrieve_by_summarize_query(
        vector_store=vector_store_ready(),
        video_id=video_id,
    )
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
    print("Summarize Video Result:", len(summarize_video), len(new_docs))
    if not docs:
        return "This part is not clearly explained at that time in the lecture."
    with open(summary_file, "w") as f:
        json.dump(summarize_video, f, indent=2)

    result = get_user_query(query, summarize_video,
                            chat_history=chat_history)
    cache_video_summaries(video_id, result)
    return {
        "type": "summarize_video",
        "message": "Routing to summarize video section",
        "query": query,
        "response": result
    }


def handle_notes_creation(query: str, chat_history=[], key: str = ""):
    # Same issue as summarize. I need to parse key or pass video_id. 
    # Key format: f"notes:{user_id}:{lecture_id}:{session_id}" (lecture_id IS video_id)
    parts = key.split(":")
    if len(parts) >= 3:
        video_id = parts[2]
    else:
        video_id = "unknown"
    if get_cached_video_notes(video_id):
        notes_video = get_cached_video_notes(video_id)
        print(f"Using cached notes_video for video {video_id}")
        return {
            "type": "notes_creation",
            "message": "Routing to notes video section (from cache)",
            "query": query,
            "response": notes_video
        }
    docs = retrieve_by_summarize_query(
        vector_store=vector_store_ready(),
        video_id=video_id,
    )
    new_docs = retrieve_all_chunks_by_video_id(
        vector_store=vector_store_ready(),
        video_id=video_id,
    )
    summary_file = f"video_{video_id}_summaries.json"
    video_notes = None
    if os.path.exists(summary_file):
        with open(summary_file, "r") as f:
            video_notes = json.load(f)
            print(f"Loaded existing summaries from {summary_file} for notes")
            
    notes = video_notes if video_notes else summarize_video_chunks(
            new_docs)
    print("Notes Video Result:", len(notes), len(new_docs))
    if not docs:
        return "This part is not clearly explained at that time in the lecture."
    with open(summary_file, "w") as f:
        json.dump(notes, f, indent=2)

    result = get_notes_query(query, notes)
    cache_video_notes(video_id, result)
    return {
        "type": "notes_creation",
        "message": "Routing to notes video section",
        "query": query,
        "response": result
    }


def handle_quiz_explanation(
    user_query: str,
    user_id: str,
    lecture_id: str,
    session_id: str,
    chat_history=[],
    summary: str =""
):
    """
    Explains a quiz question using quiz memory only.
    """

    question_id = extract_question_id(user_query)

    if not question_id:
        return {
            "type": "fallback",
            "message": "Please specify which question you want explained (e.g., Explain Question 4)."
        }
    print(f"Fetching explanation for {question_id}...", lecture_id, session_id)
    quiz = get_quiz_question(
        user_id=user_id,
        lecture_id=lecture_id,
        session_id=session_id,
        question_id=question_id
    )

    if not quiz:
        return {
            "type": "fallback",
            "message": f"I could not find {question_id}. Please try again."
        }

    # -----------------------------
    # Build Explanation (HTML)
    # -----------------------------
    explanation_html = f"""
            <ul>
            <li><b>Question:</b> {quiz["question_text"]}</li>
            <li><b>Explanation:</b>
                <ul>
                <li>{quiz["correct_answer_text"]} are examples related to this topic.</li>
                </ul>
            </li>
            """

    # Optional timestamp
    if quiz.get("timestamps"):
        explanation_html += f"""
            <li><b>Video Reference:</b>
                <a href="{quiz['timestamps'][0]}">{quiz['timestamps'][0]}</a>
            </li>
            """
    dict_str = str(quiz)
    explanation_html += "</ul>"
    print(quiz, dict_str, type(quiz), "Explanation===",
          explanation_html, user_query)
    result = get_user_query(user_query, dict_str,
                            chat_history=chat_history, summary=summary)
    return {
        "type": "quiz_explanation",
        "message": f"Explaining {question_id} from quiz memory.",
        "query": user_query,
        "response": result
    }


def adaptive_rag_answer(
    query: str,
    chat_history,
    explanation_mode: str = ExplanationMode.STANDARD,
    summary: str ="",
    video_id=None
):
    # video_id passed
    for k in RETRIEVAL_STAGES:
        print("Trying adaptive RAG with k =", k, video_id)
        # 1️⃣ Retrieve small K
        video_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.video_id",
                    match={"value": str(video_id)}
                )
            ]
        )
        docs = vector_store_ready().similarity_search(
            query=query,
            k=k,
            filter=video_filter
        )
        print("docsdocsdocs====", docs)
        # 3️⃣ Build context (timestamps preserved)
        context = build_context(docs)

        # 4️⃣ Ask LLM
        answer = get_user_query(
            query,
            context,
            chat_history=chat_history,
            explanation_mode=explanation_mode,
            summary=summary
        )
        print(f"Adaptive RAG with k={k}, answer={answer}")    
        # 5️⃣ Check sufficiency
        if not is_context_insufficient(answer):
            return {
                "response": answer,
                "used_chunks": k,
                "type": "context_retrieval",
                "adaptive": True
            }

        # else → expand K and retry

    # 6️⃣ Final fallback (max context used)
    return {
        "type": "context_retrieval",
        "message": "Routing to vector search + LLM explanation",
        "query": query,
        "response": answer
    }

def fallback_rag_answer(
    query: str,
    chat_history,
    explanation_mode: str = ExplanationMode.STANDARD,
    summary: str ="",
    video_id=None
):
    # video_id passed
    # 1️⃣ Retrieve max K
    video_filter = Filter(
        must=[
            FieldCondition(
                key="metadata.video_id",
                match={"value": str(video_id)}
            )
        ]
    )
    print("video_filtervideo_filter",video_id, video_filter)
    context_query = SortedContextBasedQuery(
            query=query,
            k=6,
            filter=video_filter,
    )
    docs_sorted = context_query.sorted_context_query()
    # print("Search Result Length:", search_result)
    context = build_context(docs_sorted)
    answer = get_fallback_response_query(
        query,
        context,
        chat_history=chat_history,
        summary=summary
    )
    print(f"Fallback RAG answer={answer}")    

    return {
        "type": "context_retrieval",
        "message": "Routing to vector search + LLM explanation",
        "query": query,
        "response": answer if answer else "something went wrong"
    }