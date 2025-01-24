elif '/master.mpd' in url:
    id = url.split("/")[-2]
    url = "https://d26g5bnklkwsh4.cloudfront.net/" + id + "/master.m3u8"

name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("×", "").replace(".", "").replace("https", "").replace("http", "").strip()
name = f'{str(count).zfill(3)}) {name1[:60]}'

if url.endswith(".pdf"):
    try:
        cc1 = f'* {str(count).zfill(3)}.* {name1}.pdf \n*Batch »* {b_name}\n\n{creditx}'
        cmd = f'aria2c -o "{name}.pdf" "{url}"'
        os.system(cmd)
        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
        count += 1
        os.remove(f'{name}.pdf')
        time.sleep(5)
    except FloodWait as e:
        await m.reply_text(str(e))
        time.sleep(e.x)
        continue
    except Exception as e:
        await m.reply_text(
            f"*Downloading Interrupted *\n{str(e)}\n*Name* » {name}\n*Link* » {url}"
        )
        continue

elif url.endswith(".zip"):
    if "youtu" in url:
        ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
    else:
        ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
    if "jw-prod" in url:
        cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
    else:
        cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
    try:
        cc = f'* {str(count).zfill(3)}.* {name1} {res}.mkv\n*Batch »* {b_name}\n\n{creditx}'
        Show = f"*⥥ Downloading »*\n\n*Name »* {name}\nQuality » {raw_text2}\n\n*Url »* {url}"
        prog = await m.reply_text(Show)
        res_file = await helper.download_video(url, cmd, name)
        filename = res_file
        await prog.delete(True)
        await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
        count += 1
        time.sleep(20)
    except Exception as e:
        await m.reply_text(
            f"*Downloading Interrupted *\n{str(e)}\n*Name* » {name}\n*Link* » {url}"
        )
        continue
else:
    if "youtu" in url:
        ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
    else:
        ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
    if "jw-prod" in url:
        cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
    else:
        cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

    try:
        cc = f'* {str(count).zfill(3)}.* {name1} {res}.mkv\n*Batch »* {b_name}\n\n{creditx}'
        Show = f"*⥥ Downloading »*\n\n*Name »* {name}\nQuality » {raw_text2}\n\n*Url »* {url}"
        prog = await m.reply_text(Show)
        res_file = await helper.download_video(url, cmd, name)
        filename = res_file
        await prog.delete(True)
        await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
        count += 1
        time.sleep(20)
    except Exception as e:
        await m.reply_text(
            f"*Downloading Interrupted *\n{str(e)}\n*Name* » {name}\n*Link* » {url}"
        )
        continue

