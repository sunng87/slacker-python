class Proxy(object):
    def __init__(self, client, namespace):
        self.client = client
        self.namespace = namespace

    def __getattr__(self, name):
        return (lambda *x: self._invoke(name, x))

    def _invoke(self, name, args):
        return self.client.call(self.namespace+"/"+name, args)

    def call(self, name, *args):
        return self._invoke(name, args)
