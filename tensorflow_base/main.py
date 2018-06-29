from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import sys
from shutil import copy
from PIL import Image
import numpy as np
from utilities import ImageUtilities as IU
from processing import SVMSorter, KNNSorter, EuclideanSorter


class ImageSorter(QWidget):

    def __init__(self, parent=None):
        super(ImageSorter, self).__init__(parent)
        self.setGeometry(700, 700, 300, 300)
        self.setWindowTitle('ImageSorter')
        self.box = QVBoxLayout()
        self.folder = None
        self.sort_path = None
        self.algorithm = 'Euclidean Distance'
        self.identifier = EuclideanSorter()
        self.model = 'models/predictor_euclidean_model.clf'
        self.textbox = None
        self.confidence_box = None
        self.threshold = 0.6
        self.detect_objects = False
        self.sort_state = True
        self.confidence = 0.4
        self.classes = list()

        self.label1 = QLabel()
        self.label2 = QLabel()
        self.status = QLabel()
        self.progress = QProgressBar()
        self.label3 = QLabel()
        self.button1 = QPushButton('Select folder containing images to sort')
        self.button2 = QPushButton('Where should the sorted images be stored?')
        self.button1.clicked.connect(self.get_folder_path)
        self.button2.clicked.connect(self.get_sorted_path)
        self.button3 = QPushButton('<< Advanced Options >>')
        self.button3.clicked.connect(self.advanced_options)
        self.button4 = QPushButton('Sort Images')
        self.button4.clicked.connect(self.sort_images)
        self.label3.setText('Select algorithm to use')
        self.algorithm_options = QComboBox()
        self.algorithm_options.addItems(['Euclidean Distance',
                                         'k-Nearest Neighbors',
                                         'Support Vector Machine(SVM)'])
        self.algorithm_options.currentIndexChanged.connect(self.set_algo)

        self.box.addWidget(self.button1)
        self.box.addWidget(self.label1)
        self.box.addWidget(self.button2)
        self.box.addWidget(self.label2)
        self.box.addWidget(self.label3)
        self.box.addWidget(self.algorithm_options)
        self.box.addWidget(self.button3)
        self.box.addWidget(self.button4)
        self.box.addWidget(self.progress)
        self.box.addWidget(self.status)

        self.setLayout(self.box)

    def generate_training_set(self):
        utils = IU()
        utils.generate_training_set()

    def get_folder_path(self):
        folder_path = QFileDialog()
        folder_path.setFileMode(QFileDialog.Directory)
        folder = None
        if folder_path.exec_():
            folder = folder_path.selectedFiles()
        if folder:
            self.folder = folder[0]
            self.label1.setText(self.folder)

    def get_sorted_path(self):
        sort_path = QFileDialog()
        sort_path.setFileMode(QFileDialog.Directory)
        sort = None
        if sort_path.exec_():
            sort = sort_path.selectedFiles()
        if sort:
            self.sort_path = sort[0]
            self.label2.setText(self.sort_path)

    def set_algo(self, i):
        self.algorithm = self.algorithm_options.currentText()
        if self.algorithm == 'Euclidean Distance':
            self.identifier = EuclideanSorter()
            self.model = 'models/predictor_euclidean_model.clf'
            self.threshold = 0.6
        elif self.algorithm == 'k-Nearest Neighbors':
            self.identifier = KNNSorter()
            self.model = 'models/predictor_knn_model.clf'
            self.threshold = 0.6
        elif self.algorithm == 'Support Vector Machine(SVM)':
            self.identifier = SVMSorter()
            self.model = 'models/predictor_svm_model.clf'
            self.threshold = 0.005

    def train_classifier(self):
        if os.path.isfile('models/training_data.clf'):
            self.status.setText('Training classifier...')
            self.identifier.train()
            self.status.setText('Model trained!')
        else:
            error = QErrorMessage()
            error.showMessage('You need to generate training data first!')
            error.exec_()

    def set_options(self):
        self.threshold = float(self.textbox.text())
        self.confidence = float(self.confidence_box.text())

    def detecting_objects(self, state, idx=15):
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
        if state == Qt.Checked:
            self.detect_objects = True
            self.classes.append(CLASSES[idx])
        else:
            try:
                self.classes.remove(CLASSES[idx])
            except:
                pass
            if len(self.classes) == 0:
                self.detect_objects = False

    def advanced_options(self):
        settings = QDialog()
        settings.setGeometry(600, 600, 300, 300)
        self.textbox = QLineEdit()
        self.confidence_box = QLineEdit()
        conf_label = QLabel()
        label = QLabel()
        valid = QDoubleValidator()
        conf_val = QDoubleValidator()
        conf_val.setRange(0.001, 1.00, 3)
        self.confidence_box.setValidator(conf_val)
        self.confidence_box.setText('0.4')
        conf_label.setText('Enter the confidence level of object detection')
        filter_label = QLabel()
        filter_label.setText('Select the objects that will be used to filter images')
        checker1 = QCheckBox('People')
        checker1.stateChanged.connect(lambda *f: self.detecting_objects(idx=15,
                                                                        state=checker1.checkState()))
        if 'person' in self.classes:checker1.toggle()
        checker2 = QCheckBox('Dogs')
        checker2.stateChanged.connect(lambda *f: self.detecting_objects(idx=12,
                                                                        state=checker2.checkState()))
        if 'dog' in self.classes:checker2.toggle()
        checker3 = QCheckBox('Cats')
        checker3.stateChanged.connect(lambda *f: self.detecting_objects(idx=8,
                                                                        state=checker3.checkState()))
        if 'cat' in self.classes:checker3.toggle()
        checker4 = QCheckBox('Cars')
        checker4.stateChanged.connect(lambda *f: self.detecting_objects(idx=7,
                                                                        state=checker4.checkState()))
        if 'car' in self.classes:checker4.toggle()
        checker5 = QCheckBox('Bicycles')
        checker5.stateChanged.connect(lambda *f: self.detecting_objects(idx=2,
                                                                        state=checker5.checkState()))
        if 'bicycle' in self.classes:checker5.toggle()
        checker6 = QCheckBox('Bottles')
        checker6.stateChanged.connect(lambda *f: self.detecting_objects(idx=5,
                                                                        state=checker6.checkState()))
        if 'bottle' in self.classes:checker6.toggle()
        checker7 = QCheckBox('Motorbikes')
        checker7.stateChanged.connect(lambda *f: self.detecting_objects(idx=14,
                                                                        state=checker7.checkState()))
        if 'motorbike' in self.classes:checker7.toggle()
        filter_check = QCheckBox('Filter images without sorting using face recognition')
        filter_check.stateChanged.connect(self.set_sort_state)
        if self.algorithm == 'Euclidean Distance':
            valid.setRange(0.005, 1.00, 3)
            self.textbox.setValidator(valid)
            label.setText('Enter an error threshold')
        elif self.algorithm == 'k-Nearest Neighbors':
            valid.setRange(0.005, 1.00, 3)
            self.textbox.setValidator(valid)
            label.setText('Enter an error threshold')
        elif self.algorithm == 'Support Vector Machine(SVM)':
            valid.setRange(0.00005, 0.0100, 5)
            self.textbox.setValidator(valid)
            label.setText('Enter a distance threshold')
        self.textbox.setText(str(self.threshold))
        button1 = QPushButton('Generate training data')
        button2 = QPushButton('Train classifier')
        button3 = QPushButton('Set threshold and confidence')
        button1.clicked.connect(self.generate_training_set)
        button2.clicked.connect(self.train_classifier)
        button3.clicked.connect(self.set_options)
        dialog = QVBoxLayout()
        dialog.addWidget(filter_label)
        dialog.addWidget(checker1)
        dialog.addWidget(checker2)
        dialog.addWidget(checker3)
        dialog.addWidget(checker4)
        dialog.addWidget(checker5)
        dialog.addWidget(checker6)
        dialog.addWidget(checker7)
        dialog.addWidget(conf_label)
        dialog.addWidget(self.confidence_box)
        dialog.addWidget(label)
        dialog.addWidget(self.textbox)
        dialog.addWidget(button3)
        dialog.addWidget(filter_check)
        dialog.addWidget(button1)
        dialog.addWidget(button2)
        settings.setWindowTitle('Advanced Options')
        settings.setLayout(dialog)
        settings.setWindowModality(Qt.ApplicationModal)
        settings.exec_()

    def set_sort_state(self, state):
        if state == Qt.Checked:
            self.sort_state = False
        else:
            self.sort_state = True

    def sort_images(self):
        if self.folder is None or self.sort_path is None:
            error = QErrorMessage()
            error.showMessage('One or more paths have not been set')
            error.exec_()
        elif self.textbox.text() == "" or self.confidence_box.text() == "":
            error = QErrorMessage()
            error.showMessage('Threshold / distance /confidence value is not set')
            error.exec_()
        elif os.path.isfile(self.model):
            self.progress.setValue(0)
            self.identifier.set_folder(self.folder)
            image_list = self.identifier.get_image_list()
            image_list.sort()
            results = list()
            if self.detect_objects is True:
                self.status.setText('Filtering images...')
                utils = IU()
                image_list = utils.detect_objects(image_list,
                                                  bar=self.progress,
                                                  classes=self.classes,
                                                  conf=self.confidence)
            if self.sort_state is True:
                increment = float(100.00/float(len(image_list)))
                self.progress.setValue(0)
                done = 0
                self.status.setText('Sorting images...')
                for image in image_list:
                    result = self.identifier.predict(image_path = image,
                                                     threshold = self.threshold)
                    if self.algorithm == 'Euclidean Distance':
                        if result is True:
                            results.append(image)
                    elif self.algorithm == 'k-Nearest Neighbors':
                        for name, loc in result:
                            if name.lower() == 'search_face':
                                results.append(image)
                                break
                    elif self.algorithm == 'Support Vector Machine(SVM)':
                        if result is True:
                            results.append(image)
                    done += increment
                    self.progress.setValue(done)
                self.progress.setValue(100)
            else:
                results = image_list
            if not os.path.exists(self.sort_path):
                os.makedirs(self.sort_path)
            self.progress.setValue(0); done = 0;
            self.status.setText('Copying results to folder...')
            increment = float(len(results) / 100.0)
            for image in results:
                copy(image, self.sort_path)
                done += increment
                self.progress.setValue(done)
            self.progress.setValue(100)
            self.status.setText('Done!')
        else:
            error = QErrorMessage()
            error.showMessage("There was an error. That's all we know.")
            error.exec_()


def main():
    app = QApplication(sys.argv)
    UI = ImageSorter()
    UI.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
        
        


