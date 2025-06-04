from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Treinamentos

@receiver(post_save, sender=Treinamentos)
def signals_treinamento_ia(sender, instance, created, **kwargs):
    # TODO: Tarefa 2 - Desenvolver o signals
    print("Desenvolver signals")
    ...

def task_treinar_ia(instance_id):
    # TODO: Tarefa 3 - Desenvolver o treinamento da IA
    ...