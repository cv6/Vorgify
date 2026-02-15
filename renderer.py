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
        
        mode_key = config["mode"] # "Preview" or "Full"
        
        # Fallback if "Full" matches something else or casing differs
        if mode_key not in ["Preview", "Full"]:
            # If standard modes are used in config but we need to match settings keys
            # App sends "Preview" or "Full", should be fine.
            if mode_key != "Preview": mode_key = "Full"

        q_settings = config["quality_settings"][mode_key]
        
        preset = q_settings["preset"]
        method = q_settings["method"] # "Bitrate" or "CRF"
        val = q_settings["value"]
        
        # Build params
        ffmpeg_params = []
        bitrate = None
        
        if method == "CRF":
             ffmpeg_params.extend(["-crf", val])
        else:
             bitrate = val # e.g. "5000k"
        
        fin.write_videofile(
            filename=out_file,
            codec="libx264",
            audio=not no_aud,
            audio_codec="aac",
            preset=preset,
            bitrate=bitrate,
            ffmpeg_params=ffmpeg_params if ffmpeg_params else None,
            threads=config.get("threads", 6),
            logger=logger
        )
            
        return out_file

    finally:
        # Cleanup
        for c in clips:
            try: c.close()
            except: pass
