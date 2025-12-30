import time
import random

from abc import abstractmethod, ABC

class Request:
    def __init__(self, user_role:str, amount:float, region:str, is_authenticated:bool=False, priority:str='LOW', metadata:dict=None):
        self.user_role, self.amount  = user_role, amount
        self.region, self.is_authenticated = region, is_authenticated
        self.priority, self.metadata = priority, metadata or {}
        self.skip_handlers = []
        self.history_handle = []

class CoRHandler(ABC):
    def __init__(self, next_handler=None, name_handle=None):
        self.next_handler = next_handler
        self.name_handle = name_handle or self.__class__.__name__

    def handle(self, req:Request):

        if self.name_handle in req.skip_handlers:
            req.history_handle.append(self.name_handle+'(SKIP)')
            return self._next(req)

        result = self._process(req)
        req.history_handle.append(self.name_handle+'(EXECUTE)')
        if result is not None:
            return result

        return self._next(req)

    @abstractmethod
    def _process(self, req:Request):
        raise NotImplementedError('Método no implementado')

    def _next(self, req:Request):
        if self.next_handler:
            return self.next_handler.handle(req)


USER_ROLES = {
    'soporte1':(0, 3000),
    'soporte2':(0, 5000),
    'enginer' :(5000, 10000)
}

class AuthenticationHandler(CoRHandler):
    def _process(self, req:Request):
        if not req.is_authenticated:
            return 'Usuario no Logeado'

class AuthorizationHandler(CoRHandler):
    def _process(self, req:Request):
        if req.user_role not in USER_ROLES:
            return 'Usuario no autorizado para realizar esta operación'

class RegionComplianceHandler(CoRHandler):
    def _process(self, req:Request):
        if req.region not in ('EU','ES','LATAM'):
            return 'Region invalida para realizar esta operación'

class AmountLimitHandler(CoRHandler):

    def _process(self, req:Request):
        min_amount, max_amount = USER_ROLES.get(req.user_role, (0, 2999))
        if not min_amount <= req.amount <= max_amount:
            return f'El role: {req.user_role} solo tiene permitidos montos de {min_amount} a {max_amount}'

class PriorityHandler(CoRHandler):
    def _process(self, req:Request):
        if req.priority == 'HIGH' and 'RegionComplianceHandler' not in req.skip_handlers:
            req.skip_handlers.append('RegionComplianceHandler')

class FinalExecutionHandler(CoRHandler):
    def _process(self, req:Request):
        print(f'Procesando reembolso por el monto de {req.amount}')
        time.sleep(random.choice([1,2,3]))
        return 'Reembolso realizado con éxito'


def code_client(req:Request):
    last_time = time.time()
    req.history_handle = []
    result = PriorityHandler(
        AuthenticationHandler(
            AuthorizationHandler(
                RegionComplianceHandler(
                    AmountLimitHandler(
                        FinalExecutionHandler()
                    )
                )
            )
        )
    ).handle(req)
    runtime = time.time() - last_time
    print(f'Tiempo de ejecución: {runtime:.4f}s Handlers ejecutados: {", ".join(req.history_handle)}\n resultado: {result}')


if __name__ == '__main__':
    ##Role monto no pasa
    req = Request(
        user_role='soporte1',
        amount=5000,
        region='LATAM',
        is_authenticated=True,
        priority='HIGH',
        metadata={'datos':'llave de dataos'}
    )
    code_client(req)
    #Tiempo de ejecución: 0.0000s Handlers ejecutados: AuthorizationHandler, AuthenticationHandler, PriorityHandler
    #resultado: El rool: soporte1 solo tiene permitidos montos de 0 a 3000

    req.user_role = 'enginer'
    code_client(req)
    # Tiempo de ejecución: 1.0002s Handlers ejecutados: AuthorizationHandler, AuthenticationHandler, PriorityHandler, AmountLimitHandler, AuthorizationHandler, AuthenticationHandler, PriorityHandler
    #  resultado: Reembolso realizado con éxito

