import matplotlib.pyplot as plt
import matplotlib.animation as animation
# import numpy as np
import json
# from datetime import datetime



def createanimation(espresso_data, fps=10):
    # Set up the figure with transparent background - single plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fig.patch.set_facecolor('none')  # Transparent background
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    ax.patch.set_alpha(0.0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    # Calculate animation parameters
    timestamps = [float(i) for i in espresso_data['timeframe']]
    pressure_data = [float(i) for i in espresso_data['data']['espresso_pressure']]
    flow_data = [float(i) for i in espresso_data['data']['espresso_flow']]
    flow_goal_data = [float(i) for i in espresso_data['data']['espresso_flow_goal']]
    flow_goal_weight_data = [float(i) for i in espresso_data['data']['espresso_flow_weight']]
    basket_temp_data = [float(i) for i in espresso_data['data']['espresso_temperature_basket']]
    total_time = max(timestamps)
    time_per_frame = 1.0 / fps  # Real time per frame

    # Create secondary y-axes for temperature and flow
    ax2 = ax.twinx()  # Secondary y-axis for temperature
    ax3 = ax.twinx()  # Third y-axis for flow
    ax4 = ax.twinx()  # Third y-axis for flow
    ax5 = ax.twinx()  # Third y-axis for flow

    # Offset the third y-axis
    ax3.spines['right'].set_position(('outward', 60))

    # Style secondary axes
    for secondary_ax in [ax2, ax3, ax4, ax5]:
        secondary_ax.set_facecolor('none')
        secondary_ax.patch.set_alpha(0.0)
        secondary_ax.spines['top'].set_visible(False)
        secondary_ax.spines['bottom'].set_visible(False)
        secondary_ax.spines['right'].set_color('white')
        secondary_ax.tick_params(colors='white')
        secondary_ax.yaxis.label.set_color('white')

    # Initialize empty lines
    line1, = ax.plot([], [], '#05c793', linewidth=2, label='Pressure (bar)')
    line2, = ax2.plot([], [], '#1fb7ea', linewidth=2, label='Flow (ml/s)')
    line3, = ax3.plot([], [], '#094f5d', linewidth=2, label='Flow Goal (ml/s)', linestyle='dashed')
    line4, = ax4.plot([], [], '#8f6400', linewidth=2, label='Weight Flow (g/s)')
    line5, = ax5.plot([], [], '#ee7733', linewidth=2, label='Basket Temp (°C)')

    # Set up the axes ranges
    ax.set_xlim(0, total_time)
    ax.set_ylim(0, max(pressure_data) * 1.5)
    ax.set_xlabel('Time (seconds)', color='white')
    ax.set_ylabel('Pressure (bar)', color='cyan')

    ax2.set_ylim(0, max(flow_data) * 1.5)
    ax2.set_ylabel('Flow (ml/s)', color='orange')

    ax3.set_ylim(0, max(flow_goal_data) * 1.5)
    # ax3.set_ylabel('Flow Goal (ml/s)', color='lime')

    ax4.set_ylim(0, max(flow_goal_weight_data) * 1.5)
    # ax4.set_ylabel('Weight Flow (g/s)', color='lime')

    ax5.set_ylim(min(basket_temp_data) - 2, max(basket_temp_data) + 2)
    # ax5.set_ylabel('Basket Temp (°C)', color='red')

    # Create combined legend
    lines = [line1, line2, line3, line4, line5]
    labels = ['Pressure (bar)', 'Flow (ml/s)', 'Flow goal (ml/s)', 'Weight Flow (g/s)', 'Basket Temp (°C)']
    lines = [line1, line2, line4, line5]
    labels = ['Pressure (bar)', 'Flow (ml/s)', 'Weight Flow (g/s)', 'Basket Temp (°C)']
    ax.legend(lines, labels, loc='upper left', frameon=False, labelcolor='black')

    plt.tight_layout()

    # Pre-process data for better performance
    max_index = len(timestamps) - 1
    
    def animate(frame):
        current_time = frame * time_per_frame
        
        # Use binary search for better performance with large datasets
        # For now, simple linear search since we're dealing with sorted data
        end_idx = 0
        for i, t in enumerate(timestamps):
            if t <= current_time:
                end_idx = i
            else:
                break
        
        if end_idx == 0 and timestamps[0] > current_time:
            # No data points yet
            for line in [line1, line2, line3, line4, line5]:
                line.set_data([], [])
        else:
            # Get data up to current time (including end_idx)
            x_data = timestamps[:end_idx + 1]
            y1_data = pressure_data[:end_idx + 1]
            y2_data = flow_data[:end_idx + 1]
            y3_data = flow_goal_data[:end_idx + 1]
            y4_data = flow_goal_weight_data[:end_idx + 1]
            y5_data = basket_temp_data[:end_idx + 1]
            
            # Update lines
            line1.set_data(x_data, y1_data)
            line2.set_data(x_data, y2_data)
            # line3.set_data(x_data, y3_data)
            line4.set_data(x_data, y4_data)
            line5.set_data(x_data, y5_data)
        
        # return line1, line2, line3, line4, line5
        return line1, line2, line4, line5

    total_frames = int(total_time * fps) + 1
    
    anim = animation.FuncAnimation(fig, animate, frames=total_frames, 
                                  interval=1000//fps, blit=True, repeat=False)

    return anim

def creategif(idx, anim):
    try:
        anim.save(f'{idx}_espresso_overlay.gif', writer='pillow', fps=10)  # Increased fps
        print("✓ GIF animation saved successfully")
    except Exception as e:
        print(f"GIF save failed: {e}")


def savevideo(idx, anim, fps=30):  # Added fps parameter
    # Check what writers are available
    available_writers = animation.writers.list()
    # print(available_writers)

    for writer_name in ['ffmpeg', 'avconv']:
        if writer_name in available_writers:
            try:
                anim.save(f'{idx}_espresso_overlay.mp4', writer=writer_name, fps=fps,
                         extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
                print(f"✓ MP4 saved successfully with {writer_name}")
                break
            except Exception as e:
                print(f"MP4 save with {writer_name} failed: {e}")

if __name__ == "__main__":

    with open("shot_data_example.json") as f:
        data = json.load(f)
    idx = data['id']
    
    # Create animation with higher fps for smoother playback
    anim = createanimation(data, fps=30)
    
    # Uncomment to save files
    # creategif(idx, anim)
    savevideo(idx, anim, fps=30)
    
    # plt.show()