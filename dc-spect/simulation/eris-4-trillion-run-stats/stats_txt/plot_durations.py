import matplotlib.pyplot as plt
import numpy as np
import re

durations = []
with open('durations.txt', 'r') as f:
    for line in f:
        match = re.search(r'duration: ([\d\.]+)', line)
        if match:
            durations.append(float(match.group(1)))

durations = np.array(durations) * 24  # Convert days to hours

plt.figure(figsize=(12, 7))
plt.hist(durations, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
plt.title('Distribution of Computing Times (Duration in Hours)', fontsize=14)
plt.xlabel('Duration (Hours)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Calculate detailed stats
mean_val = np.mean(durations)
std_val = np.std(durations)
min_val = np.min(durations)
max_val = np.max(durations)
median_val = np.median(durations)
p25 = np.percentile(durations, 25)
p75 = np.percentile(durations, 75)

# Add stats lines to the plot
plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {mean_val:.2f}h')
plt.axvline(median_val, color='green', linestyle='dashdot', linewidth=2, label=f'Median: {median_val:.2f}h')
plt.axvline(min_val, color='orange', linestyle=':', linewidth=1.5, label=f'Min: {min_val:.2f}h')
plt.axvline(max_val, color='purple', linestyle=':', linewidth=1.5, label=f'Max: {max_val:.2f}h')
plt.axvline(p25, color='blue', linestyle=(0, (3, 5, 1, 5)), linewidth=1.5, label=f'Q1 (25th): {p25:.2f}h')
plt.axvline(p75, color='blue', linestyle=(0, (3, 5, 1, 5)), linewidth=1.5, label=f'Q3 (75th): {p75:.2f}h')

# Add a text box with detailed stats
stats_text = (f"Count: {len(durations)}\n"
              f"Mean: {mean_val:.2f}h\n"
              f"Std Dev: {std_val:.2f}h\n"
              f"Min: {min_val:.2f}h\n"
              f"Max: {max_val:.2f}h\n"
              f"Median: {median_val:.2f}h\n"
              f"IQR: {p75-p25:.2f}h\n"
              f"(Q3-Q1, middle 50%)")

plt.text(0.95, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.legend(loc='upper left')
plt.tight_layout()

plt.savefig('duration_distribution_hours.png')
print(f"Distribution plot saved to duration_distribution_hours.png")
print("\n--- Detailed Statistics (Hours) ---")
print(f"Count:  {len(durations)}")
print(f"Mean:   {mean_val:.4f} hours")
print(f"Median: {median_val:.4f} hours")
print(f"Std:    {std_val:.4f} hours")
print(f"Min:    {min_val:.4f} hours")
print(f"Max:    {max_val:.4f} hours")
print(f"25th %: {p25:.4f} hours")
print(f"75th %: {p75:.4f} hours")
print(f"IQR:    {p75 - p25:.4f} hours")
