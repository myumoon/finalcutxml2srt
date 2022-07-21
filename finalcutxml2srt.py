#!usr/bin/python
# -*- coding: utf-8 -*-
# FinalCutPro(xml) -> srt

import os
import sys
import optparse
import xml.etree.ElementTree as ET 
from datetime import timedelta
import shutil

def frame_to_time(frame, fps=30):
	totalSeconds     = float(frame) / fps
	hours, remainder = divmod(totalSeconds, 3600)
	minutes, seconds = divmod(remainder, 60)

	#td = timedelta(seconds=(float(frame) / fps))
	return "{:02}:{:02}:{:02},{:03}".format(int(hours), int(minutes), int(seconds), int(frame % fps * 1.0 / fps * 1000))

class SrtWriter(object):
	def __init__(self, dest):
		self.__dest = dest
		self.__no   = 1

	def write(self, startFrame, endFrame, text):
		start_text = frame_to_time(startFrame)
		end_text   = frame_to_time(endFrame)
		self.__dest.write(str(self.__no) + "\n")
		self.__dest.write("{} --> {}\n".format(start_text, end_text))
		self.__dest.write(text + "\n")
		self.__dest.write("\n")
		self.__no += 1

def convert(file):
	if os.path.exists(file) == False:
		return False

	filename  = os.path.splitext(os.path.basename(file))[0]
	dest_path = os.path.join(os.path.dirname(file), filename + ".srt")

	# 出力ファイルを削除
	if os.path.exists(dest_path):
		os.remove(dest_path)

	with open(dest_path, "w", encoding='utf-8') as dest:
		writer = SrtWriter(dest)

		tree             = ET.parse(file) 
		root             = tree.getroot()
		transitions      = [t for t in root.iter("transitionitem")]
		transition_index = 0

		for clip in root.iter("clipitem"):
			# ラベンダーとデフォルト以外のラベルは無視
			labels = clip.find("labels")
			if labels != None:
				label2 = labels.find("label2")
				if label2 != None and label2.text != "Lavender":
					continue

			for filter in clip.iter("filter"):
				effect = filter.find("effect")
				if effect == None:
					continue
				name = effect.find("name")
				if name == None or name.text == None or name.text == "":
					continue
				effectId = effect.find("effectid")
				if effectId == None or effectId.text == None or effectId.text != "GraphicAndType":
					continue
				if name.text.startswith(u"もかちゃ ×"):
					continue

				start  = (int)(clip.find("start").text)
				end    = (int)(clip.find("end").text)

				# トランジションが入っているときは-1になる
				# トランジション時は"clipitem"の前後にstart/endトランジションの要素が入っている
				if start < 0:
					assert transition_index < len(transitions), "out of range"
					current_transition = transitions[transition_index]
					start = int(current_transition.find("start").text)
					transition_index += 1
				if end < 0:
					assert transition_index < len(transitions), "out of range"
					current_transition = transitions[transition_index]
					end = int(current_transition.find("end").text)
					transition_index += 1
				
				writer.write(start, end, name.text)
		
		print("output : {}".format(dest_path))

	duplicate_file(dest_path, "EN")

	return True

def duplicate_file(file, country):
	filename, ext = os.path.splitext(os.path.basename(file))
	dest_path     = os.path.join(os.path.dirname(file), filename + "_" + country + ext)
	shutil.copy(file, dest_path)
	print("duplicate : {}".format(dest_path))
	
def convert_files(filelist):
	for f in filelist:
		if convert(f):
			print("done : {}".format(f))
		else:
			print("convert error : {}".format(f))

def main():
	opt_parser    = optparse.OptionParser()

	options, args = opt_parser.parse_args()
	convert_files(args)

if __name__ == '__main__':
	sys.exit(main())
