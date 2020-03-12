# -*- coding: utf-8 -*-
"""
Created on Sun May 29 19:58:04 2016

@author: ajit
"""

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from wx.lib.pubsub import pub
import os
import sys
import subprocess
import csv

import preprocessing

SELECTEDFILES = [
                u'ringtoneBR.apk', u'DefaultContainerService.apk',
                u'SecFactoryPhoneTest.apk', u'FmmDS.apk',
                u'SecContacts_ENTRY.apk', u'SecGallery_ESS.apk',
                u'FotaClient.apk', u'FmmDM.apk']


# adb shell pm list packages -f
# line is similar to package:/system/priv-
# app/GoogleBackupTransport/GoogleBackupTransport.apk
# =com.google.android.backuptransport

def get_apps():
    """ It gets all the installed apps details i.e. path """
    # check if device is connected and adb is running as root
    if subprocess.Popen(
                        ['adb', 'get-state'],
                        stdout=subprocess.PIPE). communicate(0)[0].split(
                                                        "\n")[0] == "unknown":
        print "no device connected - exiting..."
        sys.exit(2)

    # dumping the list of installed apps from the device
    print "Extracting apk name data ..."
    meta = subprocess.Popen(
                            ['adb', 'shell', 'pm', 'list', 'packages', '-f'],
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    meta.wait()
    apps = []
    while True:
        line = meta.stdout.readline()
        if line != '':
            name = line.split(':')[1].split('=')[0]
            if name.split('.')[-1] == 'apk':
                # tmp = name.split('/')
                # app = (tmp[-1],'xxK',tmp[1])
                app = [name]
            else:
                continue
        else:
            break
        apps.append(app)
    return apps


def dump_apps(apps):
    """ It pull the all apps from attached devices"""
    try:
        os.stat("pulled-apks")
    except OSError:
        os.mkdir("pulled-apks")

    # change working directory to back up dir given by user
    os.chdir("pulled-apks")

    # dumping the apps from the device print "Dumping the apps ..."

    for app in apps:
        subprocess.Popen(
                        ['adb', 'pull', app[0]], stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    print "All apk dumped."
    # os.chdir("..")


def get_apk_details():
    """ It will get apk details for now filesize """
    apk_details = list()
    apps = get_apps()
    dump_apps(apps)
    print os.getcwd()
    for app in apps:
        tmp = app[0].split('/')
        filename = tmp[-1]
        try:
            filesize = (os.path.getsize(filename)) / 1000.0
        except:
            filesize = 0.0
        # filesize = "%.1f" % filesize + 'kB'   #round(1.679,2) => 1.68
        filetype = tmp[1]
        apk_meta = (filename, str(round(filesize, 1))+'kB', filetype)
        print apk_meta
        apk_details.append(apk_meta)
    os.chdir('..')
    print os.getcwd()
    return apk_details
"""
PACKAGES = [
        ('ringtoneBR.apk', '3792', 'system'),
        ('DefaultContainerService.apk', '9234', 'system'),
        ('SecFactoryPhoneTest.apk', '47662', 'system'),
        ('FmmDS.apk', '110846', 'system'),
        ('PartnerBookmarksProvider.apk', '3423', 'data'),
        ('SecContacts_ENTRY.apk', '65536', 'system'),
        ('SecGallery_ESS.apk', '65536', 'system'),
        ('TeleService_ESS.apk', '65536', 'data'),
        ('FotaClient.apk', '65536', 'system'),
        ('FmmDM.apk', '65536', 'system')]
"""
SCANREPORT = list()

PACKAGES = get_apk_details()
# PACKAGES = preprocessing.assignClassLabel(SELECTEDFILES)

# ################################################


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    """     mulitplle inheritance to implement Check List """
    def __init__(self, parent):
        # wx.LC_REPORT :Single or multicolumn report view, with optional header
        #
        wx.ListCtrl.__init__(
                            self, parent, -1, style=wx.LC_REPORT |
                            wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

# ####################################################


class ScanResult(wx.Frame):
    """This frame will show the scan result for selected applications"""

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "FAMOUS: Scanning Result", size=(800, 600))

        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel, -1)
        rightPanel = wx.Panel(panel, -1)

        # Creating Header for multi-list right panel
        self.log = wx.TextCtrl(rightPanel, -1, style=wx.TE_MULTILINE)
        print "I am in SCANREPORT FRAME"
        #print SCANREPORT
        print self.ReadScanReport()

        self.CreateFillList(CheckListCtrl, rightPanel, self.ReadScanReport())

        vbox2 = wx.BoxSizer(wx.VERTICAL)

        # Define the property of button
        malware = wx.Button(leftPanel, -1, 'Select Suspicious', size=(120, -1))
        benign = wx.Button(leftPanel, -1, 'Select Benign', size=(120, -1))
        des = wx.Button(leftPanel, -1, 'Deselect', size=(120, -1))
        move = wx.Button(leftPanel, -1, 'Move', size=(120, -1))
        report = wx.Button(leftPanel, -1, 'Report', size=(120, -1))
        exit = wx.Button(leftPanel, -1, 'Exit', size=(120, -1))
        # Binding event to button

        self.Bind(wx.EVT_BUTTON, self.OnSelectMalware, id=malware.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSelectBenign, id=benign.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnMove, id=move.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=des.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnReport, id=report.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnExit, exit)

        # Add button to panel vertical box
        vbox2.Add(malware, 0, wx.TOP, 5)
        vbox2.Add(benign)
        vbox2.Add(des)
        vbox2.Add(move)
        vbox2.Add(report)
        vbox2.Add(exit)

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        vbox.Add(self.log, 0.5, wx.EXPAND)
        vbox.Add((-1, 10))

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))

        panel.SetSizer(hbox)

        self.Centre()
        self.Show(True)

    def CreateFillList(self, CheckListCtrl, rightPanel, SCANREPORT):
        # Inherited super List contorl
        self.list = CheckListCtrl(rightPanel)
        self.list.InsertColumn(0, "Application", width=250)
        self.list.InsertColumn(1, "Package", width=250)
        self.list.InsertColumn(2, "Version")
        self.list.InsertColumn(3, "Total Permissions")
        self.list.InsertColumn(4, "EMSP")
        self.list.InsertColumn(5, "Class")

        # Use of sys.maxint gives the row number after the last row
        # InsertStringItem() method which returns the index of the current row.

        # populating the list with data
        for row in SCANREPORT:
            index = self.list.InsertStringItem(sys.maxint, row[0])
            self.list.SetStringItem(index, 1, row[1])
            self.list.SetStringItem(index, 2, row[2])
            self.list.SetStringItem(index, 3, row[3])
            self.list.SetStringItem(index, 4, row[4])
            self.list.SetStringItem(index, 5, row[5])

            if row[5] == "Suspicious":
                self.list.SetItemBackgroundColour(index, "red")

