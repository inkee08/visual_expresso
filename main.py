import visualizer as v
import egraph
import os
import igen

username, password = v.getauth()
shots = v.getshots(username, password)

if shots:
    max_videos = 4
    a = 0
    for i in shots['data']:
        shot = v.getshot(username, password, i['id'])
        if shot and a <= max_videos:
            name = shot['start_time'].split('.')[0]
            name = name.replace(':', '_')

            file_path = f"output/{name}_overlay.mov"
            if not os.path.exists(file_path):
                anim = egraph.createanimation(shot, fps=30, display_fps=30)
                egraph.savevideo(name, anim, fps=30)
            else:
                print(f'{name}_overlay.mov skipped')
            
            profile = shot['profile_title']
            bean = shot['bean_brand']
            bean_w = shot['bean_weight']
            drink_w = shot['drink_weight']
            grinder = shot['grinder_model']
            grinder_setting = shot['grinder_setting']
            duration = shot['duration']

            text = f'''
            Profile: {profile}
            Bean: {bean}
            Ratio: {bean_w}:{drink_w}
            Grinder: {grinder}
            Grinder Setting: {grinder_setting}
            Duration: {duration}s
            '''

            file_path = f"output/{name}.png"
            igen.create_image(text, output_path=f'{file_path}', font_size=64)
        a += 1