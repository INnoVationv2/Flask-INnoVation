from flask import render_template, abort, flash, request, current_app, make_response
from . import main
from pymongo import MongoClient, DESCENDING
from ..models import Temp, Permission, Post, body_html
from flask_login import login_required, current_user, redirect, url_for
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, EditPostForm, CommentForm
from ..decorators import admin_required, permission_required
from bson.objectid import ObjectId
from datetime import datetime


class Paginate:
    def __init__(self, page, show_follow):
        if show_follow == 0:
            posts = MongoClient().blog.Aritical.find().sort('issuing_time', DESCENDING)
            self.total = posts.count()
            self.posts = posts
        if show_follow == 1:
            self.posts = []
            following = MongoClient().blog.User.find_one({'username': current_user.username}).get('following')
            artical = MongoClient().blog.Aritical.find().sort('issuing_time', DESCENDING)
            # following.append([current_user.username, 'date'])
            for i in range(following.__len__()):
                for x in range(artical.count()):
                    if following[i][0] == artical[x].get('username'):
                        self.posts.append(artical[x])
                        self.posts.sort(key=lambda x: x.get('issuing_time'), reverse=True)
            self.total = self.posts.__len__()
        self.pages = int(self.total / 20)
        if self.total % 20 != 0:
            self.pages += 1
        if page == 1:
            self.has_prev = False
        else:
            self.has_prev = True
        if page == self.pages:
            self.has_next = False
        else:
            self.has_next = True
        self.next_num = page + 1
        self.page = page
        self.per_page = 20
        self.prev_num = page - 1
        self.current_num = self.total - (20 * (page - 1))
        if self.current_num > 20:
            self.current_num = 20
        self.item = []
        for i in range(self.current_num):
            self.item.append(self.posts[self.prev_num * 20 + i])

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) \
                    or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class PaginateUser:
    def __init__(self, page, username):
        posts = MongoClient().blog.Aritical.find({'username': username}).sort('issuing_time', DESCENDING)
        self.total = posts.count()
        self.pages = int(self.total / 20)
        if self.total % 20 != 0:
            self.pages += 1
        if page == 1:
            self.has_prev = False
        else:
            self.has_prev = True
        if page == self.pages:
            self.has_next = False
        else:
            self.has_next = True
        self.next_num = page + 1
        self.page = page
        self.per_page = 20
        self.prev_num = page - 1
        self.current_num = self.total - (20 * (page - 1))
        if self.current_num > 20:
            self.current_num = 20
        self.item = []
        for i in range(self.current_num):
            self.item.append(posts[self.prev_num * 20 + i])

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) \
                    or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class PaginateFollowers:
    def __init__(self, page, username):
        conn = MongoClient().blog.User.find_one({'username': username})
        posts = conn.get('followers')
        self.total = posts.__len__()
        self.pages = int(self.total / 20)
        if self.total % 20 != 0:
            self.pages += 1
        if page == 1:
            self.has_prev = False
        else:
            self.has_prev = True
        if page == self.pages:
            self.has_next = False
        else:
            self.has_next = True
        self.next_num = page + 1
        self.page = page
        self.per_page = 20
        self.prev_num = page - 1
        self.current_num = self.total - (20 * (page - 1))
        if self.current_num > 20:
            self.current_num = 20
        self.item = []
        for i in range(self.current_num):
            self.item.append(
                {'username': posts[self.prev_num * 20 + i][0], 'timestamp': posts[self.prev_num * 20 + i][1]})

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) \
                    or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class PaginateFollowing:
    def __init__(self, page, username):
        posts = MongoClient().blog.User.find_one({'username': username}).get('following')
        self.total = posts.__len__()
        self.pages = int(self.total / 20)
        if self.total % 20 != 0:
            self.pages += 1
        if page == 1:
            self.has_prev = False
        else:
            self.has_prev = True
        if page == self.pages:
            self.has_next = False
        else:
            self.has_next = True
        self.next_num = page + 1
        self.page = page
        self.per_page = 20
        self.prev_num = page - 1
        self.current_num = self.total - (20 * (page - 1))
        if self.current_num > 20:
            self.current_num = 20
        self.item = []
        for i in range(self.current_num):
            self.item.append(
                {'username': posts[self.prev_num * 20 + i][0], 'timestamp': posts[self.prev_num * 20 + i][1]})

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) \
                    or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class PaginateComments:
    def __init__(self, page, id):
        posts = MongoClient().blog.Aritical.find_one({'_id': ObjectId(id)}).get('comments')
        self.total = posts.__len__()
        self.pages = int(self.total / 20)
        if self.total % 20 != 0:
            self.pages += 1
        if page == -1:
            self.page = self.pages
        else:
            self.page = page
        if self.page == 1:
            self.has_prev = False
        else:
            self.has_prev = True
        if self.page == self.pages:
            self.has_next = False
        else:
            self.has_next = True
        self.next_num = self.page + 1
        self.per_page = 20
        self.prev_num = self.page - 1
        self.current_num = self.total - (20 * (self.page - 1))
        if self.current_num > 20:
            self.current_num = 20
        self.items = []
        for i in range(self.current_num):
            self.items.append(
                {'body': posts[self.prev_num * 20 + i][0], 'username': posts[self.prev_num * 20 + i][1],
                 'timestamp': posts[self.prev_num * 20 + i][2]})
            self.items.reverse()

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) \
                    or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        Post(body=form.body.data).new_article()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        pagination = Paginate(page, 1)
    else:
        pagination = Paginate(page, 0)
    posts = pagination.item
    return render_template('index.html', form=form, posts=posts, pagination=pagination, show_followed=show_followed)


