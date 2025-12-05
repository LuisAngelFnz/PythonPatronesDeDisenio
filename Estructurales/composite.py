from abc import ABC, abstractmethod
from typing import List, Callable
import random

class TaskComponent(ABC):

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def show(self, indent=0) -> None:
        pass

class SimpleTask(TaskComponent):

    def __init__(self, name, runtime):
        self.name = name
        self.runtime = runtime

    def execute(self) -> None:
        print('Ejecutando tarea simple: {}'.format(self.name))

    def show(self, indent=0) -> None:
        print(' '*indent + f"- {self.name} (simple, {self.runtime} ms)")

class CompositeTask(TaskComponent):
    def __init__(self, name):
        self.name = name
        self.children: List[TaskComponent] = []

    def add(self, child:TaskComponent) -> None:
        self.children.append(child)

    def execute(self) -> None:
        print(f"Iniciando tarea compuesta: {self.name}")
        for echild in self.children:
            echild.execute()
        print(f"Finalizando tarea compuesta: {self.name}")

    def show(self, indent=0) -> None:
        print(' '*indent+f'Tarea: {self.name}')
        for echild in self.children:
            echild.show(indent=indent+4)

class ParallelTask(TaskComponent):

    def __init__(self, name:str):
        self.name = name
        self.tasks: List[TaskComponent] = []

    def add(self, child:TaskComponent):
        self.tasks.append(child)
        return self

    def execute(self) -> None:
        print(f"Ejecutando tareas en paralelo: {self.name}")
        for etask in self.tasks:
            print(f" → [Paralelo] Iniciando {etask.name}")

        for etask in self.tasks:
            etask.execute()

    def show(self, indent=0) -> None:
        print(' '*indent+f'Tarea: {self.name}')
        for etask in self.tasks:
            etask.show(indent=indent+4)

class ConditionalTask(TaskComponent):

    def __init__(self, name:str, conditional_call:Callable):
        self.name = name
        self.conditional_call = conditional_call
        self.true_tasks: list[TaskComponent] = []
        self.false_tasks: list[TaskComponent] = []

    def add_true_task(self, task:SimpleTask):
        self.true_tasks.append(task)
        return self

    def add_false_task(self, task:SimpleTask):
        self.false_tasks.append(task)
        return self

    def execute(self) -> None:
        print(f'Evaluando condición: {self.name}')
        tasks = self.true_tasks if self.conditional_call() else self.false_tasks
        for etask in tasks:
            etask.execute()

    def show(self, indent=0) -> None:
        print(' '*indent + f'Tarea Condicional: {self.name}')
        tasks = self.true_tasks if self.conditional_call() else self.false_tasks
        for etask in tasks:
            print(' '*(indent+4) + f'- {etask.name}')


if __name__ == '__main__':

    data_center = CompositeTask('Automatización del Data Center')
    data_center.add(SimpleTask('Verificar conexión', 9))

    
    ## -----
    def temperatura_up():
        temp = random.randint(20, 40)
        return temp > 30

    conditional = ConditionalTask('Si temperatura > 30', temperatura_up)
    data_center.add(conditional)
    conditional.add_true_task(SimpleTask('Activa enfriamiento', 6))
    conditional.add_false_task(SimpleTask('Registrar temperatura', 2))


    ## -----
    parallel = ParallelTask('Procesos criticos')
    data_center.add(parallel)
    parallel.add(SimpleTask('Respaldar BD', 3)).add(SimpleTask('Respaldar logs', 3))

    ## -----
    deploy = CompositeTask('Deploy de servicios')
    data_center.add(deploy)
    deploy.add(SimpleTask('Detener servicios', 2))
    deploy.add(SimpleTask('Actualiza binarios', 4))

    post_deploy = CompositeTask('Validaciones post-deploy')
    deploy.add(post_deploy)
    post_deploy.add(SimpleTask('Checar Cpu', 1))
    post_deploy.add(SimpleTask('Checar memoria', 5))

    #---

    print('---SHOW---')
    data_center.show()
    print('---EXECUTE---')
    data_center.execute()



