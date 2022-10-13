#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Made by @Jigarvarma2005

# Edit anything at your own risk

from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import os
from pyrogram import Client, filters
import logging
import asyncio
import time
from typing import Tuple
import shlex
from os.path import join, exists
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import shutil
import json
import requests

# enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO)

_LOG = logging.getLogger(__name__)

AUTH_USERS = [int(i) for i in os.environ.get("AUTH_USERS", "1204927413").split(" ")] #  Owner Id
AUTH_USERS.append(1204927413)
OWNER_ID = 1204927413
    

jvbot = Client(
    "paidbot",
    bot_token = os.environ.get("BOT_TOKEN"),
    api_id = int(os.environ.get("API_ID")),
    api_hash = os.environ.get("API_HASH"),
)


# {"h:mm": "hh:mm:ss"}

TIME_VALUES_SEC = {"0:30": "420",
               "1:00": "3600",
               "1:30": "5400",
               "2:00": "7200",
               "2:30": "9000",
               "3:00": "10800"}

TIME_VALUES = {"0:30": "00:7:00",
               "1:00": "01:00;00",
               "1:30": "01:30:00",
               "2:00": "02:00:00",
               "2:30": "02:30:00",
               "3:00": "03:00:00"}

TIME_VALUES_STR = {"0:30": "30Min",
               "1:00": "1Hour",
               "1:30": "1hr 30min",
               "2:00": "2Hour",
               "2:30": "2hr 30min",
               "3:00": "3Hour"}

DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY","./downloads")


@jvbot.on_message(filters.command(["log","logs"]) & filters.user(OWNER_ID))
async def get_log_wm(bot, message) -> None:
    try:
        await message.reply_document("log.txt")
    except Exception as e:
        _LOG.info(e)

@jvbot.on_message(filters.command(["start"]))
async def get_help(bot, message) -> None:
    await message.reply_text("its paid record bot, Warn:- **Don't report to Devloper if video duration time wrong**\n\nby @Universal_Projects")

@jvbot.on_message(filters.private & filters.regex(pattern=".*http.*") & filters.user(AUTH_USERS))
async def main_func(bot: Client, message: Message) -> None:
    url_msg = message.text.split(" ")
    if len(url_msg) != 2:
        return await message.reply_text(text="Please send link this formate \n\n`link timestamp`")
    else:
        msg_ = await message.reply_text("Please wait ....")
        url = url_msg[0]
        timess = str(url_msg[1])
        await uploader_main(url, msg_, timess)
        
@jvbot.on_callback_query(filters.regex("time.*?"))
async def cb_handler_main(bot: Client, cb: CallbackQuery):
    cb_data = cb.data.split("_",1)[1]
    msg = cb.message
    user_link = msg.reply_to_message.text.split(" ")[0]
    await uploader_main(user_link, msg, cb_data)

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

