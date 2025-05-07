import re
from tempfile import TemporaryDirectory

import arxiv
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

from app.utils.img_retrival import retrive_image


def extract_text_from_arxiv(arxiv_id: str):
    """
    Arxivのidを受け取って、その論文PDFに載っている全てのテキストを返す。
    """
    try:
        if not arxiv_id:
            return ""

        with TemporaryDirectory() as tempdir:
            paper = next(arxiv.Search(id_list=[arxiv_id]).results())
            paper.download_pdf(dirpath=tempdir, filename="paper.pdf")
            loader = PyPDFLoader(str(tempdir) + "/paper.pdf")
            retrive_image(arxiv_id.replace("/", "-").replace(".", "-"), str(tempdir) + "/paper.pdf", str(tempdir))
            text_splitter = CharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200)
            pages = loader.load_and_split(text_splitter)
        return pages

    except Exception as e:
        print(f"Error: {e}")
        return ""


def arxiv_id_of(url: str) -> str:
    """
    有効なArxivのURLを受け取って、その論文のIDを返す。
    Unique id: yymm.nnnnn (or arch-ive/yymmnnn for older ones).

    URLの形
    http://arxiv.org/(abs or pdf or format)/hep-th/9603067(.pdf)

    e.g. URL to id
    http://arxiv.org/abs/hep-th/9603067 -> hep-th/9603067
    http://arxiv.org/pdf/0705.0123      -> 0705.0123
    https://arxiv.org/pdf/2310.01383.pdf-> 2310.01383

    """
    url = url.strip()
    pattern = re.compile(r'.*https?://arxiv\.org/(abs|pdf)/([\w\.\-\/]+)')
    match = pattern.match(url)
    if match:
        unique_id = match.group(2)
        if ".pdf" == unique_id[-4:]:
            unique_id = unique_id[:-4]
        # unique_idの形式チェック
        digits = ""
        # 古い形式
        if len(unique_id) == 14 and unique_id[0:7] == "hep-th/":
            digits = unique_id.split("hep-th/")[1]
        # 新形式
        elif len(unique_id) in [9, 10] and unique_id[4] == ".":
            digits = unique_id.replace(".", "")
        if digits.isdigit():
            return unique_id
    raise ValueError(f"arxiv url is invalid {url}")


if __name__ == "__main__":
    for url in [
        # valid urls
        # " http://arxiv.org/abs/hep-th/9603067",
        # "http://arxiv.org/pdf/0705.0123",
        # "https://arxiv.org/pdf/2310.01383.pdf",
        "Summarize this article . http://arxiv.org/abs/hep-th/9603067"
        # Invalid urls
        # " http://arxiv.org/abs/hep-th/96030a6a ",
        # "http://arxiv.org/pdf/aaaa,vvvv  ",
    ]:
        print(arxiv_id_of(url))
        print()
    out_txt_file = Path("/backend/app/utils/") / Path("pdf_content.txt")
    with open(out_txt_file, "w") as f:
        f.write(extract_text_from_arxiv("http://arxiv.org/abs/hep-th/9603067"))
