from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from .. import settings
from ..models.message import SlackThread

# 検索に使用する類似ドキュメント数
K = 5
EMBEDDING_MODEL = OpenAIEmbeddings(
    openai_api_key=settings.OPENAI_API_KEY,
    model="text-embedding-ada-002"
)

QDRANT_URL = settings.QDRANT_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY

client = QdrantClient(
        QDRANT_URL,
        api_key=QDRANT_API_KEY, # For Qdrant Cloud, None for local instance
    )
# EmbeddingをベクトルDBに保存する
def save_embedding_to_db(arxiv_id: str, chunks: list):
    # Saving the row chunked text
    """

    LangChain DocumentデータとEmbeddingモデルを引数に
    arxiv_idをコレクション名としてDBに保存

    """

    # Todo: From_text もあるようなので調査
    doc_store = Qdrant.from_documents(
        chunks, EMBEDDING_MODEL, url=QDRANT_URL, prefer_grpc=True,
        api_key=QDRANT_API_KEY,
        collection_name=arxiv_id,
        force_recreate=False,
    )
    return doc_store


# IDに該当するembeddingをベクトルDBから取得する
def get_embedding_and_similarity_from_db(thread: SlackThread, arxiv_id: str):
    # Addressing vector DB by arxiv_id == collection name
    qdrant_db = Qdrant(
        client=client,
        embeddings=EMBEDDING_MODEL,
        collection_name=arxiv_id,
    )

    # expose this index in a retriever interface
    retriever = qdrant_db.as_retriever(search_kwargs={'k': K})
    # related_infor = qdrant_db.similarity_search(query=thread.messages[-1].text, k=K)
    return retriever


# 全てのdb内のコレクションを確認
# def get_list_collections():
#     return client.get_collections()

# コレクションの中身を確認
# def check_a_collection(arxiv_id: str):
#     return client.get_collection(collection_name=f"{arxiv_id}")

