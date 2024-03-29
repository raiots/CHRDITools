"""
Django settings for CHRDITools project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import time
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&!38pk#dv=r!_c(+b&oegc0m(ndzoue+ez*7kvjv2uubuqootp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.31.198', '127.0.0.1', '172.20.22.40', '110.42.209.79']


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'apps.users',
    'apps.tasks',
    'apps.risks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CHRDITools.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CHRDITools.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
#STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# 登录链接与登录后跳转路径
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# 它确定库是否会在数据导入中使用数据库事务，以确保安全。
IMPORT_EXPORT_USE_TRANSACTIONS = True

SITE_NAME = '任务管理工具'
# SimpleUI 配置

# 离线模式
SIMPLEUI_STATIC_OFFLINE = True

# 关闭首页模块以及信息采集模块
SIMPLEUI_HOME_INFO = False
SIMPLEUI_HOME_QUICK = True
SIMPLEUI_HOME_ACTION = True
SIMPLEUI_ANALYSIS = False
SIMPLEUI_HOME_TITLE = SITE_NAME
# SIMPLEUI_HOME_PAGE = 'https://www.baidu.com' # 可用于嵌入其他链接，这里可以直接方便的嵌入报表链接
SIMPLEUI_HOME_ICON = 'el el-icon-platform-eleme'
# ICON 支持element-ui和fontawesome  eg：fa fa-user
# https://zhuanlan.zhihu.com/p/113447102

# 指定simpleui默认的主题,指定一个文件名，相对路径就从simpleui的theme目录读取
SIMPLEUI_DEFAULT_THEME = 'ant.design.css'

SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['任务管理', '系统配置', '关于'],      # 开启排序和过滤功能, 不填此字段为默认排序和全部显示, 空列表[] 为全部不显示.
    'dynamic': True,    # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容
    'menus': [{
        'name': '任务管理',
        'icon': 'fas fa-code',
        'models': [{
            'app': 'tasks',
            'name': '年度任务',
            'url': 'tasks/task'
        }, {
            'name': '工作包',
            'url': 'tasks/todo?o=3'
        }]
    }, {
        'app': 'admin',
        'name': '系统配置',
        'icon': 'fas fa-user-shield',
        'models': [{
            'name': '用户',
            'icon': 'fa fa-user',
            'url': 'users/user',
        }, {
            'name': '部门',
            'url': 'users/department'
        }, {
            'name': '任务属性',
            'url': 'users/taskproperty',
        }, {
            'name': '权限组',
            'url': 'users/mygroup',
        }, {
            'name': '评价等级定义',
            'url': 'users/qualitymark',
        }, {
            'name': '评价等级考核系数',
            'url': 'users/markvalue'
        }]
    }, {
        # 自2021.02.01+ 支持多级菜单，models 为子菜单名
        'name': '多级菜单测试',
        'icon': 'fa fa-file',
      	# 二级菜单
        'models': [{
            'name': 'Baidu',
            'icon': 'far fa-surprise',
            # 第三级菜单 ，
            'models': [
                {
                  'name': '爱奇艺',
                  'url': 'https://www.iqiyi.com/dianshiju/'
                  # 第四级就不支持了，element只支持了3级
                }, {
                    'name': '百度问答',
                    'icon': 'far fa-surprise',
                    'url': 'https://zhidao.baidu.com/'
                }
            ]
        }, {
            'name': '内网穿透',
            'url': 'https://www.wezoz.com',
            'icon': 'fab fa-github'
        }]
    }, {
        'name': '动态菜单测试',
        'icon': 'fa fa-desktop',
        'models': [{
            'name': time.time(),
            'url': 'http://baidu.com',
            'icon': 'far fa-surprise'
        }]
    }, {
        'name': '关于',
        'url': '/about'
    }]
}
