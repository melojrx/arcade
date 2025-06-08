from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Treinamentos
from .utils import gerar_documentos
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
from django.conf import settings
from django_q.tasks import async_task
from pathlib import Path


@receiver(post_save, sender=Treinamentos)
def signals_treinamento_ia(sender, instance, created, **kwargs):
     if created:
        async_task(task_treinar_ia, instance.id)

def task_treinar_ia(instance_id):
    try:
        instance = Treinamentos.objects.get(id=instance_id)
        documentos = gerar_documentos(instance)
        if not documentos:
            print("Nenhum documento encontrado para processar")
            return

        print(f"Processando {len(documentos)} documentos...")
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documentos)
        print(f"Criados {len(chunks)} chunks de texto")

        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

        # Usar o caminho correto que a view do chat espera
        db_path = "banco_faiss"
        
        # Criar o diretório se não existir
        Path(db_path).mkdir(exist_ok=True)
        
        # Definir caminhos dos arquivos
        index_file = os.path.join(db_path, "index.faiss")
        pkl_file = os.path.join(db_path, "index.pkl")
        
        # Verificar se já existe um índice FAISS válido
        if os.path.exists(index_file) and os.path.exists(pkl_file):
            try:
                print(f"Carregando índice existente de: {db_path}")
                vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
                vectordb.add_documents(chunks)
                vectordb.save_local(db_path)
                print("Documentos adicionados ao índice existente")
            except Exception as e:
                print(f"Erro ao carregar índice existente: {e}")
                # Remover arquivos corrompidos
                if os.path.exists(index_file):
                    os.remove(index_file)
                if os.path.exists(pkl_file):
                    os.remove(pkl_file)
                # Criar novo índice
                print("Criando novo índice FAISS")
                vectordb = FAISS.from_documents(chunks, embeddings)
                vectordb.save_local(db_path)
                print(f"Novo índice criado em: {db_path}")
        else:
            print("Criando primeiro índice FAISS")
            vectordb = FAISS.from_documents(chunks, embeddings)
            vectordb.save_local(db_path)
            print(f"Índice FAISS criado em: {db_path}")
            
    except Exception as e:
        print(f"Erro na task_treinar_ia: {e}")
        raise