import random
import time

from abc import ABC, abstractmethod
from unittest import TestCase

class RateLimitError(Exception):
    pass

class Service(ABC):

    @abstractmethod
    def generate(self, *args, **kwargs):
        pass

class PaymentService(Service):

    def generate(self, user:str, amount:float):
        print('Generando pago...')
        time.sleep(random.uniform(0.5, 1.5))
        result = bool(random.randint(0,1))
        if result:
            return result, f'Pago para {user} con el monto {amount} procesado éxitosamente'
        return result, 'El pago no pudo ser procesado'

class ReportService(Service):

    def generate(self, report_id:int):
        print(f'Generando reporte {report_id}...')
        time.sleep(random.uniform(1.0, 2.0))
        result = report_id < 5
        if result:
            return 'Reporte generado éxitosamente'
        return 'El reporte no pudo ser generado correctamente'

class ImageService(Service):

    def generate(self, image:bytes):
        print('Procesando imagen...')
        time.sleep(random.uniform(2.0, 3.0))
        result = bool(random.randint(0,1))
        if result:
            return 'Imagen procesado correctamente'
        return 'La imagen se encuentra corrupta o dañana, no pudo ser procesada'

###

class LoggingProxy(Service):

    def __init__(self, service:Service):
        self._real_service = service
        self.logs = []

    def generate(self, *args, **kwargs):
        self.logs.append(
            f'time: {time.strftime("%Y-%m-%dT%H:%M:%S")} \
            service: {self._real_service.__class__.__name__} \
            args: {args} \
            kwargs: {kwargs}'
        )
        return self._real_service.generate(*args, **kwargs)

    # def drop_and_wirte_logs(self):
    #     while self.logs:
    #         print(self.logs.pop(0))

class CachingProxy(Service):

    def __init__(self, service:Service):
        self._real_service, self.__cache = service, {}
        self.real_call_count = self.cache_hits = 0

    def generate(self, *args, **kwargs):
        cache_args = tuple(list(args) + list(kwargs.values()))
        if cache_args in self.__cache:
            self.cache_hits += 1
        else:
            print(
                f'Service: {self._real_service.__class__.__name__} args: {cache_args} saving in cache...'
            )
            self.__cache[cache_args] = self._real_service.generate(*args, **kwargs)
            self.real_call_count += 1
        return self.__cache[cache_args]

class LazyLoadingProxy(Service):
    def __init__(self, service_cls:type[Service]):
        self._service_cls = service_cls
        self._real_service = None

    def generate(self, *args, **kwargs):
        if self._real_service is None:
            print(f'Generando por unica vez instancia de {self._service_cls.__name__}')
            self._real_service = self._service_cls()
        return self._real_service.generate(*args, **kwargs)

class RateLimitProxy(Service):

    def __init__(self, service:Service, **kwargs):
        self._real_service  = service
        self._call_limit    = kwargs.pop('call_limit', 4)
        self._seconds_limit = kwargs.pop('seconds_limit', 60)
        self._timer, self._counter,  = None, 0

    def generate(self, *args, **kwargs):
        if self._timer is None:
            self._timer = time.time()

        if (time.time() - self._timer) >= self._seconds_limit:
            self._timer, self._counter = time.time(), 0

        if self._counter >= self._call_limit:
            raise RateLimitError(
                f'Maximo nro. de llamadas({self._call_limit}) permitidas en {self._seconds_limit} segundos'
            )

        self._counter += 1

        return self._real_service.generate(*args, **kwargs)

class AccessControlProxy(Service):
    def __init__(self, service:Service, service_cls:type[Service], **kwargs):
        self._real_service = service
        self._service_cls = service_cls
        self.user_role = kwargs.pop('user_role')
        acl_map = {
            'admin'   : ReportService,
            'premium' : ImageService,
            'free'    : PaymentService,
        }

        self._allowed = self.user_role in acl_map and issubclass(acl_map[self.user_role], service_cls)

    def generate(self, *args, **kwargs):
        if not self._allowed:
            raise PermissionError(
                f'El perfil({self.user_role}) no tiene permitido usar el servicio {self._service_cls.__name__}'
            )

        return self._real_service.generate(*args, **kwargs)

