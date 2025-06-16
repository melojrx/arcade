# 🤖 Sistema RAG (Retrieval-Augmented Generation) com Django

## 📋 Visão Geral

Este projeto implementa um sistema completo de **RAG (Retrieval-Augmented Generation)** utilizando Django como framework principal. O sistema permite treinar uma IA com documentos e sites, criando um assistente virtual inteligente capaz de responder perguntas baseadas no conhecimento adquirido. 

## 🎯 Funcionalidades Principais

### 🧠 Sistema de Treinamento de IA
- **Upload de documentos PDF**: Processa e indexa arquivos PDF automaticamente
- **Scraping de websites**: Extrai conteúdo de URLs fornecidas
- **Conteúdo manual**: Permite inserção direta de texto para treinamento
- **Processamento assíncrono**: Utiliza Django-Q para processamento em background

### 💬 Interface de Chat
- **Chat em tempo real**: Interface web para interação com a IA
- **Streaming de respostas**: Respostas são enviadas em tempo real utilizando Server-Sent Events
- **Histórico de conversas**: Armazena perguntas e fontes utilizadas para cada resposta
- **Visualização de fontes**: Mostra os documentos utilizados para gerar cada resposta



### 👥 Sistema de Permissões
- **Controle de acesso**: Sistema de roles e permissões para diferentes usuários
- **Permissão de treinamento**: Controla quem pode treinar a IA

## 🛠 Tecnologias Utilizadas

### Backend & Framework
- **Django 5.2.1**: Framework web principal
- **Python**: Linguagem de programação
- **SQLite**: Banco de dados para persistência
- **Django-Q**: Sistema de filas para processamento assíncrono

### Inteligência Artificial & NLP
- **LangChain 0.3.25**: Framework para desenvolvimento de aplicações com LLMs
- **OpenAI GPT-3.5-turbo**: Modelo de linguagem para geração de respostas
- **OpenAI Embeddings**: Para geração de embeddings dos documentos
- **FAISS**: Banco de dados vetorial para busca por similaridade

### Processamento de Documentos
- **PyPDF 5.5.0**: Extração de texto de arquivos PDF
- **BeautifulSoup4**: Parsing e extração de conteúdo HTML
- **Requests**: Para fazer requisições HTTP aos websites

### Integração Externa

- **APScheduler**: Agendamento de tarefas

## 📊 Fluxo do Processo RAG

### 1. 📥 Ingestão de Dados
```
Documento/Site → Extração de Conteúdo → Chunking → Embeddings → FAISS Index
```

**Detalhamento:**
- **Extração**: PDFs são processados com PyPDFLoader, sites com BeautifulSoup
- **Chunking**: Textos são divididos em chunks de 500 caracteres com overlap de 100
- **Embeddings**: Cada chunk é convertido em vetor usando OpenAI Embeddings
- **Indexação**: Vetores são armazenados no banco FAISS para busca rápida

### 2. 🔍 Recuperação de Informações
```
Pergunta → Embedding → Busca por Similaridade → Top-K Documentos Relevantes
```

**Detalhamento:**
- A pergunta do usuário é convertida em embedding
- FAISS realiza busca por similaridade coseno
- Retorna os 5 documentos mais relevantes (k=5)

### 3. 🤖 Geração de Resposta
```
Contexto + Pergunta → Prompt Engineering → GPT-3.5 → Resposta Contextualizada
```

**Detalhamento:**
- Documentos relevantes são combinados em contexto
- Prompt system define o comportamento da IA
- GPT-3.5-turbo gera resposta baseada no contexto
- Streaming permite respostas em tempo real

### 4. 💾 Persistência e Rastreamento
```
Pergunta + Fontes Utilizadas → Banco de Dados → Histórico Completo
```

## 🏗 Arquitetura do Sistema

### Estrutura de Diretórios
```
base-arcane/
├── core/                    # Configurações Django
│   ├── settings.py         # Configurações principais
│   ├── urls.py            # URLs principais
│   └── roles.py           # Sistema de permissões
├── oraculo/                # App principal RAG
│   ├── models.py          # Modelos de dados
│   ├── views.py           # Lógica de negócio
│   ├── signals.py         # Processamento automático
│   ├── utils.py           # Funções utilitárias
│   └── management/        # Comandos Django
├── usuarios/              # Sistema de usuários
├── templates/             # Interface web
├── banco_faiss/           # Banco vetorial FAISS
├── media/                 # Arquivos uploadados
└── requirements.txt       # Dependências
```

### Modelos de Dados

#### Treinamentos
```python
class Treinamentos(models.Model):
    site = models.URLField()           # URL para scraping
    conteudo = models.TextField()      # Conteúdo manual
    documento = models.FileField()     # Upload de arquivos
```

#### DataTreinamento
```python
class DataTreinamento(models.Model):
    metadata = models.JSONField()      # Metadados do documento
    texto = models.TextField()         # Conteúdo do chunk
```

#### Pergunta
```python
class Pergunta(models.Model):
    data_treinamento = models.ManyToManyField(DataTreinamento)
    pergunta = models.TextField()      # Pergunta do usuário
```

## 🚀 Configuração e Instalação

### Pré-requisitos
- Python 3.8+
- Conta OpenAI com API Key

