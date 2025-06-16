from urllib.parse import urlencode, urljoin
import requests

class BaseEvolutionAPI:

    def __init__(self):
        # Evolution API rodando localmente
        self._BASE_URL = 'http://localhost:8080'
        # Quando quiser usar Railway: 'https://evolution-api-production-2ca7.up.railway.app'
        self._API_KEY = {
            'arcane': '429683C4C977415CAAFCCE10F7D57E11'
        }

    def _send_request(
        self,
        path,
        method='GET',
        body=None,
        headers={},
        params_url={}
    ):
        
        method.upper()
        url = self._mount_url(path, params_url)

        if not isinstance(headers, dict):
            headers = {}

        headers.setdefault('Content-Type', 'application/json')

        instance = self._get_instance(path)
        headers['apikey'] = self._API_KEY.get(instance)
        request = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete
        }.get(method)

        try:
            response = request(url, headers=headers, json=body, timeout=30)
            print(f"Evolution API Response: {response.status_code}")
            return response
        except Exception as e:
            print(f"Erro ao conectar Evolution API: {e}")
            return None

    def _mount_url(self, path, params_url):
        parameters = ''
        if isinstance(params_url, dict):
            parameters = urlencode(params_url)

        url = urljoin(self._BASE_URL, path)
        if parameters:
            url = url + '?' + parameters

        return url
    
    def _get_instance(self, path):
        return path.strip('/').split('/')[-1]
    

class SendMessage(BaseEvolutionAPI):

    def send_message(self, instance, body):
        path = f'/message/sendText/{instance}/'
        return self._send_request(path, method='POST', body=body)



