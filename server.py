#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        # Потенциальный баг для внимательных =)
	#__Показывает все собщения всех пользователей,
	#__ даже если не залогинился
	#__ нужно делать проверку чтобы выводились сообщения только тем кто залогинился.
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            # login:admin -> admin
	    #__Алгоритм понимаю, с ниписанием синтаксисом проблемы, много пробелов в Питоне, первый раз на нём
	    #__Напишу так словами : )
	    #__Нужно при условии  что вводится login: запоминать в список(массив) логин
	    #__При новом вводе смотрим длину списка, проверяем циклом по нему на наличие уже подобного логина
	    #__если есть такой то выводим сообщение что такой пользователь существует, 
	    #__если нет, пропускаем дальше.
	    #__при написании сообщения пользователем записываем в список имя и сообщение
	    #__по циклу не более 10 записей, крайние записи в конец списка, а предыдущие сдвигаем вверх
	    #__При входе нового пользователя выводим ему циклом этот список в обратном порядке
            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                self.sendLine("Welcome!".encode())
            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list

    def startFactory(self):
        self.clients = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
