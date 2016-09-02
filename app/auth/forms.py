from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from pymongo import MongoClient

Province_choice = [('北京市', '北京市'), ('天津市', '天津市'), ('上海市', '上海市'), ('天津市', '天津市'), ('重庆市', '重庆市'), ('河北', '河北'),
                   ('山东', '山东'), ('辽宁', '辽宁'), ('黑龙江', '黑龙江'), ('吉林', '吉林'), ('甘肃', '甘肃'), ('青海', '青海'),
                   ('河南', '河南'), ('江苏', '江苏'), ('湖北', '湖北'), ('湖南', '湖南'), ('江西', '江西'), ('浙江', '浙江'),
                   ('广东', '广东'), ('云南', '云南'), ('福建', '福建'), ('台湾', '台湾'), ('海南', '海南省'), ('山西', '山西'),
                   ('四川', '四川'), ('陕西', '陕西'), ('贵州', '贵州'), ('安徽', '安徽'), ('广西', '广西'), ('内蒙古', '内蒙古'),
                   ('西藏', '西藏'), ('新疆', '新疆'), ('宁夏', '宁夏'), ('澳门', '澳门'), ('香港', '香港')]


class LoginForm(Form):
    email = StringField('登录邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                          Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '支持英文和字母下划线.')])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='两次密码不一致.')])
    password2 = PasswordField('确认密码', validators=[Required()])
    name = StringField('姓名', validators=[
        Required(), Length(1, 20), Regexp('^[a-zA-Z\u4e00-\u9fa5]*$', 0,
                                          '只能输入英文和中文.')])
    location = SelectField('地址', choices=Province_choice)
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('立即注册')

    def validate_email(self, field):
        if MongoClient().blog.User.find_one({'temp': field.data}):
            raise ValidationError('邮箱已被注册.')

    def validate_username(self, field):
        if MongoClient().blog.User.find_one({'username': field.data}):
            raise ValidationError('用户名已被注册.')


class PasswordResetRequestForm(Form):
    email = StringField('邮箱地址', validators=[Required(), Length(1, 64),
                                            Email()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if MongoClient().blog.User.find_one({'temp': field.data}) is None:
            raise ValidationError('邮箱不存在,请重新确认')


class PasswordResetForm(Form):
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='两次密码不一致.')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('修改')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次密码不一致.')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('修改')


class ChangeEmailForm(Form):
    email = StringField('新邮箱地址', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('修改')

    def validate_email(self, field):
        if MongoClient().blog.User.find_one({'temp': field.data}) is not None:
            raise ValidationError('此邮箱已经注册.')
