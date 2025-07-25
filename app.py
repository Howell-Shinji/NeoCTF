#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTF Platform - Neon Night Theme
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
import uuid
import json
from utils.ai_api import CTFSecurityAI
from config import config as app_config
from openai import OpenAI
import random # Added for random.randint

# 创建应用实例
app = Flask(__name__)

app.jinja_env.globals.update(min=min, max=max)

# 加载配置
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app.config.from_object(app_config[config_name])

# 覆盖数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:passward@localhost/ctf_platform'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化扩展
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录访问此页面'
login_manager.login_message_category = 'info'

# 初始化AI接口
ctf_ai = CTFSecurityAI()
# 设置API密钥和模型URL
if app.config.get('DEEPSEEK_API_KEY'):
    os.environ['DEEPSEEK_API_KEY'] = app.config.get('DEEPSEEK_API_KEY')
if app.config.get('QWEN_API_KEY'):
    os.environ['QWEN_API_KEY'] = app.config.get('QWEN_API_KEY')
# 更新模型URL
if app.config.get('LOCAL_MODEL_URL'):
    ctf_ai.local_url = app.config.get('LOCAL_MODEL_URL')
if app.config.get('LAN_MODEL_URL'):
    ctf_ai.lan_url = app.config.get('LAN_MODEL_URL')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 数据库模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    last_submit = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    submissions = db.relationship('Submission', backref='user', lazy=True)
    hint_unlocks = db.relationship('HintUnlock', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#7aa2f7')  # Neon Night blue
    
    # 关系
    challenges = db.relationship('Challenge', backref='category', lazy=True)

class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    flag = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=100)
    difficulty = db.Column(db.String(20), default='Easy')  # Easy, Medium, Hard
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_ai_generated = db.Column(db.Boolean, default=False)  # 是否由AI生成
    ai_scenario_data = db.Column(db.Text, nullable=True)  # AI场景数据(JSON)
    
    # 外键
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # 关系
    submissions = db.relationship('Submission', backref='challenge', lazy=True)
    hints = db.relationship('Hint', backref='challenge', lazy=True, cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='challenge', lazy=True, cascade='all, delete-orphan')
    attack_simulations = db.relationship('AttackSimulation', backref='challenge', lazy=True, cascade='all, delete-orphan')

class Hint(db.Model):
    __tablename__ = 'hints'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Integer, default=10)  # 提示消耗的分数
    
    # 外键
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    
    # 关系
    unlocks = db.relationship('HintUnlock', backref='hint', lazy=True)

class HintUnlock(db.Model):
    __tablename__ = 'hint_unlocks'
    
    id = db.Column(db.Integer, primary_key=True)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hint_id = db.Column(db.Integer, db.ForeignKey('hints.id'), nullable=False)

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    
    # 外键
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    flag_submitted = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    points_awarded = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)

# 新增AI攻击模拟模型
class AttackSimulation(db.Model):
    __tablename__ = 'attack_simulations'
    
    id = db.Column(db.Integer, primary_key=True)
    attack_type = db.Column(db.String(100), nullable=False)
    attack_level = db.Column(db.String(50), default='basic')
    simulation_result = db.Column(db.Text, nullable=False)
    success_probability = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)

# 新增防御策略模型
class DefenseStrategy(db.Model):
    __tablename__ = 'defense_strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    defense_level = db.Column(db.String(50), default='standard')
    strategy_content = db.Column(db.Text, nullable=False)
    estimated_effectiveness = db.Column(db.Integer, default=70)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    simulation_id = db.Column(db.Integer, db.ForeignKey('attack_simulations.id'), nullable=False)
    
    # 关系
    simulation = db.relationship('AttackSimulation', backref='defense_strategies', lazy=True)

# 新增用户评估模型
class UserEvaluation(db.Model):
    __tablename__ = 'user_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_report = db.Column(db.Text, nullable=False)
    overall_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关系
    user = db.relationship('User', backref='evaluations', lazy=True)

# 新增用户AI使用记录模型
class UserAIUsage(db.Model):
    __tablename__ = 'user_ai_usages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feature_type = db.Column(db.String(50), nullable=False) # 'defense_advice', 'security_learning'
    query = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='ai_usages', lazy=True)

# 路由
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/admin_ai')
@login_required
def admin_ai():
    if not current_user.is_admin:
        flash('权限不足', 'error')
        return redirect(url_for('dashboard'))
        
    # 获取所有挑战
    challenges = Challenge.query.all()
    
    # 获取所有攻击模拟
    simulations = AttackSimulation.query.order_by(AttackSimulation.created_at.desc()).all()
    
    # 获取所有用户
    users = User.query.filter(User.score > 0).order_by(User.score.desc()).all()
    
    return render_template('admin/ai_dashboard.html', 
                          challenges=challenges, 
                          simulations=simulations,
                          users=users,
                          config=app.config)

