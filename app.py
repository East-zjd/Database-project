from flask import Flask, request, redirect, url_for, render_template_string, session, flash
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

# Load DB config from config.py (create from config.py.example)
try:
    from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
except Exception:
    DB_HOST='localhost'; DB_PORT=3306; DB_USER='root'; DB_PASSWORD=''; DB_NAME='social_db'

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_conn():
    return pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=False)

def init_db():
    # execute schema.sql to create DB and tables
    with open('schema.sql','r',encoding='utf-8') as f:
        sql = f.read()
    # split by delimiter for simple execution
    con = get_conn()
    try:
        cur = con.cursor()
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for s in statements:
            cur.execute(s)
        con.commit()
    except Exception as e:
        con.rollback()
        print('DB init error', e)
    finally:
        con.close()

def ensure_seed():
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute('USE '+DB_NAME)
        # create admin if not exists
        cur.execute("SELECT id FROM admins WHERE username='admin'")
        if cur.fetchone() is None:
            pw = generate_password_hash('password')
            cur.execute("INSERT INTO admins (username,password,name) VALUES (%s,%s,%s)",('admin',pw,'Administrator'))
        # create demo users
        cur.execute("SELECT id FROM users WHERE username='user'")
        if cur.fetchone() is None:
            pw = generate_password_hash('password')
            cur.execute("INSERT INTO users (username,password,name) VALUES (%s,%s,%s)",('user',pw,'Demo User'))
        cur.execute("SELECT id FROM users WHERE username='alice'")
        if cur.fetchone() is None:
            pw = generate_password_hash('password')
            cur.execute("INSERT INTO users (username,password,name) VALUES (%s,%s,%s)",('alice',pw,'Alice'))
        # ensure users are friends (user <-> alice)
        cur.execute("SELECT id FROM users WHERE username='user'")
        urow=cur.fetchone(); uid = urow['id']
        cur.execute("SELECT id FROM users WHERE username='alice'")
        arow=cur.fetchone(); aid = arow['id']
        cur.execute('SELECT id FROM friends WHERE user_id=%s AND friend_id=%s',(uid,aid))
        if not cur.fetchone():
            cur.execute('INSERT INTO friends (user_id,friend_id) VALUES (%s,%s)',(uid,aid))
        cur.execute('SELECT id FROM friends WHERE user_id=%s AND friend_id=%s',(aid,uid))
        if not cur.fetchone():
            cur.execute('INSERT INTO friends (user_id,friend_id) VALUES (%s,%s)',(aid,uid))
        # create sample moments and comments if none
        cur.execute('SELECT id FROM moments WHERE user_id=%s',(uid,))
        if not cur.fetchone():
            cur.execute('INSERT INTO moments (user_id,content) VALUES (%s,%s)',(uid,'Hello from Demo User'))
            mid = cur.lastrowid
            cur.execute('INSERT INTO comments (moment_id,user_id,content) VALUES (%s,%s,%s)',(mid,aid,'Nice post'))
        con.commit()
    except Exception as e:
        con.rollback(); print('Seed error', e)
    finally:
        con.close()

@app.route('/')
def index():
    return render_template_string("""
    <h2>简易社交平台（示例）</h2>
    <p><a href='/register'>注册</a> | <a href='/login'>登录</a> | <a href='/moments'>朋友圈</a> | <a href='/admin/login'>管理员登录</a></p>
    """)

# Registration
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        try:
            con = get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
            cur.execute('SELECT id FROM users WHERE username=%s', (username,))
            if cur.fetchone():
                flash('用户名已存在')
            else:
                pw = generate_password_hash(password)
                cur.execute('INSERT INTO users (username,password) VALUES (%s,%s)', (username,pw))
                con.commit(); flash('注册成功')
                return redirect(url_for('login'))
        except Exception as e:
            con.rollback(); flash('注册失败:'+str(e))
        finally:
            con.close()
    return render_template_string("""
    <h3>注册</h3>
    <form method='post'>用户名: <input name='username'><br>密码: <input type='password' name='password'><br><button>注册</button></form>
    """)

