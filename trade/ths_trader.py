# coding=utf-8
# 导入库
import io
import os
import time
import pandas as pd
import pytesseract
import message
import config
from pywinauto.keyboard import send_keys
from pywinauto import Application, clipboard
from util import log_util
from datetime import datetime

# logger
logger = log_util.get_logger()
# 下单程序的路径
xiadan_exe_path = r'D:\同花顺软件\同花顺\xiadan.exe'
if os.getlogin().__eq__("ly"):
    xiadan_exe_path = r"D:\同花顺远航版\transaction\xiadan.exe"
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# 验证码识别，参数：图片，返回字符串
def Ocr(png):
    verification_code = pytesseract.image_to_string(png, config="--psm 6 digits")
    return verification_code


# 清空编辑栏，参数：编辑控件
def empty_edit(edit_win):
    edit_win.type_keys('{BS}{BS}{BS}{BS}{BS}{BS}{BS}{BS}', )


# 定义ThsTarder类
class ThsTrader:
    # 传入xiadan.exe的路径,股票账号，交易密码
    def __init__(self):

        # 设置tesseract路径
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # 尝试连接已经存在的交易程序
        try:
            self.app = Application(backend="uia").connect(path=xiadan_exe_path)
            # 查看顶级窗口标题
            win_name = self.app.top_window().set_focus().texts()[0]
            logger.info("进入同花顺__" + win_name)
            # 如果交易窗口存在
            if win_name == '网上股票交易系统5.0':
                logger.info('交易应用已存在,准备开始交易')
                # 连接交易窗口
                self.main_window = self.app.window(title=u"网上股票交易系统5.0", control_type="Window")
            # 如果存在的窗口不是交易窗口，则为登入窗口
            else:
                logger.info('登录应用已存在，执行登录')

        # 如果以上连接已有窗口的操作都失败，则执行打开窗口
        except Exception as ex:
            logger.info(ex)
            logger.info('没有交易窗口在运行，启动应用')

    # 连接左侧菜单，返回左侧菜单控件
    def left_menu_win(self):
        left_menu_win = self.main_window.child_window(auto_id="129", control_type="Tree")
        left_menu_win().set_focus()
        # self.left_menu_win=self.main_window.children()[0].children()[0].children()[1].children()[0].children()[0]
        # logger.info(left_menu_win.children_texts())
        logger.info('连接左侧菜单成功')
        return left_menu_win

    # 连接右侧菜单，返回右侧菜单控件
    def right_data_win(self):
        right_menu_win = self.main_window.child_window(title="HexinScrollWnd", auto_id="1047", control_type="Pane")
        right_menu_win.set_focus()
        logger.info('连接右侧菜单成功')
        return right_menu_win

    def buy_fast(self, buy_stock_number):
        # 复制临时主窗口控件，便于操作
        temporary_main_win = self.main_window
        temporary_main_win.set_focus()
        # 定位左侧市价委托控件
        left_sell_ctrl = temporary_main_win.child_window(title="买入[F1]", control_type="TreeItem")
        left_sell_ctrl.click_input()
        # 定位证券代码编辑框
        stocks_num_win = temporary_main_win.child_window(auto_id="1032", control_type="Edit")
        stocks_num_win.draw_outline(colour='red')
        empty_edit(stocks_num_win)
        # 输入证券代码
        stocks_num_win.type_keys(buy_stock_number)
        time.sleep(1)
        # 定位买入按钮
        market_buy_yes = self.main_window.child_window(title="买入", auto_id="1006", control_type="Button")
        # 确定买入
        market_buy_yes.click_input()
        # 点击是
        if config.ths_trader_debug_mode:
            self.no_win_v2()
        else:
            self.yes_win_v2()
        # 点击确定
        self.confirm_win()

    def sell_fast(self, sell_stock_number):
        # 复制临时主窗口控件，便于操作
        temporary_main_win = self.main_window
        temporary_main_win.set_focus()
        # 定位左侧市价委托控件
        left_sell_ctrl = temporary_main_win.child_window(title="卖出[F2]", control_type="TreeItem")
        left_sell_ctrl.click_input()
        # 定位证券代码编辑框
        stocks_num_win = temporary_main_win.child_window(auto_id="1032", control_type="Edit")
        stocks_num_win.draw_outline(colour='red')
        empty_edit(stocks_num_win)
        # 输入证券代码
        stocks_num_win.type_keys(sell_stock_number)
        time.sleep(1)
        # 定位买入按钮
        market_buy_yes = self.main_window.child_window(title="卖出", auto_id="1006", control_type="Button")
        # 确定买入
        market_buy_yes.click_input()
        # 点击是
        if config.ths_trader_debug_mode:
            self.no_win_v2()
        else:
            self.yes_win_v2()
        # 点击确定
        self.confirm_win()


    def yes_win_v2(self):
        yes_win_yes = self.main_window.child_window(title="是(Y)", auto_id="6", control_type="Button")
        if yes_win_yes.exists():
            yes_win_yes.click_input()

    def no_win_v2(self):
        no_win_no = self.main_window.child_window(title="否(N)", auto_id="7", control_type="Button")
        if no_win_no.exists():
            no_win_no.click_input()

    def confirm_win(self):
        confirm_win = self.main_window.child_window(title="确定", auto_id="2", control_type="Button")
        if confirm_win.exists():
            confirm_win.click_input()

    # 点击确定
    def yes_win(self):
        # 定位第一个子控件的第一个控件，也就是yes按钮
        # yes_win_yes = self.main_window.children()[0].children()[0]
        yes_win_yes = self.main_window.child_window(title="确定", auto_id="1", control_type="Button")
        if yes_win_yes.exists():
            # 点击确定
            yes_win_yes.click_input()

    # 点击否
    def no_win(self):
        # 定位第一个子控件的第二个控件，也就是否按钮
        no_win_yes = self.main_window.child_window(title="取消", auto_id="2", control_type="Button")
        if no_win_yes:
            # 点击否
            no_win_yes.click_input()

    # 查看资金
    def selet_money(self):
        logger.info('开始查询当前账户资金')
        # self.selet_ctrl = self.left_menu_win().children()[5]
        # 定位查询控件
        selet_ctrl = self.main_window.child_window(title="查询[F4]", control_type="TreeItem")
        selet_ctrl.set_focus()
        # 点击查询
        selet_ctrl.click_input()
        # self.deal_today_ctrl=self.selet_ctrl.children()[1]
        # 定位资金股票控件
        selet_money_ctrl = selet_ctrl.child_window(title="资金股份", control_type="TreeItem")
        # 点击确定
        selet_money_ctrl.click_input()
        selet_money_ctrl.draw_outline(colour='red')
        # 调用右侧菜单，获得右侧界面控件
        selet_money_win = self.right_data_win()
        selet_money_win.draw_outline(colour='red')
        selet_money_win.set_focus()
        # 进行ctrl+v操作
        send_keys('^c')
        # 定位弹出验证码的窗口
        for authentication_count in range(10):
            # auth_code_png_win=self.main_window.children()[0].children()[3]
            # 定位验证码图片控件
            auth_code_png_win = self.main_window.child_window(title="检测到您正在拷贝数据，为保护您的账号数据安全，请",
                                                              auto_id="2405",
                                                              control_type="Image")
            auth_code_png_win.draw_outline(colour='red')
            # 截图
            auth_code_png = auth_code_png_win.capture_as_image()
            # 调用Ocr识别验证码
            auth_code = Ocr(auth_code_png)
            # auth_code_win=self.main_window.children()[0].children()[5]
            # 定位验证码编辑框
            auth_code_win = self.main_window.child_window(title="提示", auto_id="2404", control_type="Edit")
            auth_code_win.draw_outline(colour='red')
            # 输入验证码
            auth_code_win.type_keys(auth_code)
            time.sleep(1)
            # 点击确定
            self.yes_win()
            time.sleep(1)
            # 如果验证码查询窗口不存在了，则说明查询成功
            if self.main_window.children()[0].get_properties()['class_name'] != '#32770':
                logger.info('查询验证码成功')
                # 从剪切板复制信息到data
                data = clipboard.GetData()
                # 以dataframe数据格式存储信息
                df = pd.read_csv(io.StringIO(data), delimiter='\t', na_filter=False)
                logger.info(df['证券名称'])
                break
            # 否则验证码输入错误，验证码弹窗依旧存在
            else:
                logger.info('第[%s]次输入验证码失败' % authentication_count)
                # 清空验证码，进行下次循环
                empty_edit(auth_code_win)

    # 连接右侧菜单，返回右侧菜单控件资金
    def balance_data_win(self):
        right_menu_win = self.main_window.child_window(title="HexinScrollWnd", auto_id="1308", control_type="Pane")
        right_menu_win.set_focus()
        logger.info('连接右侧菜单成功')
        return right_menu_win

    # 查看资金
    def selet_balance(self):
        # self.selet_ctrl = self.left_menu_win().children()[5]
        # 定位查询控件
        selet_ctrl = self.main_window.child_window(title="查询[F4]", control_type="TreeItem")
        selet_ctrl.set_focus()
        # 点击查询
        selet_ctrl.click_input()
        # self.deal_today_ctrl=self.selet_ctrl.children()[1]
        # 定位资金股票控件
        selet_money_ctrl = selet_ctrl.child_window(title="资金股份", control_type="TreeItem")
        # 点击确定
        selet_money_ctrl.click_input()
        selet_money_ctrl.draw_outline(colour='red')
        # 调用右侧菜单，获得右侧界面控件
        selet_money_win = self.balance_data_win()
        selet_money_win.draw_outline(colour='red')
        selet_money_win.set_focus()
        # 识别验证码
        self.orc_auth_code()
        # 从剪切板复制信息到data
        data = clipboard.GetData()
        # 以dataframe数据格式存储信息
        df = pd.read_csv(io.StringIO(data), delimiter='\t', na_filter=False)
        return df['可用金额'][0]

    def orc_auth_code(self):
        for authentication_count in range(10):
            time.sleep(1)
            # 进行ctrl+v操作
            send_keys('^c')
            # auth_code_png_win=self.main_window.children()[0].children()[3]
            # 定位验证码图片控件
            auth_code_png_win = self.main_window.child_window(title="检测到您正在拷贝数据，为保护您的账号数据安全，请",
                                                              auto_id="2405", control_type="Image")
            if not auth_code_png_win.exists():
                break
            auth_code_png_win.draw_outline(colour='red')
            # 截图
            auth_code_png = auth_code_png_win.capture_as_image()
            # 调用Ocr识别验证码
            auth_code = Ocr(auth_code_png)
            if (len(auth_code) == 0):
                logger.warning('第[%s]次输入验证码: 识别为空, 重新识别' % (authentication_count + 1))
                self.no_win()
                continue
            # auth_code_win=self.main_window.children()[0].children()[5]
            # 定位验证码编辑框
            auth_code_win = self.main_window.child_window(title="提示", auto_id="2404", control_type="Edit")
            auth_code_win.draw_outline(colour='red')
            time.sleep(1)
            # 输入验证码
            auth_code_win.type_keys(auth_code)
            time.sleep(1)
            # 点击确定
            self.yes_win()
            time.sleep(1)
            # 如果验证码查询窗口不存在了，则说明查询成功
            if not self.main_window.child_window(title="检测到您正在拷贝数据，为保护您的账号数据安全，请", auto_id="2405",
                                                 control_type="Image").exists():
                logger.info('第[%s]次输入验证码: 识别成功, 返回退出' % (authentication_count + 1))
                break
            # 否则验证码输入错误，验证码弹窗依旧存在
            else:
                logger.warning('第[%s]次输入验证码: 识别失败, 重新识别' % (authentication_count + 1))
                self.no_win()

    def cancel_if_auto_code(self):
        exists = self.main_window.child_window(title="检测到您正在拷贝数据，为保护您的账号数据安全，请", auto_id="2405",
                                               control_type="Image").exists()
        if exists:
            self.no_win()

    # 市价买入，传递参数：股票代码，数量
    def market_buy_fast(self, market_buy_stock_number, market_buy_amount):
        # 复制临时主窗口控件，便于操作
        temporary_main_win = self.main_window
        temporary_main_win.set_focus()
        # 定位左侧市价委托控件
        left_sell_ctrl = temporary_main_win.child_window(title="市价委托", control_type="TreeItem")
        left_sell_ctrl.draw_outline(colour='red')
        # 点击市价委托
        left_sell_ctrl.click_input()
        # 定位买入控件
        market_buy_ctrl = self.main_window.child_window(title="买入", control_type="TreeItem")
        market_buy_ctrl.draw_outline(colour='red')
        # 点击买入
        market_buy_ctrl.click_input()
        # 定位证券代码编辑框
        stocks_num_win = temporary_main_win.child_window(auto_id="1032", control_type="Edit")
        empty_edit(stocks_num_win)
        # 输入证券代码
        stocks_num_win.type_keys(market_buy_stock_number)
        # 定位数量编辑框
        amount_win = temporary_main_win.child_window(auto_id="1034", control_type="Edit")
        # 输入数量
        amount_win.type_keys(market_buy_amount)
        # 定位买入按钮
        market_buy_yes = self.main_window.child_window(title="买入", auto_id="1006", control_type="Button")
        # 确定买入
        market_buy_yes.click_input()
        # 点击确定
        if config.ths_trader_debug_mode:
            no_win_no = self.main_window.child_window(title="否(N)", auto_id="7", control_type="Button")
            if no_win_no.exists():
                no_win_no.click_input()
        else:
            yes_win_yes = self.main_window.child_window(title="是(Y)", auto_id="6", control_type="Button")
            if yes_win_yes.exists():
                yes_win_yes.click_input()

        # 点击确定
        confirm_win = self.main_window.child_window(title="确定", auto_id="2", control_type="Button")
        if confirm_win.exists():
            confirm_win.click_input()

    # 市价卖出
    def market_sell_fast(self, market_sell_stock_number, market__sell_amount):
        # 复制临时主窗口控件，便于操作
        temporary_main_win = self.main_window
        temporary_main_win.set_focus()
        # 定位左侧市价委托控件
        left_sell_ctrl = temporary_main_win.child_window(title="市价委托", control_type="TreeItem")
        left_sell_ctrl.draw_outline(colour='red')
        # 点击市价委托
        left_sell_ctrl.click_input()
        # 定位卖出控件
        market_sell_ctrl = self.main_window.child_window(title="卖出", control_type="TreeItem")
        market_sell_ctrl.draw_outline(colour='red')
        # 点击卖出
        market_sell_ctrl.click_input()
        # 定位证券代码编辑框
        stocks_num_win = temporary_main_win.child_window(auto_id="1032", control_type="Edit")
        # 输入证券代码
        stocks_num_win.type_keys(market_sell_stock_number)
        # 定位数量编辑框
        amount_win = temporary_main_win.child_window(auto_id="1034", control_type="Edit")
        # 输入数量
        amount_win.type_keys(market__sell_amount)
        # 定位卖出按钮
        market_buy_yes = self.main_window.child_window(title="卖出", auto_id="1006", control_type="Button")
        # 点击卖出
        market_buy_yes.click_input()
        # 确定
        if config.ths_trader_debug_mode:
            no_win_no = self.main_window.child_window(title="否(N)", auto_id="7", control_type="Button")
            if no_win_no.exists():
                no_win_no.click_input()
            else:
                yes_win_yes = self.main_window.child_window(title="是(Y)", auto_id="6", control_type="Button")
                if yes_win_yes.exists():
                    yes_win_yes.click_input()

        # 点击确定 消除可能的错误弹窗
        confirm_win = self.main_window.child_window(title="确定", auto_id="2", control_type="Button")
        if confirm_win.exists():
            confirm_win.click_input()


