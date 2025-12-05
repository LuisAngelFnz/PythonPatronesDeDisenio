from sys import getsizeof
from collections import deque
import random

from typing import Union, List, Tuple
# ============================================================
# UTILIDAD: Calcular memoria profunda
# ============================================================

def deep_sizeof(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    size = getsizeof(obj)

    if isinstance(obj, dict):
        for k, v in obj.items():
            size += deep_sizeof(k, seen)
            size += deep_sizeof(v, seen)
    elif isinstance(obj, (list, tuple, set, frozenset, deque)):
        for item in obj:
            size += deep_sizeof(item, seen)
    elif hasattr(obj, "__dict__"):
        size += deep_sizeof(obj.__dict__, seen)
    return size

APP_DEBUG_RENDER = False

class GameObjectType(object):

    def __init__(self, name:str, model_3d:str, texture:str, sounds:List[str], behaviors:Union[dict, list]):
        self._name = name
        self._model_3d, self._texture = model_3d, texture
        self._sounds, self._behaviors = sounds, behaviors

    def render(self, position:Tuple[int], rotation:Tuple[int], scale:Tuple[int]):
        render = '\n'.join([
            f'Renderizando objeto: {self._name}',
            f'position x: {position[0]}, y: {position[1]}',
            f'rotation rx: {rotation[0]}, ry: {rotation[1]} rz: {rotation[2]}',
            f'escala sx: {scale[0]} sy: {scale[1]} sz: {scale[2]}',
            f'modelado 3d: {self._model_3d}',
            f'texture: {self._texture}'
        ])
        if APP_DEBUG_RENDER:
            print(render)

    def play_sound(self, sound_id:str):
        assert sound_id in self._sounds, (
            f'sound_id: {sound_id} no pertenece al objeto {self._name}'
        )
        print(f'Reproduciendo sonido: {sound_id}')

    def describe(self):
        return f'Objeto: {self._name}'

class GameObjectTypeFactory:
    _game_types = {}

    @classmethod
    def get_game_object(cls, name:str, *args, **kwargs):
        if name not in cls._game_types:
            cls._game_types[name] = GameObjectType(name, *args, **kwargs)
        return cls._game_types[name]

class GameObject:
    def __init__(self,
        position:Tuple[int],
        scale:Tuple[int],
        rotation:Tuple[int],
        state:str,
        obj_type:GameObjectType
    ):
        self._position = position
        self._scale, self._rotation = scale, rotation
        self._state, self._obj_type = state, obj_type

    def render(self):
        self._obj_type.render(self._position, self._rotation, self._scale)

    def play_all_sounds(self):
        for sound_id in self._obj_type._sounds:
            self.play_sound(sound_id)

    def play_sound(self, sound_id:str):
        self._obj_type.play_sound(sound_id)

class GameWorld:

    def __init__(self, x:int, y:int, z:int):
        self._x, self._y, self._z = x,y,z
        self.objects = []

    def add_object(self, obj:GameObject):
        self.objects.append(obj)

    def render_all(self):
        for obj in self.objects:
            obj.render()

    def count_unique_flyweights(self):
        return len(GameObjectTypeFactory._game_types)

    def count_total_objects(self):
        return len(self.objects)


if __name__ == '__main__':
    simulate_model_and_texture_bytes = [
        'A', 'C', 'E', 'G', 'I', 'K', 'AB', 'CD', 'EF', 'GH', 'IJ', 'KL'
    ]
    simulate_model_and_texture_bytes = {
        char:random.randint(30, 50)
        for char in simulate_model_and_texture_bytes
    }

    state_npc = ['live', 'dead', 'run', 'walk', 'attack']
    states_npc_not_living = ['hide', 'destroy', 'visible']
    npc_names = ['Orco', 'Arquero', 'Leñador', 'Demoledor']
    base_data_objests = [
        (50000, 'Arbol',   'A', 'AB', ['Viento hojas'], ['Convertir a tronco', 'Quemar', 'Recoger']),
        (20000, 'Roca',    'C', 'CD', ['Golpeo de roca'],  ['Quebrarse', 'Tirar', 'Recoger']),
        (10000, 'Arbusto', 'E', 'EF', ['Viento hojas'], ['Aplastar', 'Podar', 'Recoger']),
        (5000, 'Cofre',   'G', 'GH', ['Bisagras abriendose'], ['Cerrarse', 'Abrirse', 'Recorger botin']),
        (10000, 'NPC',     'I', 'IJ', ['Grito', 'Conversiación'], ['Correr', 'Caminar', 'Agacharse', 'Boca abajo']),
        (5000, 'Casa',    'K', 'KL', ['Contrucción', 'Destrucción'], ['Destruir', 'Construir'])
    ]

    game_world = GameWorld(1000, 2000, 8000)
    randx = lambda:random.randint(0, game_world._x)
    randy = lambda:random.randint(0, game_world._y)
    randz = lambda:random.randint(0, game_world._z)

    for nro, name, base_model_3d, base_texture, sounds, behaviors in base_data_objests:

        model_3d = base_model_3d * simulate_model_and_texture_bytes[base_model_3d]
        texture  = base_texture * simulate_model_and_texture_bytes[base_texture]
        for _ in range(1, nro+1):
            if name != 'NPC':
                real_name = name
                state = random.choice(states_npc_not_living)
            else:
                real_name = random.choice(npc_names)
                state = random.choice(state_npc)

            obj_type = GameObjectTypeFactory.get_game_object(
                name=real_name, model_3d=model_3d, texture=texture, sounds=sounds, behaviors=behaviors
            )
            game_world.add_object(GameObject(
                position=(randx(), randy()),
                scale=(randx(), randy(), randz()),
                rotation=(randx(), randy(), randz()),
                state=state,
                obj_type=obj_type
            ))
    # APP_DEBUG_RENDER = True
    game_world.render_all()

    total_mem_objects = deep_sizeof(game_world)
    total_mem_flyweights = deep_sizeof(GameObjectTypeFactory._game_types)

    print(f'Objetos totales en el mundo: {game_world.count_total_objects()}')
    print(f'Flyweights únicos: {game_world.count_unique_flyweights()}')
    print(f"Memoria objetos extrínsecos: {total_mem_objects/1024/1024:.2f} MB")
    print(f"Memoria flyweights        : {total_mem_flyweights/1024/1024:.2f} MB")
    print(f"TOTAL: {(total_mem_objects+total_mem_flyweights)/1024/1024:.2f} MB")