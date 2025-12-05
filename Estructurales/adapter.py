import struct

from xml.etree.ElementTree import fromstring
from abc import ABC, abstractmethod

class UnifiedTelemetry(ABC):

    @abstractmethod
    def get_temperature_c(self) -> float:
        pass

    @abstractmethod
    def get_pressure_kpa(self) -> float:
        pass

    @abstractmethod
    def get_location(self) -> dict:
        """Debe devolver: { 'lat': ..., 'lng': ... }"""
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """Debe devolver: {'system': 'OK'/'FAIL', 'battery': %}"""
        pass

class LegacyThermalUnitV1:

    def read_xml(self):
        return """
        <data>
            <temperature_f> 98.6 </temperature_f>
            <pressure_psi> 14.7 </pressure_psi>
            <latitude> 19.4326 </latitude>
            <longitude> -99.1332 </longitude>
            <status> OK </status>
            <battery> 87 </battery>
        </data>
        """

class IndustrialPacketReader:

    def get_packet(self) -> bytes:
        # Ejemplo realista:
        # Temp: 253 → 25.3°C (se guarda como 253 décimas)
        # Presión: 101325 Pa
        # Latitud: 19.4326
        # Longitud: -99.1332
        # Estado: OK (1)
        # Batería: 87%

        temperature_decic = 253                # int16
        pressure_pa = 101325                   # int32
        lat = 19.4326                          # float32
        lng = -99.1332                         # float32
        status = 1                             # OK
        battery = 87                           # %
        # IMPORTANTE:
        # struct.pack necesita el formato EXACTO
        # h = int16
        # f = float32
        # B = unsigned char (byte)
        #
        # Usaremos formato LITTLE-ENDIAN: <h h f f B B

        packet = struct.pack(
            "<hiffBB",
            temperature_decic,
            pressure_pa,
            lat,
            lng,
            status,
            battery
        )

        return packet

class CloudTelemetryJSON:

    def download(self) -> dict:
        return {
            "temp_kelvin": 298.15,
            "pressure_hectopascal": 1013,
            "coordinates": "19.5,-99.1",
            "flags": {
                "ok": True,
                "battery_level": 0.45
            }
        }

class SatelliteStreamingUnit:

    def stream(self):
        # Devuelve una tupla gigante:
        # (temp_c, (pressure_bar, extra1, extra2), { 'pos': [lat, lng] }, {'alive': True, 'bat': '87%'})
        return (24.5,
                (1.02, 'unused', None),
                {'pos': [18.9, -99.0]},
                {'alive': True, 'bat': '87%'})


class LegacyThermalV1Adapter(UnifiedTelemetry):
    def __init__(self, old_legacy_thermal:LegacyThermalUnitV1):
        self.old_legacy_thermal = old_legacy_thermal

    def read_xml_parse(self):
        return fromstring(self.old_legacy_thermal.read_xml())

    def get_temperature_c(self) -> float:
        xml = self.read_xml_parse()
        temperature_fahrenheit = float(xml.find('temperature_f').text.strip())
        temperature_celcius    = (temperature_fahrenheit - 32) * 5/9
        return round(temperature_celcius, 2)

    def get_pressure_kpa(self) -> float:
        xml = self.read_xml_parse()
        psi = float(xml.find('pressure_psi').text.strip())
        kpa = psi * 6.89476
        return round(kpa, 2)

    def get_location(self) -> dict:
        xml = self.read_xml_parse()
        return {
            'lat':float(xml.find('latitude').text.strip()),
            'lng':float(xml.find('longitude').text.strip())
        }

    def get_status(self) -> dict:
        xml = self.read_xml_parse()
        return {
            'system': xml.find('status').text.strip(),
            'battery': f'{xml.find("battery").text.strip()}%'
        }

class IndustrialPacketAdapter(UnifiedTelemetry):
    def __init__(self, industrial_packet: IndustrialPacketReader):
        self.industrial_packet = industrial_packet

    def unpack(self):
        return struct.unpack(
            "<hiffBB", self.industrial_packet.get_packet()
        )

    def get_temperature_c(self) -> float:
        temperature_decic = self.unpack()[0]
        return round(temperature_decic/10, 2)

    def get_pressure_kpa(self) -> float:
        pa = self.unpack()[1]
        kpa = pa / 1000
        return round(kpa, 2)

    def get_location(self) -> dict:
        unpack_bytes = self.unpack()
        return {
            'lat': unpack_bytes[2],
            'lng': unpack_bytes[3]
        }

    def get_status(self) -> dict:
        unpack_bytes = self.unpack()
        return {
            'system': 'OK' if unpack_bytes[4] else 'FAIL',
            'battery': f'{unpack_bytes[5]}%'
        }

class CloudTelemetryAdapter(UnifiedTelemetry):

    def __init__(self, old_json_telemetry:CloudTelemetryJSON):
        self.old_json_telemetry = old_json_telemetry

    def get_temperature_c(self) -> float:
        telemetry = self.old_json_telemetry.download()
        celcius = telemetry['temp_kelvin'] - 273.15
        return round(celcius, 2)


    def get_pressure_kpa(self) -> float:
        telemetry = self.old_json_telemetry.download()
        kpa = telemetry['pressure_hectopascal'] / 10
        return round(kpa, 2)

    def get_location(self) -> dict:
        telemetry = self.old_json_telemetry.download()
        lat, lng = telemetry['coordinates'].split(',')
        return {
            'lat': float(lat.strip()),
            'lng': float(lng.strip())
        }

    def get_status(self) -> dict:
        telemetry = self.old_json_telemetry.download()['flags']
        return {
            'system': 'OK' if telemetry['ok'] else 'FAIL',
            'battery': f'{int(telemetry["battery_level"] * 100)}%'
        }

class SatelliteTelemetryAdapter(UnifiedTelemetry):

    def __init__(self, old_stream_unit:SatelliteStreamingUnit):
        self.old_stream_unit = old_stream_unit

    def get_temperature_c(self) -> float:
        return self.old_stream_unit.stream()[0]

    def get_pressure_kpa(self) -> float:
        preasure_bar = self.old_stream_unit.stream()[1][0]
        preasure_kpa = preasure_bar * 100
        return round(preasure_kpa, 2)

    def get_location(self) -> dict:
        lat, lng = self.old_stream_unit.stream()[2]['pos']
        return {
            'lat':lat, 'lng':lng
        }

    def get_status(self) -> dict:
        info_system = self.old_stream_unit.stream()[3]
        return {
            'system'  : 'OK' if info_system['alive'] else 'FAIL',
            'battery' : info_system['bat']
        }

def print_telemetry(dev: UnifiedTelemetry):
    print("TEMP C:", dev.get_temperature_c())
    print("PRESS KPA:", dev.get_pressure_kpa())
    print("LOCATION:", dev.get_location())
    print("STATUS:", dev.get_status())
    print("-" * 40)

if __name__ == '__main__':
    print_telemetry(LegacyThermalV1Adapter(LegacyThermalUnitV1()))
    print_telemetry(IndustrialPacketAdapter(IndustrialPacketReader()))
    print_telemetry(CloudTelemetryAdapter(CloudTelemetryJSON()))
    print_telemetry(SatelliteTelemetryAdapter(SatelliteStreamingUnit()))