@app.route('/tools')
@login_required
def tools():
    """工具页面"""
    return render_template('tools.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # 验证
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('密码确认不匹配', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('密码长度至少6位', 'error')
            return render_template('register.html')
        
        # 创建用户
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已成功登出', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # 获取统计数据
    total_challenges = Challenge.query.filter_by(is_active=True).count()
    solved_challenges = db.session.query(Submission.challenge_id).filter_by(
        user_id=current_user.id, is_correct=True
    ).distinct().count()
    
    # 获取最近的提交
    recent_submissions = Submission.query.filter_by(user_id=current_user.id)\
        .order_by(Submission.submitted_at.desc()).limit(5).all()
    
    # 获取排行榜前10
    top_users = User.query.order_by(User.score.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         total_challenges=total_challenges,
                         solved_challenges=solved_challenges,
                         recent_submissions=recent_submissions,
                         top_users=top_users)

@app.route('/challenges')
@login_required
def challenges():
    categories = Category.query.all()
    selected_category = request.args.get('category')
    
    if selected_category:
        challenges = Challenge.query.filter_by(
            category_id=selected_category, is_active=True
        ).all()
    else:
        challenges = Challenge.query.filter_by(is_active=True).all()
    
    # 获取用户已解决的题目
    solved_challenge_ids = [s.challenge_id for s in 
                           Submission.query.filter_by(
                               user_id=current_user.id, is_correct=True
                           ).all()]
    
    return render_template('challenges.html', 
                         categories=categories, 
                         challenges=challenges,
                         solved_challenge_ids=solved_challenge_ids,
                         selected_category=selected_category)

@app.route('/challenge/<int:challenge_id>')
@login_required
def challenge_detail(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # 检查是否已解决
    is_solved = Submission.query.filter_by(
        user_id=current_user.id, 
        challenge_id=challenge_id, 
        is_correct=True
    ).first() is not None
    
    # 获取提交历史
    submissions = Submission.query.filter_by(
        user_id=current_user.id, 
        challenge_id=challenge_id
    ).order_by(Submission.submitted_at.desc()).all()
    
    # 获取已解锁的提示
    unlocked_hints = []
    if challenge.hints:
        hint_unlocks = HintUnlock.query.filter_by(user_id=current_user.id).all()
        unlocked_hint_ids = [hu.hint_id for hu in hint_unlocks]
        unlocked_hints = [hint for hint in challenge.hints if hint.id in unlocked_hint_ids]
    
    return render_template('challenge_detail.html', 
                         challenge=challenge, 
                         is_solved=is_solved,
                         submissions=submissions,
                         unlocked_hints=unlocked_hints)

@app.route('/submit_flag', methods=['POST'])
@login_required
def submit_flag():
    challenge_id = request.form['challenge_id']
    flag = request.form['flag'].strip()
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # 检查是否已解决
    existing_correct = Submission.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge_id,
        is_correct=True
    ).first()
    
    if existing_correct:
        flash('你已经解决了这道题目！', 'info')
        return redirect(url_for('challenge_detail', challenge_id=challenge_id))
    
    # 创建提交记录
    is_correct = flag == challenge.flag
    points = challenge.points if is_correct else 0
    
    submission = Submission(
        user_id=current_user.id,
        challenge_id=challenge_id,
        flag_submitted=flag,
        is_correct=is_correct,
        points_awarded=points
    )
    
    db.session.add(submission)
    
    if is_correct:
        # 更新用户分数
        current_user.score += points
        current_user.last_submit = datetime.utcnow()
        flash(f'恭喜！Flag正确，获得{points}分！', 'success')
    else:
        flash('Flag错误，请重试', 'error')
    
    db.session.commit()
    
    return redirect(url_for('challenge_detail', challenge_id=challenge_id))

# 提示解锁功能
@app.route('/unlock_hint', methods=['POST'])
@login_required
def unlock_hint():
    hint_id = request.form['hint_id']
    hint = Hint.query.get_or_404(hint_id)
    
    # 检查是否已解锁
    existing_unlock = HintUnlock.query.filter_by(
        user_id=current_user.id,
        hint_id=hint_id
    ).first()
    
    if existing_unlock:
        return jsonify({'success': False, 'message': '提示已解锁'})
    
    # 检查分数是否足够
    if current_user.score < hint.cost:
        return jsonify({'success': False, 'message': f'分数不足，需要{hint.cost}分'})
    
    # 扣除分数并解锁提示
    current_user.score -= hint.cost
    hint_unlock = HintUnlock(user_id=current_user.id, hint_id=hint_id)
    db.session.add(hint_unlock)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'提示已解锁，消耗{hint.cost}分',
        'hint_content': hint.content,
        'new_score': current_user.score
    })

# 附件下载功能
@app.route('/download/<int:attachment_id>')
@login_required
def download_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # 检查文件是否存在
    if not os.path.exists(attachment.filepath):
        abort(404)
    
    return send_file(
        attachment.filepath,
        as_attachment=True,
        download_name=attachment.original_filename
    )

