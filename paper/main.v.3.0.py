import time  # 事件库，用于硬性等待
import re
import threading
from bs4 import BeautifulSoup
from selenium import webdriver  # 导入selenium的webdriver模块
from selenium.webdriver.chrome.service import Service
import sys

crawling_browser_dy = None  # 浏览器
comment_list = []  # 评论列表

# 打开文献浏览器
def init_crawling_browser_dy(url):
    global crawling_browser_dy
    service = Service('./chromedriver.exe')
    options = webdriver.ChromeOptions()
    # 无头模式--加上就会打开Google浏览器
    # options.add_argument('--headless')
    options.add_experimental_option('detach', True)
    # 忽略证书错误
    options.add_argument('--ignore-certificate-errors')
    # 忽略 Bluetooth: bluetooth_adapter_winrt.cc:1075 Getting Default Adapter failed. 错误
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 忽略 DevTools listening on ws://127.0.0.1... 提示
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    crawling_browser_dy = webdriver.Chrome(options=options,service=service)
    crawling_browser_dy.maximize_window()  # 浏览器全屏
    time.sleep(1)  # 等待1s
    crawling_browser_dy.get(url)

# 获取html标签中的评论文本
def get_comment_list(i) -> str:
    global comment_list ,crawling_browser_dy

    try:
        content = crawling_browser_dy.page_source
        soup = BeautifulSoup(content, 'html.parser')

         # 检查是否存在reCAPTCHA
        recaptcha_element = soup.find('div', id='gs_captcha_c')
        if recaptcha_element:
            print(f"reCAPTCHA detected at iteration i={i}.")
            sys.exit()
        # 使用CSS选择器查找具有类'gs_fma_snp'或'gs_rs'的元素
        element = soup.find_all(class_='gs_fma_snp')

        # 现在elements同样包含了所有具有'gs_fma_snp'或'gs_rs'类的元素
        item = element[0]
        return item.text

    except Exception as e:
       # 确保element变量在异常情况下也被打印
        print(f"An error occurred: {e}")
        return ''

# 定时关闭浏览器
def close_browser(after_seconds):
    def close():
        global crawling_browser_dy
        time.sleep(after_seconds)
        if crawling_browser_dy:
            crawling_browser_dy.quit()
    threading.Thread(target=close).start()

# 主函数
def main():
    year = '2023'
    read_line =0
    # 读取并打印EMNLP2024.01.txt文件
    file_path = 'Proc. IEEE_2023.txt'
    empty_files_path = 'empty_files0.txt'  # 空文件信息保存路径
    empty_files_info = []  # 存储空文件信息
    with open(file_path, 'r') as file:
        i = 0
        for line in file:
            close_browser_flag = True
            i += 1
            if i <= read_line:
                continue
            title = line.strip()
            title = re.sub(r'[\\/*?:"<>|]', '_', title)
            url = f'https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0%2C5&q={title}&btnG='
            init_crawling_browser_dy(url)
            
            abstract = get_comment_list(i)
            if abstract == '':
                close_browser_flag = False
            
            # 创建以title命名的文件路径
            save_path = f'output/{year}-{str(i)}-{title}.txt'
            
            with open(save_path, 'w', encoding='utf-8') as file:
                if close_browser_flag:
                    file.write('# title\n')
                    file.write(title + '\n\n')
                    file.write('# abstract\n')
                    file.write(abstract + '\n')
                else:
                    empty_files_info.append(f"Line {i}: {title}")
                    with open(empty_files_path, 'w', encoding='utf-8') as file:
                      for info in empty_files_info:
                         file.write(info + '\n')
                         print(f"Empty file information has been written to {empty_files_path}")  # 确认信息
                
    
            close_browser(3)  # 启动关闭浏览器的线程，但不要立即关闭
            time.sleep(3.5)  # 等待浏览器关闭后再继续下一个循环
                # 将空文件信息写入empty_files.txt



if __name__ == "__main__":
    main()