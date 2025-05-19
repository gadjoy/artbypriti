# Art by Priti

A portfolio website showcasing the artistic works of Priti, built using Hugo static site generator with the Gallery theme. The site features various collections of artwork including acrylic paintings, oil paintings, and mixed media works.

## 🎨 Collections

The portfolio includes various art collections:
- Acrylic on Canvas
- Acrylic and Oil on Canvas
- Acrylic with Texture
- Oil on Canvas
- Water Color on Paper
- Glass Tiles on Wooden Plate (Mosaic)
- Mixed Media Works

## 🛠 Technical Stack

- **Static Site Generator**: [Hugo](https://gohugo.io/)
- **Theme**: [Gallery Theme](https://github.com/nicokaiser/hugo-theme-gallery/)
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions

## 🚀 Local Development

### Prerequisites

1. Install [Hugo Extended](https://gohugo.io/installation/) (version 0.123.0 or later)
2. Git

### Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:YourUsername/artbypriti.git
   cd artbypriti
   ```

2. Start the Hugo development server:
   ```bash
   hugo server -D
   ```

3. View the site at: `http://localhost:1313/`

## 📝 Content Management

The site content is organized in the following structure:

```
content/
├── about/
├── acrylic-on-canvas/
├── acrylic-and-oil-on-canvas/
├── acrylic-on-canvas-with-texture/
├── oil-on-canvas/
├── water-color-on-paper/
└── glass-tiles-on-a-wooden-plate-(mosaic)/
```

Each artwork is stored in its own directory with:
- `index.md`: Metadata and description
- Image files in various resolutions

## 🔄 Deployment

The site is automatically deployed to GitHub Pages using GitHub Actions when changes are pushed to the main branch. The deployment workflow:

1. Builds the Hugo site
2. Minifies the output
3. Deploys to GitHub Pages

## 🌐 Domain Configuration

To use a custom domain:

1. Add your domain in GitHub repository settings under Pages
2. Configure your DNS with the following records:
   ```
   Type  Name   Value
   A     @      185.199.108.153
   A     @      185.199.109.153
   A     @      185.199.110.153
   A     @      185.199.111.153
   CNAME www    yourusername.github.io
   ```

## 📄 License

All artwork and images are copyrighted by Priti. The website code is available under the MIT license.

## 🤝 Contributing

For technical issues or suggestions:
1. Create an issue
2. Fork the repository
3. Create a pull request

For content updates, please contact the site owner directly.

## 📞 Contact

For inquiries about the artwork or the artist, please use the contact form on the website.
