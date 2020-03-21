import sys
import os
import time

from cv2 import *
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from mainwindow import Ui_mainWindow
from software import Img_Print
from Terminal_window import terminalwindow
import glob


class DetectThread(QtCore.QThread):
    # 定义线程回传信号
    finishsignal = pyqtSignal(str)

    def __init__(self, MediaPlayerUI, parent=None):
        super(DetectThread, self).__init__()
        # 绑定界面
        self.mpUI = MediaPlayerUI

    def ThreadStart(self):
            self.start()

    def run(self):
        self.mpUI.startDetection()
        self.finishsignal.emit('检测完成')


class MediaPlayerUI(QMainWindow,Ui_mainWindow):

    def __init__(self):
        super(MediaPlayerUI, self).__init__()
        self.setupUi(self)
        self.player_ori = QMediaPlayer()
        self.player_res = QMediaPlayer()
        self.player_ori.setVideoOutput(self.widget_Original)
        self.player_res.setVideoOutput(self.widget_Result)
        self.terminalwindow = terminalwindow()

    def selectFile(self):#选取视频文件

        self.Input_path = QFileDialog.getExistingDirectory()

        filelist = glob.glob(os.path.join(self.Input_path, '*.jpg'))
        self.label_Input.setText("读取文件数量：" + str(len(filelist)))

        print(self.Input_path)

    def selectModel(self):#选取模型文件

        self.Model_path = QFileDialog.getOpenFileUrl()[0].path()
        self.Model_path = self.Model_path.strip('/')
        dirname,filename = os.path.split(self.Model_path)
        self.label_Model.setText("模型文件名：" + filename)
        print(self.Model_path)

    def VideoPlay_Ori(self):
        self.player_ori.play()

    def VideoPlay_Res(self):
        self.player_res.play()

    def VideoPause_Ori(self):
        self.player_ori.pause()

    def VideoPause_Res(self):
        self.player_res.pause()

    def picvideo(self, path, size):

        filelist = os.listdir(path)  # 获取该目录下的所有文件名
        filelist.sort();

        fps = 24
        size = (320,240) #图片的分辨率片
        Video_path = path + "/video" + str(int(time.time())) + ".avi"  # 导出路径
        fourcc = cv2.VideoWriter_fourcc('I','4','2','0')  # 不同视频编码对应不同视频格式（例：'I','4','2','0' 对应avi格式 'D', 'I', 'V', 'X'对应mp4）

        video = cv2.VideoWriter(Video_path, fourcc, fps, size)

        for item in filelist:
            if item.endswith('.jpg'):  # 判断图片后缀是否是.png
                item = path + '/' + item
                img = cv2.imread(item)  # 使用opencv读取图像，直接返回numpy.ndarray 对象，通道顺序为BGR ，注意是BGR，通道值默认范围0-255。
                video.write(img)  # 把图片写进视频

        video.release()  # 释放
        return Video_path

    def readyToDetect(self):# 初始化检测线程并运行

        self.thread = DetectThread(self)
        self.thread.finishsignal.connect(self.message)
        self.terminalwindow.windowOpen()
        try:
            self.thread.ThreadStart()
        except Exception as e:
            error_box = QMessageBox(QMessageBox.Warning, '错误', str(e))
            error_box.exec_()


    def message(self,msg):# 接收检测线程结束后的回传信号量并给出提示
        print('msg: {}'.format(msg))
        QMessageBox.information(mw, "视频检测已完成", "视频检测已完成")

    def startDetection(self):

        #封装原视频
        Ori_path = self.picvideo(self.Input_path, (320, 240))


        #读取视频帧数
        video_capture = cv2.VideoCapture(Ori_path)
        total = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.label_frames.setText("视频总帧数为：" + str(total))

        #原视频绑定播放器
        Ori_path = QUrl.fromLocalFile(Ori_path)
        mc = QMediaContent(QMediaContent(Ori_path))
        self.player_ori.setMedia(mc)
        print('原视频处理完成')
        print('即将开始检测...')

        #视频检测过程
        Predictor = Img_Print(self.Input_path, self.Model_path)
        Res_path = Predictor.start()

        #封装结果视频
        Res_path = self.picvideo(Res_path, (320, 240))

        #结果视频绑定播放器
        Res_path = QUrl.fromLocalFile(Res_path)
        mc = QMediaContent(QMediaContent(Res_path))
        self.player_res.setMedia(mc)
        print('前景目标视频处理完成')


if __name__ == '__main__':
    mapp = QApplication(sys.argv)
    mw = MediaPlayerUI()
    mw.show()
    sys.exit(mapp.exec_())