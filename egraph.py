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
    line1, = ax.plot([], [], 'cyan', linewidth=3, label='Pressure (bar)')
    line2, = ax2.plot([], [], 'orange', linewidth=3, label='Flow (ml/s)')
    line3, = ax3.plot([], [], 'green', linewidth=3, label='Flow Goal (ml/s)')
    line4, = ax4.plot([], [], 'blue', linewidth=3, label='Weight Flow (g/s)')
    line5, = ax5.plot([], [], 'red', linewidth=3, label='Basket Temp (°C)')

    # Set up the axes ranges
    ax.set_xlim(0, total_time)
    ax.set_ylim(0, max(pressure_data) * 1.1)
    ax.set_xlabel('Time (seconds)', color='white')
    ax.set_ylabel('Pressure (bar)', color='cyan')

    ax2.set_ylim(0, max(flow_data) * 1.1)
    ax2.set_ylabel('Flow (ml/s)', color='orange')

    ax3.set_ylim(0, max(flow_goal_data) * 1.1)
    ax3.set_ylabel('Flow Goal (ml/s)', color='lime')

    ax4.set_ylim(0, max(flow_goal_weight_data) * 1.1)
    ax4.set_ylabel('Weight Flow (g/s)', color='lime')

    ax5.set_ylim(min(basket_temp_data) - 2, max(basket_temp_data) + 2)
    ax5.set_ylabel('Basket Temp (°C)', color='red')

    # Create combined legend
    lines = [line1, line2, line3, line4, line5]
    labels = ['Pressure (bar)', 'Flow (ml/s)', 'Flow goal (ml/s)', 'Weight Flow (g/s)', 'Basket Temp (°C)']
    ax.legend(lines, labels, loc='upper left', frameon=False, labelcolor='white')

    plt.tight_layout()

    def animate(frame):
        current_time = frame * time_per_frame

        # Find all data points up to current time
        indices = [i for i, t in enumerate(timestamps) if t <= current_time]
        
        if not indices:
            # No data points yet
            line1.set_data([], [])
            line2.set_data([], [])
            line3.set_data([], [])
            line4.set_data([], [])
            line5.set_data([], [])
        else:
            # Get data up to current time
            x_data = [timestamps[i] for i in indices]
            y1_data = [pressure_data[i] for i in indices]
            y2_data = [flow_data[i] for i in indices]
            y3_data = [flow_goal_data[i] for i in indices]
            y4_data = [flow_goal_weight_data[i] for i in indices]
            y5_data = [basket_temp_data[i] for i in indices]
            
            # Update lines
            line1.set_data(x_data, y1_data)
            line2.set_data(x_data, y2_data)
            line3.set_data(x_data, y3_data)
            line4.set_data(x_data, y4_data)
            line5.set_data(x_data, y5_data)
        
        return line1, line2, line3, line4, line5

    total_frames = int(total_time * fps) + 1
    
    anim = animation.FuncAnimation(fig, animate, frames=total_frames, 
                                  interval=1000//fps, blit=True, repeat=False)

    return anim

def creategif(idx, anim):
    try:
        anim.save(f'{idx}_espresso_overlay.gif', writer='pillow', fps=1)
        print("✓ GIF animation saved successfully")
        # video_saved = True
    except Exception as e:
        print(f"GIF save failed: {e}")


def savevideo(idx, anim):
    # Check what writers are available
    available_writers = animation.writers.list()

    for writer_name in ['ffmpeg', 'avconv']:
        if writer_name in available_writers:
            try:
                anim.save(f'{idx}_espresso_overlay.mp4', writer=writer_name, fps=1)
                print(f"✓ MP4 saved successfully with {writer_name}")
                video_saved = True
                break
            except Exception as e:
                print(f"MP4 save with {writer_name} failed: {e}")

    if not video_saved:
        print("⚠️  Video save failed - using PNG frames instead (recommended for DaVinci)")

if __name__ == "__main__":

    with open("shot_data_example.json") as f:
        data = json.load(f)
    idx = data['id']
    
    anim = createanimation(data)
    # creategif(idx, anim)
    plt.show()