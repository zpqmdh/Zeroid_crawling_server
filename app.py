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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
# Dependencia sys para poder usar print
import sys, json, ast


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
		# chrome_options = webdriver.chromeOptions()
		# chrome_options.add_argument('--headless')
		# chrome_options.add_argument('--no-sandbox')
		# chrome_options.add_argument("--single-process")
		# chrome_options.add_argumnet("--disable-dev-shm-usage")

		driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
		tabs = driver.window_handles

		# open toreta website
		site = '토레타.메인.한국'
		driver.get('http://' + site)

		# crawling
		cnt = 1 # page
		res = []
		j_res = []
		try:
			while True:
				crawling(res)
				cnt += 1
				driver.find_element(By.XPATH, r'//*[@id="root"]/div/div/div[3]/div/div[2]/div/div[2]/button[2]').send_keys(Keys.ENTER)
		finally:
			print("end: ", cnt-1) # check page
			with open('result.json', 'w', encoding='UTF-8') as f:
				for person in res:
					j_person = ast.literal_eval(person)
					j_res.append(j_person)
					f.write(json.dumps(j_person, ensure_ascii=False) + '\n')
			driver.close()
			driver = None
			return json.dumps(j_res, ensure_ascii=False)
		
	return jsonify({'status': True, 'message': 'Already Initiated'})

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
		}, ensure_ascii=False))

if __name__ == '__main__':
    app.run(host='0.0.0.0')