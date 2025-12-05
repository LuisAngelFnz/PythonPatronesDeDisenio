from abc import ABC, abstractmethod
import zlib
import base64
import hashlib


class FileProcessor(ABC):
    @abstractmethod
    def process(self) -> bytes:
        pass

class RawFileProcessor(FileProcessor):

    def __init__(self, file_path:str):
        self.file_path = file_path

    def process(self):
        print('Procesando archivo original')
        with open(self.file_path, 'rb') as file:
            return file.read()


class FileProcessorDecorator(FileProcessor):
    def __init__(self, wrapper:FileProcessor):
        self._wrapper = wrapper

    def process(self):
        return self._wrapper.process()


class CompresionFileProcessDecorator(FileProcessorDecorator):
    def process(self):
        original_data = self._wrapper.process()
        print('Procesando archivo compresión...')
        return zlib.compress(original_data)

class EncryptFileProcessDecorator(FileProcessorDecorator):
    def process(self):
        original_data = self._wrapper.process()
        print('Procesando archivo encriptación...')
        return base64.b64encode(original_data)

class SealFileProcessDecorator(FileProcessorDecorator):
    SIGNATURE = '--SIGNATURE:XYZ--'
    def process(self):
        original_data = self._wrapper.process()
        print('Procesando archivo sello...')
        return original_data + self.SIGNATURE.encode('utf-8')

class IntegrityFileProcessDecorator(FileProcessorDecorator):
    ALGORITHMIC = 'sha256'
    SHA_SIGNARURE = getattr(hashlib, ALGORITHMIC)(
        SealFileProcessDecorator.SIGNATURE.encode('utf-8')
    ).hexdigest()

    def process(self):
        '''Use SealFileProcessDecorator before'''
        original_data = self._wrapper.process()
        print('Procesando archivo integridad...')
        seal = original_data[-17:]
        if not isinstance(seal, str):
            seal = seal.encode('utf-8')
        data_signarure = getattr(hashlib, self.ALGORITHMIC)(seal).hexdigest()

        if data_signarure != self.SHA_SIGNARURE:
            raise ValueError(
                'La información esta mal sellada'
            )
        return original_data

class LoggingFileProcessDecorator(FileProcessorDecorator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logging = []

    def process(self):
        original_data = self._wrapper.process()
        print('Procesando archivo en bitacoras...')
        self.logging.append(original_data)
        return original_data

class SizeLimitFileProcessDecorator(FileProcessorDecorator):
    def process(self):
        original_data = self._wrapper.process()
        print('Procesando archivo Limitador de longitud...')
        if len(original_data) > 50:
            raise ValueError(
                'Información del archivo rebasa los 50 caracteres'
            )
        return original_data

class FormatConvertFileProcessDecorator(FileProcessorDecorator):
    def process(self):
        original_data = self._wrapper.process()
        print('Procesando archivo conversión...')
        if isinstance(original_data, str):
            original_data = {'content':original_data}
        return original_data

class AdvanceFilterFileProcessDecorator(FileProcessorDecorator):
    def process(self):
        original_data = self._wrapper.process()
        print('Procesando archivo Filtros avanzados...')
        for work in ["virus", "bomba", "hack"]:
            original_data = original_data.replace(work, '')
        return original_data


if __name__ == '__main__':
    file = RawFileProcessor('/tmp/archivo_text.txt')
    file = CompresionFileProcessDecorator(file)
    file = EncryptFileProcessDecorator(file)
    file = LoggingFileProcessDecorator(file)
    file = SealFileProcessDecorator(file)
    file = IntegrityFileProcessDecorator(file)
    print(file.process())
