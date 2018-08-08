## 컨트롤러(제어기) 기능 구현

* 파이썬으로 작성하면 라즈베리 파이에서 동작할 때 큰 문제는 없을 것으로 판단한다.
* 라즈에서는 깃에서 소스를 업데이트하여 실행하면 될 듯하다.
  - 단 실행 직전에 가상환경 설정을 일치시킬 필요가 있다.


## 패키지 정보 확인

* 설치 패키지 정보 저장하기
    - pip freeze > requirements.txt
* 패키지 자동 설치하기
    - pip install -r requirements.txt


## 기능동작 정의

* 현재까지는 3개의 프로세스로 구현할 예정이며 이중에서 입출력을 담당하는 부분은 HW 가 준비되면 작업할 예정임.
  - HW 준비전까지는 임의의 데이터를 전달하는 방법으로 진행

1. 서버통신(메인) 프로세스
1. USB 카메라 프로세스
1. 입출력 제어 프로세스 _HW 준비전까지 가상의 정보를 전달_


## 참고사이트

* [파이썬 – 멀티프로세싱(Python – Multiprocessing) - AvILoS](http://avilos.codes/programming/python/python-multiprocessing/)
  - 클래스를 사용한 예제 확인 > _Process 에서 파생된 클래스를 사용할 경우 에러가 발생함._
  - 클래스를 이용한 방법은 사용하기 힘들다는 나름의 결론...ㅠ
* [multiprocessing | Pool, Process, Queue](https://m.blog.naver.com/townpharm/220951524843)
  - 프로세스 사용예
* [17.2. multiprocessing — Process-based parallelism](https://docs.python.org/3.7/library/multiprocessing.html)
  - 역시 가장 명확한 정보를 얻을 수 있는 곳...
* [Python: Queue.Empty Exception Handling](https://stackoverflow.com/questions/11247439/python-queue-empty-exception-handling)
  - 내용을 잘 모르겠으나 **METHOD2** 를 사용하라!!
