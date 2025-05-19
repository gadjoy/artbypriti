import os
import re
import json
from datetime import datetime
import html
import argparse
import csv

def transform_image_url(match, is_post=False):
    """
    Transform WordPress image URLs to Hugo static paths.
    Args:
        match: regex match object containing the URL
        is_post: boolean indicating if this is a post (in posts subdirectory)
    Returns:
        str: markdown image link with correct relative path
    """
    url = match.group(1)
    # Extract year/month and filename from WordPress URL
    url_match = re.search(r'/(\d{4})/(\d{2})/([^/]+)$', url)
    if url_match:
        year, month, filename = url_match.groups()
        # Create Hugo static path with proper relative path
        parent_dirs = "../../" if is_post else "../"
        return f'![]({parent_dirs}static/images/{year}/{month}/{filename})'
    return f'![]({parent_dirs}static/images/{os.path.basename(url)})'  # Fallback

def clean_html(content, is_post=False):
    """
    Clean HTML content and prepare it for markdown format.
    
    Args:
        content (str): The HTML content to clean
        is_post (bool): Whether this content is for a post (affects image paths)
    
    Returns:
        str: The cleaned content in markdown format
    """
    if not content:
        return ""
        
    # First decode HTML entities
    content = html.unescape(content)
    
    # Handle WordPress blocks
    content = re.sub(r'<!-- wp:.*?-->', '', content)
    content = re.sub(r'<!-- /wp:.*?-->', '', content)
    
    # Handle common escape sequences
    content = content.replace('\\"', '"').replace('\\n', '\n').replace('\\r', '').replace('\\t', ' ')
    
    # Convert HTML tags to markdown
    content = re.sub(r'<br\s*/?\s*>', '\n', content)
    content = re.sub(r'<p[^>]*>', '\n\n', content)
    content = re.sub(r'</p>', '', content)
    content = re.sub(r'<div[^>]*>', '\n\n', content)
    content = re.sub(r'</div>', '', content)
    
    # Transform figure/img combinations
    content = re.sub(
        r'<figure[^>]*>.*?<img[^>]*src="([^"]*)".*?</figure>',
        lambda m: transform_image_url(m, is_post),
        content,
        flags=re.DOTALL
    )
    
    # Transform any remaining direct img tags
    content = re.sub(
        r'<img[^>]*src="([^"]*)"[^>]*>',
        lambda m: transform_image_url(m, is_post),
        content
    )
    
    # Transform any markdown image links that still have WordPress URLs
    parent_dirs = "../../" if is_post else "../"
    content = re.sub(
        r'!\[\]\((http://[^)]+/wp-content/uploads/(\d{4})/(\d{2})/([^)]+))\)',
        rf'![]({parent_dirs}static/images/\2/\3/\4)',
        content
    )
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Remove any remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Fix multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Strip any extra whitespace
    content = content.strip()
    
    return content

def process_content_file(file_path, output_dir):
    """
    Process a WordPress export file and convert it to Hugo markdown files.
    
    Args:
        file_path (str): Path to the WordPress export file
        output_dir (str): Directory to output Hugo markdown files
    """
    # First, remove the artwork directory if it exists as it's redundant
    artwork_dir = os.path.join(output_dir, "artwork")
    if os.path.exists(artwork_dir):
        try:
            import shutil
            shutil.rmtree(artwork_dir)
            print(f"Removed redundant artwork directory: {artwork_dir}")
        except Exception as e:
            print(f"Warning: Could not remove artwork directory: {e}")
    
    encodings = ['utf-8', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # Read TSV file
                reader = csv.DictReader(f, delimiter='\t')
                
                for row in reader:
                    title = row.get('post_title', '').strip()
                    content = row.get('post_content', '').strip()
                    post_type = row.get('post_type', '').strip()
                    post_date = row.get('post_date', '').strip()
                    post_name = row.get('post_name', '').strip()
                    categories = row.get('categories', '').strip()
                    
                    if not title or not content:
                        continue
                    
                    # Determine if this is a post (affects image paths)
                    is_post = post_type != 'page'
                    
                    # Clean the content
                    clean_content = clean_html(content, is_post)
                    
                    # Format the date
                    try:
                        date_obj = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
                        formatted_date = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        formatted_date = post_date
                    
                    # Create Hugo front matter
                    front_matter = f"""---
title: "{title}"
date: {formatted_date}
draft: false
"""
                    
                    if categories and categories.lower() != "null":
                        front_matter += f"categories: [{categories}]\n"
                    
                    front_matter += "---\n\n"
                    
                    # Combine front matter and content
                    hugo_content = front_matter + clean_content
                    
                    # Create output path
                    if not post_name:
                        post_name = title.lower().replace(' ', '-')
                        post_name = re.sub(r'[^a-z0-9-]', '', post_name)
                    
                    # Put pages in root, posts in posts directory
                    if not is_post:
                        output_path = os.path.join(output_dir, f"{post_name}.md")
                    else:
                        posts_dir = os.path.join(output_dir, "posts")
                        os.makedirs(posts_dir, exist_ok=True)
                        output_path = os.path.join(posts_dir, f"{post_name}.md")
                    
                    # Write the file
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(hugo_content)
                    print(f"Created {output_path}")
                
                # If we get here, we successfully processed the file
                return
                
        except UnicodeDecodeError:
            # Try the next encoding
            continue
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            raise
    
    # If we get here, none of the encodings worked
    print(f"Failed to process {file_path}: Could not decode with any of the attempted encodings")

def main():
    parser = argparse.ArgumentParser(description='Convert WordPress export to Hugo markdown files')
    parser.add_argument('input_dir', help='Directory containing WordPress export files')
    parser.add_argument('output_dir', help='Directory to output Hugo markdown files')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process all files in input directory
    for filename in os.listdir(args.input_dir):
        if filename.endswith('.txt'):  # Only process text files
            input_path = os.path.join(args.input_dir, filename)
            print(f"Processing {input_path}...")
            try:
                process_content_file(input_path, args.output_dir)
            except Exception as e:
                print(f"Failed to process {input_path}: {e}")
                continue

if __name__ == '__main__':
    main() 