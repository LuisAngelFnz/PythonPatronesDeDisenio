from abc import ABC, abstractmethod
import copy

class BotPrototype(ABC):

    @abstractmethod
    def clone(self):
        pass


class AutoBot(BotPrototype):

    def __init__(self, name:str, tasks:list, config:dict, version:str):
        self.name = name
        self.tasks = tasks
        self.config = config
        self.version = version

    def clone(self):
        return self.__class__(
            self.name,
            copy.deepcopy(self.tasks),
            dict(self.config),
            self.version
        )


if __name__ == '__main__':
    base_bot = AutoBot("Alpha", ["scan", "monitor"], {'name':'Angel'}, "1.0")

    bot2 = base_bot.clone()
    bot3 = base_bot.clone()

    bot2.name = "Beta"
    bot2.tasks.append("report")
    bot2.config["speed"] = "slow"

    print(
        f'base_bot \nname: {base_bot.name} \ntasks::{base_bot.tasks} \nconfig: {base_bot.config}'
    )
    print(
        f'bot2 \nname: {bot2.name} \ntasks::{bot2.tasks} \nconfig: {bot2.config}'
    )

