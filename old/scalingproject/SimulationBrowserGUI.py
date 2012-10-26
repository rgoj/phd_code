import numpy as npy
import matplotlib.cm as cm
ERR_TOL = 1e-5 # floating point slop for peak-detection

import wx
from wx import xrc

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import Toolbar
from topographicmap import plot_topographic_map, plot_topographic_map_array

class PlotPanel(wx.Panel):
    def __init__(self, parent, se):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.fig = Figure((5,4), dpi=100)
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()
        #self.toolbar.set_active([0,1])
        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

        self.se = se
        self.subject = -1


    def init_plot_data(self):
        self.plot_subject()


    def plot_subject(self):
        print('From plot_subject ' + str(self.subject))
        if self.subject >= 0:
            print('Hi from here')
            self.se.plot_topographies(
                          self.se.simulated_gen_1[0][self.subject,:], self.se.simulated_gen_2[0][self.subject,:], 
                          self.se.normal_noise_1[0][self.subject,:], self.se.normal_noise_2[0][self.subject,:], 
                          self.se.topographic_noise_1[0], self.se.topographic_noise_2[0], 
                          self.se.simulated_data_1[0][self.subject,:], self.se.simulated_data_2[0][self.subject,:],
                          fig=self.fig)
        else:
            print('Hi from there')
            self.se.plot_topographies(
                          self.se.simulated_gen_1[0], self.se.simulated_gen_2[0], 
                          self.se.normal_noise_1[0], self.se.normal_noise_2[0], 
                          self.se.topographic_noise_1[0], self.se.topographic_noise_2[0], 
                          self.se.simulated_data_1[0], self.se.simulated_data_2[0],
                          fig=self.fig)
        #self.toolbar.update()
        self.canvas.draw()


    def button_grand(self, control):
        print('Grand average my ass!')
        self.fig.clf()
        self.subject = -1
        self.plot_subject()
    

    def button_next(self, control):
        self.subject +=1
        print('Next pressed...' + str(self.subject))
        self.fig.clf()
        self.plot_subject()
        
 
 
    def button_prev(self, control):
        print('Wait a minute...')
    
    
    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    
    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass
    

class SimulationBrowserGUI(wx.App):
    def __init__(self, se):
        self.se = se
        wx.App.__init__(self, False)


    def OnInit(self):
        self.res = xrc.XmlResource("SimulationBrowserGUI.xrc")
        self.frame = self.res.LoadFrame(None, "MainFrame")
        
        fig_panel = xrc.XRCCTRL(self.frame,"fig_panel")
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.fig_panel = PlotPanel(fig_panel, self.se)
        self.fig_panel.init_plot_data()
        
        self.frame.Bind(wx.EVT_BUTTON, self.fig_panel.button_grand,
                        id=xrc.XRCID("button_grand"))
        self.frame.Bind(wx.EVT_BUTTON, self.fig_panel.button_next,
                        id=xrc.XRCID("button_next"))
        self.frame.Bind(wx.EVT_BUTTON, self.fig_panel.button_prev,
                        id=xrc.XRCID("button_prev"))
        
        sizer.Add(self.fig_panel, 1, wx.EXPAND)
        fig_panel.SetSizer(sizer)
        self.frame.Show()
        return True
