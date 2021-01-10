import argparse
from time import sleep

parser = argparse.ArgumentParser(description='PRODUCE 48 points MACRO! v1.0')
parser.add_argument('--headless', action='store_true')
parser.add_argument('--debug', action='store_true')
parser.add_argument('--facebook-id', metavar='(facebook e-mail)', type=str, required=True)
parser.add_argument('--facebook-pw', metavar='(facebook PW)',type=str, required=True)
parser.add_argument('--mnet-id', metavar='(mnet ID)', type=str, required=True)
parser.add_argument('--mnet-pw', metavar='(mnet PW)', type=str, required=True)

args = parser.parse_args()

trainees = [
    24, # Miyawaki Sakuya
    3,  # Goto Moe
    30, # Siroma Miru
    37, # Yabuki Nako
    31, # Sitao Miu
    62, # Takahasi Juri
    21  # Murase Sae
]

emoji = [
    '♪( ´θ｀)ノ',
    '٩(^‿^)۶',
    '(￣Д￣)ﾉ',
    '(*･ω･)ﾉ',
    'ヽ(￣д￣;)ノ=3=3=3',
    '(*´Д｀*)',
    '☆〜（ゝ。∂）'
]


while True:
    try:
        from p48macro import P48Macro
        macro = P48Macro(headless=args.headless, debug=args.debug)

        # Login procedure
        macro.login_p48(args.facebook_id, args.facebook_pw)

        myp_before = macro.producer_point

        # Support trainees
        print('Try voting to trainees... (Daily limit is 7 times)')
        print(f'Selected trainee indices : {trainees}')
        for trainee in trainees:
            macro.vote_to_trainee(trainee)
        print('Voting completed\n')

        # Todaystemp
        macro.get_todaystamp()

        myp_after = macro.producer_point

        # MNET Login
        macro.login_mnet(args.mnet_id, args.mnet_pw)

        mygrade_before = macro.my_grade

        miyawaki_index = 59

        print('Try submitting comments... (Daily limit is 7 times)')
        print('Exploiting produce48 API')
        comment_interval = 8
        for i, e in enumerate(emoji):
            print(f'{i + 1} / {len(emoji)}')
            macro.leave_comment(miyawaki_index, e)
            print(f'Sleeping {comment_interval} seconds')
            sleep(comment_interval)
        print('Submitting comments completed')

        print('Refreshing comments')
        my_comments = macro.get_my_comments(miyawaki_index)
        print(f'Submitted comments : {len(my_comments)}')

        print('Try deleting submitted comments...')
        for comment in my_comments:
            macro.delete_comment(comment['id'])
        print('Deleting comments completed\n')

        talk_index = 54
        print('Try submitting talk comments... (Daily limit is 5 times)')
        for i, e in enumerate(emoji[:5]):
            print(f'{i + 1} / {len(emoji[:5])}')
            macro.leave_talk_comment(talk_index, e)
            print(f'Sleeping {comment_interval} seconds')
            sleep(comment_interval)
        print('Submitting talk comments completed')

        print('Refreshing talk comments')
        my_talk_comments = macro.get_my_talk_comments(talk_index)
        print(f'Submitted talk comments : {len(my_talk_comments)}')

        print('Try deleting submitted talk comments...')
        for comment in my_talk_comments:
            macro.delete_comment(comment['id'])
        print('Deleting talk comments completed\n')

        macro.synchronize_points()

        mygrade_after = macro.my_grade

        print(f'마이 국프 포인트 : {myp_before} → {myp_after}')
        print(f'48 포인트 : {mygrade_before["point"]} → {mygrade_after["point"]}')
        print(f'등급 : {mygrade_after["grade"]}')
        break
    except KeyboardInterrupt:
        break
    except:
        pass
    finally:
        del macro