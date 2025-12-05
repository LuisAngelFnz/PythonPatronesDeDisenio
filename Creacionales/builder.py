from abc import ABC , abstractmethod


class PipelineBuilder(ABC):
    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def add_cleaning(self) -> None:
        pass

    @abstractmethod
    def add_normalization(self) -> None:
        pass

    @abstractmethod
    def add_compression(self) -> None:
        pass

    @abstractmethod
    def add_encryption(self) -> None:
        pass

    @abstractmethod
    def add_packaging(self) -> None:
        pass

    @abstractmethod
    def build(self) -> None:
        pass

class DataPipeline:

    def __init__(self):
        self.parts = []

    def run(self):
        print('Partes del pipeline')
        for step in self.parts:
            print(step)

class DataPipelineBuilder(PipelineBuilder):
    def __init__(self):
        self.reset()

    def reset(self):
        self.data_pipe_line = DataPipeline()
        return self

    def add_cleaning(self):
        self.data_pipe_line.parts.append('limpieza')
        return self

    def add_normalization(self):
        self.data_pipe_line.parts.append('normalizado')
        return self

    def add_compression(self):
        self.data_pipe_line.parts.append('comprimido')
        return self

    def add_encryption(self):
        self.data_pipe_line.parts.append('encriptado')
        return self

    def add_packaging(self):
        self.data_pipe_line.parts.append('empaquetado')
        return self

    def build(self):
        return self.data_pipe_line

class PipelineDirector:
    def __init__(self, builder:DataPipelineBuilder) -> None:
        self.builder = builder

    def build_minimal_pipeline(self) -> DataPipeline:
        return self.builder.add_cleaning().build()

    def build_secure_pipeline(self) -> DataPipeline:
        self.builder.add_cleaning().add_normalization()
        self.builder.add_compression().add_encryption()
        return self.builder.add_packaging().build()

if __name__ == '__main__':
    builder = DataPipelineBuilder()
    director = PipelineDirector(builder)
    result_pipeline = director.build_minimal_pipeline()
    print(f'Minimal pipeline: {result_pipeline}')
    result_pipeline.run()
    print('-'*40)
    builder.reset()
    result_pipeline = director.build_secure_pipeline()
    print(f'Secure pipeline: {result_pipeline}')
    result_pipeline.run()