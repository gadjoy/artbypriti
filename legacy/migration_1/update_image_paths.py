import os
import re

def get_image_ref_from_hugo_migration(filename):
    # Remove .md extension and construct hugo-migration path
    base_name = os.path.splitext(filename)[0]
    hugo_migration_path = f'hugo-migration/content/posts/{filename}'
    
    try:
        with open(hugo_migration_path, 'r') as f:
            content = f.read()
            # Find image reference in the format ![...](...)
            match = re.search(r'!\[(.*?)\]\((.*?)\)', content)
            if match:
                alt_text = match.group(1)
                image_path = match.group(2)
                return image_path
    except FileNotFoundError:
        print(f"Warning: Could not find original file in hugo-migration: {hugo_migration_path}")
    return None

def update_markdown_file(file_path):
    filename = os.path.basename(file_path)
    original_image_path = get_image_ref_from_hugo_migration(filename)
    
    if original_image_path:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Create new image reference with original path
        new_image_ref = f'![Art by Priti]({original_image_path})'
        
        # Replace existing image reference or add new one
        if re.search(r'!\[.*?\]\(.*?\)', content):
            content = re.sub(r'!\[.*?\]\(.*?\)', new_image_ref, content)
        else:
            # If no image reference exists, add it after the front matter
            content = re.sub(r'---\n(.*?\n)*?---\n', f'---\\g<0>\n{new_image_ref}\n', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
            print(f"Updated {filename} with original image path: {original_image_path}")
    else:
        print(f"Warning: No image reference found for {filename} in hugo-migration")

def main():
    posts_dir = 'content/posts'
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(posts_dir, filename)
            update_markdown_file(file_path)

if __name__ == '__main__':
    main() 