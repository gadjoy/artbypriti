import os
import shutil
import re
import yaml
from pathlib import Path

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_front_matter(content):
    """Extract front matter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if match:
        try:
            front_matter = yaml.safe_load(match.group(1))
            content = match.group(2)
            return front_matter, content
        except yaml.YAMLError:
            return {}, content
    return {}, content

def extract_first_image(content):
    """Extract the first image path from markdown content."""
    match = re.search(r'!\[.*?\]\((.*?)\)', content)
    if match:
        return match.group(1).strip()
    return None

def create_gallery_structure():
    # Create main galleries based on categories
    posts_dir = Path('content/posts')
    if not posts_dir.exists():
        print("Posts directory not found!")
        return

    # Track categories and their posts
    categories = {}
    
    # Process each post
    for post_file in posts_dir.glob('*.md'):
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        front_matter, post_content = extract_front_matter(content)
        post_categories = front_matter.get('categories', ['uncategorized'])
        
        # Get the first image
        image_path = extract_first_image(post_content)
        if not image_path:
            continue
            
        # Clean up image path
        image_path = image_path.replace('../static/', '')
        image_path = image_path.replace('static/', '')
        
        for category in post_categories:
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'title': front_matter.get('title', post_file.stem),
                'date': front_matter.get('date', ''),
                'image': image_path,
                'description': front_matter.get('description', ''),
                'original_file': post_file
            })

    # Create gallery structure
    for category, posts in categories.items():
        category_slug = slugify(category)
        category_dir = Path(f'content/{category_slug}')
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Create category index.md with front matter
        front_matter = {
            'title': category,
            'description': f"Collection of {category.lower()} artwork",
            'weight': 1,
            'menu': {
                'main': {
                    'weight': 1
                }
            },
            'params': {
                'featured_image': os.path.basename(posts[0]['image']) if posts else '',
                'theme': 'light',
                'sort_by': 'Name'
            }
        }
        
        # Add resources for each image
        resources = []
        for post in posts:
            # Copy image to gallery directory
            src_image = Path(f'static/{post["image"]}')
            if src_image.exists():
                dest_image = category_dir / src_image.name
                shutil.copy2(src_image, dest_image)
                
                # Add resource entry
                resources.append({
                    'src': src_image.name,
                    'name': post['title'],
                    'params': {
                        'description': post.get('description', ''),
                        'date': post.get('date', '')
                    }
                })
        
        # Add resources to front matter
        if resources:
            front_matter['resources'] = resources
            # Set the first image as cover
            front_matter['resources'][0]['params']['cover'] = True
        
        # Write category index.md
        with open(category_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write('---\n')
            yaml.dump(front_matter, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            f.write('---\n')

    # Create main _index.md
    main_front_matter = {
        'title': 'Art by Priti',
        'description': 'A collection of artworks showcasing creativity and passion',
        'menu': {
            'main': {
                'name': 'Home',
                'weight': -1
            }
        }
    }
    
    # Add first image from any category as cover
    for category in categories.values():
        if category:
            first_image = os.path.basename(category[0]['image'])
            main_front_matter['resources'] = [{
                'src': first_image,
                'params': {
                    'cover': True
                }
            }]
            # Copy the cover image to content root
            src_image = Path(f'static/{category[0]["image"]}')
            if src_image.exists():
                shutil.copy2(src_image, Path('content') / src_image.name)
            break
    
    with open('content/_index.md', 'w', encoding='utf-8') as f:
        f.write('---\n')
        yaml.dump(main_front_matter, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        f.write('---\n')

if __name__ == '__main__':
    create_gallery_structure() 