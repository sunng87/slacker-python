from kazoo.client import KazooClient

def query_servers_from_zk(zkaddrs, cluster, namespace):
    conn = KazooClient(hosts=zkaddrs, read_only=True)
    conn.start()

    path = "/slacker/cluster/%s/namespaces/%s" % (cluster, namespace)
    children = conn.get_children(path)
    children = filter(lambda x: not x.startswith("_"), children)
    conn.stop()
    return children
