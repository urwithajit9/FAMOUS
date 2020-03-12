# FAMOUS
FAMOUS is a forensic analysis tool built to triage Android applications and to assist the analyst in the selection of applications for further in-depth or manual analysis. The motivation behind FAMOUS is to overcome the limitations of the signature-based triaging forensic tool. The main functions of FAMOUS is to assign a proper class label (among benign and malware/suspicious) to every selected Android application by underlying classification engine. Each classification engine is built by training and testing different machine learning algorithms on proposed permission’s score based feature set that is extracted from a large dataset. Currently, in the proof-of-concept implementation, it has only best-performing classifier but it can be easily extended with more classifiers. Screenshots of the main window and result window of FAMOUS are attached for Understanding..

![Main Window of FAMOUS](https://github.com/urwithajit9/FAMOUS/blob/master/FAMOUSMainWindow.png)
![Result](https://github.com/urwithajit9/FAMOUS/blob/master/FAMOUS-result-suspicious.png)
![Architecutre](https://github.com/urwithajit9/FAMOUS/blob/master/FAMOUS-Architecture.jpg)
