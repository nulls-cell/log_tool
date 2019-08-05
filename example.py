# @Time    : 2019/7/16 11:03 AM
# @Author  : lirui
# @ qq     : 270239148
from log_tool.log_simple_util import get_logger, get_request_logger
import os

if __name__ == '__main__':
    # 当前路径，日志会写到其中
    log_path = str(os.path.abspath(__file__).rsplit('/', 1)[0]) + '/logs'
    # 是否将日志打印到控制台，默认为True
    is_debug = True
    # 普通日志会打到日志等级对应的文件中
    logger = get_logger(app_name='default', log_path=log_path, is_debug=is_debug)
    logger.debug('debug log')
    logger.info('info log')
    logger.warning('warning log')
    logger.error('error log')
    logger.critical('critical log')

    # 请求日志会打到request.log中，请求日志只接受info，warning，error3个等级的日志，其他等级会被忽略
    request_logger = get_request_logger(app_name='default', log_path=log_path, is_debug=is_debug)
    request_logger.info('request log')