@app.route('/scoreboard')
@login_required
def scoreboard():
    users = User.query.filter(User.score > 0).order_by(
        User.score.desc(), 
        User.last_submit.asc()
    ).all()
    
    # 为每个用户计算解题进度百分比
    for user in users:
        solved_count = db.session.query(Submission.challenge_id).filter_by(
            user_id=user.id, is_correct=True
        ).distinct().count()
        
        # 计算进度百分比，确保不超过100%
        user.progress_percentage = min(solved_count / 50 * 100, 100)
    
    return render_template('scoreboard.html', users=users)

# 管理员路由
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('权限不足', 'error')
        return redirect(url_for('dashboard'))
    
    # 统计数据
    total_users = User.query.count()
    total_challenges = Challenge.query.count()
    total_submissions = Submission.query.count()
    correct_submissions = Submission.query.filter_by(is_correct=True).count()
    
    # 最近活动
    recent_submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_challenges=total_challenges,
                         total_submissions=total_submissions,
                         correct_submissions=correct_submissions,
                         recent_submissions=recent_submissions,
                         recent_users=recent_users)

@app.route('/admin/challenges')
@login_required
def admin_challenges():
    if not current_user.is_admin:
        flash('权限不足', 'error')
        return redirect(url_for('dashboard'))
    
    challenges = Challenge.query.all()
    categories = Category.query.all()
    
    return render_template('admin/challenges.html', 
                         challenges=challenges, 
                         categories=categories)

