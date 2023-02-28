from spyne import Application, rpc, ServiceBase, Unicode, Integer, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

class service(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def hello(ctx, name, times):
        for i in range(times):
            yield u'Hello, %s' % name

    @rpc(Integer, Integer, _returns=Integer)
    def add(ctx, a, b):
        return a + b

    @rpc(float, float, float, float, float, float, _returns=float)
    def calcJourneyTime(ctx, distance, speed, carBatteryMax, carBatteryCurrent, carBatteryConsumption, carBatteryRechargeTime):
        return distance / speed

    @rpc(Unicode, _returns=Unicode)
    def ping(ctx, str):
        return 'ping from ' + str
    
    @rpc()
    def ping():
        return 'ping'

application = Application([service], 'spyne.examples.hello.soap',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())
wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    server = make_server('127.0.0.1', 8000, wsgi_app)
    # server = make_server('192.168.167.235', 8000, wsgi_app)
    server.serve_forever()