# Defining method according to button funcationaliter
    def OnDeselectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)

    def OnMove(self, event):
        selectedfiles = list()
        filetype = ""
        num = self.list.GetItemCount()
        for i in range(num):
            if i == 0:
                self.log.Clear()
            if self.list.IsChecked(i):
                filetype = self.list.GetItem(itemId=i, col=5).GetText()
                selectedfiles.append(self.list.GetItemText(i))
        os.mkdir(filetype)
        for f in selectedfiles:
            os.rename(os.getcwd() + '/pulled-apks/' + f,
                      os.getcwd() + '/' + filetype + '/' + f)
        print "Moved all selected file to ", filetype

    def OnReport(self, event):
        pass

    def OnSelectMalware(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            # print self.list.GetItemText(i)
            # print self.list.GetItem(itemId=i, col=2).GetText()
            if self.list.GetItem(itemId=i, col=5).GetText() == 'Malware':
                self.list.CheckItem(i)

    def OnSelectBenign(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            # print self.list.GetItemText(i)
            # print self.list.GetItem(itemId=i, col=2).GetText()
            if self.list.GetItem(itemId=i, col=5).GetText() == 'Benign':
                self.list.CheckItem(i)

    def OnExit(self, event):
        """
        Send a message and close frame
        """
        # msg = self.msgTxt.GetValue()
        # pub.sendMessage("panelListener", message=msg)
        # pub.sendMessage("panelListener", message="test2", arg2="2nd argnt!")
        self.Close()
        # ----------------------------------

    def ReadScanReport(self):
        with open('scanresult.csv') as f:
            data = [tuple(line) for line in csv.reader(f)]
        return data

# ####################################################


class MainPanel(wx.Panel):
    """This frame will show the scan result for selected applications"""
    SUSPICIOIS = list()

    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        # panel = wx.Panel(self, -1)

        pub.subscribe(self.myListener, "panelListener")

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # leftPanel = wx.Panel(panel, -1)
        # rightPanel = wx.Panel(panel, -1)
        leftPanel = wx.Panel(self, -1)
        rightPanel = wx.Panel(self, -1)
        # Creating Header for multi-list right panel
        self.log = wx.TextCtrl(rightPanel, -1, style=wx.TE_MULTILINE)

        # Inherited super List contorl
        self.list = CheckListCtrl(rightPanel)
        self.list.InsertColumn(0, 'Package', width=250)
        self.list.InsertColumn(1, 'Size')
        self.list.InsertColumn(2, 'Type')

        # # Use of sys.maxint gives the row number after the last row
        # InsertStringItem() method which returns the index of the current row.

        # # populating the list with data

        for i in PACKAGES:
            index = self.list.InsertStringItem(sys.maxint, i[0])
            self.list.SetStringItem(index, 1, i[1])
            self.list.SetStringItem(index, 2, i[2])

        vbox2 = wx.BoxSizer(wx.VERTICAL)

        # Define the property of button
        sel = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
        system = wx.Button(leftPanel, -1, 'Select SYS', size=(100, -1))
        third = wx.Button(leftPanel, -1, 'Select 3rd', size=(100, -1))
        des = wx.Button(leftPanel, -1, 'Deselect', size=(100, -1))
        apply = wx.Button(leftPanel, -1, 'Apply', size=(100, -1))
        scan = wx.Button(leftPanel, -1, 'Scan', size=(100, -1))
        btn = wx.Button(leftPanel, -1, "Show", size=(100, -1))
        exit = wx.Button(leftPanel, -1, 'Exit', size=(100, -1))
        # Binding event to button
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=sel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSelectSystem, id=system.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSelectThird, id=third.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnScan, id=scan.GetId())
        self.Bind(wx.EVT_BUTTON, self.onOpenFrame, id=btn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=des.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=apply.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnExit, exit)

        # Add button to panel vertical box
        vbox2.Add(sel, 0, wx.TOP, 5)
        vbox2.Add(system)
        vbox2.Add(third)
        vbox2.Add(des)
        vbox2.Add(apply)
        vbox2.Add(scan)
        vbox2.Add(btn)
        vbox2.Add(exit)

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        vbox.Add(self.log, 0.5, wx.EXPAND)
        vbox.Add((-1, 10))

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))

        # Dialog box for taking input from user
        box = wx.TextEntryDialog(None, "Give the Case No:", "Case Num", "")
        if box.ShowModal() == wx.ID_OK:
            caseno = box.GetValue()
            print caseno
        # wx.StaticText(panel, -1, caseno,(10,10))
        # panel.SetSizer(hbox)
        self.SetSizer(hbox)
        self.Centre()
        self.Show(True)