# 计算买入数量
def calculate_buy_amount(balance, buy_price):
    if balance < buy_price * 10:
        return 0
    elif balance > 10000:
        return 10000 // buy_price // 10
    else:
        return balance // buy_price // 10


def stock_trade(stock_number, stock_name, buy_price):
    ths_trader = ThsTrader()
    ths_trader.cancel_if_auto_code()
    # 查看资金明细
    balance = ths_trader.selet_balance()
    logger.info("当前账户可用金额：{}", balance)
    # 计算买入数量
    buy_amount = calculate_buy_amount(balance, buy_price)
    if buy_amount != 0:
        # 执行市价买入
        logger.info('准备开始交易，[{}]以市价[{}]买入[{}][{}]股票[{}]手', datetime.now(), buy_price, stock_name,
                    stock_number, buy_amount)
        ths_trader.market_sell_fast(stock_number, buy_amount)
        new = '通知：在[%s]时委托下单，以市价[%s]买入[%s][%s]股票[%s]手' % (
            datetime.now(), buy_price, stock_name, stock_number, buy_amount)
        logger.info(new)
        message.send(new)


# 实例化ThsTarder
if __name__ == '__main__':
    ths_trader = ThsTrader()
    ths_trader.market_buy_fast(123130, 133.900, 80)

