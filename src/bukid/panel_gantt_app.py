"""
Panel UI Integration for Vegetable Schedule Gantt Chart

This shows different ways to display your Gantt chart in a Panel application.

Requirements:
    pip install panel

Usage:
    panel serve panel_gantt_app.py --show
"""

#import panel as pn
import json
from pathlib import Path
#from bukid.tools.generate_gantt_with_json import generate_gantt_html_with_data

# Enable Panel extensions
#pn.extension('terminal', 'ace', sizing_mode='stretch_width')


# ============================================================================
# METHOD 1: Embed HTML directly in Panel (RECOMMENDED)
# ============================================================================

def create_gantt_html_pane(data):
    """
    Create a Panel HTML pane with the Gantt chart
    This is the BEST method for Panel - embedded directly in the UI
    """
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    schedules = data.get('vegetable_schedule', [])
    
    # Generate the HTML for the Gantt chart
    html = '''
    <style>
        .gantt-container {
            width: 100%;
            overflow-x: auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
        }
        
        .legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 20px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .legend-color {
            width: 30px;
            height: 20px;
            border-radius: 4px;
        }
        
        .planting { background: #10b981; }
        .harvesting { background: #f59e0b; }
        .pricing { background: #bada55; }
        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }
        
        th, td {
            padding: 5px;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        
        th {
            background: #495057;
            color: white;
            font-weight: 600;
        }
        
        .vegetable-name {
            background: #f8f9fa;
            font-weight: 600;
            text-align: left;
            color: #495057;
            min-width: 80px;
        }
        
        .month-cell {
            background: white;
            min-width: 50px;
        }
        
        .bar {
            height: 20px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 500;
            font-size: 9px;
        }
        
        .bar.plant {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }
        
        .bar.harvest {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        .bar.price {
            background: linear-gradient(135deg, #bada55 0%, #bada55 100%);
        }

        .companion-plant{
            font-weight: lighter;
            font-size: x-small;
        }
    </style>
    
    <div class="gantt-container">
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color planting"></div>
                <span>Planting Period</span>
            </div>
            <div class="legend-item">
                <div class="legend-color harvesting"></div>
                <span>Harvesting Period</span>
            </div>
            <div class="legend-item">
                <div class="legend-color pricing"></div>
                <span>Average Price per Kilo for Previous Year</span>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th class="vegetable-name" >Vegetable</th>
                    <th class="vegetable-name" >Reason</th>
                    <th class="vegetable-name" >Companion Plant</th>
    '''
    
    # Add month headers
    for month in months:
        html += f'<th>{month}</th>'
    
    html += '</tr></thead><tbody>'
    
    # Add rows for each vegetable
    for veg in schedules:
        html += f'<tr><td class="vegetable-name" rowspan="2">{veg["vegetable"]}</td>'
        html += f'<td class="companion-plant" rowspan="2">{veg["reason"]}</td>'
        html += f'<td class="companion-plant">{veg["companion_plant"]}</td>'

        
        for month in range(1, 13):
            html += '<td class="month-cell">'
            if veg['plant_start_month']<=veg['plant_end_month']:
                if month >= veg['plant_start_month'] and month <= veg['plant_end_month']:
                    html += '<div class="bar plant">Plant</div>'
                
            elif veg['plant_start_month']>veg['plant_end_month']:
                if month >= veg['plant_start_month'] and month <= 12:
                    html += '<div class="bar plant">Plant</div>'
                if month <= veg['plant_end_month'] and month >= 1:
                    html += '<div class="bar plant">Plant</div>'
            
            if veg['harvest_start_month']<=veg['harvest_end_month']:
                if month >= veg['harvest_start_month'] and month <= veg['harvest_end_month']:
                    html += '<div class="bar harvest">Harvest</div>'
            elif veg['harvest_start_month']>veg['harvest_end_month']:
                if month >= veg['harvest_start_month'] and month <= 12:
                    html += '<div class="bar harvest">Harvest</div>'
                if month <= veg['harvest_end_month'] and month >= 1:
                    html += '<div class="bar harvest">Harvest</div>'
            html += '</td>'
        
        html += '</tr>'

        price_list = veg['vegetable_price']
        html += '<tr>'
        html += f'<td class="companion-plant">Average Price per Kilo in {veg["vegetable_price_currency"]}</td>'
        html += f'<td class="month-cell">{price_list["jan"]}</td>'
        html += f'<td class="month-cell">{price_list["feb"]}</td>'
        html += f'<td class="month-cell">{price_list["mar"]}</td>'
        html += f'<td class="month-cell">{price_list["apr"]}</td>'
        html += f'<td class="month-cell">{price_list["may"]}</td>'
        html += f'<td class="month-cell">{price_list["jun"]}</td>'
        html += f'<td class="month-cell">{price_list["jul"]}</td>'
        html += f'<td class="month-cell">{price_list["aug"]}</td>'
        html += f'<td class="month-cell">{price_list["sep"]}</td>'
        html += f'<td class="month-cell">{price_list["oct"]}</td>'
        html += f'<td class="month-cell">{price_list["nov"]}</td>'
        html += f'<td class="month-cell">{price_list["dec"]}</td>'    
        html += '</tr>'

    
    html += '</tbody></table></div>'
    #return pn.pane.HTML(html, sizing_mode='stretch_width', height=600)

