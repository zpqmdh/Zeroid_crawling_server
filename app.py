# Flask = Framework para web service
# 참고: https://github.com/OscarDHdz/selenium-flask
# Dependencias de Flask
from flask import Flask
from flask import jsonify
from flask import request
# Selenium dependencies
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
# Dependencia sys para poder usar print
import sys, json


app = Flask(__name__)
driver = None
tabs = None

def validateDriver():
	global driver
	if ( driver is None ):
		return {'status': False, 'message': 'Driver not initialized'}
	try:
		title = driver.current_url
	except:
		return {'status': False, 'message': 'Disconnected Driver'}
	return {'status': True, 'message': 'Driver initiated'}

@app.route('/status', methods=['GET'])
def get_status():
	return jsonify(validateDriver())

@app.route('/', methods=['GET']) # init
def get_init():
	global driver
	global tabs
	status = validateDriver();
	if ( status['status'] is False ):
		driver = webdriver.Chrome()
		tabs = driver.window_handles
		return jsonify({'status': True, 'message': 'Initialized'})
	return jsonify({'status': True, 'message': 'Already Initiated'})

@app.route('/open', methods=['GET']) 
def get_open():
	status = validateDriver()
	site = '토레타.메인.한국' # toreta website
	if ( status['status'] is True ):
		driver.get('http://' + site)
		return jsonify({'status': True})
	return jsonify(status)

@app.route('/close', methods=['GET']) # 작업 다 끝나면 자동으로 호출되도록 수정 예정
def get_close():
	global driver
	status = validateDriver()
	if ( status['status'] is True ):
		driver.close();
		driver = None;
		return jsonify({'status': True})
	return jsonify(status)

@app.route('/login', methods=['POST'])
def login():
    id = ''
    pw = ''
    '''
    toreta website에서 login기능
	id와 pw를 어떻게 안전하게 다룰 것인가? -> .env 파일 사용
    '''

def wait_page_ready(driver):
    WebDriverWait(driver, timeout=60).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

def crawling(res):
	html = driver.page_source
	bs = BeautifulSoup(html, 'html.parser')

	# data field 확인하여 toreta와 잘 matching 해주기
	id_list = bs.find_all('div', {'data-field' : 'id'})
	name_list = bs.find_all('div', {'data-field' : 'name'})
	age_list = bs.find_all('div', {'data-field' : 'age'})
	visit_list = bs.find_all('div', {'data-field' : 'visit'})
	phoneNumber_list = bs.find_all('div', {'data-field' : 'phoneNumber'})
	
	# 비어있는 field 처리 해주기
	for i in range(1, len(id_list)):
		res.append(json.dumps({
			'id': id_list[i].text,
			'name': name_list[i].text,
			'age': age_list[i].text,
			'visit': visit_list[i].text,
			'phoneNumber': phoneNumber_list[i].text
		}))

@app.route('/get-customer', methods=['GET'])
def get_customer():
	cnt = 1 # page
	res = [] # result / 호출될 때 마다 초기화 후 크롤링
	try:
		while True:
			crawling(res)
			cnt += 1
			driver.find_element(By.XPATH, r'//*[@id="root"]/div/div/div[3]/div/div[2]/div/div[2]/button[2]').click()
	finally:
		print("end: ", cnt-1) # 총 넘긴 페이지 수 확인
		with open('result.json', 'w') as f:
			for person in res:
				f.write(person + '\n')
		return json.dumps(res, indent=4)

if __name__ == '__main__':
    app.run(debug=True)