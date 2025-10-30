#!/usr/bin/env python3
"""
Enhanced Figma to HTML/CSS Converter

This enhanced version includes better handling of:
- Flexbox layouts
- Text styling
- Component instances
- Auto-layout properties
- Better CSS organization
"""

import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import re

# Load environment variables
load_dotenv()

class EnhancedFigmaConverter:
    def __init__(self):
        self.access_token = os.getenv('FIGMA_ACCESS_TOKEN')
        self.file_key = os.getenv('FIGMA_FILE_KEY')
        self.base_url = 'https://api.figma.com/v1'
        self.headers = {
            'X-Figma-Token': self.access_token
        }
        
        if not self.access_token:
            raise ValueError("FIGMA_ACCESS_TOKEN not found in environment variables")
    
    def fetch_figma_file(self) -> Dict[str, Any]:
        """Fetch the Figma file data from the API"""
        url = f"{self.base_url}/files/{self.file_key}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Figma file: {e}")
            raise
    
    def convert_color(self, color: Dict[str, float]) -> str:
        """Convert Figma color to CSS color"""
        if not color:
            return 'transparent'
        
        r = int(color.get('r', 0) * 255)
        g = int(color.get('g', 0) * 255)
        b = int(color.get('b', 0) * 255)
        a = color.get('a', 1)
        
        if a < 1:
            return f"rgba({r}, {g}, {b}, {a})"
        else:
            return f"rgb({r}, {g}, {b})"
    
    def convert_fill(self, fills: List[Dict[str, Any]]) -> str:
        """Convert Figma fills to CSS background"""
        if not fills:
            return 'transparent'
        
        fill = fills[0]  # Take the first fill
        
        if fill.get('type') == 'SOLID':
            return self.convert_color(fill.get('color', {}))
        elif fill.get('type') == 'GRADIENT_LINEAR':
            # Handle linear gradients
            gradient_stops = []
            for stop in fill.get('gradientStops', []):
                color = self.convert_color(stop.get('color', {}))
                position = int(stop.get('position', 0) * 100)
                gradient_stops.append(f"{color} {position}%")
            
            return f"linear-gradient({gradient_stops[0] if gradient_stops else 'transparent'})"
        
        return 'transparent'
    
    def convert_text_style(self, style: Dict[str, Any]) -> Dict[str, str]:
        """Convert Figma text style to CSS"""
        css = {}
        
        # Font family
        if 'fontFamily' in style:
            css['font-family'] = f'"{style["fontFamily"]}", sans-serif'
        
        # Font size
        if 'fontSize' in style:
            css['font-size'] = f"{style['fontSize']}px"
        
        # Font weight
        if 'fontWeight' in style:
            css['font-weight'] = str(style['fontWeight'])
        
        # Line height
        if 'lineHeightPx' in style:
            css['line-height'] = f"{style['lineHeightPx']}px"
        
        # Letter spacing
        if 'letterSpacing' in style:
            css['letter-spacing'] = f"{style['letterSpacing']}px"
        
        # Text alignment
        if 'textAlignHorizontal' in style:
            align_map = {
                'LEFT': 'left',
                'CENTER': 'center',
                'RIGHT': 'right',
                'JUSTIFIED': 'justify'
            }
            css['text-align'] = align_map.get(style['textAlignHorizontal'], 'left')
        
        # Text decoration
        if 'textDecoration' in style:
            if style['textDecoration'] == 'UNDERLINE':
                css['text-decoration'] = 'underline'
            elif style['textDecoration'] == 'STRIKETHROUGH':
                css['text-decoration'] = 'line-through'
        
        return css
    
    def convert_layout(self, node: Dict[str, Any], parent_bbox: dict = None) -> Dict[str, str]:
        """Convert Figma layout properties to CSS, positioned relative to parent if present"""
        css = {}
        
        # Position and dimensions
        if 'absoluteBoundingBox' in node:
            bbox = node['absoluteBoundingBox']
            if parent_bbox:
                rel_x = bbox['x'] - parent_bbox['x']
                rel_y = bbox['y'] - parent_bbox['y']
                css['position'] = 'absolute'
                css['left'] = f"{rel_x}px"
                css['top'] = f"{rel_y}px"
            else:
                css['position'] = 'absolute'
                css['left'] = f"{bbox['x']}px"
                css['top'] = f"{bbox['y']}px"
            css['width'] = f"{bbox['width']}px"
            css['height'] = f"{bbox['height']}px"
        
        # Auto layout properties
        if 'layoutMode' in node:
            if node['layoutMode'] == 'HORIZONTAL':
                css['display'] = 'flex'
                css['flex-direction'] = 'row'
            elif node['layoutMode'] == 'VERTICAL':
                css['display'] = 'flex'
                css['flex-direction'] = 'column'
            
            # Primary axis alignment
            if 'primaryAxisAlignItems' in node:
                align_map = {
                    'MIN': 'flex-start',
                    'CENTER': 'center',
                    'MAX': 'flex-end',
                    'SPACE_BETWEEN': 'space-between',
                    'SPACE_AROUND': 'space-around'
                }
                css['justify-content'] = align_map.get(node['primaryAxisAlignItems'], 'flex-start')
            
            # Counter axis alignment
            if 'counterAxisAlignItems' in node:
                align_map = {
                    'MIN': 'flex-start',
                    'CENTER': 'center',
                    'MAX': 'flex-end',
                    'BASELINE': 'baseline'
                }
                css['align-items'] = align_map.get(node['counterAxisAlignItems'], 'flex-start')
        
        # Padding
        if 'paddingLeft' in node:
            css['padding-left'] = f"{node['paddingLeft']}px"
        if 'paddingRight' in node:
            css['padding-right'] = f"{node['paddingRight']}px"
        if 'paddingTop' in node:
            css['padding-top'] = f"{node['paddingTop']}px"
        if 'paddingBottom' in node:
            css['padding-bottom'] = f"{node['paddingBottom']}px"
        
        # Gap
        if 'itemSpacing' in node:
            css['gap'] = f"{node['itemSpacing']}px"
        
        # Border radius
        if 'cornerRadius' in node:
            css['border-radius'] = f"{node['cornerRadius']}px"
        
        # Constraints (for responsive behavior)
        if 'constraints' in node:
            constraints = node['constraints']
            if constraints.get('horizontal') == 'CENTER':
                css['margin-left'] = 'auto'
                css['margin-right'] = 'auto'
            elif constraints.get('horizontal') == 'RIGHT':
                css['margin-left'] = 'auto'
        
        return css
    
    def convert_node_to_html(self, node: Dict[str, Any], level: int = 0, parent_bbox=None) -> str:
        """Convert a Figma node to HTML"""
        indent = "  " * level
        
        # Determine HTML tag based on node type
        tag_map = {
            'FRAME': 'div',
            'GROUP': 'div',
            'RECTANGLE': 'div',
            'ELLIPSE': 'div',
            'TEXT': 'p',
            'VECTOR': 'div',
            'COMPONENT': 'div',
            'INSTANCE': 'div',
            'BOOLEAN_OPERATION': 'div',
            'CANVAS': 'div'
        }
        
        tag = tag_map.get(node.get('type', 'FRAME'), 'div')
        
        # Generate CSS class name with safe characters (no colons)
        raw_id = node.get('id', 'unknown')
        safe_id = re.sub(r"[^A-Za-z0-9_-]", "-", raw_id)
        class_name = f"figma-{node.get('type', 'frame').lower()}-{safe_id}"
        
        # Handle text content
        content = ""
        if node.get('type') == 'TEXT' and 'characters' in node:
            content = node['characters']
        
        # Handle children
        children_html = ""
        if 'children' in node:
            this_bbox = node.get('absoluteBoundingBox')
            # children get THIS node's bbox as parent_bbox
            for child in node['children']:
                children_html += self.convert_node_to_html(child, level + 1, parent_bbox=this_bbox)
        
        # Combine content and children
        inner_content = content + children_html
        
        return f"{indent}<{tag} class=\"{class_name}\">{inner_content}</{tag}>\n"
    
    def convert_node_to_css(self, node: Dict[str, Any], parent_bbox=None) -> str:
        """Convert a Figma node to CSS"""
        raw_id = node.get('id', 'unknown')
        safe_id = re.sub(r"[^A-Za-z0-9_-]", "-", raw_id)
        class_name = f"figma-{node.get('type', 'frame').lower()}-{safe_id}"
        css_rules = []

        # Layout properties
        layout_css = self.convert_layout(node, parent_bbox)
        css_rules.extend([f"  {prop}: {value};" for prop, value in layout_css.items()])

        # Fills for background or text color
        if 'fills' in node:
            fill = node['fills'][0] if node['fills'] else None
            if node.get('type') == 'TEXT' and fill and fill.get('type') == 'SOLID':
                color = self.convert_color(fill.get('color', {}))
                css_rules.append(f"  color: {color};")
                # Do NOT set background for text node
            elif fill:
                background = self.convert_fill(node['fills'])
                if background != 'transparent':
                    css_rules.append(f"  background: {background};")

        # Text styling
        if node.get('type') == 'TEXT' and 'style' in node:
            text_css = self.convert_text_style(node['style'])
            css_rules.extend([f"  {prop}: {value};" for prop, value in text_css.items()])

        # Border
        if 'strokes' in node and node['strokes']:
            stroke = node['strokes'][0]
            if stroke.get('type') == 'SOLID':
                color = self.convert_color(stroke.get('color', {}))
                stroke_weight = stroke.get('strokeWeight', 1)
                css_rules.append(f"  border: {stroke_weight}px solid {color};")

        # Effects (shadows, blurs, etc.)
        if 'effects' in node:
            for effect in node['effects']:
                if effect.get('type') == 'DROP_SHADOW':
                    offset_x = effect.get('offset', {}).get('x', 0)
                    offset_y = effect.get('offset', {}).get('y', 0)
                    blur_radius = effect.get('radius', 0)
                    color = self.convert_color(effect.get('color', {}))
                    css_rules.append(f"  box-shadow: {offset_x}px {offset_y}px {blur_radius}px {color};")

        # Convert to CSS block
        if css_rules:
            css_block = f".{class_name} {{\n" + "\n".join(css_rules) + "\n}\n\n"
            return css_block

        return ""
    
    def generate_html_css(self, figma_data: Dict[str, Any]) -> tuple[str, str]:
        """Generate HTML and CSS from Figma data"""
        document = figma_data.get('document', {})
        
        # Start HTML
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Figma Design</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #ffffff;
        }
        .figma-container {
            position: relative;
            width: 100%;
            min-height: 100vh;
        }
