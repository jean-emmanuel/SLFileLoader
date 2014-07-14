#!/usr/bin/env python
#encoding: utf-8
"""
SooperLooper File Loader
Usage : python slfileloader.py

sl_host : ip of the SooperLooper engine host
sl_port : control port of SooperLooper

return_host, return_port : ip and control port for SooperLooper error handling

directories : absolute paths to the folders containing the audio files (.wav or .aif) to load.
              Must be an array of strings, one path per loop. Last '/' in path is optionnal.
"""


############################


sl_host = '127.0.0.1'
sl_port = 9951

return_host = '127.0.0.1'
return_port = 18726

directories = [
    '/home/bordun/Bureau/', # Loop 1 audio files
    '/home/bordun/Bureau/', # Loop 2 audio files
    '/home/bordun/Bureau'   # Loop 3 audio files
]


############################

import wx, os
import liblo as osc
from math import log10, log

# N of loops
n_loop = len(directories)

# List of files for each loop
files = [[f for f in os.listdir(directories[i]) if f[-4:] in ['.wav', '.aif']] for i in range(n_loop)]

# Sorts files by name and adds last '/' in paths if missing 
for i in range(n_loop):
    if directories[i][-1] != '/':
        directories[i] = directories[i]+'/'
    files[i].sort()

