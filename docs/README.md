# FarmVision Landing Page

This directory contains the landing page for FarmVision, hosted on GitHub Pages.

## 🌐 Live Site

**URL:** https://chronocoders.github.io/farmvision

## 📁 Structure

```
docs/
├── index.html          # Main landing page
├── css/
│   └── style.css       # Styles
├── js/
│   └── main.js         # JavaScript
├── _config.yml         # GitHub Pages config
└── README.md           # This file
```

## 🚀 Features

- **Responsive Design** - Works on all devices
- **Modern UI** - Clean, professional design
- **Animations** - Smooth scroll and fade-in effects
- **Interactive** - Tab switching, code copying
- **SEO Optimized** - Meta tags, Open Graph, Twitter Cards
- **Fast Loading** - Optimized assets and code

## 🎨 Sections

1. **Hero** - Main introduction with CTA buttons
2. **Features** - 6 key features with descriptions
3. **Technology** - Tech stack showcase
4. **Demo** - Demo placeholder (can be updated)
5. **Installation** - Quick start with tabs (Docker, Manual, GitHub)
6. **Documentation** - Links to all docs
7. **CTA** - Final call-to-action
8. **Footer** - Links and information

## 🛠️ Local Development

To test locally:

```bash
# Simple HTTP server
cd docs
python -m http.server 8080

# Or use live-server
npm install -g live-server
cd docs
live-server
```

Visit: http://localhost:8080

## 🔧 Customization

### Update Colors

Edit `css/style.css`:

```css
:root {
    --primary-color: #10b981;  /* Green */
    --secondary-color: #3b82f6; /* Blue */
}
```

### Update Content

Edit `index.html` sections:
- Hero text
- Feature descriptions
- Installation commands
- Links and URLs

### Add Images

Place images in `docs/assets/` and update paths in HTML:

```html
<img src="assets/screenshot.png" alt="Screenshot">
```

## 📱 Mobile Menu

Mobile menu automatically activates on screens < 768px:
- Hamburger icon toggles menu
- Smooth animations
- Click outside to close

## 🎯 SEO

The page includes:
- Meta description
- Open Graph tags (Facebook)
- Twitter Card tags
- Structured data
- Sitemap (auto-generated)

## 🔗 Links to Update

Before going live, update these links in `index.html`:

1. GitHub repository URLs
2. Wiki links
3. Documentation links
4. Social media links (if any)
5. Email addresses

## 📦 GitHub Pages Setup

### Enable GitHub Pages

1. Go to repository **Settings**
2. Navigate to **Pages** section
3. Source: Deploy from **branch**
4. Branch: **main**
5. Folder: **/docs**
6. Save

### Custom Domain (Optional)

To use a custom domain:

1. Create `CNAME` file in `docs/`:
   ```
   farmvision.com
   ```

2. Configure DNS:
   - Add CNAME record pointing to `chronocoders.github.io`
   - Or A records to GitHub Pages IPs

3. Enable HTTPS in GitHub Pages settings

## 🐛 Troubleshooting

### Page Not Loading

- Check if GitHub Pages is enabled in settings
- Verify branch is set to `main` and folder to `/docs`
- Wait 1-2 minutes for deployment
- Check for 404 errors in browser console

### CSS Not Loading

- Verify file paths are correct
- Check if `_config.yml` baseurl matches
- Hard refresh browser (Ctrl+F5)

### Mobile Menu Not Working

- Check if JavaScript is enabled
- Verify `js/main.js` is loading
- Check browser console for errors

## 🔄 Updates

To update the landing page:

1. Edit files in `docs/` directory
2. Commit and push to `main` branch
3. GitHub Pages will auto-deploy (1-2 minutes)

```bash
git add docs/
git commit -m "Update landing page"
git push origin main
```

## 📊 Analytics

To add Google Analytics:

1. Uncomment in `_config.yml`:
   ```yaml
   google_analytics: UA-XXXXXXXXX-X
   ```

2. Or add directly to `index.html`:
   ```html
   <!-- Google Analytics -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXXXXXX-X"></script>
   ```

## 🎨 Design Credits

- **Colors:** Custom gradient scheme
- **Fonts:** Inter from Google Fonts
- **Icons:** Font Awesome 6
- **Animation:** Custom CSS transitions

## 📝 License

Same as main project - MIT License

## 🙋 Support

For issues with the landing page:
- Open an issue on GitHub
- Contact: support@farmvision.com
- Check documentation: https://github.com/ChronoCoders/farmvision/wiki

---

**Last Updated:** January 2025
**Version:** 1.0.0