"""
        
        # Start CSS
        css = ""
        
        # Process all nodes recursively
        def process_node(node: Dict[str, Any], parent_bbox=None):
            nonlocal css
            css += self.convert_node_to_css(node, parent_bbox)
            
            if 'children' in node:
                this_bbox = node.get('absoluteBoundingBox')
                for child in node['children']:
                    process_node(child, this_bbox)
        
        # Process document
        process_node(document)
        
        # Add CSS to HTML
        html += css
        html += "    </style>\n</head>\n<body>\n"
        html += '    <div class="figma-container">\n'
        
        # Add HTML content
        html += self.convert_node_to_html(document, 2, parent_bbox=None)
        
        html += "    </div>\n</body>\n</html>"
        
        return html, css
    
    def save_output(self, html: str, css: str):
        """Save HTML and CSS to files"""
        os.makedirs('output', exist_ok=True)
        
        with open('output/index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        with open('output/styles.css', 'w', encoding='utf-8') as f:
            f.write(css)
        
        print("Files saved to output/ directory:")
        print("- output/index.html")
        print("- output/styles.css")
    
    def run(self):
        """Main execution method"""
        print("Fetching Figma file...")
        figma_data = self.fetch_figma_file()
        
        print("Converting to HTML/CSS...")
        html, css = self.generate_html_css(figma_data)
        
        print("Saving output files...")
        self.save_output(html, css)
        
        print("Conversion complete!")

def main():
    """Main function"""
    try:
        converter = EnhancedFigmaConverter()
        converter.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your FIGMA_ACCESS_TOKEN")
        print("2. Copied the Figma file to your workspace")
        print("3. Updated the FIGMA_FILE_KEY in your .env file")

if __name__ == "__main__":
    main()
