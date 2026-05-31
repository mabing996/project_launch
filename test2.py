doc_template_path = './assets/索屿-专审材料/RD/高精准金型模具的研发.docx'

from docx import Document
doc = Document(doc_template_path)
texts = [ para.text for para in doc.paragraphs]
print('1')