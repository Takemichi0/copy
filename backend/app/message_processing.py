from langchain.chains import RetrievalQAWithSourcesChain
from langchain.llms import OpenAI
from langchain.callbacks.base import AsyncCallbackHandler
from time import sleep
from typing import Optional

from langchain.prompts import PromptTemplate

from . import settings
from .models.arxiv import ArxivPaper, VectorizationStatus
from .models.message import SlackThread
from .models.reply import ReplyCallback
from .repository.arxiv import find_arxiv_vectorization_status, update_arxiv_vectorization_status
from .repository.message_history import upsert_message_history
from .utils.arxiv_extraction import extract_text_from_arxiv
from .utils.database import save_embedding_to_db, get_embedding_and_similarity_from_db
from .utils.general_database import fetch_image


VECTORIZATION_WATING_LIMIT = 1 * 60  # seconds
VECTORIZATION_WATING_INTERVAL = 1  # seconds


def generate_slack_reply(thread: SlackThread, reply_callback: ReplyCallback) -> None:
    upsert_message_history(thread)

    arxiv_paper = ArxivPaper(id=thread.arxiv_id)

    generate_response(thread, arxiv_paper, reply_callback)


def generate_response(thread: SlackThread, arxiv_paper: ArxivPaper, reply_callback: ReplyCallback) -> str:
    vectorization_status = find_arxiv_vectorization_status(
        arxiv_paper.id_safe_for_path)

    should_vectorize = vectorization_status == VectorizationStatus.NOT_STARTED or wait_until_vectorization_fails(arxiv_paper)
    if should_vectorize:
        update_arxiv_vectorization_status(
            arxiv_paper.id_safe_for_path, VectorizationStatus.IN_PROGRESS)
        save_vectorized_content(arxiv_paper)
        update_arxiv_vectorization_status(
            arxiv_paper.id_safe_for_path, VectorizationStatus.COMPLETED)
    images_path = fetch_image(arxiv_paper.id_safe_for_path)
    if thread.requires_summary():
        return generate_summary(thread, arxiv_paper, images_path, reply_callback)
    return call_openai(thread, arxiv_paper, reply_callback)


def wait_until_vectorization_fails(arxiv_paper: ArxivPaper) -> None:
    """
    一定時間以上ベクトル化処理のステータスが変わらない場合は、なんらかの要因により
    ベクトル化処理が失敗していると判断し、ベクトル化処理を再度実行したい
    @return: ベクトル化処理が失敗してると判断した場合はTrue、それ以外はFalse
    """
    wating_time = 0
    while find_arxiv_vectorization_status(arxiv_paper.id_safe_for_path) != VectorizationStatus.COMPLETED:
        if wating_time > VECTORIZATION_WATING_LIMIT:
            return True
        sleep(VECTORIZATION_WATING_INTERVAL)
        wating_time += VECTORIZATION_WATING_INTERVAL
    return False


def generate_summary(thread: SlackThread, arxiv_paper: ArxivPaper, images_path: Optional[list[str]], reply_callback: ReplyCallback) -> None:
    if images_path is not None:
        reply_callback.set_images(images_path)
    paper_summary(thread, arxiv_paper, reply_callback)
    return

def save_vectorized_content(arxiv_paper: ArxivPaper) -> None:
    paper_docs = extract_text_from_arxiv(arxiv_paper.id)
    save_embedding_to_db(arxiv_paper.id_safe_for_path, paper_docs)

class StreamingCallbackHandler(AsyncCallbackHandler):
    def __init__(self, callback: ReplyCallback) -> None:
        self.callback = callback

    async def on_llm_start(self, _serializ, _prompts, **_) -> None:
        await self.callback.add_token("")
        if self.callback.has_images():
            await self.callback.show_images()

    async def on_llm_new_token(self, token: str, **_) -> None:
        await self.callback.add_token(token)

    async def on_llm_end(self, _result, **_) -> None:
        await self.callback.finish()


def call_openai(thread: SlackThread, arxiv_paper: ArxivPaper, reply_callback: ReplyCallback) -> None:
    retriever = get_embedding_and_similarity_from_db(
        thread, arxiv_paper.id_safe_for_path)

    custom_template = """Please provide a detailed answer to the follow-up question below.
        Chat History:
        {chat_history}
        Summaries:
        {summaries}
        Follow Up Question: {question}"""
    prompt = PromptTemplate(template=custom_template, input_variables=[
                            "chat_history", "summaries", "question"])
    chain_type_kwargs = {"prompt": prompt}
    qa = RetrievalQAWithSourcesChain.from_chain_type(
        llm=OpenAI(model_name='gpt-3.5-turbo-16k',
                   openai_api_key=settings.OPENAI_API_KEY,
                   streaming=True,
                   callbacks=[StreamingCallbackHandler(reply_callback)]),
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=False,
        verbose=False)

    thread_dict = thread.messages_to_dict()
    print("GO GPT!")
    result = qa.stream({
        "question": thread.messages[-1].text,
        "chat_history": [message["text"] for message in thread_dict[:-1]]
        }, return_only_outputs=True)
    next(result)


sections = ['[Backgrounds]', '[Purposes]',
            '[Experimental Methods]', '[Experiment Results]', '[Discussions]']
first_query = f"""You are the world class experienced researcher. Create detailed summary including {sections} sections. Use bullet points to write each point. Do not make up any infomation, and only write fact from the papers."""


def paper_summary(thread: SlackThread, arxiv_paper: ArxivPaper, reply_callback: ReplyCallback):
    # 要約を返す
    # 最初の実行はthreadにはURLがくる, urlを渡す必要はない
    thread.messages[-1].text = first_query
    return call_openai(thread, arxiv_paper, reply_callback)
