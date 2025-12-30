from __future__ import annotations
from abc import ABC, abstractmethod
import random
import time

class Context:

    def __init__(self, state:State):
        self.switch_state(state)

    def switch_state(self, state:State):
        self.__state = state
        self.__state.context = self

    def deposit(self, *args, **kwargs):
        return self.__state.deposit(*args, **kwargs)

    def withdraw(self, *args, **kwargs):
        return self.__state.withdraw(*args, **kwargs)

    def close(self, *args, **kwargs):
        return self.__state.close(*args, **kwargs)

class State(ABC):

    @property
    def context(self) -> Context:
        return self.__context

    @context.setter
    def context(self, new_context:Context) -> None:
        self.__context = new_context

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    def close(self):
        print(f'Cerrando sessión desde el estado: {self.__class__.__name__}...')
        self.context.switch_state(ClosedState())
        return f'Sessión cerrada desde {self.__class__.__name__}'

class ActiveState(State):
    fronzen_limit = 10000
    withdraw_limit = 5000
    def deposit(self, amount:float) -> str:
        print('Realizando deposito desde ActiveState...')
        time.sleep(random.choice([1,2,3]))
        return f'Deposito generado del monto: {amount} con éxito desde: ActiveState'

    def withdraw(self, amount:float):
        print('Realizando retiro desde ActiveState...')
        if amount >= self.fronzen_limit:
            print('Congelando cuenta')
            self.context.switch_state(FrozenState())
            return (
                'Por motivos de seguridad se ha congelado su cuenta ya que'
                f' el limite de retiro es {self.fronzen_limit} y usted esta retirando: {amount}'
            )
        if amount >= self.withdraw_limit:
            print('Sobre girando cuenta...')
            self.context.switch_state(OverdrawnState())
            return (
                f'La cuenta ha sido sobre girada su monto es: {amount} y el limite es: {self.withdraw_limit}'
            )
        time.sleep(random.choice([1,2,3]))
        return f'Retiro generado del monto : {amount} con éxito desde: ActiveState'

class FrozenState(State):

    def deposit(self, amount:float) -> str:
        print('Realizando deposito desde FrozenState...')
        time.sleep(random.choice([1,2,3]))
        return f'Deposito generado del monto: {amount} con éxito desde: FrozenState'

    def withdraw(self, amount:float):
        print('Rechazando retiro desde FrozenState...')
        return f'No se puede realizar el retiro por el monto de: {amount} desde el estado FrozenState'

class OverdrawnState(State):

    def deposit(self, amount:float) -> str:
        print('Realizando deposito desde OverdrawnState...')
        time.sleep(random.choice([1,2,3]))
        self.context.switch_state(ActiveState())
        return f'Deposito generado del monto: {amount} con éxito desde: OverdrawnState'

    def withdraw(self, amount:float):
        print('Rechazando retiro desde OverdrawnState...')
        return f'No se puede realizar el retiro por el monto de: {amount} desde el estado OverdrawnState'

class ClosedState(State):
    def deposit(self, amount:float):
        return 'Imposible realizar depositos en estado ClosedState'

    def withdraw(self, amount:float):
        return 'Imposible realizar retiros en estado ClosedState'

    def close(self):
        return 'Imposible cerrar sessión desde el estado ClosedState'

if __name__ == '__main__':
    context = Context(ActiveState())
    print(context.withdraw(10000))
    print(context.withdraw(100))

    context = Context(ActiveState())
    print(context.withdraw(5001))
    print(context.withdraw(100))
    print(context.deposit(100))
    print(context.withdraw(100))
