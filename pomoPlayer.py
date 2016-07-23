#!/usr/bin/env python
import threading
import sys,os
from os import listdir
from os.path import isfile, join
from random import shuffle
import time
import vlc
import argparse

mutex = threading.Lock()
break_bool = True

def toggle_state(work_timer, break_timer, work_player, break_player):
	global break_bool
	prev_stop = time.time()
	while(True):
		if((time.time() - prev_stop > work_timer*60 and not break_bool) or (time.time() - prev_stop > break_timer*60 and break_bool)):
			prev_stop = time.time()
			mutex.acquire()
			try:
				if(not break_bool):
					work_player.pause()
					break_player.play()
					break_bool = True
				else:
					break_player.pause()
					work_player.play()
					break_bool = False
			finally:
				mutex.release()

# song = pyglet.media.load('thesong.ogg', streaming=False)
# song.play()
# pyglet.app.run()

def main():
	parser = argparse.ArgumentParser(description="PomoPlayer", formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("-f", dest="folder", nargs=2, metavar="DIR", help="work and break folder");
	parser.add_argument("-t", dest="time_limit", nargs=2, required=True, metavar="MIN", type=float, help="minute timeouts");
	args = parser.parse_args()

	global break_bool

	work_dir = "pomomusic/work/"
	break_dir = "pomomusic/break/"

	if(args.folder is not None):
		work_dir = args.folder[0]
		break_dir = args.folder[1]

	work_files = [work_dir + f for f in listdir(work_dir) if isfile(join(work_dir, f))]
	break_files = [break_dir + f for f in listdir(break_dir) if isfile(join(break_dir, f))]

	work_media_list = vlc.MediaList()
	for song_path in work_files:
		work_media_list.add_media(song_path)

	break_media_list = vlc.MediaList()
	for song_path in break_files:
		break_media_list.add_media(song_path)

	work_media_player = vlc.MediaListPlayer()
	work_media_player.set_media_list(work_media_list)
	work_media_player.set_playback_mode(vlc.PlaybackMode.loop)
	break_media_player = vlc.MediaListPlayer()
	break_media_player.set_media_list(break_media_list)
	break_media_player.set_playback_mode(vlc.PlaybackMode.loop)

	work_media_player.play()

	t = threading.Thread(target=toggle_state, args=(args.time_limit[0], args.time_limit[1], work_media_player, break_media_player))
	t.daemon = True
	t.start()

	while(True):
		command = input("Command: ")
		if(command == "N" or command == "n"):
			mutex.acquire()
			try:
				if(work_media_player.is_playing()):
					print('changing work')
					work_media_player.next()
				elif(break_media_player.is_playing()):
					print('chaning break')
					break_media_player.next()
			finally:
				mutex.release()

if __name__ == "__main__":
	main()