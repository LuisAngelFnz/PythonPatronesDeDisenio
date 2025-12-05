from abc import ABC, abstractmethod

class Notification(ABC):

    @abstractmethod
    def send(self, message:str) -> None:
        pass

class EmailNotification(Notification):

    def send(self, message) -> None:
        print(f'Enviando notificación por Email, mensaje: {message}')

class SMSNotification(Notification):

    def send(self, message) -> None:
        print(f'Enviando notificación por SMS, mensaje: {message}')

class PushNotification(Notification):

    def send(self, message) -> None:
        print(f'Enviando notificación por PUSH, mensaje: {message}')


class NotificationCreator(ABC):

    @abstractmethod
    def create_notification(self) -> Notification:
        pass

    def notify(self, message: str) -> None:
        notification =  self.create_notification()
        notification.send(message)

class EmailNotificationCreator(NotificationCreator):

    def create_notification(self) -> Notification:
        return EmailNotification()

class SMSNotificationCreator(NotificationCreator):

    def create_notification(self) -> Notification:
        return SMSNotification()

class PushNotificationCreator(NotificationCreator):

    def create_notification(self) -> Notification:
        return PushNotification()

def client_code(creator: NotificationCreator):
    print('Iniciando app')
    creator.notify('Empezando acutalización')
    creator.notify('A mitad de acutalización')
    creator.notify('Finalización de actualización')
    print('Terminando app')

if __name__ == '__main__':
    client_code(EmailNotificationCreator())
    client_code(SMSNotificationCreator())
    client_code(PushNotificationCreator())