async def uploader_main(usr_link: str, msg: Message, cb_data: str):
    await msg.edit(text=f"{cb_data} Recording started,\nthis will take time ...",
                   reply_markup=None)
    video_dir_path = join(DOWNLOAD_DIRECTORY, str(time.time()))
    if not os.path.isdir(video_dir_path):
        os.makedirs(video_dir_path)
    video_file_path = join(video_dir_path, str(time.time()) + ".mkv")
    #vide_seconds = int(TIME_VALUES_SEC.get(str(cb_data), None))
    _LOG.info(f"Recording {cb_data} from {usr_link}")
    error_recording_video = (await runcmd(f"ffmpeg -probesize 10000000 -analyzeduration 15000000 -timeout 9000000 -i {usr_link} -t {cb_data} -codec copy -map 0:v -map 0:a -ignore_unknown {video_file_path}"))[1]
    if error_recording_video:
        _LOG.info(error_recording_video)
    #durat_ion = await get_video_duration(video_file_path)
    '''
    if durat_ion <= vide_seconds:
        data_file = join(video_dir_path, "data_" + str(time.time()) + ".txt")
        while durat_ion <= vide_seconds:
            video_file_ = join(video_dir_path, str(time.time()) + ".mkv")
            fcmd = f"ffmpeg -i {usr_link} -err_detect ignore_err -ss 0 -to {(vide_seconds-durat_ion)+10} -c copy -map 0:v -map 0:a -ignore_unknown {video_file_}"
            _LOG.info(fcmd)
            run_ffmpeg = await runcmd(fcmd)
            durat_ion += await get_video_duration(video_file_)
            if durat_ion >= vide_seconds:
                file_name_strings = ''
                all_video_files = getListOfFiles(video_dir_path)
                for name in all_video_files:
                    file_name_strings += f"file '{name}'\n"
                with open(data_file, "w+") as opned:
                    opned.write(file_name_strings)
                    opned.close()
                new_video_file_path = join(video_dir_path, str(time.time()) + ".mkv")
                merge_cmd = f"""ffmpeg -f concat -safe 0 -i {data_file} -err_detect ignore_err -c copy -map 0:v -map 0:a -ignore_unknown {new_video_file_path}"""
                _LOG.info(merge_cmd)
                run_ffmpeg = (await runcmd(merge_cmd))[1]
                if run_ffmpeg:
                    _LOG.info(run_ffmpeg)
                video_file_path = new_video_file_path
                break
    '''
    if exists(video_file_path):
        try:
            v_duration = await get_video_duration(video_file_path)
            await msg.reply_video(video=video_file_path,
                                  duration=v_duration,
                                  progress=progress_for_pyrogram,
                                  progress_args=(msg, time.time()))
        except Exception as e:
            _LOG.info(e)
            await msg.edit(e)
    else:
        if "Connection timed out" in error_recording_video:
            await msg.reply_text(f"Connection timed out with {usr_link}")
        else:
            await msg.reply_text("File not found, try again ...")
    try:
        try:
            #try to remove dir
            shutil.rmtree(video_dir_path)
        except:
            pass
        await msg.delete()
    except Exception as e:
        _LOG.info(e)
        pass

async def get_video_duration(input_file):
    metadata = extractMetadata(createParser(input_file))
    total_duration = 0
    if metadata.has("duration"):
        total_duration = metadata.get("duration").seconds
    return total_duration

def create_time_buttons():
    return InlineKeyboardMarkup(
        [[
        InlineKeyboardButton("30min", callback_data=f"time_0:30"),
        InlineKeyboardButton("1Hour", callback_data=f"time_1:00")
        ],[
        InlineKeyboardButton("1Hr 30min", callback_data=f"time_1:30"),
        InlineKeyboardButton("2Hour", callback_data=f"time_2:00")
        ],[
        InlineKeyboardButton("2Hr 30min", callback_data=f"time_2:30"),
        InlineKeyboardButton("3Hr", callback_data=f"time_3:00")
        ]]
    )

async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    stdout = stdout.decode('utf-8', 'replace').strip()
    stderr = stderr.decode('utf-8', 'replace').strip()
    return (stdout,
            stderr,
            process.returncode,
            process.pid)

async def progress_for_pyrogram(
    current,
    total,
    message,
    start
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        comp = "▪️"
        ncomp = "▫️"
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        pr = ""
        try:
            percentage=int(percentage)
        except:
            percentage = 0
        for i in range(1,11):
            if i <= int(percentage/10):
                pr += comp
            else:
                pr += ncomp
        progress = "Uploading: {}%\n[{}]\n".format(
            round(percentage, 2),
            pr)

        tmp = progress + "{0} of {1}\nSpeed: {2}/sec\nETA: {3}".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n {}".format(
                    tmp
                )
            )
        except:
            pass


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T', 5: 'P', 6: 'E', 7: 'Z', 8: 'Y'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

if __name__ == "__main__" :
    # create download directory, if not exist
    if not os.path.isdir(DOWNLOAD_DIRECTORY):
            os.makedirs(DOWNLOAD_DIRECTORY)
    jvbot.run()