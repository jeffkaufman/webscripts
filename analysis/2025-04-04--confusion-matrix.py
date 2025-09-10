#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Define the appliances (columns) and tasks (rows)
appliances = ['Toaster', 'Dishwasher', 'Microwave', 'Washing\nMachine',
'Stove/\nOven', 'Dryer']
tasks = ['Make\nToast', 'Wash\nDishes', 'Cook a\nFrozen Dinner',
         'Wash\nClothes', 'Cook\nEggs', 'Dry\nClothes']

# Define the effectiveness matrix
# 0: Red (bad idea)
# 1: Yellow (might work)
# 2: Green (good idea)
effectiveness = np.array([
    [2, 0, 1, 0, 2, 0],  # Make Toast
    [0, 2, 0, 1, 1, 0],  # Wash Dishes
    [0, 1, 2, 0, 2, 0],  # Cook Frozen Dinner
    [0, 0, 0, 2, 0, 1],  # Wash Clothes
    [0, 0, 2, 0, 2, 0],  # Cook Eggs
    [0, 0, 0, 0, 0, 2],  # Dry Clothes
])


# Create custom colormap (red, yellow, green)
colors = ['#ffb3b3', '#ffffb3', '#b3ffb3']  # Light red, light yellow, light green
cmap = ListedColormap(colors)

# Create the figure and axis
fig, ax = plt.subplots(figsize=(10, 8))

# Create the table with colored cells
table = ax.table(
        cellText=np.full_like(effectiveness, '', dtype=object),
            cellColours=cmap(effectiveness/2),
                colLabels=appliances,
                    rowLabels=tasks,
                        loc='center',
                            cellLoc='center'
                            )

# Style the table
table.scale(1, 1.5)
table.auto_set_font_size(False)
table.set_fontsize(12)

# Add annotations for special cases
annotations = [
    (0, 0, "✓"),  # Toaster making toast
    (1, 1, "✓"),  # Dishwasher washing dishes
    (2, 2, "✓"),  # Microwave cooking frozen dinner
    (2, 4, "✓"),  # Stove cooking frozen dinner
    (3, 3, "✓"),  # Washing machine washing clothes
    (4, 2, "✓"),  # Microwave cooking eggs
    (4, 4, "✓"),  # Stove cooking eggs
    (5, 5, "✓"),  # Dryer drying clothes
    (1, 4, "Sterilized\nat least"),  # Stove washing dishes
    (2, 1, "Fish might\nbe cooked")  # Dishwasher cooking frozen dinner
]

# Add the annotations to cells
for row, col, text in annotations:
    cell = table[(row+1, col)]
    cell.get_text().set_text(text)
    cell.get_text().set_fontsize(10)
    
# Remove axis
ax.axis('off')
    
# Add title
plt.title('Household Appliance Usage Guide (XKCD Style)',
          fontsize=16, pad=20)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()
    
