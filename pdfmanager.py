import sys ,os, io
if hasattr(sys,'frozen'):
    os.environ['PATH']=sys._MEIPASS + ';' + os.environ['PATH']

from PyQt5.QtWidgets import QApplication, QWidget,QLabel, QLineEdit,QPushButton,QListWidget, \
QVBoxLayout,QHBoxLayout,QGridLayout, \
QDialog, QFileDialog,QMessageBox,QAbstractItemView

from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon 
from PyPDF2 import PdfMerger

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setAcceptDrops(True)
        self.setStyleSheet('font-size: 30px;')
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection) 
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            return super().dragEnterEvent(event)
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            pdfFiles=[]

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if url.toString().endswith('.pdf'):
                        pdfFiles.append(url.toLocalFile())
            self.addItems(pdfFiles)
        else:
            return super().dropEvent(event)
    
    def dragMoveEvent(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            return super().dragMoveEvent(event)

class  output_field(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet('font-size: 30px;')
        self.height=55
        self.setFixedHeight(self.height)

    def  dragEnterEvent(self,event):
        if  event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    def dragMoveEvent(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            if event.mimeData().urls():
                self.setText(event.mimeData().urls()[0].toLocalFile())

        else:
            event.ignore()
class button(QPushButton):
    def __init__(self,label_text):
        super().__init__()
        self.setText(label_text)
        self.setStyleSheet('''font-size: 30px;
        width: 180px;
        height:30px''')
class pdfManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.resize(1200,600)
        self.initUI()

    def initUI(self):
        mainLayout=QVBoxLayout()
        outputFolderRow=QHBoxLayout()
        buttonLayout=QHBoxLayout()
        self.outputFile=output_field()
        outputFolderRow.addWidget(self.outputFile)
        self.buttonBrowseOutputFile=button('&save to ')
        self.buttonBrowseOutputFile.clicked.connect(self.populateFileName)
        outputFolderRow.addWidget(self.buttonBrowseOutputFile)
        #listbox 
        self.pdfListWidget=ListWidget(self)
        #buttons
        self.buttonDeleteSelect=button('&Delete')
        buttonLayout.addWidget(self.buttonDeleteSelect,1,Qt.AlignRight)
        self.buttonDeleteSelect.clicked.connect(self.deleteSelected)
        self.buttonMerge=button('&merge')
        buttonLayout.addWidget(self.buttonMerge)
        self.buttonMerge.clicked.connect(self.mergeFile)
        self.buttonClose=button('&close')
        self.buttonClose.clicked.connect(QApplication.quit)
        buttonLayout.addWidget(self.buttonClose)
        self.buttonReset=button('&reset')
        self.buttonReset.clicked.connect(self.clearQueue)
        buttonLayout.addWidget(self.buttonReset)
        ## adding layout to app
        mainLayout.addLayout(outputFolderRow)
        mainLayout.addWidget(self.pdfListWidget)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
    
    def deleteSelected(self):
        for item in self.pdfListWidget.selectedItems():
            self.pdfListWidget.takeItem(self.pdfListWidget.row(item))
    def clearQueue(self):
        self.pdfListWidget.clear()
        self.outputFile.setText('')
    
    def dialogMessage(self,message):
        dig=QMessageBox.information(self,"PDF Merger",message)
        dig.setIcon(QMessageBox.Information)
        dig.setText(message)
        dig.show()
    
    def _getSaveFilePath(self):
        file_save_path,_ =QFileDialog.getSaveFileName(self,'Save PDF File',os.getcwd(),'PDF file (*.pdf)')
        return file_save_path
    def populateFileName(self):
        path=self._getSaveFilePath()
        if path:
            self.outputFile.setText(path)
    def mergeFile(self):
        if not self.outputFile.text():
            self.populateFileName()
            return
        if self.pdfListWidget.count()>0:
            pdfMerger=PdfMerger()

            try:
                for i in range(self.pdfListWidget.count()):
                    pdfMerger.append(self.pdfListWidget.item(i).text())
                pdfMerger.write(self.outputFile.text())
                self.dialogMessage("PDF merged successfully!")
                #self.clearQueue()
            except Exception as e:
                self.dialogMessage(str(e))
        else:
            self.dialogMessage("No PDF files to merge!")      
app=QApplication(sys.argv)
app.setStyle('fusion')
pdfApp=pdfManager()
pdfApp.show()

sys.exit(app.exec_())