# Login (user)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']; password=request.form['password']
        try:
            con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
            cur.execute('SELECT * FROM users WHERE username=%s', (username,))
            user=cur.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id']=user['id']; session['username']=user['username']
                return redirect(url_for('moments'))
            flash('登录失败')
        except Exception as e:
            flash('登录错误:'+str(e))
        finally:
            con.close()
    return render_template_string("""
    <h3>用户登录</h3>
    <form method='post'>用户名: <input name='username'><br>密码: <input type='password' name='password'><br><button>登录</button></form>
    """)

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    uid = session['user_id']
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    if request.method=='POST':
        name=request.form.get('name'); gender=request.form.get('gender'); birth=request.form.get('birth'); age=request.form.get('age')
        try:
            cur.execute('UPDATE users SET name=%s, gender=%s, birthdate=%s, age=%s WHERE id=%s', (name,gender,birth or None, age or None, uid))
            con.commit(); flash('更新成功'); con.close(); return redirect(url_for('moments'))
        except Exception as e:
            con.rollback(); flash('更新失败:'+str(e))
    cur.execute('SELECT username,name,gender,birthdate,age FROM users WHERE id=%s',(uid,))
    user=cur.fetchone(); con.close()
    return render_template_string('''
    <p><a href='/'>首页</a> | <a href='/moments'>朋友圈</a> | <a href='/friends'>好友</a> | <a href='/profile'>个人</a> | <a href='/logout'>登出</a></p>
    {% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
    <h3>个人信息</h3>
    <form method='post'>姓名: <input name='name' value='{{user.name or ""}}'><br>性别: <select name='gender'><option value='O'>未知</option><option value='M'>男</option><option value='F'>女</option></select><br>出生: <input name='birth' type='date' value='{{user.birthdate}}'><br>年龄: <input name='age' value='{{user.age}}'><br><button>保存</button></form>
    ''', user=user)

# Moments and Friends listing and posting
@app.route('/moments', methods=['GET','POST'])
def moments():
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    if request.method=='POST':
        if 'user_id' not in session:
            flash('请先登录')
            return redirect(url_for('login'))
        content=request.form['content']
        try:
            if not content or len(content)>500:
                raise ValueError('内容为空或超出500字限制')
            cur.execute('INSERT INTO moments (user_id,content) VALUES (%s,%s)', (session['user_id'],content))
            con.commit(); flash('发表成功')
        except Exception as e:
            con.rollback(); flash('发表失败:'+str(e))
    # list moments: only self and friends when logged in
    if 'user_id' in session:
        uid = session['user_id']
        cur.execute('SELECT m.id,m.content,m.created_at,m.last_update,u.username,m.user_id FROM moments m JOIN users u ON m.user_id=u.id WHERE m.user_id=%s OR m.user_id IN (SELECT friend_id FROM friends WHERE user_id=%s) ORDER BY m.last_update DESC', (uid, uid))
    else:
        cur.execute('SELECT m.id,m.content,m.created_at,m.last_update,u.username,m.user_id FROM moments m JOIN users u ON m.user_id=u.id ORDER BY m.last_update DESC')
    rows=cur.fetchall(); con.close()
    return render_template_string('''
    <h3>朋友圈（仅显示自己与好友）</h3>
    {% if session.username %}
      <form method='post'>内容(<=500):<br><textarea name='content' rows=3 cols=50></textarea><br><button>发表</button></form>
    {% else %}
      <p><a href='/login'>登录</a> 可发表</p>
    {% endif %}
    <ul>
    {% for r in rows %}
      <li><b>{{r.username}}</b>: {{r.content}} <small>更新:{{r.last_update}}</small>
        {% if session.user_id == r.user_id %} <a href='/moment/{{r.id}}/edit'>编辑</a> <form style='display:inline' method='post' action='/moment/{{r.id}}/delete'><button>删除</button></form>{% endif %}
        <a href='/moment/{{r.id}}'>查看</a>
      </li>
    {% endfor %}
    </ul>
    ''', rows=rows)

