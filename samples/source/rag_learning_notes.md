# RAG Learning Notes

## What Is RAG?

RAG means retrieval augmented generation. It is a common pattern for building LLM applications that answer questions using external documents.

Instead of asking the model to answer from memory, the system first retrieves relevant text from a knowledge base. Then the model generates an answer using that retrieved context.

## Basic RAG Flow

1. Load documents.
2. Split documents into chunks.
3. Convert chunks into embeddings.
4. Store embeddings in a vector database.
5. Convert the user question into an embedding.
6. Retrieve similar chunks.
7. Send the chunks and question to the language model.
8. Generate an answer with sources.

## Why Chunking Matters

Large documents are too long to send directly to a language model. Chunking breaks a document into smaller pieces.

A good chunk should be large enough to contain useful meaning, but small enough to retrieve accurately.

Chunk overlap helps preserve context across boundaries. For example, if one paragraph ends in one chunk and the next paragraph continues in another chunk, overlap can reduce information loss.

## Embeddings

An embedding is a numerical representation of text. Similar meanings should have similar vectors.

Embeddings make semantic search possible. For example, the question "What should I learn for this role?" may match document text about "required skills" even if the exact words are different.

## Vector Store

A vector store saves text chunks and their embeddings. When the user asks a question, the system searches for the most similar vectors.

Common vector stores include Chroma, FAISS, Pinecone, Weaviate, and Milvus.

## Hallucination Control

RAG can reduce hallucination, but it cannot remove it completely.

Useful techniques include:

- Ask the model to answer only from the provided context.
- Show source snippets.
- Refuse to answer when context is not enough.
- Retrieve multiple chunks and compare them.
- Add evaluation checks for relevance and faithfulness.

## Beginner Learning Advice

For a beginner, the first goal is not to build a complex agent. The first goal is to understand each step of the RAG pipeline.

Start by loading a PDF and printing the extracted text. Then split the text into chunks. Only after that should you add embeddings, vector search, and model generation.

