# @Time    : 2019/7/16 11:03 AM
# @Author  : lirui
# @ qq     : 270239148

import logging.config
import os
import sys
curr_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curr_path)
import mlogging_handlers

'''
日志的配置参数，日志对象主要有3个子模块，分别为formater（输出格式），handler（日志操作类型），logger（日志名），要分别进行设置。
其中hadlers为日志的具体执行，依赖于formater和日志操作类型或一些属性，比如按大小分片还是时间分片，是写入还是打印到控制台。
logger负责调用handle，一个logger可以调用多个handler，比如logger.info调用了打印到控制台handler（logging.StreamHandler）
和写入到文件handler（mlogging_handlers.TimedRotatingFileHandler_MP），在没有指定logger名字的时候，即logger=logging.get_logger()的时候，
logger会自动选择名为root的logger
'''

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            # 简单的输出模式
            'format': '%(asctime)s %(levelname)s file:%(filename)s|lineno:'
                      '%(lineno)d|logger:%(name)s - %(message)s'
        },
        'standard': {
            # 较为复杂的输出模式，可以进行自定义
            'format': '%(asctime)s %(levelname)s threadId:%(thread)d|processId:%(process)d:|file:%(filename)s|lineno:'
                      '%(lineno)d|func:%(funcName)s|module:%(module)s|logger:%(name)s - %(message)s'
        }
    },

    # 过滤器
    "filters": {
        'debug_filter': {
            '()': 'log_filters.DebugFilter'
        },
        'info_filter': {
            '()': 'log_filters.InfoFilter'
        },
        'warning_filter': {
            '()': 'log_filters.WarningFilter'
        },
        'error_filter': {
            '()': 'log_filters.ErrorFilter'
        },
        'critical_filter': {
            '()': 'log_filters.CriticalFilter'
        },
        'no_debug_filter': {
            '()': 'log_filters.NoDebugFilter'
        }
    },

    "handlers": {
        # # 写入到文件的hanler，写入等级为info，命名为request是为了专门记录一些网络请求日志
        # "request": {
        #     # 定义写入文件的日志类，此类为按时间分割日志类，还有一些按日志大小分割日志的类等
        #     "class": "mlogging_handlers.TimedRotatingFileHandlerMP",
        #     # 日志等级
        #     "level": "INFO",
        #     # 日志写入格式，因为要写入到文件后期可能会debug用，所以用了较为详细的standard日志格式
        #     "formatter": "standard",
        #     # 要写入的文件名
        #     "filename": os.path.join(log_root_path, 'default', 'request.log'),
        #     # 分割单位，D日，H小时，M分钟，W星期，一般是以小时或天为单位
        #     # 比如文件名为test.log，到凌晨0点的时候会自动分离出test.log.yyyy-mm-dd
        #     "when": 'D',
        #     "encoding": "utf8",
        # },
        # 输出到控制台的handler
        # "debug": {
        #     # 定义输出流的类
        #     "class": "logging.StreamHandler",
        #     # handler等级，如果实际执行等级高于此等级，则不触发handler
        #     "level": "DEBUG",
        #     # 输出的日志格式
        #     "formatter": "simple",
        #     # 流调用系统输出
        #     "stream": "ext://sys.stdout"
        # },
    },
    "loggers": {

    },
    # 基础logger，当不指定logger名称时，默认选择此logger
    "root": {
        'handlers': [],
        'level': "DEBUG",
        'propagate': False
    }
}