@app.route('/moment/<int:mid>', methods=['GET','POST'])
def moment_view(mid):
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    if request.method=='POST':
        # add comment
        if 'user_id' not in session:
            flash('请登录')
            return redirect(url_for('login'))
        content=request.form['content']
        try:
            if not content:
                raise ValueError('评论不能为空')
            cur.execute('INSERT INTO comments (moment_id,user_id,content) VALUES (%s,%s,%s)', (mid, session['user_id'], content))
            con.commit(); flash('评论成功')
        except Exception as e:
            con.rollback(); flash('评论失败:'+str(e))
    cur.execute('SELECT m.*,u.username FROM moments m JOIN users u ON m.user_id=u.id WHERE m.id=%s',(mid,))
    moment=cur.fetchone()
    cur.execute('SELECT c.*,u.username FROM comments c JOIN users u ON c.user_id=u.id WHERE c.moment_id=%s ORDER BY c.created_at',(mid,))
    comments=cur.fetchall(); con.close()
    return render_template_string('''
    <p><a href='/'>首页</a> | <a href='/moments'>朋友圈</a> | <a href='/friends'>好友</a> | <a href='/profile'>个人</a> | <a href='/logout'>登出</a></p>
    {% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
    <h3>动态详情</h3>
    <p><b>{{moment.username}}</b>: {{moment.content}} <small>最后更新时间:{{moment.last_update}}</small></p>
    {% if session.user_id == moment.user_id %}
      <p><a href='/moment/{{moment.id}}/edit'>编辑</a> <form style='display:inline' method='post' action='/moment/{{moment.id}}/delete'><button>删除</button></form></p>
    {% endif %}
    <h4>评论</h4>
    <ul>{% for c in comments %}<li>{{c.username}}: {{c.content}}</li>{% endfor %}</ul>
    {% if session.username %}
      <form method='post'>评论:<input name='content'> <button>提交</button></form>
    {% else %}
      <p>请先登录</p>
    {% endif %}
    ''', moment=moment, comments=comments)

# Edit moment
@app.route('/moment/<int:mid>/edit', methods=['GET','POST'])
def moment_edit(mid):
    if 'user_id' not in session: return redirect(url_for('login'))
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    cur.execute('SELECT * FROM moments WHERE id=%s',(mid,))
    m=cur.fetchone()
    if not m:
        con.close(); flash('动态不存在'); return redirect(url_for('moments'))
    if m['user_id'] != session['user_id']:
        con.close(); flash('无权编辑'); return redirect(url_for('moments'))
    if request.method=='POST':
        content=request.form.get('content')
        try:
            if not content or len(content)>500: raise ValueError('内容为空或超出500字')
            cur.execute('UPDATE moments SET content=%s WHERE id=%s',(content,mid))
            con.commit(); flash('更新成功'); con.close(); return redirect(url_for('moment_view', mid=mid))
        except Exception as e:
            con.rollback(); flash('更新失败:'+str(e)); con.close(); return redirect(url_for('moment_view', mid=mid))
    con.close()
    return render_template_string('''
      <p><a href='/'>首页</a> | <a href='/moments'>朋友圈</a> | <a href='/friends'>好友</a> | <a href='/profile'>个人</a> | <a href='/logout'>登出</a></p>
      {% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
      <h3>编辑动态</h3>
      <form method='post'>内容:<br><textarea name='content' rows=4 cols=50>{{m.content}}</textarea><br><button>保存</button></form>
    ''', m=m)

# Delete moment
@app.route('/moment/<int:mid>/delete', methods=['POST'])
def moment_delete(mid):
    if 'user_id' not in session: return redirect(url_for('login'))
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    try:
        cur.execute('SELECT user_id FROM moments WHERE id=%s',(mid,))
        row=cur.fetchone()
        if not row or row['user_id']!=session['user_id']:
            flash('无权删除'); con.close(); return redirect(url_for('moments'))
        cur.execute('DELETE FROM moments WHERE id=%s',(mid,))
        con.commit(); flash('删除成功')
    except Exception as e:
        con.rollback(); flash('删除失败:'+str(e))
    finally:
        con.close()
    return redirect(url_for('moments'))

