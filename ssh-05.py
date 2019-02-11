import subprocess
import requests
import socket
import json
from threading import Thread
from collections import OrderedDict
import time
import sys
import os
import re

def MACtoSTR(_input):
    output = b''
    tmp = re.split(':', _input)
    for i in range(6):
        output = output + bytes.fromhex(tmp[i])
    return b'\xff'*6 + output*16

def sendSER(_input, _com, _baudrate):
    tmpFileName = "TEMP_FILE_FOR_SERIAL.txt"
    _com = 'COM' + str(_com)
    _cfg = str(_baudrate) + ",8,1,N,N"
    cmd = ['plink', '-serial', _com, '-sercfg', _cfg, "<", tmpFileName]

    tmpfile = open(tmpFileName,'w')
    tmpfile.write(_input + "\n\\x0d")
    tmpfile.close()
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        out = process.stdout.readline(10)
        FNULL = open(os.devnull, 'w')
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=process.pid), stdout=FNULL, stderr=subprocess.STDOUT)
    except:
        return False
    return out

def sendCMD(_input, _IP, return_type):
    out = None
    cmd = ['plink', 'root@{} '.format(_IP), _input]
    # cmd = ['plink', 'root@{} '.format(_IP), '-pw',"", _input]

    # out = json.loads( subprocess.check_output(cmd, universal_newlines=True ) )
    # print(out)
    # SubProcess 생성
    proc = subprocess.Popen(cmd,shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    #Test print
    out = proc.stdout.readline()
    print(out)
    out = out.decode('utf-8')
    print(out)

    #SubProcess 정리
    proc.stdin.flush()
    proc.stdout.flush()
    proc.stdin.close()
    proc.stdout.close()
    proc.terminate()
    proc.wait(timeout=2)

    # 옵션 처리
    if return_type != "no":
        if return_type == "json" :
            out = json.loads( out )

    return out

def print_select_menu():
    print("\nLeft List!!")
    print("1: Set modelName, AreaOptionValue, DebugLevel, SerialBaudRate")
    print("2: Set Tooloptions")
    print("3: Set Mailing service")
    print("4: OPS Synctest")
    print("exit: Exit to Loop\n")
    select_n = str(input("Enter what want to do: ") )
    return select_n

def print_smpt_seq_info():
    print("SMPT setting sequence")
    print("1.")
    print("  1.1 Get smpt server")
    print("2.")
    print("  2.2 Get Reporter email addr")
    print("  2.3 Get Reporter passwd")
    print("3.")
    print("  3.1 Get Recipient email addr\n")

def set_instart_info(_IP,info_v_list):
    info_list = ["modelName","areaOptionValue","debugLevel","serialBaudRate"]

    # 받아온 내용 셋팅
    # modelName은 셋팅 안함.
    for num in range(1, len(info_v_list) ):
        luna = '''luna-send -n 1 luna://com.webos.service.tv.systemproperty/setProperties '{"'''+ info_list[num] +'''" : "'''+  info_v_list[num]   +'''" }' '''
        sendCMD( luna , _IP, "no")
        time.sleep(1)
    # 디버그 레벨 : luna-send -n 1 -f luna://com.webos.service.tv.systemproperty/setProperties '{ "debugLevel" : "debug" }'
    # 시리얼 속도 : luna-send -n 1 -f luna://com.webos.service.tv.systemproperty/setProperties '{ "serialBaudRate" : "115200" }'

    #입력값이 반영되었는지 확인.
    print("Checking.. ")
    for num in range(0, len( info_v_list )):
        luna = '''luna-send -n 1 luna://com.webos.service.tv.systemproperty/getProperties '{ "keys" : ["'''+info_list[num]+ '''"] }' '''
        check_result = sendCMD(luna,_IP, "json")

        time.sleep(1)
        if info_v_list[num] == str( check_result[ info_list[num] ] ) :
            print("Enter value: " + info_v_list[num])
            print("Setting value: " + str( check_result[ info_list[num] ] ) )
            print("OK!")
            time.sleep(1)
        else:
            print("Error!!")
            break

def set_tooloption(_IP, tool_op_list):
    print('We will set Tooloption by Typing\nWant to stop : exit')

    tool_op_count = len(tool_op_list) +1

    # 툴 옵 셋팅
    for num in range(1,tool_op_count):
        luna = '''luna-send -n 1 luna://com.webos.service.tv.systemproperty/setProperties "{'toolOption''' +str(num)+ '''Value':' ''' + tool_op_list[num-1] +''' '}" '''
        #
        sendCMD(luna, _IP, "no")
        time.sleep(1)

    #입력값이 반영되었는지 확인.
    print("Checking..")
    for num in range(1,tool_op_count):
        luna = '''luna-send -n 1 luna://com.webos.service.tv.systemproperty/getProperties '{"keys":["toolOption''' + str(num) +'''Value"]}' '''
        check_result = sendCMD(luna, _IP, "json")

        # print(tool_op_list[num-1])
        # print( str( check_result["toolOption"+ str(num) + "Value"]) )
        time.sleep(1)
        if tool_op_list[num-1] == str( check_result["toolOption"+ str(num) + "Value"]) :
            print("enter num: " + tool_op_list[num-1])
            print("setting num: " +str( check_result["toolOption"+ str(num) + "Value"] ) )
            print("OK!")
            time.sleep(1)
        else:
            print("Error!!")
            break

def set_mail_server_addr_user_id_pw(_IP, info_list):

    print("SMPT Server, Reporter Email ID PW setting... ")
    luna = '''luna-send -n 1 luna://com.webos.settingsservice/setSystemSettings '{"settings": {"status'''
    luna += '''ReportUserEmail": "''' + info_list[1] + '''", "statusReportAccount": {"id": "''' + info_list[1] + '''", "p'''
    luna += '''assword": "''' + info_list[2] + '''", "smtpServer": "'''+info_list[0] +'''"} }, "category":"commercial"}' '''
    sendCMD(luna, _IP, "no")
    time.sleep(1)

    print("Recipient Email ID setting...  ")
    luna = '''luna-send -n 1 luna://com.webos.settingsservice/setSystemSettings '{"sett'''
    luna += '''ings": {"statusReportRecipient": ["''' + info_list[3] +'''"]}, "category":"commercial"}' '''
    sendCMD(luna, _IP, "no")
    time.sleep(1)

    print("ReportMode Start!")
    luna = '''luna-send -n 1 luna://com.webos.settingsservice/setSystemSettings '{"settings": {"statusReportMode":"on"}, "category":"commercial"}' '''
    sendCMD(luna, _IP, "no")
    time.sleep(1)

    print("Now enter New HDMI signal")
    input("Complete ? : ")
    print("Detach HDMI cable")
    input("Complete ? : ")
    print("Now Enter gmail. And, wait a minute")

def get_instart_info_s(_IP):
    info_list = ["modelName","areaOptionValue","debugLevel","serialBaudRate"]
    info_value_list = []
    ment_str = None
    for info in info_list:

        if info != "debugLevel":
            ment_str = "Enter " + info+" : "
        else :
            ment_str = "Enter " + info+ "(debug, event, release) : "

        info_value_list.append( str(input(ment_str)) )

    return info_value_list

def get_toolop_info_s(_IP):
    print('We will set Tooloption by Typing\nWant to stop : exit')
    tool_op_list=[]
    tool_op_count = 9

    for num in range(1,tool_op_count+1):
        str_num = str(num)
        inp = input("Enter! toolOption" + str_num + " : ")
        if inp == "exit":
            break
        tool_op_list.append(str(inp))


    return tool_op_list

def get_mail_server_addr_user_id_pw():
    #데이터 분리는 나중에 일단 리스트에 넣는다.
    info_list = []
    info_list.append( str( input("smpt server [ rec:  smtp.gmail.com:587  ] : ") ) )
    info_list.append( str( input("Reporter email [ rec: qazwsx741.edcrfv852@gmail.com ]: " )) )
    info_list.append( str( input("Reporter pass [ rec: qazwsx741edcrfv852 ]: " ) ))
    info_list.append( str( input("Recipient email [ rec: lge.statusreport@gmail.com ]: ") ) )
    return info_list

def ops_test(_IP):
    #ops지원 모델 확인
    luna = '''luna-send -n 1 luna://com.webos.service.settings/getSystemSettings '{"category":"commercial", "keys":["opsReady"]}' '''
    out = sendCMD(luna,_IP,"json")
    #OPS 지원 모델인지 검사
    if out["settings"]["opsReady"] == "off":
        print("This device not support OPS!")
        time.sleep(1)
    else:
        print("This device support OPS")
        time.sleep(1)
        luna = ''' luna-send -n 1 luna://com.webos.service.settings/getSystemSettings '{"category":"commercial", "keys":["opsConnection"]}' '''
        out = sendCMD(luna,_IP,"json")
        #OPS 연결 되었는지 검사
        if out["settings"]["opsConnection"] == "false":
            print("But, OPS is not connected")
            time.sleep(1)
        else:
            #OPS Mode 자동 설정
            print("OPS is connected.\nReady to test!")
            time.sleep(1)
            luna = ''' luna-send -n 1 luna://com.lge.settingsservice/setSystemSettings'''
            luna += ''' '{"category":"commercial","settings":{"opsPowerControl":"SyncOn"}}' '''

            print("First setting : SyncOn Mode")
            time.sleep(1)
            sendCMD(luna,_IP,"no")


            luna = ''' luna-send -n 1 luna://com.lge.settingsservice/setSystemSettings'''
            luna += ''' '{"category":"commercial","settings":{"opsPowerControl":"SyncOnOff"}}' '''

            print("First setting : SyncOnOff Mode")
            time.sleep(1)
            sendCMD(luna,_IP,"no")

def check_simplink_popup(_IP,_com,_baudrate):
    # 현재 값 확인.
    luna = '''luna-send -n 1 luna://com.lge.settingsservice/getSystemSettings '{"category":"other","keys":["simplinkEnable"], "subscribe": true}' '''
    out = sendCMD(luna, _IP, "json")
    before_sim_Enable_value = out["settings"]["simplinkEnable"]
    time.sleep(1)
    # 리모컨 signal 전송.
    sendSER("mc 01 7e", _com, _baudrate)
    time.sleep(1)

    # checking 변경된 값.
    out = sendCMD(luna ,_IP, "json")
    after_sim_Enable_value = out["settings"]["simplinkEnable"]

    if before_sim_Enable_value != after_sim_Enable_value:
        print("Commed Hit!\nPop up will be open!")
        print("before: " +before_sim_Enable_value)
        print("after: " +before_sim_Enable_value)
        time.sleep(1)
    else :
        print("Commed didn't Hit")
    time.sleep(2)

def check_simplink_rc_control(_IP,_com,_baudrate):

    # 외부입력 연결체크
    externel_device_id = check_externel_device(_IP)
    
    # 입력이 있는 곳으로 이동
    if externel_device_id is not None :
        print("ex!!! ::: externel_device_id")
        time.sleep(2)
        print("\nMove to externel")
        luna = '''luna-send -n 1 luna://com.webos.applicationManager/launch '{"id":"com.webos.app.'''+ externel_device_id +'''"}' '''
        sendCMD(luna, _IP, "no")
        print("Waiting for few second....")
        print("turn on externel device.")
        time.sleep(7)
    # # 없으면 종료
    # else :
    #     return False
    # # 이동 Serial
    # # HDMI1 : ae 00 31
    # # HDMI2 : ae 00 32
    # # HDMI3 : ae 00 33

    # Kwikwai 연결체크
    is_kwikwai_connect = check_kwikwai_connect(_IP)
    if is_kwikwai_connect == True:
        print("Kwikwai is connected!!")
        time.sleep(2)
    else :
        print("Kwikwai is not connected")
        print("Try later!!")
        print("Exit this session\n")
        time.sleep(3)
        return False
    # # 모든 장치 확인 OK
    # # Kwikwai를 이용해 재생, 뒤로가기 체크
    check_play_back_button_work(_IP,_com, _baudrate)

def check_play_back_button_work(_IP,_com, _baudrate):
    # pooling 상태 끊는다. 뮤트 버튼
    # simplink play 버튼 검증
    sendSER("mc 01 09", _com, _baudrate)
    time.sleep(3)
    print("Enter play key seesion")
    out = http_and_serial_threading("play",_com, _baudrate)

    if out == True:
        print("Play key verified")
    else:
        print("Play key not verified")
        print("Auto verify end")

    # simplink pause 버튼 검증
    # sendSER("mc 01 09", _com, _baudrate)
    print("\nNext is Pause key...")
    time.sleep(1)
    for i in range(0,4) :
        print("wait...")
        time.sleep(1)
    
    print("Enter puase key seesion")
    out = http_and_serial_threading("pause",_com, _baudrate)
   
    if out == True:
        print("pause key verified")
    else:
        print("pause key not verified")
        print("Auto verify end")
    # Pre_step 미디어 위치 찾아가기
    #   OK, 우, OK, 플레이, 뒤로가기
    # sendSER("mc 01 44", _com, _baudrate)
    # sendSER("mc 01 06", _com, _baudrate)
    # sendSER("mc 01 44", _com, _baudrate)
    # sendSER("mc 01 B0", _com, _baudrate)
    # sendSER("mc 01 28", _com, _baudrate)

def thread_http_req(ack,index):
    try:
        ack[index] = requests.get('http://kwikwai/ARK?index=0', timeout=2)
    except BaseException:
        print("Time out")

def thread_send_play_key(_com,_baudrate):
    print("Play key pressed.")
    sendSER("mc 01 B0", _com, _baudrate)

def thread_send_pause_key(_com,_baudrate):
    print("Pause key pressed.")
    sendSER("mc 01 BA", _com, _baudrate)

def http_and_serial_threading(serial_mode,_com, _baudrate):
    # thread의 값을 받아올 배열
    ack = [None] *1
    threads = [None] *2

    # http request send
    # OK serial send
    threads[0] = Thread(target=thread_http_req, args=(ack,0) )
    # kf 01 20
    threads[0].start()
    time.sleep(0.5)

    if serial_mode == "play":
        threads[1] = Thread(target=thread_send_play_key, args=(_com, _baudrate) )
    elif serial_mode == "pause":
        threads[1] = Thread(target=thread_send_pause_key, args=(_com, _baudrate) )
    threads[1].start()
    threads[1].join()
    threads[0].join()

    print(ack[0])
    # str 변환
    ack[0] = str(ack[0].json())
    # http 에서 Return 시, Json type에 호환되지않는 데이터 전송
    # json 형태로 string을 바꿔줌
    ack[0] = ack[0].replace("'",'"')
    ack[0] = ack[0].replace(", None", "" )
    ack[0]= ack[0].replace("False","false")
    ack[0] = ack[0].replace("True", "true")

    # json 변환
    ack_json = json.loads(ack[0])

    # ack_json['messages'][0]['blocks'][2] 의 값으로 누른 값 판별 가능
    # print(ack_json['messages'][0]['blocks'][2])

    if ack_json['messages'][0]['blocks'][2] == 17536:
        print("Cec play key detected!!")
    elif ack_json['messages'][0]['blocks'][2] == 18048:
        print("CeC pause key detedted!!")
    else:
        return False
    
    return True
        # try:
        #     ack = requests.get('http://kwikwai/ARK?index=0', timeout=0.6)
        # except BaseException:
        #     #   OK 우 OK 플레이
        #     sendSER("mc 01 44", _com, _baudrate)
        #     sendSER("mc 01 06", _com, _baudrate)
        #     sendSER("mc 01 44", _com, _baudrate)
        #     ack = requests.get('http://kwikwai/ARK?index=0')
        #     time.sleep(1)
        #     sendSER("mc 01 B0", _com, _baudrate)
        #     time.sleep(1)
        #     ack = requests.get('http://kwikwai/ARK?index=0')
        #     time.sleep(1)
        #     sendSER("mc 01 28", _com, _baudrate)

def test_func_____check_req(_IP,_com,_baudrate):
    # while True:
    #     ack = None
    #     try:
    #         # ack = requests.get('http://kwikwai/ARK?index=0')
    #         # print(ack.json())
    #         # print(ack)
    #         # print( ack['devices'])
    #         # print( ack['messages'])
    #
    #         # print(ack.json()['messages'][0])
    #         # for s1 in ack.json()['messages']['blocks']:
    #         #     print(s1)
    #     except BaseException:
    #         print("tout\n")


    ack_str = ''' {'devices': [{'age': 10}, None, None, None, {'osd_name': 'BD PLAYER      ', 'age': 10}, None, None, None, None, None, None, None, None, None, None], 'messages': [ {'timestamp': 1548841761300, 'ack': 1, 'sent': False, 'bus': 'A', 'blocks': [1024, 17408, 1152]} ], 'next': 80} '''
    ack_str = ack_str.replace("'",'"')
    ack_str = ack_str.replace(", None", "" )
    ack_str = ack_str.replace("False","false")
    ack_str = ack_str.replace("True", "true")

    # print(ack_str)

    ack = json.loads(ack_str)
    # print(ack)

    print(ack['messages'][0]['blocks'][2])

    time.sleep(1)


# 448,704,  960, 1152, 1472, 1728,1984,2240,2496,2752,3008,3264,3520, 3776,
# 3904,34624,64,57408,37312
# ack = requests.get('http://kwikwai/ARK?index=0')

# {'devices': [{'age': 10}, None, None, None, {'osd_name': 'BD PLAYER      ', 'age': 10}, None, None, None, None, None, None, None, None, None, None],
# 'messages': [ {'timestamp': 1548841761300, 'ack': 1, 'sent': False, 'bus': 'A', 'blocks': [1024, 17408, 1152]} ],
# 'next': 80}

def check_kwikwai_connect(_IP):

    # Kwikwai 가 연결되어 있는지 체크
    ping_count = 0
    print("Kwikwai connect checking.....")
    while True:
        check_kwikwai = None
        try :
            check_kwikwai = requests.get('http://kwikwai/', timeout=2 )
        except requests.exceptions.Timeout:
            print("ping...")
        except requests.exceptions.HTTPError :
            print("ping...")
        except BaseException :
            print("ping...")
        print("ping...")
        ping_count += 1
        time.sleep(2)

        if check_kwikwai is not None :
            # print(check_kwikwai.text)
            return True
        elif ping_count == 4:
            return False


def check_externel_device(_IP):
    print('\nGets externaldevice Input StatusList ..')

    luna = '''luna-send -n 1 palm://com.webos.service.tv.externaldevice/getExternalInputStatusList '{"subscribe":true}' '''
    ex_input_status = sendCMD(luna,_IP, "json")

    #연결된 Device 있는지 검사.
    for deviceList in ex_input_status['deviceList']:
        if deviceList['signalDetection'] == True :
            
            device_id = deviceList["deviceID"]
            device_id = device_id.replace("_","")
            device_id = device_id.lower()
            print("Exist {0}".format(device_id))

            return device_id
    # print( type(device_list['signalDetection']))
    # print("\nExternel_device is not connected!")
    # print("plz connect Externel device\n")

    print("not exist")
    return None
# luna-send -n 1 -f luna://com.webos.applicationManager/launch '{"id":"com.webos.app.hdmi3"}'
# Threading test 함수들
def check_cec_cmd_by_thread_http_req2(ack,i):
    try:
        ack[i] = requests.get('https://code.i-harness.com/en/q/693190', timeout=2)
        time.sleep(3)
    except BaseException:
        print("Time out")

def check_cec_cmd_by_thread_http_req3(ack,i):
    try:
        ack[i] = requests.get('https://code.i-harness.com/en/q/693190', timeout=2)
        time.sleep(1)
    except BaseException:
        print("Time out")

if __name__ == '__main__':
    global MACaddr, IPaddr
    MACaddr = '38:8C:50:E3:F5:E1'
    IPaddr = '192.168.0.48'
    WOLenable = False
    WOLwaitTime = 1
    defaultCOM = '4'
    defaultRate = 115200

    while True:
        select_n = print_select_menu()

        if select_n == "1":
            # 모델이름, 지역 옵션, 디버그 레벨, 시리얼 보드레이트
            # 모델, 지역, 디버그, 시티얼 옵션 입력
            info_v_list = get_instart_info_s(IPaddr)
            # Luna 커맨드로 셋팅
            set_instart_info(IPaddr,info_v_list)
        elif select_n == "2":
            # 툴옵션들
            # 툴옵션s 입력
            tool_op_v_list = get_toolop_info_s(IPaddr)
            # Luna 커맨드로 셋팅
            set_tooloption(IPaddr, tool_op_v_list)
        elif select_n == "3":
            #메일링 서비스 셋팅
            print_smpt_seq_info()
            info_list = get_mail_server_addr_user_id_pw()
            set_mail_server_addr_user_id_pw(IPaddr, info_list)
        elif select_n == "4":
            # OPS 연결 확인
            # 확인 시퀀스
            # 가능 모델 검사 -> 연결상태 검사 -> 각 단계 수행.
            ops_test(IPaddr)
        elif select_n == "5":
            # luna = '''luna-send -n 1 luna://com.webos.service.tv.capture/executeOneShot '{"path":"/tmp/usb/sda/sda1/", "method":"DISPLAY", "width":1080, "height":720,"format":"JPEG"}' '''
            luna = '''luna-send -n 1 luna://com.webos.service.tv.capture/executeOneShot '{"path":"/media/", "method":"DISPLAY", "width":1080, "height":720,"format":"JPEG"}' '''
            sendCMD(luna, IPaddr, "no")
            print("Screen captured\n/media/")
        elif select_n =="6":   
            #  
            luna = '''luna-send -n 1 luna://com.lge.settingsservice/setSystemSettings'{"category":"hotelMode", "settings":{"noActivityPowerOffHours":"off"}}' '''
            sendCMD(luna, IPaddr, "no")
        elif select_n == "8":
            check_play_back_button_work(IPaddr,defaultCOM,defaultRate)
        elif select_n == "9":
            check_simplink_rc_control(IPaddr,defaultCOM,defaultRate)
            # print("TEST Menu START!!")
            # ack = [None]*2
            # threads = [None]*2

            # threads[0] = Thread(target=check_cec_cmd_by_thread_http_req2, args=(ack,0) )
            # threads[0].start()
            # threads[1] = Thread(target=check_cec_cmd_by_thread_http_req3, args=(ack,1) )
            # threads[1].start()
            # threads[1].join()
            # print(ack[1].text)
            # print("First End")
            # time.sleep(2)
            # threads[0].join()
            # print(ack[0].text)
            # print("Second End")

        else:
            break

    # luna-send -n 1 luna://com.lge.settingsservice/getSystemSettings '{"category":"other","keys":["simplinkEnable"], "subscribe": true}'
    # OPS 연결 확인
    # externel_device 는 Luna 확인 필요 // 안먹힌다.
    # check_externel_device(IPaddr)

    #########################################################
    # for test
    # for i in range(0,2):
    #     luna = '''luna-send -n 1 luna://com.webos.service.settings/getSystemSettings '{"category":"commercial", "keys":["opsReady"]}' '''
    #     out =sendCMD(luna, IPaddr, "json")

    #     someting = input("Enter : ")
    #     print(someting)
    #############################################################