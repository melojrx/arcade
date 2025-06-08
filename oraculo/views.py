from django.shortcuts import render, redirect
from rolepermissions.checkers import has_permission
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from .models import Treinamentos
from django_q.models import Task
from django.http import JsonResponse
from .models import Pergunta, DataTreinamento
from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path
from langchain_openai import ChatOpenAI
from django.http import StreamingHttpResponse

def treinar_ia(request):
    if not has_permission(request.user, 'treinar_ia'):
        raise Http404()
    if request.method == 'GET':
        tasks = Task.objects.all()
        return render(request, 'treinar_ia.html', {'tasks': tasks})
    elif request.method == 'POST':
        site = request.POST.get('site')
        conteudo = request.POST.get('conteudo')
        documento = request.FILES.get('documento')

        treinamento = Treinamentos(
            site=site,
            conteudo=conteudo,
            documento=documento
        )
        treinamento.save()

        return redirect('treinar_ia')


@csrf_exempt
def chat(request):
    if request.method == 'GET':
        return render(request, 'chat.html')
    elif request.method == 'POST':
        pergunta_user = request.POST.get('pergunta')

        pergunta = Pergunta(
            pergunta=pergunta_user
        )
        pergunta.save()

        return JsonResponse({'id': pergunta.id})
    
@csrf_exempt
def stream_response(request):
    id_pergunta = request.POST.get('id_pergunta')
    
    try:
        pergunta = Pergunta.objects.get(id=id_pergunta)
    except Pergunta.DoesNotExist:
        return JsonResponse({'error': 'Pergunta não encontrada'}, status=404)
    
    def stream_generator():
        try:
            embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            
            # Verificar se o banco FAISS existe
            if not Path("banco_faiss").exists():
                yield "Erro: Banco de conhecimento não encontrado. Por favor, treine a IA primeiro."
                return
            
            vectordb = FAISS.load_local("banco_faiss", embeddings, allow_dangerous_deserialization=True)

            docs = vectordb.similarity_search(pergunta.pergunta, k=5)
            
            if not docs:
                yield "Desculpe, não encontrei informações relevantes para sua pergunta."
                return
                
            for doc in docs:
                dt = DataTreinamento.objects.create(
                    metadata=doc.metadata,
                    texto=doc.page_content
                )
                pergunta.data_treinamento.add(dt)

            contexto = "\n\n".join([
                f"Material: {Path(doc.metadata.get('source', 'Desconhecido')).name}\n{doc.page_content}"
                for doc in docs
            ])

            messages = [
                {"role": "system", "content": f"Você é um assistente virtual e deve responder com precissão as perguntas sobre uma empresa.\n\n{contexto}"},
                {"role": "user", "content": pergunta.pergunta}
            ]

            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                streaming=True,
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY
            )

            for chunk in llm.stream(messages):
                token = chunk.content
                if token:
                    yield token
                    
        except Exception as e:
            yield f"Erro interno: {str(e)}"

    return StreamingHttpResponse(stream_generator(), content_type='text/plain; charset=utf-8')

def ver_fontes(request, id):
    pergunta = Pergunta.objects.get(id=id)
    for i in pergunta.data_treinamento.all():
        print(i.metadata)
        print(i.texto)
        print('---')
    print(pergunta.pergunta)

    return render(request, 'ver_fontes.html', {'pergunta': pergunta})