# Defining method according to button funcationaliter
    # ----------------------------------------------------------------------

    def myListener(self, message, arg2=None):
        """
        Listener function
        """
        print "Received the following message: " + message
        if arg2:
            print "Received another arguments: " + str(arg2)

    # ----------------------------------------------------------------------
    def onOpenFrame(self, event):
        """
        Opens secondary frame
        """
        frame = ScanResult()
        frame.Show()
    # ---------------------------------------------------------

    def WriteReport(self, ListOfTuples):
        with open("scanresult.csv", "w") as the_file:
            csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
            writer = csv.writer(the_file, dialect="custom")
            for tup in ListOfTuples:
                writer.writerow(tup)
        print "Scan result written to file scanresult.csv"

    def OnSelectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i)

    def OnDeselectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)

    def OnApply(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            if i == 0:
                self.log.Clear()
            if self.list.IsChecked(i):
                self.log.AppendText(self.list.GetItemText(i) + '\n')

    def OnScan(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            if i == 0:
                self.log.Clear()
            if self.list.IsChecked(i):
                self.SUSPICIOIS.append(self.list.GetItemText(i))
        print self.SUSPICIOIS
        SCANREPORT = preprocessing.assignClassLabel(self.SUSPICIOIS)
        # print SCANREPORT
        self.WriteReport(SCANREPORT)

    def OnSelectSystem(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            # print self.list.GetItemText(i)
            # print self.list.GetItem(itemId=i, col=2).GetText()
            if self.list.GetItem(itemId=i, col=2).GetText() == 'system':
                self.list.CheckItem(i)

    def OnSelectThird(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            # print self.list.GetItemText(i)
            # print self.list.GetItem(itemId=i, col=2).GetText()
            if self.list.GetItem(itemId=i, col=2).GetText() != 'system':
                self.list.CheckItem(i)

    def OnExit(self, event):
        self.Close(True)

#  ----------------------------------------------------------------------


class FAMOUS(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="FAMOUS: Applications Listing", size=(600, 600))
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText('Total applications:' + str(len(PACKAGES)))
        panel = MainPanel(self)
        self.Show()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = FAMOUS()
    app.MainLoop()