class Gui(wx.Frame):
    def __init__(self, parent=None, title='SL File Loader', pos=(100,100), size=(444,2+82*n_loop)):
        wx.Frame.__init__(self, parent, id=-1, title=title, pos=pos, size=size)
        self.loop_durations, self.loops, self.labels, self.selectors, self.prev_buttons, self.next_buttons, self.load_buttons, self.gauges, self.trig_buttons, self.once_buttons, self.mute_buttons, self.pause_buttons, self.volume_sliders, self.volume_labels = range(n_loop), [], [], [], [], [], [], [], [], [], [], [], [], []
        
        for i in range(n_loop):
            
            self.loops.append(wx.Panel(self, id=i, pos=(2, 2+i*82), size=(440,80)))
            
            self.labels.append(wx.Button(self.loops[i], id=-1, pos=(0,0), label='Loop '+str(i+1), size=(60,40)))

            self.selectors.append(wx.Choice(self.loops[i], id=-1, pos=(60,0), size=(240,40), choices=files[i]))
            
            self.prev_buttons.append(wx.Button(self.loops[i], id=-1, pos=(300,0), label='❮', size=(40,40)))
            self.prev_buttons[i].Bind(wx.EVT_BUTTON, self.prev)
            
            self.next_buttons.append(wx.Button(self.loops[i], id=-1, pos=(340,0), label='❯', size=(40,40)))
            self.next_buttons[i].Bind(wx.EVT_BUTTON, self.next)
            
            self.load_buttons.append(wx.Button(self.loops[i], id=-1, pos=(380,0), label='Load', size=(60,40)))
            self.load_buttons[i].Bind(wx.EVT_BUTTON, self.load)
            
            self.gauges.append(wx.Gauge(self.loops[i], id=-1, range=100, pos=(0,40), size=(60,40), style=wx.GA_HORIZONTAL))

            self.trig_buttons.append(wx.Button(self.loops[i], id=-1, pos=(60,40), label='Trig', size=(60,40)))
            self.trig_buttons[i].Bind(wx.EVT_BUTTON, self.trig)
            
            self.once_buttons.append(wx.Button(self.loops[i], id=-1, pos=(120,40), label='Once', size=(60,40)))
            self.once_buttons[i].Bind(wx.EVT_BUTTON, self.once)
            
            self.mute_buttons.append(wx.ToggleButton(self.loops[i], id=-1, pos=(180,40), label='Mute', size=(60,40)))
            self.mute_buttons[i].Bind(wx.EVT_TOGGLEBUTTON, self.mute)
            
            self.pause_buttons.append(wx.ToggleButton(self.loops[i], id=-1, pos=(240,40), label='Pause', size=(60,40)))
            self.pause_buttons[i].Bind(wx.EVT_TOGGLEBUTTON, self.pause)
            
            self.volume_sliders.append(wx.Slider(self.loops[i], id=-1, value=100, minValue=0, maxValue=100, pos=(300,40), size=(140,20)))
            self.volume_sliders[i].Bind(wx.EVT_SLIDER, self.volume)
            self.volume_labels.append(wx.StaticText(self.loops[i], id=-1, label="0.0 dB", pos=(303,61), size=(140,20)))
            
    def start_osc(self):        
        self.server = osc.ServerThread(return_port)
        self.server.register_methods(self)
        self.server.start()
        
        for i in range(n_loop):
            # Loop position watcher
            osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/get','loop_len',return_host+':'+str(return_port),'/loop_len/'+str(i+1))
            osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/register_auto_update','loop_pos',200,return_host+':'+str(return_port),'/loop_pos/'+str(i+1))
            osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/register_auto_update','loop_len',500,return_host+':'+str(return_port),'/loop_len/'+str(i+1))
            
            # Loop state watcher (pause/mute)
            osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/get','state',return_host+':'+str(return_port),'/state/'+str(i+1))
            osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/register_auto_update','state',200,return_host+':'+str(return_port),'/state/'+str(i+1))
            
            osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/register_auto_update','wet',200,return_host+':'+str(return_port),'/volume/'+str(i+1))
           
    def getLoop(self,e):
        return e.GetEventObject().GetParent().GetId()
            
    def prev(self,e):
        i = self.getLoop(e)
        s = self.selectors[i].GetSelection()
        if (s-1) in range(len(files[i])):
            self.selectors[i].SetSelection(s-1)
            
    def next(self,e):
        i = self.getLoop(e)
        s = self.selectors[i].GetSelection()
        if (s+1) in range(len(files[i])):
            self.selectors[i].SetSelection(s+1)
            
    def load(self,e):
        i = self.getLoop(e)
        file_path = directories[i]+files[i][self.selectors[i].GetSelection()]
        osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/load_loop',file_path,return_host+':'+str(return_port),'/load_error/'+str(i+1))

    def trig(self,e):
        i = self.getLoop(e)
        osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/hit','trigger')

    def once(self,e):
        i = self.getLoop(e)
        osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/hit','oneshot')

    def mute(self,e):
        v = e.GetInt()
        i = self.getLoop(e)
        self.mute_buttons[i].SetValue(abs(v-1))
        osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/hit','mute')
    
    def pause(self,e):
        v = e.GetInt()
        i = self.getLoop(e)
        self.pause_buttons[i].SetValue(abs(v-1))
        osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/hit','pause')
    
    def volume(self,e):
        v = (e.GetInt() / 100.0)**2.71
        i = self.getLoop(e)
        osc.send('osc.udp://'+sl_host+':'+str(sl_port),'/sl/'+str(i)+'/set','wet',v)

    
    @osc.make_method(None, 'ss')
    def error(self,path,args):
        if 'load_error' in path:
            print 'Loop ' + path.split('/')[-1] + ' : ' + args[1]

    @osc.make_method(None, None)
    def osc_callback(self,path,args):
        if 'loop_pos' in path:
            if self.loop_durations[args[0]] != 0:
                v = args[2]/self.loop_durations[args[0]]*1.0
                wx.CallAfter(self.setGauge, v, args[0])
        elif 'loop_len' in path:
            self.loop_durations[args[0]]=args[2]
        elif 'state' in path:
            if args[2] in [10,20]:
                # Muted, unpaused 
                self.mute_buttons[args[0]].SetValue(1)
                self.pause_buttons[args[0]].SetValue(0)
            elif args[2] in [4,12]:
                # Playing, unpaused, unmuted
                self.mute_buttons[args[0]].SetValue(0)
                self.pause_buttons[args[0]].SetValue(0)
            elif args[2] == 14:
                # Paused, unmuted
                self.pause_buttons[args[0]].SetValue(1)
                self.mute_buttons[args[0]].SetValue(0)
        elif 'volume' in path:
            wx.CallAfter(self.setVolume, args[2], args[0])
    def setGauge(self,value,loop):
        self.gauges[loop].SetValue(round(value*100))
    def setVolume(self,value,loop):
        s = round(100*(value**(1/2.71)))
        self.volume_sliders[loop].SetValue(s)
        if value != 0:
            db = 20*log10(value)
            self.volume_labels[loop].SetLabel("%.1f dB" %db)
        else:
            self.volume_labels[loop].SetLabel("-inf dB")

############################

app = wx.App()
mainFrame = Gui()
mainFrame.Show()
mainFrame.start_osc()

app.MainLoop()
