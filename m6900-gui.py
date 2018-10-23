#!/usr/bin/python3
import argparse
import usb.core
import usb.util
import gi
import usb.control
from gi.repository import Gtk

mouse = usb.core.find(idVendor=0xe0ff, idProduct=0x0005)
	
preset = 0
dpi = 1

def set_dpi(preset, dpi, dev):
	
	if dev is None:
		raise ValueError('Device not found')
	else:
		print ('Device has been found')
	
	hadDriver0 = False
	hadDriver1 = False
	#detatch both mouse interfaces from any kernel drivers (HID driver in particular)
	if dev.is_kernel_driver_active(0):
		dev.detach_kernel_driver(0)
		hadDriver0 = True
	else:
		hadDriver0 = True
	
	if dev.is_kernel_driver_active(1):
		dev.detach_kernel_driver(1)
		hadDriver1 = True
	else:
		hadDriver1 = True
	
	
	# set the active configuration. With no arguments, the first configuration will be the active one.
	dev.set_configuration()
	
	usb.util.claim_interface(dev,0)
	def release(self):
	  usb.util.release_interface(self._dev, 0)
		
	
	# get an endpoint instance
	cfg = dev.get_active_configuration()
	intf = cfg[(0,0)]
	
	ep = usb.util.find_descriptor(
				intf,
	# match the first OUT endpoint
				custom_match = \
				lambda e: \
				usb.util.endpoint_direction(e.bEndpointAddress) == \
				usb.util.ENDPOINT_OUT)
	
	presetStart = [0x19]
	presetEnd = [0x00,0x00,0xe8,0x6c,0x00,0x01]
	hexValues = {0:[0x00], 1:[0x01], 2:[0x02], 3:[0x03], 4:[0x04], 5:[0x05], 6:[0x06]}
	dpiStart = [0x18]
	dpiEnd = [0x01,0x01,0x01,0x01,0x48]
	
	
	if preset > -1 and preset < 3:
		presetData = presetStart + hexValues[preset] + presetEnd
		#Change the DPI preset. the second byte is the preset
		dev.ctrl_transfer(bmRequestType=0x21, bRequest=9, wValue=0x0300, wIndex=0, data_or_wLength=presetData)
	elif preset > 2:
		rint ('Preset value too high') 
	elif preset < 0:
		print ('Preset value too low')	
	
	if dpi > -1 and dpi < 7:
		dpiData = dpiStart + hexValues[preset] + hexValues[dpi] + dpiEnd
		# Change the DPI value. Second byte is the preset you want to write to and the third one is the value
		dev.ctrl_transfer(bmRequestType=0x21, bRequest=9, wValue=0x0300, wIndex=0, data_or_wLength=dpiData)
	elif dpi < 0:
		print ('DPI value too low')
	elif dpi > 6:
		print ('DPI value too high')
	
	
	if hadDriver0:
		usb.util.release_interface(dev,0)
		dev.attach_kernel_driver(0)
	if hadDriver1:
		usb.util.release_interface(dev,1)
		dev.attach_kernel_driver(1)

builder = Gtk.Builder()
builder.add_from_file("m6900.glade")
print (builder.get_objects())
class Handler:
	def on_window1_destroy(self, *args):
		Gtk.main_quit()
	def on_scale1_value_changed(self, scale):
		adjustment=builder.get_object("adjustment1")
		set_dpi(0, int(adjustment.get_value()), mouse)
	def on_scale2_value_changed(self, scale):
		adjustment=builder.get_object("adjustment2")
		set_dpi(1, int(adjustment.get_value()), mouse)
	def on_scale3_value_changed(self, scale):
		adjustment=builder.get_object("adjustment3")
		set_dpi(2, int(adjustment.get_value()), mouse)

builder.connect_signals(Handler())
win = builder.get_object("window1")
win.show_all()
Gtk.main()
#set_dpi(preset, dpi, mouse)
