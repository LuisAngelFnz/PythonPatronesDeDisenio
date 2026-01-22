from __future__ import annotations
from abc import ABC, abstractmethod


class Command(ABC):

    def __init__(self, receiver, *args, **kwargs):
        self.receiver = receiver
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class CreateReportCommand(Command):


    def execute(self):
        return self.receiver.generate(*self.args, **self.kwargs)

    def undo(self):
        return self.receiver.delete(*self.args, **self.kwargs)

class SendNotificationCommand(Command):

    def execute(self):
        self.receiver.send(*self.args, **self.kwargs)

    def undo(self):
        return self.receiver.drop(*self.args, **self.kwargs)

class BackupDataCommand(Command):

    def execute(self):
        self.receiver.backup(*self.args, **self.kwargs)

    def undo(self):
        return self.receiver.stop(*self.args, **self.kwargs)

class RollbackOperationCommand(Command):

    def execute(self):
        self.receiver.rollback(*self.args, **self.kwargs)

    def undo(self):
        return self.receiver.stop(*self.args, **self.kwargs)

class CreateReportReceiver:

    def generate(self, report_type:int):
        if report_type == 5:
            raise ValueError(f'Ha ocurrido un error al regenrar el reporte: {report_type}')

        print(f'Creando reporte de tipo: {report_type}')

    def delete(self, report_type:int):
        print(f'Intentando borrar reporte: {report_type}')

class SendNotificationReceiver:

    def send(self, notify_data:dict):
        print(f'Simulación de envio de notificación: {notify_data}')

    def drop(self, notify_data:int):
        print(f'Intentando borrar notificación del cliente: {notify_data}')

class BackupDataReceiver:

    def backup(self, data_name:str):
        print(f'Haciendo respaldo de: {data_name}')

    def stop(self, data_name:int):
        print(f'Intentando parar ejecución backup: {data_name}')

class RollbackOperationReceiver:

    def rollback(self, roll_type:int):
        print(f'Regresando a versión anterior: {roll_type}')

    def stop(self, roll_type:int):
        print(f'Intentando parar ejecución del rollback: {roll_type}')

class JobRunner:

    def __init__(self):
        self.jobs = []
        self.history = []

    def add(self, job:Command):
        self.jobs.append(job)

    def run(self):

        for ejob in self.jobs:
            try:

                ejob.execute()
                self.history.append(ejob.__class__.__name__)
            except:
                print(f'Error al ejecutar job: {ejob.__class__.__name__} intentando revertir')
                ejob.undo()


if __name__ == '__main__':
    job_runner = JobRunner()
    job_runner.add(
        CreateReportCommand(CreateReportReceiver(), report_type=22)
    )
    job_runner.add(
        SendNotificationCommand(SendNotificationReceiver(), notify_data={'id':22})
    )
    job_runner.add(
        BackupDataCommand(BackupDataReceiver(), data_name='operations')
    )
    job_runner.add(
        RollbackOperationCommand(RollbackOperationReceiver(), roll_type=55)
    )
    job_runner.run()
    print(f'Jobs ejecutados: {job_runner.history}')
    ####
    job_runner = JobRunner()
    job_runner.add(
        CreateReportCommand(CreateReportReceiver(), report_type=5)
    )
    job_runner.add(
        SendNotificationCommand(SendNotificationReceiver(), notify_data={'id':22})
    )
    job_runner.add(
        BackupDataCommand(BackupDataReceiver(), data_name='operations')
    )
    job_runner.run()
    print(f'Jobs ejecutados: {job_runner.history}')