# 添加题目
@app.route('/admin/add_challenge', methods=['POST'])
@login_required
def admin_add_challenge():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        title = request.form['title']
        description = request.form['description']
        flag = request.form['flag']
        points = int(request.form['points'])
        difficulty = request.form['difficulty']
        category_id = int(request.form['category_id'])
        
        challenge = Challenge(
            title=title,
            description=description,
            flag=flag,
            points=points,
            difficulty=difficulty,
            category_id=category_id
        )
        
        db.session.add(challenge)
        db.session.flush()  # 获取challenge.id
        
        # 处理附件上传
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    
                    attachment = Attachment(
                        filename=unique_filename,
                        original_filename=filename,
                        filepath=file_path,
                        challenge_id=challenge.id
                    )
                    db.session.add(attachment)
        
        # 处理提示
        hints_data = request.form.get('hints', '')
        if hints_data:
            import json
            try:
                hints = json.loads(hints_data)
                for hint_data in hints:
                    hint = Hint(
                        content=hint_data['content'],
                        cost=int(hint_data['cost']),
                        challenge_id=challenge.id
                    )
                    db.session.add(hint)
            except json.JSONDecodeError:
                pass
        
        db.session.commit()
        return jsonify({'success': True, 'message': '题目添加成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})

# 编辑题目
@app.route('/admin/edit_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def admin_edit_challenge(challenge_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '权限不足'})
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    try:
        challenge.title = request.form['title']
        challenge.description = request.form['description']
        challenge.flag = request.form['flag']
        challenge.points = int(request.form['points'])
        challenge.difficulty = request.form['difficulty']
        challenge.category_id = int(request.form['category_id'])
        challenge.is_active = request.form.get('is_active') == 'true'
        
        db.session.commit()
        return jsonify({'success': True, 'message': '题目更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})

# 删除题目
@app.route('/admin/delete_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def admin_delete_challenge(challenge_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '权限不足'})
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    try:
        # 删除相关附件文件
        for attachment in challenge.attachments:
            if os.path.exists(attachment.filepath):
                os.remove(attachment.filepath)
        
        db.session.delete(challenge)
        db.session.commit()
        return jsonify({'success': True, 'message': '题目删除成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('权限不足', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# 用户管理
@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_admin(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '权限不足'})
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能修改自己的管理员权限'})
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = '管理员' if user.is_admin else '普通用户'
    return jsonify({'success': True, 'message': f'用户{user.username}已设置为{status}'})

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '权限不足'})
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能删除自己的账户'})
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'用户{user.username}已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})

# API路由
@app.route('/api/stats')
@login_required
def api_stats():
    stats = {
        'total_users': User.query.count(),
        'total_challenges': Challenge.query.filter_by(is_active=True).count(),
        'total_submissions': Submission.query.count(),
        'correct_submissions': Submission.query.filter_by(is_correct=True).count()
    }
    return jsonify(stats)

@app.route('/api/challenge/<int:challenge_id>')
@login_required
def api_challenge_detail(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    
    return jsonify({
        'id': challenge.id,
        'title': challenge.title,
        'description': challenge.description,
        'points': challenge.points,
        'difficulty': challenge.difficulty,
        'category': challenge.category.name,
        'attachments': [
            {
                'id': att.id,
                'filename': att.original_filename
            } for att in challenge.attachments
        ],
        'hints': [
            {
                'id': hint.id,
                'cost': hint.cost,
                'unlocked': HintUnlock.query.filter_by(
                    user_id=current_user.id, 
                    hint_id=hint.id
                ).first() is not None
            } for hint in challenge.hints
        ]
    })

@app.route('/api/user/<int:user_id>')
@login_required
def api_user_detail(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # 计算解题统计
    solved_challenges = Submission.query.filter_by(
        user_id=user_id, is_correct=True
    ).distinct(Submission.challenge_id).count()
    
    total_submissions = Submission.query.filter_by(user_id=user_id).count()
    correct_submissions = Submission.query.filter_by(
        user_id=user_id, is_correct=True
    ).count()
    
    success_rate = '0%'
    if total_submissions > 0:
        success_rate = f"{(correct_submissions / total_submissions * 100):.1f}%"
    
    # 获取最近提交
    recent_submissions = db.session.query(
        Submission, Challenge.title.label('challenge_title')
    ).join(Challenge).filter(
        Submission.user_id == user_id
    ).order_by(Submission.submitted_at.desc()).limit(10).all()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'score': user.score,
        'created_at': user.created_at.isoformat(),
        'last_submit': user.last_submit.isoformat() if user.last_submit else None,
        'solved_challenges': solved_challenges,
        'total_submissions': total_submissions,
        'success_rate': success_rate,
        'recent_submissions': [
            {
                'challenge_title': sub.challenge_title,
                'is_correct': sub.Submission.is_correct,
                'submitted_at': sub.Submission.submitted_at.isoformat(),
                'points_awarded': sub.Submission.points_awarded
            } for sub in recent_submissions
        ]
    })

# 新增AI相关路由
@app.route('/api/generate_scenario', methods=['POST'])
@login_required
def api_generate_scenario():
    """生成动态场景"""
    data = request.get_json()
    difficulty = data.get('difficulty', 'Medium')
    category = data.get('category', 'Web')
    context = data.get('context', None)
    
    try:
        # 获取模型选项
        model_option = data.get('model_option', 'Qwen3.0-Local')
        
        # 调用AI接口生成场景
        scenario = ctf_ai.generate_dynamic_scenario(difficulty, category, context, model_option=model_option)
        
        # 如果是管理员，创建新的挑战
        if current_user.is_admin:
            category_obj = Category.query.filter_by(name=category).first()
            if not category_obj:
                return jsonify({'success': False, 'message': f'未找到{category}类别'})
            
            # 创建challenge对象
            challenge = Challenge(
                title=scenario.get('title', f'AI生成{category}挑战'),
                description=scenario.get('description', ''),
                flag=scenario.get('flag', f'flag{{{uuid.uuid4()}}}'),
                points=int(scenario.get('difficulty_score', 0)) or 100,
                difficulty=difficulty,
                category_id=category_obj.id,
                is_ai_generated=True,
                ai_scenario_data=json.dumps(scenario, ensure_ascii=False)
            )
            db.session.add(challenge)
            db.session.commit()
            
            # 添加提示
            if 'hints' in scenario and isinstance(scenario['hints'], list):
                for i, hint_text in enumerate(scenario['hints']):
                    hint_content = hint_text.get('content', hint_text) if isinstance(hint_text, dict) else hint_text
                    hint = Hint(
                        content=hint_content,
                        cost=10 + i * 5,  # 提示成本递增
                        challenge_id=challenge.id
                    )
                    db.session.add(hint)
            
            db.session.commit()
            return jsonify({'success': True, 'scenario': scenario, 'challenge_id': challenge.id})
        else:
            # 普通用户只返回场景，不创建挑战
            return jsonify({'success': True, 'scenario': scenario})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成场景失败：{str(e)}'})

@app.route('/api/simulate_attack/<int:challenge_id>', methods=['POST'])
@login_required
def api_simulate_attack(challenge_id):
    """模拟攻击"""
    challenge = Challenge.query.get_or_404(challenge_id)
    
    data = request.get_json()
    attack_level = data.get('attack_level', 'basic')
    target_info = data.get('target_info', None)
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    try:
        # 获取场景数据
        if challenge.ai_scenario_data:
            scenario_data = json.loads(challenge.ai_scenario_data)
        else:
            scenario_data = {
                "title": challenge.title,
                "description": challenge.description,
                "category": challenge.category.name,
                "difficulty": challenge.difficulty
            }
        
        # 调用AI接口模拟攻击
        attack_result = ctf_ai.simulate_attack(scenario_data, target_info, attack_level, model_option=model_option)
        
        # 保存攻击模拟结果
        simulation = AttackSimulation(
            attack_type=attack_result['attack_type'],
            attack_level=attack_result['attack_level'],
            simulation_result=attack_result['simulation_result'],
            success_probability=attack_result['success_probability'],
            challenge_id=challenge.id
        )
        db.session.add(simulation)
        db.session.commit()
        
        return jsonify({'success': True, 'simulation': attack_result, 'simulation_id': simulation.id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'模拟攻击失败：{str(e)}'})

@app.route('/api/generate_defense/<int:simulation_id>', methods=['POST'])
@login_required
def api_generate_defense(simulation_id):
    """生成防御策略"""
    simulation = AttackSimulation.query.get_or_404(simulation_id)
    
    data = request.get_json()
    defense_level = data.get('defense_level', 'standard')
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    try:
        # 构建攻击数据
        attack_data = {
            "attack_type": simulation.attack_type,
            "attack_level": simulation.attack_level,
            "simulation_result": simulation.simulation_result,
            "success_probability": simulation.success_probability
        }
        
        # 调用AI接口生成防御策略
        defense_result = ctf_ai.adaptive_defense(attack_data, defense_level=defense_level, model_option=model_option)
        
        # 保存防御策略
        defense = DefenseStrategy(
            defense_level=defense_result['defense_level'],
            strategy_content=defense_result['defense_strategy'],
            estimated_effectiveness=defense_result['estimated_effectiveness'],
            simulation_id=simulation.id
        )
        db.session.add(defense)
        db.session.commit()
        
        return jsonify({'success': True, 'defense': defense_result, 'defense_id': defense.id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成防御策略失败：{str(e)}'})

@app.route('/api/evaluate_user/<int:user_id>', methods=['POST'])
@login_required
def api_evaluate_user(user_id):
    """评估用户能力"""
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'success': False, 'message': '权限不足'})
    
    data = request.get_json()
    model_option = data.get('model_option', 'Qwen3.0-Local') if request.is_json else 'Qwen3.0-Local'
    
    try:
        user = User.query.get_or_404(user_id)
        
        # 获取用户信息
        user_data = {
            'username': user.username,
            'score': user.score,
            'joined_at': user.created_at.isoformat()
        }
        
        # 获取用户挑战信息
        submissions = Submission.query.filter_by(user_id=user.id).all()
        solved_challenges = {}
        
        for sub in submissions:
            if sub.is_correct and sub.challenge_id not in solved_challenges:
                challenge = Challenge.query.get(sub.challenge_id)
                solved_challenges[sub.challenge_id] = {
                    'title': challenge.title,
                    'category': challenge.category.name,
                    'difficulty': challenge.difficulty,
                    'points': challenge.points,
                    'solved_at': sub.submitted_at.isoformat()
                }
        
        # 获取提交历史
        submission_history = []
        for sub in submissions:
            challenge = Challenge.query.get(sub.challenge_id)
            submission_history.append({
                'challenge_title': challenge.title,
                'category': challenge.category.name,
                'submitted_at': sub.submitted_at.isoformat(),
                'is_correct': sub.is_correct
            })
        
        # 调用AI生成评估报告
        challenge_data = list(solved_challenges.values())
        evaluation_result = ctf_ai.generate_evaluation_report(
            user_data, challenge_data, submission_history, model_option=model_option
        )
        
        # 尝试从报告中提取总体评分
        try:
            report = evaluation_result['evaluation_report']
            # 尝试匹配报告中的评分数字
            import re
            score_matches = re.findall(r'整体能力评分[：:]\s*(\d+)', report)
            overall_score = int(score_matches[0]) if score_matches else 0
        except:
            overall_score = 0
        
        # 保存评估结果
        user_eval = UserEvaluation(
            user_id=user.id,
            evaluation_report=evaluation_result['evaluation_report'],
            overall_score=overall_score
        )
        db.session.add(user_eval)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户能力评估完成',
            'evaluation_result': evaluation_result,
            'evaluation_id': user_eval.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'用户评估失败：{str(e)}'})

@app.route('/api/suggest_solution/<int:challenge_id>', methods=['POST'])
@login_required
def api_suggest_solution(challenge_id):
    """获取题目解决方案建议"""
    challenge = Challenge.query.get_or_404(challenge_id)
    
    if not challenge.is_active:
        return jsonify({'success': False, 'message': '该挑战不可用'})
    
    data = request.get_json()
    partial_solution = data.get('partial_solution', None)
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    try:
        # 获取挑战信息
        challenge_data = {
            'title': challenge.title,
            'description': challenge.description,
            'category': challenge.category.name,
            'difficulty': challenge.difficulty
        }
        
        # 如果是AI生成的挑战，添加场景数据
        if challenge.is_ai_generated and challenge.ai_scenario_data:
            try:
                scenario_data = json.loads(challenge.ai_scenario_data)
                challenge_data.update({
                    'technical_details': scenario_data.get('technical_details', ''),
                    'background_story': scenario_data.get('background_story', '')
                })
            except:
                pass
        
        # 调用AI提供解决方案建议
        solution_result = ctf_ai.suggest_challenge_solution(challenge_data, partial_solution, model_option=model_option)
        
        return jsonify({
            'success': True,
            'message': '解决方案建议生成成功',
            'suggestion': solution_result['solution_suggestion']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成解决方案建议失败：{str(e)}'})

# 新增API配置更新路由
@app.route('/api/update_ai_config', methods=['POST'])
@login_required
def api_update_ai_config():
    """更新AI API配置"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '权限不足'})
    
    data = request.get_json()
    
    try:
        # 更新环境变量
        if 'deepseek_api_key' in data and data['deepseek_api_key']:
            os.environ['DEEPSEEK_API_KEY'] = data['deepseek_api_key']
            app.config['DEEPSEEK_API_KEY'] = data['deepseek_api_key']
        
        if 'qwen_api_key' in data and data['qwen_api_key']:
            os.environ['QWEN_API_KEY'] = data['qwen_api_key']
            app.config['QWEN_API_KEY'] = data['qwen_api_key']
        
        # 更新模型URL
        if 'local_model_url' in data and data['local_model_url']:
            app.config['LOCAL_MODEL_URL'] = data['local_model_url']
            ctf_ai.local_url = data['local_model_url']
        
        if 'lan_model_url' in data and data['lan_model_url']:
            app.config['LAN_MODEL_URL'] = data['lan_model_url']
            ctf_ai.lan_url = data['lan_model_url']
        
        # 重新初始化AI客户端
        if app.config.get('DEEPSEEK_API_KEY'):
            ctf_ai.deepseek_api_key = app.config.get('DEEPSEEK_API_KEY')
            ctf_ai.deepseek_client = OpenAI(
                api_key=ctf_ai.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
        
        if app.config.get('QWEN_API_KEY'):
            ctf_ai.qwen_api_key = app.config.get('QWEN_API_KEY')
            ctf_ai.qwen_headers = {
                "Authorization": f"Bearer {ctf_ai.qwen_api_key}",
                "Content-Type": "application/json"
            }
        
        return jsonify({'success': True, 'message': 'API配置已更新'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新配置失败: {str(e)}'})

# 导航栏添加AI训练场链接
@app.context_processor
def inject_menu_items():
    menu_items = [
        {'name': '仪表板', 'url': url_for('dashboard'), 'icon': 'fas fa-tachometer-alt'},
        {'name': '挑战', 'url': url_for('challenges'), 'icon': 'fas fa-flag'},
        {'name': '排行榜', 'url': url_for('scoreboard'), 'icon': 'fas fa-trophy'},
        {'name': 'AI训练场', 'url': url_for('ai_arena'), 'icon': 'fas fa-robot'}
    ]
    
    if current_user.is_authenticated and current_user.is_admin:
        menu_items.append({'name': '管理', 'url': url_for('admin'), 'icon': 'fas fa-cog'})
    
    return {'menu_items': menu_items}

# AI训练场路由
@app.route('/ai-arena')
@login_required
def ai_arena():
    """AI安全训练场，普通用户可以使用AI-Agent进行攻防训练"""
    # 获取所有挑战
    challenges = Challenge.query.filter_by(is_active=True).all()
    
    return render_template('ai_arena.html', challenges=challenges)

@app.route('/api/simulate_apt_attack', methods=['POST'])
@login_required
def api_simulate_apt_attack():
    """APT攻击链模拟"""
    data = request.get_json()
    target_info = data.get('target_info', '')
    attack_phases = data.get('attack_phases', [])
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    if not target_info:
        return jsonify({'success': False, 'message': '请提供目标系统信息'})
    
    try:
        # 构建攻击链模拟提示
        prompt = f"""
        作为一个网络安全专家，请模拟针对以下目标系统的APT攻击链：
        
        目标系统信息：
        {target_info}
        
        攻击阶段：
        {', '.join(attack_phases)}
        
        请详细描述每个攻击阶段的具体步骤、使用的技术和工具。
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = ctf_ai.get_model_request(messages, model_option=model_option)
        
        return jsonify({
            'success': True,
            'simulation': {
                'result': result,
                'attack_phases': attack_phases,
                'target_info': target_info
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/simulate_social_engineering', methods=['POST'])
@login_required
def api_simulate_social_engineering():
    """社会工程学攻击模拟"""
    data = request.get_json()
    target_info = data.get('target_info', '')
    attack_type = data.get('attack_type', '钓鱼邮件')
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    if not target_info:
        return jsonify({'success': False, 'message': '请提供目标信息'})
    
    try:
        prompt = f"""
        作为一个网络安全专家，请模拟以下社会工程学攻击场景：
        
        攻击类型：{attack_type}
        目标信息：{target_info}
        
        请详细描述攻击过程、可能的成功率和防范措施。
        注意：这是用于安全教育目的的模拟。
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = ctf_ai.get_model_request(messages, model_option=model_option)
        
        return jsonify({
            'success': True,
            'simulation': {
                'result': result,
                'attack_type': attack_type,
                'target_info': target_info
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/generate_adaptive_defense', methods=['POST'])
@login_required
def api_generate_adaptive_defense():
    """生成自适应防御策略"""
    data = request.get_json()
    attack_data = data.get('attack_data', '')
    system_config = data.get('system_config', '')
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    if not attack_data:
        return jsonify({'success': False, 'message': '请提供攻击数据'})
    
    try:
        prompt = f"""
        作为一个网络安全防御专家，请为以下攻击场景生成自适应防御策略：
        
        攻击数据：
        {attack_data}
        
        系统配置：
        {system_config}
        
        请提供：
        1. 威胁分析
        2. 具体的防御措施
        3. 自适应响应策略
        4. 预防类似攻击的建议
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = ctf_ai.get_model_request(messages, model_option=model_option)
        
        return jsonify({
            'success': True,
            'defense': {
                'content': result,
                'attack_data': attack_data,
                'system_config': system_config
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/evaluate_attack_defense', methods=['POST'])
@login_required
def api_evaluate_attack_defense():
    """攻防演练评估"""
    data = request.get_json()
    simulation_id = data.get('simulation_id', '')
    defense_id = data.get('defense_id', '')
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    if not simulation_id or not defense_id:
        return jsonify({'success': False, 'message': '请选择攻击模拟和防御策略'})
    
    try:
        # 这里可以根据实际的模拟ID获取对应的数据
        # 目前使用模拟数据
        prompt = f"""
        作为一个网络安全评估专家，请对以下攻防演练进行综合评估：
        
        攻击模拟ID：{simulation_id}
        防御策略ID：{defense_id}
        
        请提供：
        1. 攻击效果评估
        2. 防御有效性分析
        3. 安全态势评分
        4. 改进建议
        5. 总体评估报告
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = ctf_ai.get_model_request(messages, model_option=model_option)
        
        return jsonify({
            'success': True,
            'evaluation_report': result,
            'simulation_id': simulation_id,
            'defense_id': defense_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# 用户版AI仪表板
@app.route('/ai_lab')
@login_required
def ai_lab():
    """用户版AI仪表板，提供自动攻防体验"""
    
    # 获取所有挑战
    challenges = Challenge.query.all()
    
    # 获取当前用户的攻击模拟
    simulations = AttackSimulation.query.filter(
        AttackSimulation.challenge_id.in_([c.id for c in challenges])
    ).order_by(AttackSimulation.created_at.desc()).all()
    
    return render_template('ai_dashboard.html', 
                          challenges=challenges, 
                          simulations=simulations)

# 普通用户的防御建议API
@app.route('/api/user_defense_advice', methods=['POST'])
@login_required
def api_user_defense_advice():
    """为普通用户提供防御建议"""
    data = request.get_json()
    vulnerability = data.get('vulnerability', '')
    question = data.get('question', '')
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    if not vulnerability or not question:
        return jsonify({'success': False, 'message': '请提供漏洞描述和问题'})
    
    try:
        prompt = f"""
        作为一个网络安全防御专家，请针对以下漏洞或攻击场景，提供专业的防御建议：
        
        漏洞/攻击场景:
        {vulnerability}
        
        用户问题:
        {question}
        
        请提供:
        1. 漏洞/攻击的简要分析
        2. 具体的防御措施和修复方法
        3. 最佳安全实践建议
        4. 如果适用，提供代码示例或配置示例
        
        回答应该清晰、专业，并针对用户的具体问题提供实用的解决方案。
        """
        
        messages = [{"role": "user", "content": prompt}]
        defense_advice = ctf_ai.get_model_request(messages, model_option=model_option)
        
        # 记录用户使用AI助手的情况
        user_log = UserAIUsage(
            user_id=current_user.id,
            feature_type='defense_advice',
            query=vulnerability + "\n" + question,
            model_used=model_option,
            created_at=datetime.utcnow()
        )
        db.session.add(user_log)
        db.session.commit()
        
        return jsonify({'success': True, 'defense_advice': defense_advice})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成防御建议失败：{str(e)}'})

# 安全学习资料API
@app.route('/api/security_learning', methods=['POST'])
@login_required
def api_security_learning():
    """为用户提供安全学习资料"""
    data = request.get_json()
    topic = data.get('topic', '')
    skill_level = data.get('skill_level', 'intermediate')
    question = data.get('question', '')
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    if not topic or not question:
        return jsonify({'success': False, 'message': '请选择学习主题并提供问题'})
    
    try:
        topic_map = {
            'web': 'Web安全',
            'crypto': '密码学',
            'reverse': '逆向工程',
            'pwn': '二进制利用',
            'forensics': '数字取证',
            'network': '网络安全'
        }
        
        level_map = {
            'beginner': '初学者',
            'intermediate': '中级',
            'advanced': '高级'
        }
        
        topic_name = topic_map.get(topic, topic)
        level_name = level_map.get(skill_level, skill_level)
        
        prompt = f"""
        作为一个网络安全教育专家，请为一名{level_name}水平的学习者提供关于{topic_name}的学习资料和指导。
        
        学习者的问题:
        {question}
        
        请提供:
        1. 针对问题的详细解答
        2. 相关的概念解释和背景知识
        3. 实用的学习资源推荐（书籍、网站、工具等）
        4. 实践建议和练习方法
        5. 进阶学习路径
        
        内容应该符合{level_name}水平，既不要过于基础也不要过于高深，使用清晰易懂的语言。
        """
        
        messages = [{"role": "user", "content": prompt}]
        learning_material = ctf_ai.get_model_request(messages, model_option=model_option)
        
        # 记录用户使用AI助手的情况
        user_log = UserAIUsage(
            user_id=current_user.id,
            feature_type='security_learning',
            query=f"主题: {topic_name}, 水平: {level_name}, 问题: {question}",
            model_used=model_option,
            created_at=datetime.utcnow()
        )
        db.session.add(user_log)
        db.session.commit()
        
        return jsonify({'success': True, 'learning_material': learning_material})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成学习资料失败：{str(e)}'})

# 新增自我评估API端点
@app.route('/api/evaluate_self', methods=['POST'])
@login_required
def api_evaluate_self():
    """生成当前用户的能力评估"""
    data = request.get_json()
    model_option = data.get('model_option', 'Qwen3.0-Local')
    
    try:
        # 获取用户数据
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "score": current_user.score,
            "last_submit": current_user.last_submit.isoformat() if current_user.last_submit else None,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
        
        # 获取用户提交历史
        submissions = Submission.query.filter_by(user_id=current_user.id).all()
        submission_history = [{
            "challenge_id": sub.challenge_id,
            "challenge_title": sub.challenge.title if sub.challenge else "未知挑战",
            "category": sub.challenge.category.name if sub.challenge and sub.challenge.category else "未知类别",
            "is_correct": sub.is_correct,
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
        } for sub in submissions]
        
        # 获取用户解决的挑战
        solved_challenges = Challenge.query.join(Submission).filter(
            Submission.user_id == current_user.id,
            Submission.is_correct == True
        ).all()
        
        challenge_data = [{
            "id": ch.id,
            "title": ch.title,
            "category": ch.category.name if ch.category else "未知类别",
            "difficulty": ch.difficulty,
            "points": ch.points
        } for ch in solved_challenges]
        
        # 调用AI接口生成评估报告
        evaluation_result = ctf_ai.generate_evaluation_report(user_data, challenge_data, submission_history, model_option=model_option)
        
        # 保存评估结果
        evaluation = UserEvaluation(
            evaluation_report=evaluation_result['evaluation_report'],
            overall_score=random.randint(50, 95),  # 随机生成一个总体评分
            user_id=current_user.id
        )
        db.session.add(evaluation)
        db.session.commit()
        
        return jsonify({'success': True, 'evaluation': evaluation_result, 'evaluation_id': evaluation.id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成评估报告失败：{str(e)}'})

# 初始化数据库
def init_db():
    with app.app_context():
        # 先删除所有表，然后重新创建
        db.drop_all()
        db.create_all()
        
        # 创建默认分类
        if not Category.query.first():
            categories = [
                Category(name='Web', description='Web安全题目', color='#7aa2f7'),
                Category(name='Crypto', description='密码学题目', color='#bb9af7'),
                Category(name='Reverse', description='逆向工程题目', color='#7dcfff'),
                Category(name='Pwn', description='二进制漏洞题目', color='#f7768e'),
                Category(name='Forensics', description='取证分析题目', color='#9ece6a'),
                Category(name='Misc', description='杂项题目', color='#e0af68'),
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.flush()
        
        # 创建管理员用户
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@ctf.local',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # 创建示例题目
        web_category = Category.query.filter_by(name='Web').first()
        if web_category:
            example_challenge = Challenge(
                title='Welcome to CTF',
                description='这是一道简单的入门题目。Flag就在页面源码中！\n\n',
                flag='flag{welcome_to_neon_ctf}',
                points=50,
                difficulty='Easy',
                category_id=web_category.id,
                is_ai_generated=False,
                ai_scenario_data=None
            )
            db.session.add(example_challenge)
            db.session.flush()
            
            # 添加示例提示
            hint1 = Hint(
                content='查看页面源代码，Flag可能隐藏在HTML注释中',
                cost=5,
                challenge_id=example_challenge.id
            )
            hint2 = Hint(
                content='使用Ctrl+U或F12开发者工具查看源码',
                cost=10,
                challenge_id=example_challenge.id
            )
            db.session.add(hint1)
            db.session.add(hint2)
        
        db.session.commit()
        print("数据库初始化完成！")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
