import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from time import sleep

SUPPORT_MAIN = 'https://produce48.kr/index.php'
TODAY_STAMP = 'https://produce48.kr/m48_stemp.php'
VOTE_SCRIPT = 'dayhug("dayhug", "{}")'
M48_VOTING = 'https://produce48.kr/m48_test.php?idx={}&cate=hug'
P48_MNET = 'http://produce48.mnet.com'

class P48Macro:
    def __init__(self, chrome_driver='chromedriver', headless=False, debug=False, delay=2):
        self.logger = logging.getLogger('produce48')
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.logger.addHandler(logging.StreamHandler())

        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1920x1080')

        self.driver = webdriver.Chrome(executable_path=chrome_driver, chrome_options=chrome_options)
        self.delay = delay

    def __del__(self):
        self.driver.quit()

    def login_p48(self, facebook_id, facebook_pw):
        logger = self.logger
        driver = self.driver

        logger.info('Try logging into produce48.kr...')
        logger.debug(f'GET : {SUPPORT_MAIN}')
        driver.get(SUPPORT_MAIN)
        logger.debug(f'Execute : {VOTE_SCRIPT.format("none")}')
        driver.execute_script(VOTE_SCRIPT.format('none'))

        mother_window = driver.current_window_handle
        logger.debug(f'Main window handle : {mother_window}')
        login_window = [handle for handle in driver.window_handles if handle != driver.current_window_handle][0]
        logger.debug(f'Login window handle : {login_window}')
        driver.switch_to.window(login_window)

        driver.find_element_by_id('email').send_keys(facebook_id)
        driver.find_element_by_id('pass').send_keys(facebook_pw)
        driver.find_element_by_id('u_0_0').click()
        sleep(self.delay)

        driver.switch_to.window(mother_window)

        if login_window in driver.window_handles:
            logger.error('Facebook authentication failed!')
            driver.quit()
            raise Exception('Facebook authentication failed!')

        logger.info('Login completed : produce48.kr\n')

    @property
    def producer_point(self):
        driver = self.driver

        driver.get('https://produce48.kr/umypage.php')
        selector = '#myPage > div > article > table > tbody > tr > td:nth-child(1) > b'
        point = self.driver.find_element_by_css_selector(selector).text
        return int(point)

    def vote_to_trainee(self, trainee_index):
        logger = self.logger
        driver = self.driver

        logger.debug(f'GET : {M48_VOTING.format(trainee_index)}')
        driver.get(M48_VOTING.format(trainee_index))
        logger.info(f'Voting to trainee {trainee_index}')
        logger.debug(f'Execute : {VOTE_SCRIPT.format(trainee_index)}')
        driver.execute_script(VOTE_SCRIPT.format(trainee_index))
        sleep(self.delay)
        try:
            driver.switch_to.alert.accept()
        except UnexpectedAlertPresentException:
            logger.warning(f'Already voted to {trainee_index} today!')
            driver.switch_to.alert.accept()
        except NoAlertPresentException:
            pass

    def get_todaystamp(self):
        logger = self.logger
        driver = self.driver

        logger.info('Try getting today stamp...')
        logger.debug(f'GET : {TODAY_STAMP}')
        driver.get(TODAY_STAMP)
        driver.find_element_by_id('todaystemp').click()
        sleep(self.delay)
        try:
            driver.switch_to.alert.accept()
        except UnexpectedAlertPresentException:
            driver.switch_to.alert.accept()
        except NoAlertPresentException:
            pass
        logger.info('Getting today stamp completed\n')

    def login_mnet(self, mnet_id, mnet_pw):
        logger = self.logger
        driver = self.driver

        logger.info('Try logging into mnet.com...')
        logger.debug(f'GET : {P48_MNET}')
        driver.get(P48_MNET)
        sleep(self.delay)
        logger.debug('Execute : gnbLogin()')
        driver.execute_script('gnbLogin()')
        driver.find_element_by_id('userId').send_keys(mnet_id)
        driver.find_element_by_id('pw').send_keys(mnet_pw)
        driver.find_element_by_id('loginSubmitBtn').click()

        logger.info('Login completed : mnet.com\n')

    @property
    def my_grade(self):
        driver = self.driver
        driver.get(P48_MNET)
        script = '''
            var res;
            $.ajax({
                type: "get",
                url: "/api/points/mygrade",
                dataType: "json",
                async: false,
                success: function(result) {
                    res = result;
                }
            });
            return res;
        '''
        result = driver.execute_script(script)
        if result['code'] == '0000':
            return result['data']['grade']
        else:
            return result['message']

    def leave_comment(self, trainee_index, comment):
        logger = self.logger
        driver = self.driver

        logger.info('Try leaving comment...')
        logger.info(f'trainee_index : {trainee_index}, comment : {comment}')
        trainee_profile_url = f'{P48_MNET}/pc/profile/{trainee_index}'
        logger.debug(f'GET : {trainee_profile_url}')
        driver.get(trainee_profile_url)
        script = f'''
            var res;
            $.ajax({{
                type: "post",
                url: "/api/comment/p48-profile-{trainee_index}",
                dataType: "json",
                data: {{contents: "{comment}"}},
                async: false,
                success: function(result) {{
                    res = result;
                }}
            }});
            return res;
        '''
        result = driver.execute_script(script)
        logger.debug(f'Server response : {result}')

    def get_my_comments(self, trainee_index, page=1):
        logger = self.logger
        driver = self.driver

        logger.info('Try retrieving my comments...')
        trainee_profile_url = f'{P48_MNET}/pc/profile/{trainee_index}'
        logger.debug(f'GET : {trainee_profile_url}')
        driver.get(trainee_profile_url)
        script = f'''
            var res;
            $.ajax({{
                type: "get",
                url: "/api/comment/p48-profile-{trainee_index}",
                data: {{page: {page}}},
                dataType: "json",
                async: false,
                success: function(result) {{
                    res = result.data.list.filter(comment => comment.mine == "Y");
                }}
            }});
            return res;
        '''
        return driver.execute_script(script)

    def delete_comment(self, comment_id):
        logger = self.logger
        driver = self.driver

        logger.info(f'Try deleting comment_id = {comment_id}...')
        logger.debug(f'GET : {P48_MNET}')
        driver.get(P48_MNET)
        script = f'''
            var res;
            $.ajax({{
                type: "post",
                url: "/api/comment/{comment_id}/delete",
                dataType: "json",
                async: false,
                success: function(result) {{
                    res = result;
                }}
            }});
            return res;
        '''
        result = driver.execute_script(script)
        logger.debug(f'Server response : {result}')

    def leave_talk_comment(self, talk_index, comment):
        logger = self.logger
        driver = self.driver

        logger.info('Try leaving talk comment...')
        logger.info(f'talk_index : {talk_index}, comment : {comment}')
        logger.debug(f'GET : {P48_MNET}')
        driver.get(P48_MNET)
        script = f'''
            var res;
            $.ajax({{
                type: "post",
                url: "/api/comment/p48-talk-{talk_index}",
                dataType: "json",
                data: {{contents: "{comment}"}},
                async: false,
                success: function(result) {{
                    res = result;
                }}
            }});
            return res;
        '''
        result = driver.execute_script(script)
        logger.debug(f'Server response : {result}')

    def get_my_talk_comments(self, talk_index, page=1):
        logger = self.logger
        driver = self.driver

        logger.info('Try retrieving my talk comments...')
        logger.debug(f'GET : {P48_MNET}')
        driver.get(P48_MNET)
        script = f'''
            var res;
            $.ajax({{
                type: "get",
                url: "/api/comment/p48-talk-{talk_index}",
                data: {{page: {page}}},
                dataType: "json",
                async: false,
                success: function(result) {{
                    res = result.data.list.filter(comment => comment.mine == "Y");
                }}
            }});
            return res;
        '''
        return driver.execute_script(script)

    def synchronize_points(self):
        logger = self.logger
        driver = self.driver

        logger.info(f'Try synchronizing points...')
        logger.debug(f'GET : {P48_MNET}')
        driver.get(P48_MNET)
        script = f'''
            var res;
            $.ajax({{
                type: "get",
                url: "/api/points/getPatnerPoints",
                dataType: "json",
                async: false,
                success: function(result) {{
                    res = result
                }}
            }});
            return res;
        '''
        result = driver.execute_script(script)
        logger.info(result['message'])
        logger.debug(f'Server response : {result}')
