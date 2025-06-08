from django.core.management.base import BaseCommand
from oraculo.models import Treinamentos
from oraculo.signals import task_treinar_ia
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Reprocessa todos os treinamentos e recria o banco FAISS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa o banco FAISS antes de reprocessar',
        )

    def handle(self, *args, **options):
        # Limpar banco FAISS se solicitado
        if options['limpar']:
            banco_path = Path("banco_faiss")
            if banco_path.exists():
                shutil.rmtree(banco_path)
                self.stdout.write(
                    self.style.SUCCESS('Banco FAISS removido.')
                )
        
        # Buscar todos os treinamentos
        treinamentos = Treinamentos.objects.all()
        
        if not treinamentos:
            self.stdout.write(
                self.style.WARNING('Nenhum treinamento encontrado.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Reprocessando {treinamentos.count()} treinamentos...')
        )
        
        # Reprocessar cada treinamento
        for treinamento in treinamentos:
            try:
                self.stdout.write(f'Processando treinamento ID: {treinamento.id}')
                task_treinar_ia(treinamento.id)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Treinamento {treinamento.id} processado')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro no treinamento {treinamento.id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Reprocessamento concluído!')
        ) 