### 1. Clonagem e Ambiente Virtual
```bash
git clone <seu-repositorio>
cd base-arcane
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Instalação de Dependências
```bash
pip install -r requirements.txt
```

### 3. Configuração de Variáveis de Ambiente
Crie um arquivo `.env`:
```env
OPENAI_API_KEY=sua_chave_openai_aqui
SECRET_KEY=sua_secret_key_django
DEBUG=True
```

### 4. Configuração do Banco de Dados
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Inicialização do FAISS
```bash
python manage.py inicializar_faiss
```

### 6. Execução do Sistema
```bash
# Terminal 1 - Servidor Django
python manage.py runserver

# Terminal 2 - Worker Django-Q (tarefas assíncronas)
python manage.py qcluster
```

## 📚 Guia de Uso

### Treinamento da IA

1. **Acesse o painel administrativo**:
   ```
   http://localhost:8000/treinar-ia/
   ```

2. **Adicione conteúdo**:
   - **Site**: Insira URL completa (https://exemplo.com)
   - **Conteúdo**: Cole texto diretamente
   - **Documento**: Faça upload de PDF

3. **Processamento automático**:
   - O sistema processa automaticamente via Django-Q
   - Documentos são indexados no FAISS
   - Status pode ser acompanhado na interface

### Testando o Chat

1. **Acesse a interface de chat**:
   ```
   http://localhost:8000/chat/
   ```

2. **Faça perguntas**:
   - Digite sua pergunta
   - Receba resposta em tempo real
   - Veja as fontes utilizadas

## 🔄 Comandos Django Customizados

### Inicializar FAISS
```bash
python manage.py inicializar_faiss
```
Cria um banco FAISS vazio se não existir.

### Reprocessar Treinamentos
```bash
python manage.py reprocessar_treinamentos
```
Reprocessa todos os treinamentos existentes.

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro "Banco de conhecimento não encontrado"
```bash
python manage.py inicializar_faiss
```

#### 2. Erro de API Key OpenAI
- Verifique se `OPENAI_API_KEY` está configurada no `.env`
- Confirme que a chave é válida e tem créditos

#### 3. Django-Q não processa tarefas
```bash
# Execute em terminal separado
python manage.py qcluster
```



## 🔧 Personalização

### Modificando o Modelo de IA
Em `oraculo/views.py` e `oraculo/utils.py`:
```python
llm = ChatOpenAI(
    model_name="gpt-4",  # Altere para gpt-4 ou outro modelo
    temperature=0.1,     # Ajuste a criatividade
    max_tokens=500       # Limite de tokens na resposta
)
```

### Ajustando Parâmetros do RAG
Em `oraculo/signals.py`:
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # Tamanho dos chunks
    chunk_overlap=200   # Sobreposição entre chunks
)
```

Em `oraculo/views.py`:
```python
docs = vectordb.similarity_search(pergunta.pergunta, k=10)  # Mais documentos
```

### Customizando Prompts
Em `oraculo/views.py` e `oraculo/utils.py`:
```python
{"role": "system", "content": f"Você é um especialista em [SUA_ÁREA] e deve...\n\n{contexto}"}
```

## 📈 Monitoramento e Logs

### Logs do Django-Q
```bash
# Ver tarefas executadas
python manage.py shell
>>> from django_q.models import Task
>>> Task.objects.all()
```



## 🔐 Segurança

### Pontos de Atenção
- **API Keys**: Mantenha sempre em variáveis de ambiente
- **FAISS**: `allow_dangerous_deserialization=True` apenas em ambiente controlado
- **Rate Limiting**: Considere implementar para evitar spam

### Melhorias Recomendadas
- Implementar autenticação JWT para APIs
- Adicionar rate limiting nas rotas
- Criptografar dados sensíveis
- Implementar logs de auditoria

## 🚀 Deployment

### Ambiente de Produção
1. **Configure variáveis de ambiente**:
   ```env
   DEBUG=False
   ALLOWED_HOSTS=seu-dominio.com
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   ```

2. **Use PostgreSQL**:
   ```python
   DATABASES = {
       'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
   }
   ```

3. **Configure Redis para cache**:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': os.environ.get('REDIS_URL'),
       }
   }
   ```

## 🤝 Contribuindo

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Padrões de Código
- Siga PEP 8 para Python
- Documente funções complexas
- Adicione testes para novas funcionalidades
- Mantenha o README atualizado

## 📊 Estrutura de Dados do FAISS

### Formato dos Embeddings
```python
# Cada documento é convertido em:
{
    "text": "conteúdo do chunk",
    "metadata": {
        "source": "arquivo.pdf",
        "page": 1,
        "chunk_id": "uuid"
    },
    "embedding": [0.1, 0.2, ...] # Vetor 1536 dimensões
}
```

### Otimização de Performance
- **Chunk Size**: 500 caracteres (otimizado para contexto)
- **Overlap**: 100 caracteres (mantém contexto entre chunks)
- **Top-K**: 5 documentos (balance entre relevância e contexto)

## 🔍 Algoritmo de Similaridade

### Busca Vetorial
1. **Query Embedding**: Pergunta → Vetor 1536D
2. **Similarity Search**: Cosine Similarity no FAISS
3. **Ranking**: Top-K por score de similaridade
4. **Context Building**: Concatenação dos chunks relevantes

### Métricas de Performance
- **Latência de busca**: ~50ms para 10k documentos
- **Precisão**: Dependente da qualidade dos embeddings
- **Recall**: Melhorado com overlap entre chunks

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção Troubleshooting
2. Consulte a documentação das dependências
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando Django, LangChain e OpenAI**