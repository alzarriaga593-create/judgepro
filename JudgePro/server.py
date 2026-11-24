import http.server, json, os
from urllib.parse import urlparse, parse_qs

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("SIRVIENDO DESDE:", os.getcwd())

atletas = []
votos = {}
info = {"evento":"MR QUITO","lugar":"QUITO","nivel":"CLASIFICADO","modalidad":"FISICO CULTURISMO","categoria":"JUNIOR","division":"HASTA 80KG"}
jueces = []

class Handler(http.server.SimpleHTTPRequestHandler):
    def send_response(self, code, message=None):
        super().send_response(code, message)
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')

    def _json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/votos':
            self._json({"atletas":atletas,"votos":votos,"info":info})
            return
        if parsed.path == '/api/solicitudes-jueces':
            self._json(jueces)
            return
        if parsed.path == '/api/estado-juez':
            qs = parse_qs(parsed.query)
            jnum = qs.get('juez',[None])[0]
            nombre = qs.get('nombre',[None])[0]
            estado = 'PENDIENTE'
            for j in jueces:
                if str(j.get('juez'))==str(jnum) and j.get('nombre')==nombre:
                    estado = j.get('estado','PENDIENTE')
                    break
            self._json({"estado":estado})
            return
        return super().do_GET()

    def do_POST(self):
        global info
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length',0))
        raw = self.rfile.read(length).decode() if length>0 else '{}'
        data = json.loads(raw or '{}')
        if parsed.path == '/api/info':
            info.update(data)
        elif parsed.path == '/api/atletas':
            if data.get('borrar'):
                atletas.clear()
            elif data.get('id'):
                ex = next((a for a in atletas if a['id']==data['id']), None)
                if ex:
                    if 'nombre' in data: ex['nombre']=data['nombre']
                else:
                    atletas.append({"id":data['id'],"nombre":data.get('nombre','')})
        elif parsed.path == '/api/atletas_masivo':
            # NUEVO: para CARGAR PESAJE MASIVO XLS - recibe lista de atletas
            lista = data.get('atletas', [])
            for item in lista:
                if not item.get('id'): continue
                ex = next((a for a in atletas if a['id']==item['id']), None)
                if ex:
                    ex.update(item)
                else:
                    atletas.append(item)
        elif parsed.path == '/api/voto':
            juez = str(data.get('juez'))
            cals = data.get('calificaciones',{})
            for aid, lugar in cals.items():
                if lugar=='-' or lugar=='' : continue
                if aid not in votos: votos[aid]={}
                try: votos[aid][juez]=int(lugar)
                except: pass
        elif parsed.path == '/api/reset_votos':
            votos.clear()
        elif parsed.path == '/api/solicitud-juez':
            nombre = (data.get('nombre') or '').strip().upper()
            juez = str(data.get('juez'))
            ex = next((j for j in jueces if str(j.get('juez'))==juez), None)
            if ex:
                ex['nombre']=nombre
                ex['estado']='PENDIENTE'
            else:
                jueces.append({"nombre":nombre,"juez":juez,"estado":"PENDIENTE"})
        elif parsed.path == '/api/aprobar-juez':
            juez = str(data.get('juez'))
            estado = data.get('estado')
            for j in jueces:
                if str(j.get('juez'))==juez:
                    j['estado']=estado
        elif parsed.path == '/api/solicitudes-jueces':
            juez = str(data.get('juez'))
            estado = data.get('estado')
            nombre = (data.get('nombre') or '').strip().upper()
            for j in jueces:
                if str(j.get('juez'))==juez or j.get('nombre')==nombre:
                    j['estado']=estado
        elif parsed.path == '/api/borrar-juez':
            juez = str(data.get('juez')) if data.get('juez') else None
            nombre = (data.get('nombre') or '').strip().upper()
            id_borrar = str(data.get('id')) if data.get('id') else None
            jueces[:] = [j for j in jueces if not (
                (juez and str(j.get('juez'))==juez) or
                (nombre and j.get('nombre')==nombre) or
                (id_borrar and str(j.get('id'))==id_borrar)
            )]
        self._json({"ok":True})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length',0))
        raw = self.rfile.read(length).decode() if length>0 else '{}'
        try:
            data = json.loads(raw or '{}')
        except:
            data = {}
        if '/api/atletas' in self.path:
            atletas.clear(); votos.clear()
        elif '/api/solicitudes-jueces' in self.path:
            juez = str(data.get('juez')) if data.get('juez') else None
            nombre = (data.get('nombre') or '').strip().upper()
            id_borrar = str(data.get('id')) if data.get('id') else None
            jueces[:] = [j for j in jueces if not (
                (juez and str(j.get('juez'))==juez) or
                (nombre and j.get('nombre')==nombre) or
                (id_borrar and str(j.get('id'))==id_borrar)
            )]
        self._json({"ok":True})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()

print("EASY REFEREE SERVIDOR V3.4 - EN VIVO en http://localhost:8001")
http.server.HTTPServer(('0.0.0.0',8001), Handler).serve_forever()