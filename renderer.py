import os
import time
from datetime import datetime
from moviepy import VideoFileClip, concatenate_videoclips
import moviepy.video.fx as vfx

def render_video(config, logger, cancel_check_callback):
    """
    Renders the video based on the provided configuration.
    
    config: dict containing:
        - source_folder
        - destination_folder
        - output_filename
        - video_files (list)
        - clip_settings (dict)
        - global_speed
        - fade_in
        - fade_out
        - crossfade
        - audio_enabled
        - mode ("Preview" or "Full")
        - threads
    logger: ProgressBarLogger instance
    cancel_check_callback: function returning bool
    """
    
    out_dir = config["destination_folder"]
    os.makedirs(out_dir, exist_ok=True)
    
    fname = config["output_filename"]
    out_file = os.path.join(out_dir, fname)
    
    active_files = config["video_files"]
    clips = []
    
    g_speed = config["global_speed"]
    no_aud = not config["audio_enabled"]
    fi = config["fade_in"]
    cr = config["crossfade"]
    fo = config["fade_out"]
    
    try:
        for i, f in enumerate(active_files):
            if cancel_check_callback():
                raise Exception("Abbruch")
            
            full_path = os.path.join(config["source_folder"], f)
            c = VideoFileClip(full_path, audio=not no_aud)
            
            s = config["clip_settings"].get(f, {"speed": 1.0, "reverse": False})
            
            if s["reverse"]:
                c = c.with_effects([vfx.TimeMirror()])
            
            ts = s["speed"] * g_speed
            if ts != 1.0:
                c = c.with_effects([vfx.MultiplySpeed(ts)])
            
            fx = []
            if i == 0 and fi > 0:
                fx.append(vfx.FadeIn(fi))
            if i > 0 and cr > 0:
                fx.append(vfx.CrossFadeIn(cr))
            
            clips.append(c.with_effects(fx))

        if cancel_check_callback():
             raise Exception("Abbruch")

        fin = concatenate_videoclips(clips, method="compose", padding=-cr)
        if fo > 0:
            fin = fin.with_effects([vfx.FadeOut(fo)])
        
        p = {
            "filename": out_file,
            "codec": "libx264",
            "audio": not no_aud,
            "threads": config.get("threads", 6),
            "logger": logger,
            "audio_codec": "aac"
        }
        
        if config["mode"] == "Preview":
            fin.write_videofile(**p, preset="ultrafast", bitrate="5000k")
        else:
            fin.write_videofile(**p, preset="slow", ffmpeg_params=["-crf", "16"])
            
        return out_file

    finally:
        # Cleanup
        for c in clips:
            try: c.close()
            except: pass
