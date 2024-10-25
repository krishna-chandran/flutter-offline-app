import os
import re
from bs4 import BeautifulSoup

# Root directory where your static files are located
root_dir = r"C:\\Users\\sivab\\OneDrive\\Pictures\\static_dir"

def update_links_in_file(file_path, current_dir):
    # Open the file and parse the HTML content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Find all <a> tags with href and <img>/<script> tags with src
    tags_with_links = soup.find_all(['a', 'img', 'script', 'link'], href=True) + soup.find_all(['img', 'script'], src=True)
    
    # Find all <button> elements with the "onclick" attribute
    buttons_with_onclick = soup.find_all('button', onclick=True)
    
    # Find all <a> tags with the onclick attribute
    a_tags_with_onclick = soup.find_all('a', onclick=True)

    # Update links in <a>, <img>, <script>, <link>, and <iframe> tags
    for tag in tags_with_links:
        # Update links in <a> tags
        if tag.name == 'a' and tag.has_attr('href'):
            link = tag['href']
            new_link = update_link(link, current_dir)
            if new_link:
                tag['href'] = new_link

            # Additional condition: append /index.html if the link does not contain "static"
            if 'static' not in link:
                tag['href'] += '/index.html'
        
        # Update src attributes in <img> and <script> tags
        elif tag.name in ['img', 'script'] and tag.has_attr('src'):
            link = tag['src']
            new_link = update_link(link, current_dir)
            if new_link:
                tag['src'] = new_link
        
        # Update href attributes in <link> tags
        elif tag.name == 'link' and tag.has_attr('href'):
            link = tag['href']
            new_link = update_link(link, current_dir)
            if new_link:
                tag['href'] = new_link

    # Update "onclick" attributes in <button> elements
    for button in buttons_with_onclick:
        onclick_value = button['onclick']
        new_onclick_value = update_onclick(onclick_value)
        if new_onclick_value:
            button['onclick'] = new_onclick_value
            
    # Update <video> tags and their <source> elements
    for video in soup.find_all('video'):
        for source in video.find_all('source'):
            if source.has_attr('src'):
                video_src = source['src']
                new_src = update_link(video_src, current_dir)
                if new_src:
                    source['src'] = new_src

    # Update <iframe> tags and their src attributes
    for iframe in soup.find_all('iframe'):
        if iframe.has_attr('src'):
            iframe_src = iframe['src']
            new_src = update_link(iframe_src, current_dir)
            if new_src:
                iframe['src'] = new_src

    # Update <a> tags with "onclick" attributes
    for tag in a_tags_with_onclick:
        if tag.has_attr('onclick'):
            # Extract the URL from the onclick attribute
            match = re.search(r"location\.href='([^']+)'", tag['onclick'])
            if match:
                url = match.group(1)
                parts = url.strip('/').split('/')

                # Get the last part, which is the page number (e.g., '15')
                last_part = parts[-1]

                # Update the onclick to set it to the desired format
                tag['onclick'] = f"location.href='{last_part}/index.html';"

                # Optionally, remove href attribute if it's not needed
                if tag.has_attr('href'):
                    del tag['href']

    # Handle inline "style" attributes with "background-image"
    divs_with_bg_image = soup.find_all('div', style=True)
    for div in divs_with_bg_image:
        style_value = div['style']
        # Match the URL inside the background-image CSS
        match = re.search(r"background-image: url\('([^']+)'\)", style_value)
        if match:
            bg_url = match.group(1)
            new_bg_url = update_link(bg_url, current_dir)
            if new_bg_url:
                # Replace backslashes with forward slashes in the updated URL
                new_bg_url = new_bg_url.replace('\\', '/')
                # Replace the background-image URL in the style attribute
                div['style'] = style_value.replace(bg_url, new_bg_url)


    # Save the updated HTML back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def update_link(link, current_dir):
    # Treat %20 as a space in URLs
    link = link.replace('%20', ' ')

    # Ignore links that are absolute (start with http:// or https://) or empty
    if re.match(r'^https?://', link) or link == "":
        return None

    # Remove leading slashes if they exist
    if link.startswith('/'):
        link = link[1:]

    # Determine the absolute path of the linked file based on current_dir
    linked_file_path = os.path.join(root_dir, link)

    # If the linked file exists, calculate relative path
    if os.path.exists(linked_file_path):
        relative_path = os.path.relpath(linked_file_path, current_dir)
        # Adjust the relative path if necessary
        if not relative_path.startswith('.'):
            relative_path = f"./{relative_path}"
        return relative_path

    return None

def update_onclick(onclick_value):
    """
    Modify the URL in the 'onclick' based on folder structure rules.
    """
    # Pattern to extract the URL from onclick
    match = re.search(r"window\.location\.href='([^']+)'", onclick_value)
    
    if match:
        url = match.group(1)

        # Split the URL into parts by '/'
        parts = url.strip('/').split('/')

        # Remove the first word from the URL
        if len(parts) > 1:
            parts = parts[1:]

        # Check if 'chapter' and 'page' are present in the URL path
        if 'chapter' in parts and 'page' in parts:
            # If 'page' is inside 'chapter', use '../../../'
            new_url = '../../../' + '/'.join(parts) + '/index.html'
        elif 'chapter' in parts:
            # If only 'chapter' is present, use '../../'
            new_url = '../../' + '/'.join(parts) + '/index.html'
        else:
            # Default to '../../' for other cases
            new_url = '../../' + '/'.join(parts) + '/index.html'

        # Replace the original onclick value with the new one
        new_onclick_value = f"window.location.href='{new_url}'"
        
        return new_onclick_value

    return None

def process_html_files():
    # Traverse through the entire root_dir and process HTML files
    for subdir, dirs, files in os.walk(root_dir):
        # Skip 'WebViewer' and 'mediafiles' folders
        if 'WebViewer' in subdir or 'mediafiles' in subdir:
            continue
            
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(subdir, file)
                update_links_in_file(file_path, subdir)

if __name__ == '__main__':
    process_html_files()
