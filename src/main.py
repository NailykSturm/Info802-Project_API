from spyne import Application, rpc, ServiceBase, Unicode, Integer, Iterable, ComplexModel, Array
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
# from spyne.middleware import cors
from wsgiref.simple_server import make_server


class GeoJSONStep(ComplexModel):  # Step of a segment
    distance = float  # Distance in meters
    duration = float  # Duration in seconds
    # Reference to index of coordinates [start, end]
    way_points = Array(Integer).customize(max_occurs=2, min_occurs=2)


class GeoJSONSegment(ComplexModel):
    distance = float  # Distance in meters
    duration = float  # Duration in seconds
    steps = Array(GeoJSONStep)
    # Reference to index of coordinates [start, end]
    way_points = Array(Integer).customize(max_occurs=2, min_occurs=2)


class GeoJSON(ComplexModel):  # GeoJSON object
    coordinates = Array(Array(float))  # Array of coordinates [lat, lon]
    # A segment is a part of the route between two points defined by the user
    segments = Array(GeoJSONSegment)


class CarRangeDetails(ComplexModel):
    city = float
    highway = float
    combined = float


class ChargeTripRange(ComplexModel):
    best = float
    worst = float


class CarRange(ComplexModel):
    best = CarRangeDetails
    chargetrip_range = ChargeTripRange
    worst = CarRangeDetails


class CarRoutingInfo(ComplexModel):
    fast_charging_support = bool


class Car(ComplexModel):
    battery = float
    routing = CarRoutingInfo
    range = CarRange


class Station(ComplexModel):
    coordonates = Array(Array(float).customize(max_occurs=2, min_occurs=2))
    speed = Unicode


class service(ServiceBase):
    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def hello(ctx, name, times):
        ctx.transport.resp_headers['Access-Control-Allow-Origin'] = '*'
        for i in range(times):
            yield u'Hello, %s' % name

    @rpc(Integer, Integer, _returns=Integer)
    def add(ctx, a, b):
        ctx.transport.resp_headers['Access-Control-Allow-Origin'] = '*'
        return a + b

    @rpc(Unicode, _returns=Unicode)
    def ping(ctx, str):
        ctx.transport.resp_headers['Access-Control-Allow-Origin'] = '*'
        return 'ping from ' + str

    @rpc()
    def ping(ctx):
        ctx.transport.resp_headers['Access-Control-Allow-Origin'] = '*'
        print('poulet')
        return 'ping'

    @rpc(GeoJSON, Car, Station, _returns=float)
    def calcJourneyTime(ctx, geoJSON, car, stations):
        ctx.transport.resp_headers['Access-Control-Allow-Origin'] = '*'
        segments = geoJSON.segments

        return 0

    @rpc(GeoJSON, Car, _returns=Iterable(Iterable(float)))
    def getStopPoints(ctx, geoJSON, car):
        ctx.transport.resp_headers['Access-Control-Allow-Origin'] = '*'
        coords = geoJSON.coordinates
        segments = geoJSON.segments

        listStopPoints = []
        distLastStop = 0

        ## KEEP IN MIND segment & step is probably the key of segments & segment.steps (instead of values)
        for segment in segments:
            for step in segment.steps:
                # x100 because the distance is in meters
                if (distLastStop + step.distance >= (car.range.worst.combined * 100)):
                    listStopPoints.append(coords[0][step.way_points[0]])
                    print("Stop point added at " +
                          str(coords[0][step.way_points[0]]) + " (distance: " + str(distLastStop) + ")")
                    distLastStop = 0
                distLastStop += step.distance
        return listStopPoints


application = Application([service], 'spyne.usmb.journey.planner.soap',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())
# application = cors.CORSMiddleware().apply(application)
wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    # server = make_server('192.168.167.235', 8000, wsgi_app)
    server = make_server('127.0.0.1', 8000, wsgi_app)
    server.serve_forever()