# 定义日志类
class Logger:

    # 单例模式存储对象
    __instance = {}
    __is_init = False

    # 对于每个app name单例模式
    def __new__(cls, app_name: str, log_path: str, *args, **kwargs):
        if app_name not in cls.__instance:
            cls.__instance[app_name] = super().__new__(cls)
        return cls.__instance[app_name]

    # 初始化logger，通过LOGGING配置logger
    def __init__(self, app_name: str, log_path: str=None, is_debug=True, is_write_file=True):
        if self.__is_init is True:
            return
        # #校验传入参数
        # app_name不能为空字符串
        assert(type(app_name) is str and app_name != ''), f'app_name必须为字符串类型，且不能为空字符串，当前传入的app_name为：{app_name}，类型为{type(app_name)}'
        # is_debug和is_write_file至少有一个为True
        assert (is_debug or is_write_file), f'不存在既不输出到控制台也不写入文件的日志，is_debug和is_write_file至少有一个为True'
        # 防止再次实例化
        self.__is_init = True
        self.is_debug = is_debug
        # 初始化logging配置参数
        global LOGGING
        # 将日志时间中的逗号格式改成点
        logging.Formatter.default_msec_format = '%s.%03d'
        # 将日志等级的WARNING修改为WARN
        level_conf = getattr(logging, '_levelToName')
        level_conf[30] = 'WARN'

        # 初始化logger配置
        logger_name = f'{app_name}_logger'
        # 初始化logger字典配置，空架子，未添加任何handler
        LOGGING['loggers'][logger_name] = self.get_logger_conf()
        logger_handlers = LOGGING['loggers'][logger_name]['handlers']

        # request_logger初始化，空架子，未添加任何handler
        request_logger_name = f'{app_name}_request_logger'
        LOGGING['loggers'][request_logger_name] = self.get_request_logger_conf()
        request_logger_handlers = LOGGING['loggers'][request_logger_name]['handlers']

        # 当需要打印到控制台时
        if is_debug:
            # 添加debug handler
            handler_name = f'{app_name}_debug'
            LOGGING['handlers'][handler_name] = self.get_console_handler_conf()
            logger_handlers.append(handler_name)
            # 添加request debug 日志
            request_logger_handlers.append(handler_name)
            print(f"app名为{app_name}的日志的打印到控制台功能被初始化了，日志将输出到控制台")

        # 当需要写入到文件
        if is_write_file:
            # 创建加锁文件夹，mlogging_handlers.py需要用到此文件夹
            _lock_dir = str(os.path.abspath(__file__).rsplit('/', 1)[0]) + '/.lock'
            if not os.path.exists(_lock_dir):
                os.mkdir(_lock_dir)

            # 校验文件路径
            assert(type(log_path) is str), f'传入的日志路径必须为字符串，当前传入的路径为：{log_path}，类型为：{type(log_path)}'
            # app_name名对应日志路径
            log_file_dir = os.path.join(log_path, app_name)
            # 如果日志文件夹不存在，则创建
            if not os.path.exists(log_file_dir):
                os.makedirs(log_file_dir)

            # 默认日志路径，为request_logger使用
            default_log_file_dir = os.path.join(log_path, 'default')
            # 如果默认日志文件夹不存在，则创建
            if not os.path.exists(default_log_file_dir):
                os.makedirs(default_log_file_dir)
                print(f'默认日志路径：{default_log_file_dir} 被创建')

            # 启动服务时的友好提示
            print(f'默认日志路径：{default_log_file_dir} ，当中间件找不到是调用哪个app时'
                  f'（如404 not found情况下，不知道调用的哪个app），日志会记录到此文件夹下')
            print(f"app名为{app_name}的日志的写入文件功能被初始化了，日志会写入到：{log_file_dir} 文件夹下")

            # 添加日志handlers
            log_levels = ['info', 'warning', 'error',  'critical']

            # 根据app_name动态更新LOGGING配置，为每个app_name创建文件夹，配置handler
            for level in log_levels:
                # handler 对应文件名，如 logs/default/info.log
                # 为app_name 日志添加handler
                handler_name = f'{app_name}_{level}'

                # 为app_name日志添加handler
                filename = os.path.join(log_file_dir, (level + '.log'))
                # 日志等级转大写
                lev_up = level.upper()
                LOGGING['handlers'][handler_name] = self.get_file_handler_conf(filename=filename, level=lev_up)
                logger_handlers.append(handler_name)

                # 为request 日志添加handler
                request_handler_name = f'{app_name}_request_{level}'
                request_filename = os.path.join(log_file_dir, 'request.log')
                LOGGING['handlers'][request_handler_name] = self.get_file_handler_conf(filename=request_filename, level=lev_up)
                request_logger_handlers.append(request_handler_name)

        # import json
        # print(json.dumps(LOGGING, indent=2))

        # 将LOGGING中的配置信息更新到logging中
        logging.config.dictConfig(LOGGING)

    # 控制台输出handler配置
    @staticmethod
    def get_console_handler_conf():
        console_handler_conf = {
            # 定义输出流的类
            "class": "logging.StreamHandler",
            # handler等级，如果实际执行等级高于此等级，则不触发handler
            "level": "DEBUG",
            # 输出的日志格式
            "formatter": "simple",
            # 流调用系统输出
            "stream": "ext://sys.stdout",
            "filters": ["debug_filter"]
        }
        return console_handler_conf

    @staticmethod
    # 写入文件handler配置
    def get_file_handler_conf(filename: str, level='INFO'):
        file_handler_conf = {
            # 定义写入文件的日志类，此类为按时间分割日志类，还有一些按日志大小分割日志的类等
            "class": "mlogging_handlers.TimedRotatingFileHandlerMP",
            # 日志等级
            "level": "",
            # 日志写入格式，因为要写入到文件后期可能会debug用，所以用了较为详细的standard日志格式
            "formatter": "standard",
            # 要写入的文件名
            "filename": '',
            # 分割单位，D日，H小时，M分钟，W星期，一般是以小时或天为单位
            # 比如文件名为test.log，到凌晨0点的时候会自动分离出test.log.yyyy-mm-dd
            "when": 'D',
            "encoding": "utf8",
            "filters": []
        }
        filters = ['%s_filter' % (level.lower())]
        update_dict = {'filename': filename, 'level': level, 'filters': filters}
        file_handler_conf.update(update_dict)
        return file_handler_conf

    @staticmethod
    # logger 配置
    def get_logger_conf():
        logger_conf = {
            'handlers': [],
            'level': "DEBUG",
            'propagate': False
        }
        return logger_conf

    @staticmethod
    # request logger配置
    def get_request_logger_conf():
        logger_conf = {
            'handlers': [],
            'level': "DEBUG",
            'propagate': False
        }
        return logger_conf


# 获取日常logger
def get_logger(app_name: str, log_path: str=None, is_debug=True, is_write_file=True):
    Logger(log_path=log_path, app_name=app_name, is_debug=is_debug, is_write_file=is_write_file)
    logger_name = '%s_logger' % app_name
    logger = logging.getLogger(logger_name)
    return logger


# 获取request logger
def get_request_logger(app_name: str, log_path: str=None, is_debug=True, is_write_file=True):
    Logger(app_name=app_name, log_path=log_path, is_debug=is_debug, is_write_file=is_write_file)
    logger_name = '%s_request_logger' % app_name
    logger = logging.getLogger(logger_name)
    return logger


if __name__ == '__main__':
    # 临时目录
    log_root_path = '/Users/lr/my_git/data_scripts/pypip/build/lib/log_tool'
    # 单例模式测试
    logger = get_logger(app_name='devenv', log_path=log_root_path, is_debug=True, is_write_file=False)
    request_logger = get_request_logger(app_name='devenv', log_path=log_root_path, is_debug=True, is_write_file=False)

    # logger.debug('debug log')
    # logger.info('info log')
    logger.warning('warning log')
    # logger.error('error log')
    # logger.critical('critical log')
    request_logger.info('request log')