@main.route('/user/<username>')
@login_required
def user(username):
    user_temp = MongoClient().blog.User.find_one({'username': username})
    if user_temp is None:
        abort(404)
    user = Temp(id=user_temp.get('_id'), username=user_temp.get('username'), email=user_temp.get('email'),
                password=user_temp.get('password'), activate=user_temp.get('activate'), role=user_temp.get('role'),
                name=user_temp.get('name'),
                location=user_temp.get('location'), about_me=user_temp.get('about_me'),
                last_since=user_temp.get('last_since'),
                member_since=user_temp.get('member_since'))
    page = request.args.get('page', 1, type=int)
    pagination = PaginateUser(page, username)
    posts = pagination.item
    followers = user_temp.get('followers')
    following = user_temp.get('following')
    return render_template('user.html', user=user, posts=posts, pagination=pagination, followers=followers,
                           following=following)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        MongoClient().blog.User.update({'email': current_user.email}, {'$set': {'name': form.name.data}})
        MongoClient().blog.User.update({'email': current_user.email}, {'$set': {'location': form.location.data}})
        MongoClient().blog.User.update({'email': current_user.email}, {'$set': {'about_me': form.about_me.data}})
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        flash('更改已保存')
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = MongoClient().blog.User.find_one({'_id': ObjectId(id)})
    if user is None:
        return abort(404)
    user_temp = Temp(id=user.get('_id'), username=user.get('username'), email=user.get('email'),
                     password=user.get('password'), activate=user.get('activate'), role=user.get('role'),
                     name=user.get('name'),
                     location=user.get('location'), about_me=user.get('about_me'),
                     last_since=user.get('last_since'),
                     member_since=user.get('member_since'))
    form = EditProfileAdminForm(user=user_temp)
    if form.validate_on_submit():
        MongoClient().blog.User.update({'email': user_temp.email}, {'$set': {'name': form.name.data}})
        MongoClient().blog.User.update({'email': user_temp.email}, {'$set': {'username': form.username.data}})
        MongoClient().blog.User.update({'email': user_temp.email}, {'$set': {'email': form.email.data}})
        MongoClient().blog.User.update({'email': user_temp.email}, {'$set': {'activate': form.activate.data}})
        MongoClient().blog.User.update({'email': user_temp.email}, {'$set': {'role': form.role.data}})
        MongoClient().blog.User.update({'email': user_temp.email}, {'$set': {'location': form.location.data}})
        MongoClient().blog.User.update({'email': user_temp.email}, {'$set': {'about_me': form.about_me.data}})
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user_temp.username))
    form.email.data = user_temp.email
    form.username.data = user_temp.username
    form.activate.data = user_temp.activate
    form.role.data = user_temp.role.name
    form.name.data = user_temp.name
    form.location.data = user_temp.location
    form.about_me.data = user_temp.about_me
    return render_template('edit_profile.html', form=form, user=user_temp)


