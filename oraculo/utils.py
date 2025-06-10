from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler


def html_para_texto_rag(html_str: str) -> str:
    soup = BeautifulSoup(html_str, "html.parser")
    texto_final = []

    for tag in soup.find_all(["h1", "h2", "h3", "p", "li",]):
        texto = tag.get_text(strip=True)

        if not texto:
            continue

        if tag.name in ["h1", "h2", "h3"]:
            texto_formatado = f"\n\n### {texto.upper()}"
        elif tag.name == "li":
            texto_formatado = f" - {texto}"
        else:
            texto_formatado = texto

        texto_final.append(texto_formatado)
        
    return "\n".join(texto_final).strip()


def gerar_documentos(instance):
    documentos = []
    if instance.documento:
        extensao = instance.documento.name.split('.')[-1].lower()
        if extensao == 'pdf':
            loader = PyPDFLoader(instance.documento.path)
            pdf_doc = loader.load()
            for doc in pdf_doc:
                doc.metadata['url'] = instance.documento.url
            documentos += pdf_doc
    if instance.conteudo:
        document = Document(page_content=instance.conteudo)
        documentos.append(document)

    if instance.site:
        site_url = instance.site if instance.site.startswith('https://') else f'https://{instance.site}'
        content = requests.get(site_url, timeout=10).text
        content = html_para_texto_rag(content)
        documentos.append(Document(page_content=content))   

    return documentos

from django.core.cache import cache
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.cache import cache
import datetime
from .wrapper_evolutionapi import SendMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()
scheduler.start()


def send_message_response(phone):
    messages = cache.get(f"wa_buffer_{phone}", [])
    if messages:
        question = "\n".join(messages)
        embeddings = OpenAIEmbeddings()
        vectordb = FAISS.load_local("banco_faiss", embeddings, allow_dangerous_deserialization=True)
        docs = vectordb.similarity_search(question, k=5)
        context = "\n\n".join([doc.page_content for doc in docs ])

        messages = [
            {"role": "system", "content": f"Você é um assistente virtual e deve responder com precissão as perguntas sobre uma empresa.\n\n{context}"},
            {"role": "user", "content": question}
        ]
        
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
        )

        response = llm.invoke(messages).content

        SendMessage().send_message('arcane', {"number": phone, "textMessage": {"text": response}})
        
        cache.delete(f"wa_buffer_{phone}")
        cache.delete(f"wa_timer_{phone}")

def sched_message_response(phone):
    if not cache.get(f'wa_timer_{phone}'):
        print('Agendando')
        scheduler.add_job(
           send_message_response,
           'date',
           run_date=datetime.now() + timedelta(seconds=15),
           kwargs={'phone':phone},
           misfire_grace_time=60
        )
        cache.set(f'wa_timer_{phone}', True, timeout=60)
