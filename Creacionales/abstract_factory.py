from abc import ABC, abstractmethod


class ClimateDevice(ABC):
    def __init__(self):
        self.temperature_grades = 0

    @abstractmethod
    def regulate_temperature(self, grades:int):
        pass

class SolarClimateDevice(ClimateDevice):
    def regulate_temperature(self, grades:int):
        print(f'Asignando temperatura de {grades} grados desde Energia Solar')
        self.temperature_grades = grades

class ElectricClimateDevice(ClimateDevice):
    def regulate_temperature(self, grades:int):
        print(f'Asignando temperatura de {grades} grados desde Energia Electrica')
        self.temperature_grades = grades

class HybridClimateDevice(ClimateDevice):
    def regulate_temperature(self, grades:int):
        print(f'Asignando temperatura de {grades} grados desde Energia Hibrida')
        self.temperature_grades = grades


class LightDevice(ABC):
    def __init__(self):
        self._is_turn_on = False

    @abstractmethod
    def turn_on(self):
        result = not self._is_turn_on
        print(f'{"Encendiendo" if result else "Apagando"} Ilumicación')
        self._is_turn_on = not self._is_turn_on

class SolarLightDevice(LightDevice):
    def turn_on(self):
        result = not self._is_turn_on
        print(f'{"Encendiendo" if result else "Apagando"} Ilumicación desde Energia Solar')
        self._is_turn_on = not self._is_turn_on

class ElectricLightDevice(LightDevice):
    def turn_on(self):
        result = not self._is_turn_on
        print(f'{"Encendiendo" if result else "Apagando"} Ilumicación desde Energia Electrica')
        self._is_turn_on = not self._is_turn_on

class HybridLightDevice(LightDevice):
    def turn_on(self):
        result = not self._is_turn_on
        print(f'{"Encendiendo" if result else "Apagando"} Ilumicación desde Energia Hibrida')
        self._is_turn_on = not self._is_turn_on


class DeviceFactory(ABC):

    @abstractmethod
    def create_climate_device(self):
        pass

    @abstractmethod
    def create_light_device(self):
        pass

class SolarDeviceFactory(DeviceFactory):
    def create_climate_device(self):
        return SolarClimateDevice()

    def create_light_device(self):
        return SolarLightDevice()

class ElectricDeviceFactory(DeviceFactory):
    def create_climate_device(self):
        return ElectricClimateDevice()

    def create_light_device(self):
        return ElectricLightDevice()

class HybridDeviceFactory(DeviceFactory):
    def create_climate_device(self):
        return HybridClimateDevice()

    def create_light_device(self):
        return HybridLightDevice()


if __name__ == '__main__':
    factory = SolarDeviceFactory()
    climate = factory.create_climate_device()
    light = factory.create_light_device()

    climate.regulate_temperature(10)
    light.turn_on()
