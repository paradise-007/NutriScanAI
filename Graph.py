import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from Database import retrieve_data
from Home import url, db, user_collection

def pie_graph(variable=None, top=None, color=None, count_types=False, days=7):
    try:
        documents = retrieve_data(url, db, user_collection)
        data = pd.DataFrame(list(documents))
    except Exception as e:
        print(f"Problem with Retrieving Data: {e}")
        return None  # Exit if there is an issue with data retrieval

    data['date'] = pd.to_datetime(data['date'])

    # Filter data based on the number of past days specified
    start_date = datetime.now() - timedelta(days=days)
    filtered_data = data[data['date'] >= start_date]

    if count_types:
        # Count ingredients in type3, type2, type1, type0
        type_columns = ['type3', 'type2', 'type1', 'type0']
        type_counts = {col: filtered_data[col].notna().sum() for col in type_columns}

        # For each type, count the number of ingredients present (ing1, ing2, etc.)
        type_counts_ingredients = {}
        for col in type_columns:
            ingredient_count = filtered_data[col].apply(lambda x: len(x) if isinstance(x, dict) else 0).sum()
            type_counts_ingredients[col] = ingredient_count

        labels = list(type_counts_ingredients.keys())
        sizes = list(type_counts_ingredients.values())

        # Custom color mapping for each type
        type_colors = {
            'type3': '#ff0909',
            'type2': '#ff9413',
            'type1': '#f4db0b',
            'type0': '#25ff0f'
        }

        # Get colors based on the type order
        color = [type_colors.get(type, 'gray') for type in labels]
        
    else:
        if variable not in filtered_data.columns:
            raise ValueError(f"Column {variable} not found in the data")

        variables = filtered_data[variable].dropna()
        variable_count = Counter(variables)

        df = pd.DataFrame(variable_count.items(), columns=[variable, 'Count'])
        df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
        df = df.dropna(subset=['Count'])

        if top is not None and top > len(df):
            top = len(df)

        top_variables = df.nlargest(top, 'Count')
        other_variables = df.loc[~df[variable].isin(top_variables[variable]), 'Count'].sum()

        other_df = pd.DataFrame({variable: ['Other'], 'Count': [other_variables]})
        top_variables = pd.concat([top_variables, other_df], ignore_index=True)
        top_variables = top_variables.query('Count != 0')

        labels = top_variables[variable].tolist()
        sizes = top_variables['Count'].tolist()

        # If only one gender is present, assign color based on gender
        if variable == 'gender':
            if len(labels) == 1:
                if 'male' in labels:
                    color = ['#79f3fc']
                elif 'female' in labels:
                    color = ['#ff6fb3']
            else:
                # Default color scheme if both genders are present
                color = ['#79f3fc', '#ff6fb3']
        
        elif variable == 'state':  # Handle state-based pie chart
            # Example: Assign colors to states if needed
            state_colors = ['#7cff8d', '#f0f254', '#9f93fe', '#ff6b8b', '#f47f2e', '#2e8df4']
            if len(labels) > len(state_colors):
                color = state_colors * (len(labels) // len(state_colors)) + state_colors[:len(labels) % len(state_colors)]
            else:
                color = state_colors[:len(labels)]

    # Check if sizes or color is None, and if so, provide a fallback value
    if not sizes:
        print("No valid sizes to plot.")
        return None

    if color is None:
        color = ['gray'] * len(sizes)  # Fallback to gray if color is not set

    if len(color) < len(sizes):
        color = color * (len(sizes) // len(color)) + color[:len(sizes) % len(color)]  # Repeat color if necessary

    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Plot pie chart
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        colors=color, 
        startangle=140, 
        autopct='%1.1f%%',
        wedgeprops=dict(edgecolor='black', linewidth=0.5)
    )

    # Customize text appearance
    for autotext in autotexts:
        autotext.set_fontweight('normal')  # Ensure percentage text is not bold

    for text in texts:
        text.set_fontweight('bold')  # Set the label text to bold
        text.set_color('white')  # Adjust label color if needed
        text.set_fontsize(10)  # Adjust label size

    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    # Calculate the total for percentage calculation
    total = sum(sizes)
    
    # Add percentages to the radius lines
    for i, p in enumerate(wedges):
        # Calculate the percentage for the current slice
        percentage = sizes[i] / total * 100
        # Get the angle of the slice's midpoint
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        # Adjust rotation for better readability
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        rotation_angle = ang if x > 0 else ang + 180  # Adjust rotation for readability
        ax.annotate(f'{percentage:.1f}%', xy=(x, y), xytext=(x * 0.7, y * 0.7),
                    horizontalalignment=horizontalalignment, verticalalignment='center',
                    rotation=rotation_angle, color='black', fontsize=10)

    # Remove the default annotations
    for autotext in autotexts:
        autotext.set_visible(False)

    fig.patch.set_alpha(0)  # Makes the figure background transparent
    ax.set_facecolor('none')
    plt.tight_layout()
    return fig

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def line_graph(x_axis=None, y_axis=None, days=7, total_users=False):
    try:
        documents = retrieve_data(url, db, user_collection)
        data = pd.DataFrame(list(documents))
    except Exception as e:
        print(f"Problem with Retrieving Data: {e}")
        return

    data['date'] = pd.to_datetime(data['date'])
    start_date = datetime.now() - timedelta(days=days)
    filtered_data = data[data['date'] >= start_date]

    if total_users and (x_axis or y_axis):
        raise ValueError("Cannot plot both total users and specific x and y axes at the same time. Please choose one.")

    fig, ax = plt.subplots(figsize=(12, 6))

    if total_users:
        # Total users line graph
        daily_user_count = filtered_data.groupby(filtered_data['date'].dt.date).size()
        ax.plot(daily_user_count.index, daily_user_count.values, marker='o', label='Total Users', alpha=0.75, color='#79f3fc')

        ax.set_title(f'Total Users Over the Last {days} Days', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', color='white', fontsize=12)
        ax.set_ylabel('Total Users', color='white', fontsize=12)
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')

    elif x_axis and y_axis:
        # If both x_axis and y_axis are specified, aggregate data accordingly
        if x_axis not in filtered_data.columns or y_axis not in filtered_data.columns:
            raise ValueError(f"Columns {x_axis} or {y_axis} not found in the data")

        # Filter data based on x and y axis and aggregate accordingly
        aggregated_data = filtered_data.groupby([x_axis, y_axis]).size().unstack(fill_value=0)

        # Custom color mapping for gender
        gender_colors = {'male': '#79f3fc', 'female': '#ff6fb3'}

        # If x_axis is 'date' and y_axis is 'gender', assign gender colors
        if y_axis == 'gender':
            # Ensure gender is lower case for consistency
            aggregated_data = aggregated_data[['male', 'female']] if 'male' in aggregated_data.columns and 'female' in aggregated_data.columns else aggregated_data

            # Get colors for each gender category
            colors = [gender_colors.get(gender.lower(), '#808080') for gender in aggregated_data.columns]

            # Plot each gender line
            for category, color in zip(aggregated_data.columns, colors):
                ax.plot(aggregated_data.index, aggregated_data[category], marker='o', label=category, alpha=0.75, color=color)
            
            ax.set_title(f'Line Graph for Last {days} Days Usage With Respective Gender', color='white', fontsize=14, fontweight='bold')
            ax.set_xlabel(x_axis, color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            ax.tick_params(axis='x', colors='white', rotation=45)
            ax.tick_params(axis='y', colors='white')

        else:
            # For other combinations of x_axis and y_axis, use tab20 colors
            colors = plt.cm.tab20.colors[:len(aggregated_data.columns)]

            # Plot each category
            for category, color in zip(aggregated_data.columns, colors):
                ax.plot(aggregated_data.index, aggregated_data[category], marker='o', label=category, alpha=0.75, color=color)

            ax.set_title(f'{y_axis} by {x_axis} Over the Last {days} Days', color='white', fontsize=14, fontweight='bold')
            ax.set_xlabel(x_axis, color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            ax.tick_params(axis='x', colors='white', rotation=45)
            ax.tick_params(axis='y', colors='white')

    # Common plot styling
    legend = ax.legend()
    legend.get_frame().set_edgecolor('none')
    legend.get_frame().set_facecolor('none')
    for text in legend.get_texts():
        text.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
        spine.set_linewidth(1)

    ax.grid(False)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    plt.tight_layout()
    return fig


def stacked_bar_graph(x_axis=None, y_axis=None, days=7, top=None):
    try:
        documents = retrieve_data(url, db, user_collection)
        data = pd.DataFrame(list(documents))
    except Exception as e:
        print(f"Problem with Retrieving Data: {e}")
        return None

    data['date'] = pd.to_datetime(data['date'])
    start_date = datetime.now() - timedelta(days=days)
    filtered_data = data[data['date'] >= start_date]

    if x_axis not in filtered_data.columns or y_axis not in filtered_data.columns:
        raise ValueError(f"Columns {x_axis} or {y_axis} not found in the data")

    aggregated_data = filtered_data.groupby([x_axis, y_axis]).size().unstack(fill_value=0)

    # Handle the 'top' parameter
    if top is not None:
        top_x_values = aggregated_data.sum(axis=1).nlargest(top).index
        aggregated_data = aggregated_data.loc[top_x_values]

    # Custom color mapping for gender
    gender_colors = {'male': '#79f3fc', 'female': '#ff6fb3'}

    # Normalize gender values to lowercase for matching
    if y_axis == 'gender':
        # Convert gender values to lowercase and map to colors
        colors = [
            gender_colors.get(gender.lower(), '#808080')  # Default gray if no match
            for gender in aggregated_data.columns
        ]
    else:
        # Use tab20 color palette for other categories
        colors = plt.cm.tab20.colors[:len(aggregated_data.columns)]  # Get the first n colors from tab20

    # Plot the stacked bar graph with explicit color mapping
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the bar chart with the specified colors
    aggregated_data.plot(kind='bar', stacked=True, ax=ax, color=colors)

    ax.set_title(f'Stacked Bar Graph of {y_axis} by {x_axis} Over the Last {days} Days', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel(x_axis.capitalize(), color='white', fontsize=12)
    ax.set_ylabel('Count', color='white', fontsize=12)

    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')

    # Customize legend
    legend = ax.legend(title=y_axis.capitalize())
    legend.get_frame().set_edgecolor('none')
    legend.get_frame().set_facecolor('none')
    for text in legend.get_texts():
        text.set_color('white')

    # Customize axis appearance
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    ax.grid(False)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    plt.tight_layout()
    return fig
