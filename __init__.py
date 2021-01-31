from kiwoom.kiwoom import *
import sys
from PyQt5.QtWidgets import *  # QtWidgets에 있는 QApplication 클래스는 프로그램을 앱처럼 실행하거나 홈페이지처럼 실행할수 있도록 그래픽적인 요소를 제어하는 기능 포함      # 그 기능 중 동시성을 처리할 수 있게 해주는 함수도 포함

class Main():
  def __init__(self):
    print("Main() Start")

    self.app = QApplication(sys.argv) #PyQt5로 실행할 파일명을 자동 설정
    self.kiwoom = Kiwoom() # 키움 클래스 객체화
    self.app.exec_() # 이벤트 루프 실행

    Kiwoom()

if __name__ == "__main__":
  Main()    

