import os
import random

from abc import ABC, abstractmethod
from typing import Union
from io import TextIOBase, StringIO


class ProcessFile(ABC):
    def run(self, textio_or_path:Union[str, TextIOBase]):
        metadata = {}
        success, error = self.validity(textio_or_path, metadata)
        if not success:
            return success, error

        success, error = self.preprocess(metadata)
        if not success:
            return success, error

        success, error = self.process(metadata)
        if not success:
            return success, error

        success, error = self.postprocess(metadata)
        if not success:
            return success, error

        success, error = self.save(metadata)
        return success, error


    @abstractmethod
    def validity(self, textio_or_path:Union[str, TextIOBase], metadata:dict) -> tuple[bool, str]:
        pass

    @abstractmethod
    def preprocess(self, metadata:dict):
        pass

    @abstractmethod
    def process(self, metadata:dict):
        pass

    @abstractmethod
    def postprocess(self, metadata:dict):
        pass

    @abstractmethod
    def save(self, metadata:dict):
        pass


class CSVProcessor(ProcessFile):

    def validity(self, textio_or_path:Union[str, TextIOBase], metadata:dict) -> tuple[bool, str]:
        if isinstance(textio_or_path, TextIOBase):
            metadata['content'] = textio_or_path.read()
            metadata['filename'] = getattr(textio_or_path, 'name', 'desconocido.txt')
        elif isinstance(textio_or_path, str):
            _, extension = os.path.splitext(textio_or_path)
            if extension.lower() != '.csv':
                return False, f'La extensión({extension}) del archivo no es .csv'

            if not os.path.exists(textio_or_path):
                return False, f'La ruta: {textio_or_path} del archivo no existe'

            if not os.path.isfile(textio_or_path):
                return False, f'La ruta: {textio_or_path} no es un archivo'

            with open(textio_or_path, 'r') as file:
                metadata['content'] = file.read()
                metadata['filename'] = file.name

        return True, 'OK'

    def preprocess(self, metadata:dict):
        metadata['content'] = metadata['content'].splitlines()
        metadata['content'] = [el.split(',') for el in metadata['content'][1:]]
        return True, 'OK'

    def process(self, metadata:dict):
        for nro,el in enumerate(metadata['content']):
            if len(el) < 4:
                return False, f'Linea: {nro}, El tamaño de la linea({len(el)}) no es 4'
            for chars in el:
                if len(chars) > 50:
                    return False, f'Linea: {nro}, El tamaño de la celda supera los 50 caracteres'
        return True, 'OK'

    def postprocess(self, metadata:dict):
        print(f'Enviando por email a test@gmail.com, archivo: {metadata["filename"]}')
        return True, 'Ok'

    def save(self, metadata:dict):
        data_to_save = []
        for el in metadata['content']:
            data_to_save.append(dict(zip(['nombre', 'primer_apellido', 'segundo_apellito', 'fecha_de_nacimiento'], el)))

        if random.choice([True, False]):
            print('Salvando información en la base de datos postgres')
            return True, 'OK'
        else:
            print('Error al guardar la información en la base datos postgres')
            return False, 'Error de conexión a la base de datos'

class JSONProcessor(ProcessFile):

    def validity(self, textio_or_path:Union[str, TextIOBase], metadata:dict) -> tuple[bool, str]:
        if random.choice(['.csv', '.json']) != '.json':
            print('Archivo json validado correctamente')
            return True, 'OK'
        return False, 'El archivo no es un .json'

    def preprocess(self, metadata:dict):
        if random.choice([True, False]):
            print('Archivo json preproceado correctamente')
            return True, 'OK'
        return False, 'Error preprocesando el archivo .json'

    def process(self, metadata:dict):
        if random.choice([True, False]):
            print('Archivo json extraido correctamente')
            return True, 'Ok'
        return False, 'Existe un dato incorrecto'

    def postprocess(self, metadata:dict):
        if random.choice([True, False]):
            print('Registrado en la bitacora del archivo json')
            return True, 'ok'
        return False, 'Error al registrar en las bitacoras'

    def save(self, metadata:dict):
        if random.choice([True, False]):
            print('Información guardada en la base de datos mongo')
            return True, 'ok'
        return False, 'Error al registrar en las bitacoras'

class XMLProcessor(ProcessFile):

    def validity(self, textio_or_path:Union[str, TextIOBase], metadata:dict) -> tuple[bool, str]:
        if random.choice(['.csv', '.json']) != '.json':
            print('Archivo xml validado correctamente')
            return True, 'OK'
        return False, 'El archivo no es un .xml'

    def preprocess(self, metadata:dict):
        if random.choice([True, False]):
            print('Archivo xml preproceado correctamente')
            return True, 'OK'
        return False, 'Error preprocesando el archivo .xml'

    def process(self, metadata:dict):
        if random.choice([True, False]):
            print('Archivo xml extraido correctamente')
            return True, 'Ok'
        return False, 'Existe un dato incorrecto en el archivo xml'

    def postprocess(self, metadata:dict):
        if random.choice([True, False]):
            print('Replicando en desarrollo')
            return True, 'ok'
        return False, 'Error al replicar en desarrollo'

    def save(self, metadata:dict):
        if random.choice([True, False]):
            print('Información guardada en la base de datos cassandra')
            return True, 'ok'
        return False, 'Error al registrar en las cassandra'

if __name__ == '__main__':
    file = StringIO('Nombre,PrimerApellido,SegundoApellido,FechaDeNacimiento\nALberto,Ramirez,Rojas,12-12-1990\nRaul,Contreras,Izquierda,11-04-1994')
    # processor = CSVProcessor()
    # processor = JSONProcessor()
    processor = XMLProcessor()
    success,msj = processor.run(file)
    print(success)
    print(msj)
