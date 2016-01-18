import time
import requests
import requests_cache

def make_throttle_hook(timeout=1.0):
    """
    Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached
    """
    def hook(response, **kwargs):
        if not getattr(response, 'from_cache', False):
            print 'sleeping'
            time.sleep(timeout)
        return response
    return hook

if __name__ == '__main__':
requests_cache.install_cache('wait_test')
requests_cache.clear()

s = requests_cache.CachedSession()
s.hooks = {'response': make_throttle_hook(0.1)}
s.get('http://httpbin.org/delay/get')
s.get('http://httpbin.org/delay/get')

/Line/{ids}/Disruption