@main.route('/post/<id>', methods=['GET', 'POST'])
def post(id):
    post = MongoClient().blog.Aritical.find({'_id': ObjectId(id)})
    form = CommentForm()
    if form.validate_on_submit():
        comments = post[0].get('comments')
        body = form.body.data
        comments.append([body, current_user.username, datetime.utcnow()])
        MongoClient().blog.Aritical.update({'_id': ObjectId(id)}, {'$set': {'comments': comments}})
        flash('评论发布成功.')
        return redirect(url_for('.post', id=id, page=-1))
    page = request.args.get('page', 1, type=int)
    pagination = PaginateComments(page, id)
    comments = pagination.items
    comment = (post[0].get('username') != current_user.username)
    return render_template('post.html', posts=post, form=form, i=0,
                           comments=comments, pagination=pagination, author=comment, id=id)


@main.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = MongoClient().blog.Aritical.find_one({'_id': ObjectId(id)})
    if current_user.id != post.get('user_id') and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        MongoClient().blog.Aritical.update({'_id': ObjectId(id)},
                                           {'$set': {'body': form.body.data, 'body_html': body_html(form.body.data)}})
        flash('修改成功')
        return redirect(url_for('.post', id=post.get('_id')))
    form.body.data = post.get('body')
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = MongoClient().blog.User.find_one({'username': username})
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    very = False
    temp = MongoClient().blog.User.find_one({'username': current_user.username}).get('following')
    for i in range(temp.__len__()):
        if temp[i][0] == username:
            very = True
            break
    if very:
        flash('您已经关注过了他，不能重复关注.')
        return redirect(url_for('.user', username=username))
    followers = user.get('followers')
    time = datetime.utcnow()
    follow = [current_user.username, time]
    followers.append(follow)
    MongoClient().blog.User.update({'username': username}, {'$set': {'followers': followers}})
    post2 = MongoClient().blog.User.find_one({'username': current_user.username})
    following = post2.get('following')
    follow = [user.get('username'), time]
    following.append(follow)
    MongoClient().blog.User.update({'username': current_user.username}, {'$set': {'following': following}})
    flash('您成功关注了 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = MongoClient().blog.User.find_one({'username': username})
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    very = False
    temp = MongoClient().blog.User.find_one({'username': current_user.username}).get('following')
    for i in range(temp.__len__()):
        if temp[i][0] == username:
            very = True
            break
    if not very:
        flash('您没有关注这个用户.')
        return redirect(url_for('.user', username=username))
    followers = user.get('followers')
    for i in range(followers.__len__()):
        if followers[i][0] == current_user.username:
            followers.remove(followers[i])
            break
    MongoClient().blog.User.update({'username': username}, {'$set': {'followers': followers}})
    post2 = MongoClient().blog.User.find_one({'username': current_user.username})
    following = post2.get('following')
    for i in range(following.__len__()):
        if following[i][0] == username:
            following.remove(following[i])
            break
    MongoClient().blog.User.update({'username': current_user.username}, {'$set': {'following': following}})
    flash('您取消关注了 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = MongoClient().blog.User.find_one({'username': username})
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = PaginateFollowers(page=page, username=username)
    follows = pagination.item
    return render_template('followers.html', user=user, title="关注", title1='关注', title2='的人',
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/following/<username>')
def following(username):
    user = MongoClient().blog.User.find_one({'username': username})
    if user is None:
        flash('此用户不存在.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = PaginateFollowing(page=page, username=username)
    follows = pagination.item
    return render_template('followers.html', user=user, title='关注的人', title1='', title2='关注的人',
                           endpoint='.following', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/delete/<id>')
@login_required
def delete(id):
    user = MongoClient().blog.Aritical.find({'_id': ObjectId(id)})
    if not current_user.username == user[0].get('username') and not current_user.is_administrator():
        abort(304)
    timedata = request.args.get('data')
    comments = user[0].get('comments')
    for i in range(comments.__len__()):
        time = str(comments[i][2])
        if time == timedata:
            del comments[i]
            break
    MongoClient().blog.Aritical.update({'_id': ObjectId(id)}, {'$set': {'comments': comments}})
    return redirect(url_for('.post', id=id))
