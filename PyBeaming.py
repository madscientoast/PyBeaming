# PyBeaming Prototype #
# Programmed by: Robert Snuggs #

import sys
import math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from Calculations import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# This class essentially makes matplotlib usable as a Qt Widget #
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

# This is the core program, results initializes from within this routine #
class PyBeaming(QWidget):					#Start from initial dialog to input initial conditions
   def __init__(self, parent = None):       
      super(PyBeaming, self).__init__(parent)
      
      #Initial Parameters - can be changed live#
      layout = QVBoxLayout()
      self.l1 = QLabel("Set Initial Conditions")
      self.l1.setAlignment(Qt.AlignCenter)
      self.l2 = QLabel("Species")
      self.l2.setAlignment(Qt.AlignCenter)
      self.l3 = QLabel("Z number")
      self.l3.setAlignment(Qt.AlignCenter)
      self.l4 = QLabel("mass number")
      self.l4.setAlignment(Qt.AlignCenter)
      self.l5 = QLabel("foil thickness")
      self.l5.setAlignment(Qt.AlignCenter)
      self.l6 = QLabel("Voltage")
      self.l6.setAlignment(Qt.AlignCenter)
      layout.addWidget(self.l1)
	  
	  #5 Initial variables - Create and Set Them at runtime#
      self.spName_in = QLineEdit() # Species Name - String
      self.spZ_in = QSpinBox() #Z number - integer
      self.spM_in = QDoubleSpinBox() # Mass Number - float
      self.Target_in = QDoubleSpinBox() #Target Thickness - float
      self.Voltage_in = QDoubleSpinBox() # Voltage - float
      
      #Need to set maximums for float boxes due to them capping at 99 otherwise#
      self.spM_in.setMaximum(300)
      self.Voltage_in.setMaximum(300)
      self.Target_in.setValue(2.3)
      
      self.button = QPushButton("Confirm")
      self.button.clicked.connect(self.onConfirm)

      #This just adds the widgets to the dialog - just Qt stuff#
      layout.addWidget(self.l2)
      layout.addWidget(self.spName_in)
      layout.addWidget(self.l3)
      layout.addWidget(self.spZ_in)
      layout.addWidget(self.l4)
      layout.addWidget(self.spM_in)
      layout.addWidget(self.l5)
      layout.addWidget(self.Target_in)
      layout.addWidget(self.l6)
      layout.addWidget(self.Voltage_in)
      layout.addWidget(self.button)

      self.setLayout(layout)
      self.setWindowTitle("PyBeaming")
      
      # HERE we initialize the second window (so we can send info from dialog to results window)
      self.program = PyBeaming2()
      
   # This was required so that closing the dialogue shuts the whole program down #   
   def closeEvent(self, event):
        qApp.quit()
        sys.exit() # I found I needed this as a backup measure to ensure that the program stops executing the moment you close it. No leaks here.
   
   #This is where everything happens. Once you click confirm all the calculations run/refresh#
   def onConfirm(self):
        self.name = self.spName_in.text() 
        self.Z = self.spZ_in.value() 
        self.m = self.spM_in.value()
        self.target = self.Target_in.value()
        self.voltage = self.Voltage_in.value()

        E_I = self.voltage
        Z_I = self.Z
        M_I = self.m
        t = self.target
        
        # Calculations running #
        v_i = 0.4396 * math.sqrt(E_I/M_I) #Pre-Foil Velocity#
        E_f, E_loss_e, E_loss_n, ELNF, ELNA = Lindhard(a_0, Z_I, Z_T, M_I, M_T, t, E_I)
        v_f = 0.4396 * math.sqrt(E_f/M_I) #post-foil velocity # 
        theta_half, qb = gbar(v_i, v_f, Z_I, M_T, t, E_f)
        flife = foil_life(E_I, Z_I, M_I)
        
        ########################################################
        #                 charge distribution                  #
        ########################################################
        self.num =[] # here are the lists we use to create the charge distribution plot #
        self.count=[]
        k=0.6
        dum = 1.0 - ((qb/Z_I)**(1.0/k)) #dummy variable
        width = 0.5 * math.sqrt(qb*dum)
        for i in range(Z_I):
            q = i
            
            self.num.append(q)
            fq = math.exp(-((q-qb)**2)/(2.0*(width**2)))/math.sqrt(2.0*math.pi*(width**2))
            if fq > 0.01: #this runs so that we don't concern ourselves with the tiniest parts of the distribution
                self.count.append(fq)
        
        del self.num[len(self.count):] # this ensures our lists are compatible
        
        # Now to clear plot and create new plot
        self.program.sc.axes.cla()
        self.program.sc.axes.plot(self.num,self.count, 'r')
        self.program.sc.axes.set_title("Charge Distribution")
        self.program.sc.draw()
        
        #These are the strings we'll send to be displayed in the results window#
        v_i = "Pre-Foil Velocity: " + str(v_i) + " (mm/ns)"
        v_f = "Post-foil Velocity: " + str(v_f) + " (mm/ns)"
        E_f = "Post-foil Energy: " + str(E_f)
        E_loss_e = "Energy Loss - electronic: " + str(E_loss_e)
        E_loss_n = "Energy Loss - nuclear: " + str(E_loss_n)
        ELNF = "Garnir Nuclear Forward: " + str(ELNF)
        ELNA = "Garnir Nuclear All Angles: " + str(ELNA)
        theta_half = "Angle of half-beam intensity: " + str(theta_half) + "\u00B0"
        qb = "Average Charge: " + str(qb)
        self.program.label1.setText(v_i)
        self.program.label2.setText(v_f)
        self.program.label3.setText(E_f)
        self.program.label4.setText(E_loss_e)
        self.program.label5.setText(E_loss_n)
        self.program.label6.setText(ELNF)
        self.program.label7.setText(ELNA)
        self.program.label8.setText(theta_half)
        self.program.label9.setText(qb)
        self.program.show()

