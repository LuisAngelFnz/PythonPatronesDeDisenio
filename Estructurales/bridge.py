from abc import abstractmethod, ABC

class Transmitter(ABC):

    @abstractmethod
    def send(self, data:dict):
        pass

class WifiTransmitter(Transmitter):

    def send(self, data:dict) -> None:
        print(f'Enviando datos: {data} con WifiTransmitter')

class SatelliteTransmitter(Transmitter):

    def send(self, data:dict) -> None:
        print(f'Enviando datos: {data} con SatelliteTransmitter')

class FiberTransmitter(Transmitter):

    def send(self, data:dict) -> None:
        print(f'Enviando datos: {data} con FiberTransmitter')

class Camera(ABC):

    def __init__(self, transmitter:Transmitter):
        self.__transmitter = transmitter

    @abstractmethod
    def analyze_frame(self, frame_id:int):
        pass

    def stream(self, frame_id:int):
        self.__transmitter.send(self.analyze_frame(frame_id))


class BasicCamera(Camera):

    def analyze_frame(self, frame_id:int) -> dict:
        print(f'BasicCamera analizando frame: {frame_id} convirtiendo a octal...')
        return {'frames':oct(frame_id)}

class FaceRecognitionCamera(Camera):

    def analyze_frame(self, frame_id:int) -> dict:
        print(f'FaceRecognitionCamera analizando frame: {frame_id} convirtiendo a hexadecimal...')
        return {'frames':hex(frame_id)}

class ThermalCamera(Camera):

    def analyze_frame(self, frame_id:int) -> dict:
        print(f'ThermalCamera analizando frame: {frame_id} convirtiendo a str...')
        return {'frames':str(frame_id)}


if __name__ == '__main__':
    basic_camera_with_fiber_transmission = BasicCamera(FiberTransmitter())
    basic_camera_with_fiber_transmission.stream(20)


    thermal_camera_with_satellite_transmiter = ThermalCamera(SatelliteTransmitter())
    thermal_camera_with_satellite_transmiter.stream(30)

    face_camera_with_wifi_transmiter = FaceRecognitionCamera(WifiTransmitter())
    face_camera_with_wifi_transmiter.stream(50)