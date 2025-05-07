from pdfrw import PdfReader, PdfWriter
from pdfrw.findobjs import trivial_xobjs, wrap_object, find_objects
from pdfrw.objects import PdfDict, PdfArray, PdfName
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas

from app.utils.general_database import upload_image
from app.utils.general_database import upload_image_to_firestore


def retrive_image(arxiv_id, pdf_path, output_path) -> [str]:
    WIDTH = 8.5*72
    MARGIN = 0.5*72

    pdf = PdfReader(pdf_path)
    objects = []
    for xobj in list(find_objects(pdf.pages)):
        if xobj.Type == PdfName.XObject and xobj.Subtype == PdfName.Form:
            if '/PTEX.FileName' in xobj:
                wrapped = wrap_object(xobj, WIDTH, MARGIN)
                objects.append(wrapped)

    """
       取得した画像を新しいPDFに書き出す -> img.pdf
    """
    if not objects:
        # 画像がない時
        return []


    """
    書き出したimg.pdfをページごとpngフォーマットに変換し保存する
    """
    # Todo: temporay directoryにする
    writer = PdfWriter(output_path + '/img.pdf')
    writer.addpages(objects)
    writer.write()
    images = convert_from_path(output_path+ '/img.pdf')
    storage_path = []
    for i in range(len(images)):
        images[i].save(output_path + '/'  + arxiv_id + '_image_' + str(i) + '.png')
        storage_path.append(upload_image(arxiv_id, output_path + '/'  + arxiv_id + '_image_' + str(i) + '.png'))
    upload_image_to_firestore(arxiv_id, storage_path)
    return storage_path