class CircuitBreakerProxy(Service):

    def __init__(self, service:Service, max_failure_error:int=3):
        self._real_service = service
        self.state = 'CLOSED'
        self.failure_count = 0
        self.max_failure_error = max_failure_error
        self.last_failure_time = None
        self.failure_timeout = 10

    def generate(self, *args, **kwargs):
        if self.state == 'OPEN':
            if (time.time() - self.last_failure_time) > self.failure_timeout:
                self.state = 'HALF-OPEN'
            else:
                return 'El servicio no esta disponible por el momento intentelo más tarde'
        try:
            result = self._real_service.generate(*args, **kwargs)
            self.state = 'CLOSED'
        except Exception as error:
            self.failure_count += 1

            if self.failure_count >= self.max_failure_error:
                self.state = 'OPEN'
                self.last_failure_time = time.time()
            raise error

        return result

class GlobalServiceProxy(Service):

    def __init__(self, service_cls:type[Service], user_role:str):
        self._circuit = CircuitBreakerProxy(
            AccessControlProxy(
                LazyLoadingProxy(service_cls),
                service_cls=service_cls,
                user_role=user_role
            )
        )
        self._cache = CachingProxy(self.circuit)
        self._proxy_pipeline = LoggingProxy(RateLimitProxy(self._cache))

    def generate(self, *args, **kwargs):
        return self._proxy_pipeline.generate(*args, **kwargs)

    @property
    def cache(self):
        return self._cache

    @property
    def circuit(self):
        return self._circuit

def test_access_control_blocks01():
    proxy = GlobalServiceProxy(PaymentService, user_role="free")
    result = proxy.generate(user='juanito', amount=200)
    print(result)
    result = proxy.generate(user='banana', amount=150)
    print(result)

def test_access_control_blocks02():
    proxy = GlobalServiceProxy(ReportService, user_role="free")
    with TestCase().assertRaises(PermissionError):
        proxy.generate(report_id=1)

def test_cache_avoids_real_call():
    proxy = GlobalServiceProxy(PaymentService, user_role="free")

    r1 = proxy.generate(user="a", amount=100)
    r2 = proxy.generate(user="a", amount=100)

    assert r1 == r2
    ## No se como llegar a estos atributos ya que esta dentro las instancias del pipeline
    # Se podría con proxy._real_service._real_service._real_service pero no se si sea lo correcto
    assert proxy.cache.real_call_count == 1
    assert proxy.cache.cache_hits == 1

def test_rate_limit():
    proxy = GlobalServiceProxy(ImageService, user_role="premium")

    proxy.generate(image=b'muchos bytes')
    proxy.generate(image=b'muchos bytes')
    proxy.generate(image=b'muchos bytes')
    proxy.generate(image=b'muchos bytes')

    with TestCase().assertRaises(RateLimitError):
        proxy.generate(image=b'muchos bytes')

def test_circuit_breaker_opens():
    class FakeService(Service):
        def generate(self, *args, **kwargs):
            raise Exception("fail")

    proxy = GlobalServiceProxy(FakeService, user_role="admin")

    for attemp in range(3):
        with TestCase().assertRaises(PermissionError):
            proxy.generate(bytes(attemp))

    #De nuevo no se si esta bien así
    assert proxy.circuit.state == "OPEN"

def test_half_open_recovery():
    proxy = GlobalServiceProxy(ReportService, user_role="admin")
    for id_report in range(1,4):
        with TestCase().assertRaises(TypeError):
            proxy.generate(param_no_exists=id_report)

    assert proxy.circuit.state == "OPEN"

    time.sleep(proxy.circuit.failure_timeout)
    proxy.generate(report_id=6)
    assert proxy.circuit.state == "CLOSED"

def test_cache_does_not_trigger_breaker():
    proxy = GlobalServiceProxy(PaymentService, user_role="free")

    proxy.generate(user="a", amount=50)
    proxy.generate(user="a", amount=50)

    assert proxy.circuit.failure_count == 0
    assert proxy.circuit.state == "CLOSED"


if __name__ == '__main__':
    test_access_control_blocks01()
    test_access_control_blocks02()
    test_cache_avoids_real_call()
    test_rate_limit()
    test_circuit_breaker_opens()
    test_half_open_recovery()
    test_cache_does_not_trigger_breaker()