# Friends and groups
@app.route('/friends', methods=['GET','POST'])
def friends():
    if 'user_id' not in session: return redirect(url_for('login'))
    uid=session['user_id']
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    search_results=[]
    if request.method=='POST':
        action=request.form.get('action')
        if action=='search':
            q=request.form.get('username')
            cur.execute("SELECT id,username,name FROM users WHERE username LIKE %s LIMIT 20",('%'+q+'%',))
            search_results=cur.fetchall()
        elif action=='add':
            try:
                target=int(request.form.get('target_id'))
                if target==uid: raise ValueError('不能添加自己为好友')
                cur.execute('SELECT id FROM users WHERE id=%s',(target,))
                if not cur.fetchone(): raise ValueError('用户不存在')
                # insert directional friendship if not exists
                cur.execute('SELECT id FROM friends WHERE user_id=%s AND friend_id=%s',(uid,target))
                if not cur.fetchone():
                    cur.execute('INSERT INTO friends (user_id,friend_id) VALUES (%s,%s)',(uid,target))
                # also insert reciprocal to represent mutual friendship
                cur.execute('SELECT id FROM friends WHERE user_id=%s AND friend_id=%s',(target,uid))
                if not cur.fetchone():
                    cur.execute('INSERT INTO friends (user_id,friend_id) VALUES (%s,%s)',(target,uid))
                con.commit(); flash('已添加为好友')
            except Exception as e:
                con.rollback(); flash('添加好友失败:'+str(e))
        elif action=='create_group':
            name=request.form.get('group_name')
            if name:
                try:
                    cur.execute('INSERT INTO friend_groups (user_id,name) VALUES (%s,%s)',(uid,name))
                    con.commit(); flash('分组创建成功')
                except Exception as e:
                    con.rollback(); flash('创建分组失败:'+str(e))
    # fetch groups and friends
    cur.execute('SELECT id,name FROM friend_groups WHERE user_id=%s',(uid,))
    groups=cur.fetchall()
    cur.execute('SELECT f.id as fid,u.id as uid,u.username,fg.name as group_name FROM friends f JOIN users u ON f.friend_id=u.id LEFT JOIN friend_groups fg ON f.group_id=fg.id WHERE f.user_id=%s',(uid,))
    friends_list=cur.fetchall(); con.close()
    return render_template_string('''
      <p><a href='/'>首页</a> | <a href='/moments'>朋友圈</a> | <a href='/friends'>好友</a> | <a href='/profile'>个人</a> | <a href='/logout'>登出</a></p>
      {% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
      <h3>好友管理</h3>
      <h4>创建分组</h4>
      <form method='post'><input name='group_name'> <button name='action' value='create_group'>创建</button></form>
      <h4>搜索用户</h4>
      <form method='post'>用户名:<input name='username'> <button name='action' value='search'>搜索</button></form>
      {% if search_results %}
        <ul>{% for s in search_results %}<li>{{s.username}} ({{s.name}}) <form style='display:inline' method='post'><button name='action' value='add' type='submit'>添加</button><input type='hidden' name='target_id' value='{{s.id}}'></form></li>{% endfor %}</ul>
      {% endif %}
      <h4>我的好友</h4>
      <ul>{% for f in friends_list %}<li>{{f.username}} - 分组: {{f.group_name or '未分组'}} <form style='display:inline' method='post' action='/friend/remove/{{f.uid}}'><button>删除</button></form></li>{% endfor %}</ul>
      <h4>分组</h4>
      <ul>{% for g in groups %}<li>{{g.name}} (ID:{{g.id}})</li>{% endfor %}</ul>
    ''', search_results=search_results, friends_list=friends_list, groups=groups)

@app.route('/friend/remove/<int:fid>', methods=['POST'])
def friend_remove(fid):
    if 'user_id' not in session: return redirect(url_for('login'))
    uid=session['user_id']
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    try:
        cur.execute('DELETE FROM friends WHERE user_id=%s AND friend_id=%s',(uid,fid))
        cur.execute('DELETE FROM friends WHERE user_id=%s AND friend_id=%s',(fid,uid))
        con.commit(); flash('已移除好友')
    except Exception as e:
        con.rollback(); flash('移除失败:'+str(e))
    finally:
        con.close()
    return redirect(url_for('friends'))

@app.route('/friend/assign/<int:fid>', methods=['POST'])
def friend_assign(fid):
    if 'user_id' not in session: return redirect(url_for('login'))
    uid = session['user_id']
    group_id = request.form.get('group_id')
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    try:
        if group_id:
            cur.execute('SELECT id FROM friend_groups WHERE id=%s AND user_id=%s',(group_id,uid))
            if not cur.fetchone(): raise ValueError('分组不存在')
        cur.execute('UPDATE friends SET group_id=%s WHERE user_id=%s AND friend_id=%s',(group_id or None, uid, fid))
        con.commit(); flash('分组分配成功')
    except Exception as e:
        con.rollback(); flash('分配失败:'+str(e))
    finally:
        con.close()
    return redirect(url_for('friends'))

@app.route('/admin/moment/delete/<int:mid>', methods=['POST'])
def admin_delete_moment(mid):
    if 'admin_id' not in session: return redirect(url_for('admin_login'))
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    try:
        cur.execute('DELETE FROM moments WHERE id=%s',(mid,))
        con.commit(); flash('动态已删除')
    except Exception as e:
        con.rollback(); flash('删除失败:'+str(e))
    finally:
        con.close()
    return redirect(url_for('admin_panel'))


