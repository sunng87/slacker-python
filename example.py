from slacker.geventbackend import Client
from slacker.proxy import Proxy
c = Client("127.0.0.1:2104")
p = Proxy(c, "slacker.example.api")
print p.timestamp()
