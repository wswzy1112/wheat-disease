"""
小麦病虫害识别系统 - 生产级后端
安全特性: JWT认证 | 密码哈希 | 文件验证 | 速率限制 | CORS锁 | 安全响应头
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
import datetime
import uuid
import re
import json as json_mod
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(64).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:w1z2y072@localhost/wheat_disease')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
BASE = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE, 'static', 'uploads'))
app.config['JWT_EXPIRATION_HOURS'] = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')

limiter = Limiter(get_remote_address, app=app, default_limits=['200 per day', '50 per hour'], storage_uri='memory://')

allowed = (os.environ.get('ALLOWED_ORIGINS') or '').strip()
if allowed:
    CORS(app, origins=[x.strip() for x in allowed.split(',')], supports_credentials=True)
else:
    CORS(app)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    records = db.relationship('Record', backref='user', lazy='dynamic')
    def set_password(self, pw): self.password = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password, pw)

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    suggestion = db.Column(db.String(500))

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    result = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    warning = db.Column(db.Boolean, default=False)
    suggestion = db.Column(db.String(500))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

def create_token(uid):
    return jwt.encode({'user_id': uid, 'iat': datetime.datetime.utcnow(), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])}, app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(t):
    try: return jwt.decode(t, app.config['SECRET_KEY'], algorithms=['HS256'])
    except: return None

def login_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        h = request.headers.get('Authorization', '')
        if not h.startswith('Bearer '):
            return jsonify({'success': False, 'msg': '未提供认证令牌'}), 401
        p = decode_token(h[7:])
        if not p:
            return jsonify({'success': False, 'msg': '令牌无效或已过期'}), 401
        u = User.query.get(p['user_id'])
        if not u:
            return jsonify({'success': False, 'msg': '用户不存在'}), 401
        return f(u, *a, **kw)
    return wrap

ALLOWED_EXT = {'jpg','jpeg','png','gif','webp','bmp'}
def validate_image(file):
    e = file.filename.rsplit('.',1)[1].lower() if '.' in file.filename else ''
    if e not in ALLOWED_EXT: return False, '请上传JPG/PNG/GIF/WebP/BMP格式'
    if file.content_type and not file.content_type.startswith('image/'): return False, '文件类型错误'
    try:
        from PIL import Image; import io
        file.seek(0); Image.open(io.BytesIO(file.read(2*1024*1024))).verify(); file.seek(0)
    except: return False, '文件不是有效图片'
    return True, ''

def safe_name(orig):
    e = orig.rsplit('.',1)[1].lower() if '.' in orig else 'jpg'
    return f"{datetime.datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:16]}.{e}"

MODEL_PATH = os.environ.get('MODEL_PATH', os.path.join(BASE, 'model/model/cnn_model.pth'))
LABEL_PATH = os.environ.get('LABEL_PATH', os.path.join(BASE, 'model/model/labels.json'))
FRONTEND_DIR = os.environ.get('FRONTEND_DIR', os.path.join(BASE, 'wheat-frontend', 'dist'))
print(f'[INFO] 加载模型: {MODEL_PATH}')
import torch; from torchvision import transforms
if not os.path.exists(MODEL_PATH): raise FileNotFoundError(f'模型文件不存在: {MODEL_PATH}')
model = torch.load(MODEL_PATH, map_location='cpu'); model.eval()
with open(LABEL_PATH, encoding='utf-8') as f: labels = json_mod.load(f)
transform = transforms.Compose([transforms.Resize((160,160)), transforms.ToTensor()])
E2C = {"Aphid":"蚜虫","Black Rust":"黑锈病","Blast":"稻瘟病","Brown Rust":"褐锈病","Common Root Rot":"普通根腐病","Fusarium Head Blight":"赤霉病","Healthy":"健康","Leaf Blight":"叶枯病","Mildew":"白粉病","Mite":"螨虫害","Septoria":"壳针孢病","Smut":"黑粉病","Stem fly":"秆蝇虫害","Tan spot":"褐斑病","Yellow Rust":"黄锈病"}

@app.route('/api/health', methods=['GET'])
def health(): return jsonify({'status':'ok','time':datetime.datetime.utcnow().isoformat()})

@app.route('/api/register', methods=['POST'])
@limiter.limit('5 per minute')
def register():
    d = request.get_json(silent=True)
    if not d: return jsonify({'success':False,'msg':'请求数据无效'}),400
    uname = (d.get('username') or '').strip(); pw = d.get('password') or ''
    if not uname: return jsonify({'success':False,'msg':'用户名不能为空'}),400
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]{2,20}$', uname):
        return jsonify({'success':False,'msg':'用户名2-20位，支持中文/字母/数字/下划线'}),400
    if len(pw) < 6 or len(pw) > 128: return jsonify({'success':False,'msg':'密码长度6-128位'}),400
    if User.query.filter_by(username=uname).first(): return jsonify({'success':False,'msg':'用户名已存在'}),409
    try:
        u = User(username=uname); u.set_password(pw); db.session.add(u); db.session.commit()
        t = create_token(u.id)
        return jsonify({'success':True,'msg':'注册成功','token':t,'user_id':u.id,'username':u.username}),201
    except: db.session.rollback(); return jsonify({'success':False,'msg':'注册失败'}),500

@app.route('/api/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    d = request.get_json(silent=True)
    if not d: return jsonify({'success':False,'msg':'请求数据无效'}),400
    uname = (d.get('username') or '').strip(); pw = d.get('password') or ''
    if not uname or not pw: return jsonify({'success':False,'msg':'用户名和密码不能为空'}),400
    u = User.query.filter_by(username=uname).first()
    if not u or not u.check_password(pw): return jsonify({'success':False,'msg':'用户名或密码错误'}),401
    t = create_token(u.id)
    return jsonify({'success':True,'msg':'登录成功','token':t,'user_id':u.id,'username':u.username})

@app.route('/api/upload', methods=['POST'])
@login_required
@limiter.limit('30 per hour')
def upload(u):
    if 'image' not in request.files: return jsonify({'success':False,'msg':'未选择图片'}),400
    f = request.files['image']
    if not f.filename: return jsonify({'success':False,'msg':'文件名为空'}),400
    ok, err = validate_image(f)
    if not ok: return jsonify({'success':False,'msg':err}),400
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    sn = safe_name(f.filename); fp = os.path.join(app.config['UPLOAD_FOLDER'], sn)
    f.save(fp)
    try:
        img = Image.open(fp).convert('RGB'); t = transform(img).unsqueeze(0)
        with torch.no_grad():
            out = model(t); prob = torch.softmax(out, dim=1); idx = torch.argmax(prob).item()
            conf = prob[0][idx].item(); en = labels[idx]
        if conf < 0.85:
            os.remove(fp)
            return jsonify({'success':True,'result':'识别失败','confidence':round(conf,4),'warning':False,'suggestion':'图片不清晰，请上传更清晰的图片','filename':None})
        dn = E2C.get(en, en)
        ds = Disease.query.filter_by(name=en).first() or Disease.query.filter_by(name=dn).first(); sug = ds.suggestion if ds else '暂无建议'
        rec = Record(filename=sn, result=dn, confidence=conf, warning=True, suggestion=sug, user_id=u.id)
        db.session.add(rec); db.session.commit()
        return jsonify({'success':True,'filename':sn,'result':dn,'confidence':round(conf,4),'warning':True,'suggestion':sug})
    except:
        if os.path.exists(fp): os.remove(fp)
        db.session.rollback(); return jsonify({'success':False,'msg':'识别处理失败'}),500

@app.route('/api/records', methods=['GET'])
@login_required
def get_records(u):
    pg = max(1, min(request.args.get('page',1,type=int), 1000))
    lim = max(1, min(request.args.get('limit',10,type=int), 50))
    sort = request.args.get('sort','time'); order = request.args.get('order','desc')
    kw = (request.args.get('keyword') or '').strip()
    q = Record.query.filter_by(user_id=u.id)
    if kw: q = q.filter(Record.result.contains(kw))
    if sort == 'time': q = q.order_by(Record.time.desc() if order=='desc' else Record.time.asc())
    elif sort == 'result': q = q.order_by(Record.result.asc() if order=='asc' else Record.result.desc())
    else: q = q.order_by(Record.time.desc())
    p = q.paginate(page=pg, per_page=lim, error_out=False)
    items = [{'filename':r.filename,'result':r.result,'confidence':round(r.confidence,4) if r.confidence else 0,'warning':r.warning,'suggestion':r.suggestion,'time':r.time.strftime('%Y-%m-%d %H:%M:%S') if r.time else ''} for r in p.items]
    return jsonify({'records':items,'total':p.total,'page':pg,'limit':lim})

@app.route('/api/diseases', methods=['GET'])
def diseases(): return jsonify([{'id':d.id,'name':d.name,'suggestion':d.suggestion} for d in Disease.query.all()])

@app.route('/api/user/profile', methods=['GET'])
@login_required
def profile(u):
    return jsonify({'user_id':u.id,'username':u.username,'created_at':u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else '','record_count':Record.query.filter_by(user_id=u.id).count()})

@app.route('/uploads/<filename>')
@limiter.limit('60 per minute')
def serve_upload(filename):
    if '..' in filename or '/' in filename or '\\' in filename: return jsonify({'error':'非法路径'}),400
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', defaults={'path':''})
@app.route('/<path:path>')
def frontend(path):
    if path.startswith('api/'): return jsonify({'error':'API路由错误'}),404
    target = os.path.join(FRONTEND_DIR, path) if path else os.path.join(FRONTEND_DIR, 'index.html')
    if os.path.exists(target) and os.path.isfile(target): return send_from_directory(FRONTEND_DIR, path if path else 'index.html')
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.after_request
def security(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    if app.config.get('ENV') == 'production':
        resp.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
    return resp

@app.errorhandler(400)
def e400(e): return jsonify({'success':False,'msg':'请求参数错误'}),400
@app.errorhandler(401)
def e401(e): return jsonify({'success':False,'msg':'未授权访问'}),401
@app.errorhandler(413)
def e413(e): return jsonify({'success':False,'msg':'文件过大，最大10MB'}),413
@app.errorhandler(429)
def e429(e): return jsonify({'success':False,'msg':'请求过于频繁'}),429
@app.errorhandler(500)
def e500(e): db.session.rollback(); return jsonify({'success':False,'msg':'服务器内部错误'}),500

if __name__ == '__main__':
    with app.app_context(): db.create_all(); print('[INFO] 数据库表已就绪')
    debug = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    print(f'[INFO] 启动 http://0.0.0.0:{port} | 环境: {"开发" if debug else "生产"}')
    app.run(host='0.0.0.0', port=port, debug=debug)
