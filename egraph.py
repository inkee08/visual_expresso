import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patheffects as pe
from matplotlib.ticker import MultipleLocator
# from matplotlib import font_manager
import json

def integer_formatter(x, pos):
    return f'{int(x)}'

def createanimation(espresso_data, fps=10, display_fps=30):
    # Set up the figure with transparent background - two subplot layout
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), height_ratios=[2, 1])
    fig.patch.set_facecolor('none')  # Transparent background
    fig.patch.set_alpha(0.0)
    
    # Style both axes
    for ax in [ax1, ax2]:
        ax.set_facecolor('none')
        ax.patch.set_alpha(0.0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#c8c8c8')
        ax.spines['left'].set_visible(False)

    # Set ticks to appear only at integer locations
    ax1.yaxis.set_major_locator(MultipleLocator(1))
    ax2.xaxis.set_major_locator(MultipleLocator(1))
    ax2.yaxis.set_major_locator(MultipleLocator(5))
    
    ax1.tick_params(colors='none', bottom=False, left=True, labelbottom=False, which='both')
    ax2.tick_params(colors='none', bottom=True, left=True, labelbottom=True, which='both')

    
    shadoww = 3
    # Add path effects to ax1 tick labels
    for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontfamily('DejaVu Sans')
        label.set_color('white')
        label.set_fontsize(18)
        label.set_fontweight('semibold')  # 'normal', 'bold', 'light'
        label.set_fontstyle('normal')  # 'normal', 'italic'
        label.set_path_effects([
            pe.withStroke(linewidth=shadoww, foreground='black'),
            pe.Normal()
        ])

    # Calculate animation parameters
    timestamps = [float(i) for i in espresso_data['timeframe']]
    pressure_data = [float(i) for i in espresso_data['data']['espresso_pressure']]
    flow_data = [float(i) for i in espresso_data['data']['espresso_flow']]
    flow_goal_data = [float(i) for i in espresso_data['data']['espresso_flow_goal']]
    flow_goal_weight_data = [float(i) for i in espresso_data['data']['espresso_flow_weight']]
    basket_temp_data = [float(i) for i in espresso_data['data']['espresso_temperature_basket']]
    total_time = max(timestamps)
    time_per_frame = 1.0 / fps  # Real time per frame

    # Create secondary y-axes for flow data on the main chart
    ax1_flow = ax1.twinx()  # Secondary y-axis for flow
    ax1_flow_weight = ax1.twinx()  # Fourth y-axis for flow weight

    # Style secondary axes for main chart
    for secondary_ax in [ax1_flow, ax1_flow_weight]:
        secondary_ax.set_facecolor('none')
        secondary_ax.patch.set_alpha(0.0)
        secondary_ax.spines['top'].set_visible(False)
        secondary_ax.spines['bottom'].set_visible(False)
        secondary_ax.spines['right'].set_visible(False)
        secondary_ax.spines['left'].set_visible(False)
        secondary_ax.tick_params(colors='none')

    lw = 4

    # Initialize empty lines for main chart (pressure + flow data)
    line1, = ax1.plot([], [], '#05c79d', linewidth=lw, label='Pressure (bar)')
    line2, = ax1_flow.plot([], [], '#1fb7ea', linewidth=lw, label='Flow (ml/s)')
    line4, = ax1_flow_weight.plot([], [], '#8f6400', linewidth=lw, label='Weight Flow (g/s)')
    
    # Initialize empty line for temperature chart
    line5, = ax2.plot([], [], '#ee7733', linewidth=lw, label='Basket Temp (°C)')

    # Set up the main chart axes ranges (pressure + flow)
    ax1.set_xlim(0, total_time)
    ax1.set_ylim(0, max(pressure_data) * 1.5)

    ax1_flow.set_ylim(0, max(flow_data) * 1.5)
    ax1_flow_weight.set_ylim(0, max(flow_goal_weight_data) * 1.5)

    # Set up the temperature chart axes ranges
    ax2.set_xlim(0, total_time)
    ax2.set_ylim(min(basket_temp_data) - 2, max(basket_temp_data) + 4)

    for i in range(1, int(max(pressure_data) * 1.5)+1):
        ax1.axhline(y=i, color='#c8c8c8', linestyle='-', alpha=0.5, linewidth=1)
    for i in range(0, int(max(basket_temp_data)) + 5, 5):
        ax2.axhline(y=i, color='#c8c8c8', linestyle='-', alpha=0.5, linewidth=1)

    # Create combined legend below the plot
    lines = [line1, line2, line4, line5]
    labels = ['Pressure (bar)', 'Flow (ml/s)', 'Weight Flow (g/s)', 'Basket Temp (°C)']
    legend = ax.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), 
            frameon=False, labelcolor='white', ncol=3, handlelength=1.5,
            )

    for text in legend.get_texts():
        text.set_fontfamily('DejaVu Sans')
        text.set_fontsize(18)
        text.set_fontweight('semibold')  # 'normal', 'bold', 'light'
        text.set_fontstyle('normal')  # 'normal', 'italic'
        text.set_path_effects([
            pe.withStroke(linewidth=shadoww, foreground='black'),
            pe.Normal()
        ])

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Add space at bottom for legend

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
            # for line in [line1, line2, line3, line4, line5]:
            for line in [line1, line2, line4, line5]:
                line.set_data([], [])
        else:
            # Get data up to current time (including end_idx)
            x_data = timestamps[:end_idx + 1]
            y1_data = pressure_data[:end_idx + 1]
            y2_data = flow_data[:end_idx + 1]
            y3_data = flow_goal_data[:end_idx + 1]
            y4_data = flow_goal_weight_data[:end_idx + 1]
            y5_data = basket_temp_data[:end_idx + 1]
            
            # Update lines for main chart (pressure + flow)
            line1.set_data(x_data, y1_data)
            line2.set_data(x_data, y2_data)
            # line3.set_data(x_data, y3_data)
            line4.set_data(x_data, y4_data)
            
            # Update line for temperature chart
            line5.set_data(x_data, y5_data)
        
        return line4, line2, line1, line5

    total_frames = int(total_time * fps) + 1
    
    # For plt.show() to display at desired fps, interval must be set correctly
    # interval is in milliseconds - for 30fps use 1000/30 = 33.33ms
    anim = animation.FuncAnimation(fig, animate, frames=total_frames, 
                                  interval=1000//display_fps, blit=True, repeat=False)

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

    for writer_name in ['ffmpeg', 'avconv']:
        if writer_name in available_writers:
            try:
                # Try saving as MOV instead of MP4 for better transparency support
                anim.save(f'output/{idx}_overlay.mov', writer='ffmpeg', fps=30,
                        extra_args=['-vcodec', 'png', '-pix_fmt', 'rgba'])
                print(f'{idx} MOV saved')
            except Exception as e:
                print(f"error: {e}")

if __name__ == "__main__":
    with open("shot_data_example.json") as f:
        data = json.load(f)
    idx = data['id']
    
    # Create animation with higher fps for smoother playback
    anim = createanimation(data, fps=30, display_fps=30)
    
    # Uncomment to save files
    # creategif(idx, anim)
    savevideo(idx, anim, fps=30)
    
    # plt.show()