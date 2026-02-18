"""
Generate Gantt Chart HTML with Embedded JSON Data

This script creates a self-contained HTML file with your JSON data already embedded.
No need to upload files - just open the HTML and see your chart!
"""

import json
import sys
from pathlib import Path


def generate_gantt_html_with_data(json_data, output_file='gantt_chart_with_data.html'):
    """
    Generate an HTML Gantt chart with JSON data already embedded
    
    Args:
        json_data: Dictionary containing vegetable schedule data
        output_file: Path where to save the HTML file
    """
    
    # Convert JSON data to JavaScript format
    json_string = json.dumps(json_data, indent=2)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vegetable Planting & Harvesting Schedule - Gantt Chart</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .chart-container {{
            padding: 30px;
            overflow-x: auto;
        }}

        .gantt-chart {{
            min-width: 1200px;
        }}

        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .legend-color {{
            width: 30px;
            height: 20px;
            border-radius: 4px;
        }}

        .planting {{
            background: #10b981;
        }}

        .harvesting {{
            background: #f59e0b;
        }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }}

        th, td {{
            padding: 12px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}

        th {{
            background: #495057;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .vegetable-name {{
            background: #f8f9fa;
            font-weight: 600;
            text-align: left;
            color: #495057;
            min-width: 120px;
        }}

        .month-cell {{
            background: white;
            position: relative;
            min-width: 80px;
        }}

        .bar {{
            height: 35px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
        }}

        .bar:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }}

        .bar.plant {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}

        .bar.harvest {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }}

        .info-box {{
            margin: 20px 30px;
            padding: 20px;
            background: #e7f3ff;
            border-left: 4px solid #667eea;
            border-radius: 8px;
        }}

        .info-box h3 {{
            color: #495057;
            margin-bottom: 10px;
        }}

        .info-box p {{
            color: #6c757d;
            line-height: 1.6;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px 30px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            color: #6c757d;
            margin-top: 5px;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 Vegetable Planting & Harvesting Schedule</h1>
            <p>Interactive Gantt Chart Visualization</p>
        </div>

        <div id="statsContainer"></div>
        <div id="chartContainer" class="chart-container"></div>
        <div id="infoContainer"></div>
    </div>

    <script>
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        // Embedded JSON data from your CrewAI agent
        const data = {json_string};

        function renderGanttChart(data) {{
            const schedules = data.vegetable_schedule;
            
            // Render stats
            renderStats(data, schedules);
            
            // Render chart
            let html = `
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color planting"></div>
                        <span>Planting Period</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color harvesting"></div>
                        <span>Harvesting Period</span>
                    </div>
                </div>
                <div class="gantt-chart">
                    <table>
                        <thead>
                            <tr>
                                <th class="vegetable-name">Vegetable</th>
            `;

            // Add month headers
            for (let i = 0; i < 12; i++) {{
                html += `<th>${{months[i]}}</th>`;
            }}
            html += `</tr></thead><tbody>`;

            // Add rows for each vegetable
            schedules.forEach(veg => {{
                html += `<tr><td class="vegetable-name">${{veg.vegetable}}</td>`;
                
                for (let month = 1; month <= 12; month++) {{
                    html += '<td class="month-cell">';
                    
                    // Check if this month is in planting period
                    if (month >= veg.plant_start_month && month <= veg.plant_end_month) {{
                        html += '<div class="bar plant">Plant</div>';
                    }}
                    // Check if this month is in harvesting period
                    else if (month >= veg.harvest_start_month && month <= veg.harvest_end_month) {{
                        html += '<div class="bar harvest">Harvest</div>';
                    }}
                    
                    html += '</td>';
                }}
                html += '</tr>';
            }});

            html += '</tbody></table></div>';
            
            document.getElementById('chartContainer').innerHTML = html;
            
            // Render info box
            renderInfo(data);
        }}

        function renderStats(data, schedules) {{
            const totalVegetables = schedules.length;
            const avgPlantingMonths = schedules.reduce((sum, v) => 
                sum + (v.plant_end_month - v.plant_start_month + 1), 0) / totalVegetables;
            const avgHarvestMonths = schedules.reduce((sum, v) => 
                sum + (v.harvest_end_month - v.harvest_start_month + 1), 0) / totalVegetables;

            const html = `
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">${{totalVegetables}}</div>
                        <div class="stat-label">Vegetables</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{avgPlantingMonths.toFixed(1)}}</div>
                        <div class="stat-label">Avg Planting Months</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{avgHarvestMonths.toFixed(1)}}</div>
                        <div class="stat-label">Avg Harvest Months</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${{data.timestamp || 'N/A'}}</div>
                        <div class="stat-label">Generated Date</div>
                    </div>
                </div>
            `;
            
            document.getElementById('statsContainer').innerHTML = html;
        }}

        function renderInfo(data) {{
            const html = `
                <div class="info-box">
                    <h3>📝 About This Schedule</h3>
                    <p><strong>Generated by:</strong> ${{data.generated_by || 'Unknown'}}</p>
                    <p><strong>Notes:</strong> ${{data.notes || 'No additional notes'}}</p>
                </div>
            `;
            
            document.getElementById('infoContainer').innerHTML = html;
        }}

        // Render chart on page load
        window.addEventListener('load', () => {{
            renderGanttChart(data);
        }});
    </script>
</body>
</html>'''
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Generated Gantt chart: {output_file}")
    return output_file


def main():
    """Example usage"""
    
    # Example: Load JSON from file
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        with open(json_file, 'r') as f:
            data = json.load(f)
    else:
        # Use sample data
        data = {{
            "vegetable_schedule": [
                {{"vegetable": "Tomatoes", "plant_start_month": 3, "plant_end_month": 5, 
                  "harvest_start_month": 6, "harvest_end_month": 9}},
                {{"vegetable": "Lettuce", "plant_start_month": 3, "plant_end_month": 4, 
                  "harvest_start_month": 5, "harvest_end_month": 6}},
            ],
            "generated_by": "CrewAI Gardening Agent",
            "timestamp": "2026-02-14",
            "notes": "Sample schedule"
        }}
    
    # Generate HTML
    output_file = Path('outputs') / 'gantt_chart_with_data.html'
    output_file.parent.mkdir(exist_ok=True)
    
    generate_gantt_html_with_data(data, str(output_file))
    
    print(f"🎉 Done! Open {output_file} in your browser to view the chart.")


if __name__ == "__main__":
    main()