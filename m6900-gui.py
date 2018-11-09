#!/usr/bin/python3
import argparse
import usb.core
import usb.util
import gi
import usb.control
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

mouse = usb.core.find(idVendor=0xe0ff, idProduct=0x0005)
	
preset = 0
dpi = 1

presetStart = [0x19]
presetEnd = [0x00,0x00,0xe8,0x6c,0x00,0x01]
hexValues = {0:[0x00], 1:[0x01], 2:[0x02], 3:[0x03], 4:[0x04], 5:[0x05], 6:[0x06]}
dpiStart = [0x18]
dpiEnd = [0x01,0x01,0x01,0x01,0x48]

def grab_mouse(dev):
	#detatch both mouse interfaces from any kernel drivers (HID driver in particular)
	if dev.is_kernel_driver_active(0):
		dev.detach_kernel_driver(0)
	if dev.is_kernel_driver_active(1):
		dev.detach_kernel_driver(1)
	dev.set_configuration()
	
	# set the active configuration. With no arguments, the first configuration will be the active one.
	usb.util.claim_interface(dev,0)
	
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
	
def release_mouse(dev):
	usb.util.release_interface(dev,0)
	dev.attach_kernel_driver(0)

	usb.util.release_interface(dev,1)
	dev.attach_kernel_driver(1)

def set_preset(preset, dev):
	#Change the preset. the second byte is the preset
	presetData = presetStart + hexValues[preset] + presetEnd
	dev.ctrl_transfer(bmRequestType=0x21, bRequest=9, wValue=0x0300, wIndex=0, data_or_wLength=presetData)

def set_dpi2(dpi, preset, dev):
	# Change the DPI value. Second byte is the preset you want to write to and the third one is the value
	dpiData = dpiStart + hexValues[preset] + hexValues[dpi] + dpiEnd
	dev.ctrl_transfer(bmRequestType=0x21, bRequest=9, wValue=0x0300, wIndex=0, data_or_wLength=dpiData)

builder = Gtk.Builder()
builder.add_from_file("m6900.glade")
note=builder.get_object("notebook1")
note.set_current_page(2)
current = note.get_current_page()
print (current)
class Handler:
	def on_window1_destroy(self, *args):
		Gtk.main_quit()

	def on_scale1_value_changed(self, scale):
		adjustment=builder.get_object("adjustment1")
		grab_mouse(mouse)
		set_preset(0, mouse)
		set_dpi2(int(adjustment.get_value()), 0, mouse)
		release_mouse(mouse)

	def on_scale2_value_changed(self, scale):
		adjustment=builder.get_object("adjustment2")
		grab_mouse(mouse)
		set_preset(1, mouse)
		set_dpi2(int(adjustment.get_value()), 1, mouse)
		release_mouse(mouse)

	def on_scale3_value_changed(self, scale):
		adjustment=builder.get_object("adjustment3")
		grab_mouse(mouse)
		set_preset(2, mouse)
		set_dpi2(int(adjustment.get_value()), 2, mouse)
		release_mouse(mouse)

builder.connect_signals(Handler())
win = builder.get_object("window1")
win.show_all()
Gtk.main()