# Admin login and delete user
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        u=request.form['username']; p=request.form['password']
        try:
            con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
            cur.execute('SELECT * FROM admins WHERE username=%s',(u,))
            a=cur.fetchone()
            if a and check_password_hash(a['password'], p):
                session['admin_id']=a['id']; session['admin']=a['username']; return redirect(url_for('admin_panel'))
            flash('登录失败')
        except Exception as e:
            flash(str(e))
        finally:
            con.close()
    return render_template_string("""
    <p><a href='/'>首页</a></p>
    {% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
    <h3>管理员登录</h3>
    <form method='post'>用户名:<input name='username'><br>密码:<input type='password' name='password'><br><button>登录</button></form>
    """)

@app.route('/admin/profile', methods=['GET','POST'])
def admin_profile():
    if 'admin_id' not in session: return redirect(url_for('admin_login'))
    aid = session['admin_id']
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    if request.method=='POST':
        name = request.form.get('name')
        password = request.form.get('password')
        try:
            if password:
                pw = generate_password_hash(password)
                cur.execute('UPDATE admins SET name=%s, password=%s WHERE id=%s', (name, pw, aid))
            else:
                cur.execute('UPDATE admins SET name=%s WHERE id=%s', (name, aid))
            con.commit(); flash('更新成功')
        except Exception as e:
            con.rollback(); flash('更新失败:'+str(e))
        finally:
            con.close()
        return redirect(url_for('admin_panel'))
    cur.execute('SELECT username,name FROM admins WHERE id=%s',(aid,))
    admin=cur.fetchone(); con.close()
    return render_template_string('''
    <p><a href='/admin'>管理员面板</a> | <a href='/admin/profile'>个人</a> | <a href='/admin/logout'>登出</a></p>
    {% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
    <h3>管理员个人信息</h3>
    <form method='post'>用户名: <b>{{admin.username}}</b><br>姓名: <input name='name' value='{{admin.name or ""}}'><br>新密码: <input type='password' name='password'><br><button>保存</button></form>
    ''', admin=admin)

@app.route('/admin', methods=['GET','POST'])
def admin_panel():
    if 'admin_id' not in session: return redirect(url_for('admin_login'))
    if request.method=='POST':
        # delete user transactionally
        uid = request.form.get('delete_user')
        if uid:
            con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
            try:
                cur.execute('START TRANSACTION')
                # delete user will cascade to friends, moments, comments
                cur.execute('DELETE FROM users WHERE id=%s',(uid,))
                con.commit(); flash('用户及相关数据已删除')
            except Exception as e:
                con.rollback(); flash('删除失败:'+str(e))
            finally:
                con.close()
    # show all moments
    con=get_conn(); cur=con.cursor(); cur.execute('USE '+DB_NAME)
    cur.execute('SELECT m.id,m.content,m.last_update,u.username FROM moments m JOIN users u ON m.user_id=u.id')
    moments=cur.fetchall(); con.close()
    return render_template_string('''
    <p><a href='/admin'>管理员面板</a> | <a href='/admin/profile'>个人</a> | <a href='/admin/logout'>登出</a></p>
    {% with messages = get_flashed_messages() %}{% if messages %}<ul>{% for m in messages %}<li>{{m}}</li>{% endfor %}</ul>{% endif %}{% endwith %}
    <h3>管理员面板</h3>
    <h4>所有动态</h4>
    <ul>{% for m in moments %}<li>{{m.username}}: {{m.content}} <small>{{m.last_update}}</small> <form style='display:inline' method='post' action='/admin/moment/delete/{{m.id}}'><button>删除</button></form></li>{% endfor %}</ul>
    <h4>删除用户（会删除其所有相关信息）</h4>
    <form method='post'>用户ID: <input name='delete_user'> <button>删除</button></form>
    ''', moments=moments)

@app.route('/logout')
def logout():
    session.clear(); flash('已登出'); return redirect(url_for('index'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None); session.pop('admin', None); flash('管理员已登出'); return redirect(url_for('index'))

if __name__=='__main__':
    # initialize DB and seed demo accounts
    print('Initializing DB...')
    init_db(); ensure_seed()
    app.run(debug=True)