#This is the results window - this just updates after all the actual work is done by the core program#
class PyBeaming2(QWidget):					#Start from initial dialog to input initial conditions
   def __init__(self, parent = None):       
      super(PyBeaming2, self).__init__(parent)
      self.setGeometry(900, 200, 400, 800)
      self.setStyleSheet("QLabel{font-size: 18pt;}") # This guy makes everything actually legible.
      groupbox = QGroupBox("Lindhard/Garnir")
      groupbox2 = QGroupBox("gbar")
      
      #Initialize Labels
      self.label1 = QLabel("Pre-Foil Velocity: ")
      self.label2 = QLabel("Post-foil Velocity: ")
      self.label3 = QLabel("Post-foil Energy: ")
      self.label4 = QLabel("Energy Loss - electronic: ")
      self.label5 = QLabel("Energy Loss - nuclear:")
      self.label6 = QLabel("Garnir Nuclear Forward: ")
      self.label7 = QLabel("Garnir Nuclear All Angles: ")
      self.label8 = QLabel("Angle of half-beam intensity: ")
      self.label9 = QLabel("Average Charge: ")
      
      #Initialize Plot
      self.sc = MplCanvas(self, width=5, height=6, dpi=100)
      self.sc.axes.set_title("Charge Distribution")
      
      #Here we have a stretch of code for a button that shows our references
      def ref_clicked():
            self.refs = References()
            self.refs.show()
      ref_button = QPushButton()
      ref_button.setText("References")
      ref_button.clicked.connect(ref_clicked)
      
      #The rest is just Qt stuff#
      layout = QVBoxLayout()
      group_layout = QVBoxLayout()
      group_layout2 = QVBoxLayout()
      groupbox.setLayout(group_layout)
      groupbox2.setLayout(group_layout2)
      layout.addWidget(groupbox)
      layout.addWidget(groupbox2)
      layout.addWidget(self.sc)
      layout.addWidget(ref_button)
      group_layout.addWidget(self.label1)
      group_layout.addWidget(self.label2)
      group_layout.addWidget(self.label3)
      group_layout.addWidget(self.label4)
      group_layout.addWidget(self.label5)
      group_layout.addWidget(self.label6)
      group_layout.addWidget(self.label7)
      group_layout2.addWidget(self.label8)
      group_layout2.addWidget(self.label9)
      self.setLayout(layout)
      self.setWindowTitle("PyBeaming")
      
      
#This is just the Qt object code for the references window
class References(QWidget):					#Start from initial dialog to input initial conditions
   def __init__(self, parent = None):       
      super(References, self).__init__(parent)
      self.setStyleSheet("QLabel{font-size: 14pt;}")
      groupbox = QGroupBox("References")
      self.label1 = QLabel("#1. J.Lindhard, m. Scharff, & H.E.Schiott,\nKgl. Danske Videnskab. Selskab.,\nMat-Fys. Medd. _33_, #14 (1963)")
      self.label2 = QLabel("#2. F.S.Garnir-Gonjoie & H.P.Garnir,\nJ. Physique _41_, 31-33 (1980)")
      self.label3 = QLabel("#3. Nikolaev & Dmitriev\nPhys. Letters _28a_, 277-278 (1968)")
      self.label4 = QLabel("#4. Hogberg, Norden, & Barry\nNucl.Instr.Meth. _90_ 283-288 (1970)")
      self.label5 = QLabel("#5. R.L.Auble & D.M.Galbraith,\nNucl.Instr.Meth. _200_, 13-14 (1982)")
      
      layout = QVBoxLayout()
      group_layout = QVBoxLayout()
      groupbox.setLayout(group_layout)
      layout.addWidget(groupbox)
      group_layout.addWidget(self.label1)
      group_layout.addWidget(self.label2)
      group_layout.addWidget(self.label3)
      group_layout.addWidget(self.label4)
      group_layout.addWidget(self.label5)
      self.setLayout(layout)
      self.setWindowTitle("PyBeaming")


#Here is where the program EXECUTES
def main():
   app = QApplication(sys.argv)
   ex = PyBeaming()
   ex.show()
   
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()