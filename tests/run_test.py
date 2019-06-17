# coding=utf8
import os
import time
import sys
import shutil
import webbrowser

current_dir = os.path.dirname(os.path.abspath(__file__))  # NOQA
parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))  # noqa
www_dir = os.path.abspath(os.path.join(parent_dir, 'www'))
sys.path.append(parent_dir)  # NOQA
os.environ['PYTHONPATH'] = ':'.join((parent_dir, www_dir))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.settings'

risk_env = os.environ.get('RISK_ENV')
assert risk_env and risk_env == 'test', '注意，此部分只能在测试环境中执行'


def find_test_file_paths():
    current_dir = os.getcwd()
    sub_dirs = [t for t in os.listdir(current_dir) if os.path.isdir(t)]

    testfiles = []
    for suite in sub_dirs:
        # 获取测试目录下的所有测试文件
        testfiles.extend(
            [os.path.abspath(os.path.join(suite, f)) for f in os.listdir(suite)
             if f.endswith('py')]
        )

    return testfiles


def coverage_html():
    """ 将coverage结果放置到html中并自动打开浏览器 """
    output_dir = os.path.join(os.getcwd(), 'coverage_output')
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    now_str = time.strftime("%Y%m%d%H%M")
    html_result_path = os.path.join(output_dir, now_str)
    html_cmd = 'coverage html -d {path}'.format(path=html_result_path)
    for test_file_path in find_test_file_paths():
        coverage_cmd = "coverage run -a --source=risk_models,builtin_funcs {path}".format(
            path=test_file_path)
        os.system(coverage_cmd)
    os.system(html_cmd)
    os.remove(os.path.join(os.getcwd(), '.coverage'))
    webbrowser.open_new(
        'file:///{base_dir}/index.html'.format(base_dir=html_result_path))


def print_coverage_result():
    """ 直接回显coverage结果 """
    report_cmd = 'coverage report'
    for test_file_path in find_test_file_paths():
        coverage_cmd = "coverage run -a --source=risk_models,builtin_funcs {path}".format(
            path=test_file_path)
        os.system(coverage_cmd)
    os.system(report_cmd)
    os.remove(os.path.join(os.getcwd(), '.coverage'))


def clear_test_data():
    from clients import get_mongo_client, get_config_redis_client

    db = get_mongo_client()
    db.client.drop_database(db.name)

    client = get_config_redis_client()
    client.flushdb()


if __name__ == "__main__":
    clear_test_data()
    print_coverage_result()
    # coverage_html()
    clear_test_data()
