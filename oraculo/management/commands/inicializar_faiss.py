from django.core.management.base import BaseCommand
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Inicializa o banco FAISS se não existir'

    def handle(self, *args, **options):
        banco_path = Path("banco_faiss")
        
        if banco_path.exists():
            self.stdout.write(
                self.style.SUCCESS('Banco FAISS já existe.')
            )
            return
        
        try:
            # Verificar se a API key existe
            if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
                self.stdout.write(
                    self.style.ERROR('OPENAI_API_KEY não configurada. Configure no settings.py ou arquivo .env')
                )
                return
                
            # Criar embeddings
            embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            
            # Criar banco FAISS vazio com documento dummy
            dummy_texts = ["Banco de conhecimento inicializado. Adicione documentos para treinamento."]
            vectordb = FAISS.from_texts(dummy_texts, embeddings)
            
            # Salvar banco
            vectordb.save_local("banco_faiss")
            
            self.stdout.write(
                self.style.SUCCESS('Banco FAISS inicializado com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao inicializar banco FAISS: {str(e)}')
            ) 