import sys
from PyQt5.QAxContainer import * # QAxContainer은 마이크로소프트사에서 제공하는 프로세스를 가지고 화면을 구성하는데 필요한 기능, 여기서 필요한건 QAxContainer에 속한 QAxWidget
from PyQt5.QtCore import * 
from config.errorCode import *
from PyQt5.QtTest import *

class Kiwoom(QAxWidget):
  def __init__(self):
    super().__init__()  # QAxWidget.__init__() 과 동일
    print("Kiwoom() class start.")

    #### 이벤트 루프를 실행하기 위한 변수 모음 ####
    self.login_event_loop = QEventLoop()  # login_event_loop 변수는 로그인을 요청하고 안전하게 완료될 때까지 기다리게 만들기 위한 이벤트 루프 변수 (PyQt5, QtCore에 포함)
    self.detail_account_info_event_loop = QEventLoop() # 예수금 요청용 이벤트 루프
    ############################################

    ############# 계좌 관련된 변수 ##############
    self.account_stock_dict = {}    # 앞으로 거래하기 위해 가져온 종목들과 정보들을 담아놓고 사용할 딕셔너리 (키: 종목코드 self.account_stock_dict[code] )
    self.not_account_stock_dict = {} # 미체결 정보는 같은 종목을 여러번 주문할 수 있으며, 주문이 바로 체결되지 않고 매수/매도 과정을 거쳐야 함. 그러면 같은 종목에 대해서 주문번호가 다르게 할당되고 , 가격 형태, 주문형태가 주문별로 다르기 때문에 같은 종목이어도 구분을 해야함. 이를 위해 주문번호를 딕셔너리의 키값으로 정보를 업데이트해야함
    self.account_num = None         # 계좌번호 담아둘 변수
    self.deposit = 0                # 예수금
    self.use_money = 0              # 실제 투자에 사용할 금액
    self.use_money_percent = 0.5    # 예수금에서 실제 사용할 비율
    self.output_deposit = 0         # 출금가능 
    self.total_profit_loss_money =0 # 총 평가손익금액
    self.total_profit_loss_rate = 0.0 # 총 수익률(%)
    #############################################

    ############# 요청 스크린 번호 ##############
    self.screen_my_info = "2000"    # 계좌 관련한 스크린 번호
    #############################################

    ########## 초기 셋팅함수들 바로실행 ##########
    self.get_ocx_instance()         # OCX 방식을 파이썬에서 사용할 수 있게 반환해주는 함수 실행
    self.event_slots()              # 키움과 연결하기 위한 시그널/슬롯 모음
    self.signal_login_commConnect() # 로그인 요청 시그널 포함
    self.get_account_info()         # 계좌번호 가져오기
    self.detail_account_info()      # 예수금 요청 시그널 포함
    self.detail_account_mystock()   # 계좌평가잔고내역 가져오기
    QTimer.singleShot(5000, self.not_concluded_account) # 5초 뒤에 미체결 종목들 가져오기 실행
    #############################################


  def get_ocx_instance(self):
    self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # QAxWidget 기능 중 키움API의 모듈을 파이썬에 쓸수있도록 setControl() 함수 필요, .ocx 확장자로 저장된 키움API를 파이썬에서 사용할 수 있도록함
                                                 # 키움 API 설치시 레지스트리에 API 모듈 등록 > 그안엔 ocx방식으로 구성된 키움관련 정보가 들어있으며, 그 레지스트리 파일명이 KHOPENAPI.KHOpenAPICtrl.1
  def event_slots(self):
    self.OnEventConnect.connect(self.login_slot) # 로그인 관련 이벤트
    self.OnReceiveTrData.connect(self.trdata_slot) # 트랜잭션 요청 관련 이벤트
  
  def signal_login_commConnect(self): # 로그인 요청을 담당하는 시그널
    self.dynamicCall("CommConnect()") # 로그인 요청 시그널 # DinamicCall() 은 PyQt5에서 제공하는 함수, 서버에 데이터를 송수신해주는 기능.
    self.login_event_loop.exec_()     # 이벤트 루프 실행

  def login_slot(self,err_code):
    print(errors(err_code)[1])
    self.login_event_loop.exit() # 로그인 처리가 완료됐으면 이벤트루프를 종료
      
    
  def get_account_info(self):
    account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO") # 계좌번호 반환
    account_num = account_list.split(';')[0]
    self.account_num = account_num
    print("[계좌번호] : %s" %account_num)

  def detail_account_info(self, sPrevNext="0"):
    print("[예수금상세현황 요청]")
    self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "jjy10751")
    self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
    self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "3")
    self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)
    
    # self.detail_account_info_event_loop = QEventLoop()
    self.detail_account_info_event_loop.exec_()

  def detail_account_mystock(self, sPrevNext="0"):
    print("[계좌평가잔고내역 요청]") 
    self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "jjy10751")
    self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
    self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
    self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

    # self.detail_account_info_event_loop = QEventLoop()
    self.detail_account_info_event_loop.exec_()

  def not_concluded_account(self, sPrevNext="0"):
    print("[미체결 종목 요청]")
    self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
    self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
    self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

    self.detail_account_info_event_loop.exec_()
  
  def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
    if sRQName == "예수금상세현황요청": # 트랜잭션 요청할 떄 사용한 이름과 동일하게 반환되므로 결과값 구분 가능
      print("[예수금상세현황요청 결과]")
      deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
      self.deposit = int(deposit)

      use_money = float(self.deposit) * self.use_money_percent
      self.use_money = int(use_money)
      self.use_money = self.use_money / 4

      output_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
      self.output_deposit = int(output_deposit)

      print("예수금 : %s" %self.output_deposit)
      self.stop_screen_cancel(self.screen_my_info)
      self.detail_account_info_event_loop.exit()

    elif sRQName =="계좌평가잔고내역요청":
      print("[계좌평가잔고내역요청 결과]")
      total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
      self.total_buy_money = int(total_buy_money)
      total_profit_loss_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
      self.total_profit_loss_money = int(total_profit_loss_money)
      total_profit_loss_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
      self.total_profit_loss_rate = float(total_profit_loss_rate)

      print("계좌평가잔고내역요청 싱글데이터 : %s - %s - %s" %(total_buy_money, total_profit_loss_money, total_profit_loss_rate))
      rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
      
      for i in range(rows):
        code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
        code = code.strip()[1:]

        code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
        stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
        buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
        learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
        current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
        total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
        possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

        print("종목번호: %s - 종목명: %s - 보유수량: %s - 매입가: %s - 수익률: %s - 현재가: %s" %(code, code_nm, stock_quantity, buy_price, learn_rate, current_price))  

        if code in self.account_stock_dict:
          pass
        else:
          self.account_stock_dict[code] = {}
        
        # 반환받은 데이터 타입 변경 후 딕셔너리의 키에 맞게 업데이트
        code_nm = code_nm.strip()
        stock_quantity = int(stock_quantity.strip())
        buy_price = int(buy_price.strip())
        learn_rate = float(learn_rate.strip())
        current_price = int(current_price.strip())
        total_chegual_price = int(total_chegual_price.strip())
        possible_quantity = int(possible_quantity.strip())

        self.account_stock_dict[code].update({"종목명" : code_nm})
        self.account_stock_dict[code].update({"보유수량" : stock_quantity})
        self.account_stock_dict[code].update({"매입가" : buy_price})
        self.account_stock_dict[code].update({"수익률(%)" : learn_rate})
        self.account_stock_dict[code].update({"현재가" : current_price})
        self.account_stock_dict[code].update({"매매금액": total_chegual_price})
        self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

      print("sPrevNext : %s" % sPrevNext)
      print("계좌에 가지고 있는 종목은 %s " % rows)

      if sPrevNext == "2":
        self.detail_account_mystock(sPrevNext="2")
      else:
        self.detail_account_info_event_loop.exit()

      # self.stop_screen_cancel(self.screen_my_info)
    
    elif sRQName =="실시간미체결요청":
      print("[실시간미체결요청 결과]")
      rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

      for i in range(rows):
        code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
        code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
        order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
        order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") # 접수->확인-> 체결
        order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량") 
        order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
        order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") # +매수, -매도, +매수정정, -매도정정
        not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
        ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

        code = code.strip()
        code_nm = code_nm.strip()
        order_no = int(order_no.strip())
        order_status = order_status.strip()
        order_quantity = int(order_quantity.strip())
        order_price = int(order_price.strip())
        order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
        not_quantity = int(not_quantity.strip())
        ok_quantity = int(ok_quantity.strip())

        if order_no in self.not_account_stock_dict:
          pass
        else:
          self.not_account_stock_dict[order_no] = {}
        
        self.not_account_stock_dict[order_no].update({'종목코드': code})
        self.not_account_stock_dict[order_no].update({'종목명': code_nm})
        self.not_account_stock_dict[order_no].update({'주문번호': order_no})
        self.not_account_stock_dict[order_no].update({'주문상태': order_status})
        self.not_account_stock_dict[order_no].update({'주문수량': order_quantity})
        self.not_account_stock_dict[order_no].update({'주문가격': order_price})
        self.not_account_stock_dict[order_no].update({'주문구분': order_gubun})
        self.not_account_stock_dict[order_no].update({'미체결수량': not_quantity})
        self.not_account_stock_dict[order_no].update({'체결량': ok_quantity})

        print("미체결 종목 : %s" % self.not_account_stock_dict[order_no])
      
      self.detail_account_info_event_loop.exit()

  def stop_screen_cancel(self, sScrNo=None):
    self.dynamicCall("DisconnectRealData(QString)", sScrNo) #스크린 번호 연결 끊기


  def get_code_list_by_market(self, market_code):
    code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
    code_list = code_list.split(';')[:-1]
    return code_list
  
  def calculator_fnc(self):
    code_list = self.get_code_list_by_market("10") # 10: 코스닥